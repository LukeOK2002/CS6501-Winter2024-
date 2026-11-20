"""kz.py - flat-vector, Kurzgesagt-like rendering toolkit for portrait reels (skia-python).

Usage from a scene script:
    import sys; sys.path.insert(0, '<skill>/scripts')
    from kz import *
    def draw(cv, t, fi): ...          # draw one frame at time t (seconds)
    run('my_reel', 12.0, draw)        # -> ./my_reel.mp4   (STILLS=1.0,4.5 env -> PNG stills only)

Output goes to $KZ_OUT (default: current working directory).
"""
import os, math, random, re, subprocess
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('KZ_FONTS', os.path.join(HERE, '..', 'assets', 'fonts'))


def _tf(n):
    tf = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, n))
    if tf is None:
        raise FileNotFoundError(f'font {n} not found in {FONT_DIR}')
    return tf


TF = {'med': _tf('SG-Medium.ttf'), 'semi': _tf('SG-SemiBold.ttf'),
      'bold': _tf('SG-Bold.ttf'), 'od': _tf('OD.otf')}
_FC = {}


def font(k, size):
    key = (k, round(size, 1))
    if key not in _FC:
        f = skia.Font(TF[k], size)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _FC[key] = f
    return _FC[key]


# ---------------------------------------------------------------- colour
def hx(h):
    if isinstance(h, tuple):
        return h[:3]
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def col(c, a=255):
    r, g, b = hx(c)
    return skia.ColorSetARGB(int(max(0, min(255, a))), r, g, b)


def cc(c):
    if isinstance(c, tuple) and len(c) == 2:
        return col(c[0], c[1])
    return col(c)


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dark(c, f=.2):
    return mix(c, (40, 20, 70), f)


def light(c, f=.2):
    return mix(c, (255, 250, 240), f)


# ---------------------------------------------------------------- easing
def clamp(x, a=0., b=1.):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b != a else float(t >= a)


def ease(x):
    x = clamp(x)
    return 4 * x * x * x if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ein(x):
    x = clamp(x)
    return x * x * x


def eback(x, s=1.7):
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


# ---------------------------------------------------------------- paint/shapes
def paint(c='#ffffff', a=255, stroke=0, blur=0, shader=None, blend=None, cap='round'):
    p = skia.Paint(AntiAlias=True)
    p.setColor(col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == 'round' else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
    if blend is not None:
        p.setBlendMode(blend)
    return p


def lin(x0, y0, x1, y1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [cc(c) for c in cols], pos)


def rad(x, y, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(x, y), max(r, 0.01), [cc(c) for c in cols], pos)


def R(l, t, r, b):
    return skia.Rect.MakeLTRB(l, t, r, b)


def rrp(l, t, r, b, rd):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(R(l, t, r, b), rd, rd))
    return p


def cp(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, max(r, 0.01))
    return p


def op(l, t, r, b):
    p = skia.Path()
    p.addOval(R(l, t, r, b))
    return p


def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def fill(cv, path, c, a=255, **k):
    cv.drawPath(path, paint(c, a, **k))


def glow(cv, x, y, r, c, a, mid=None):
    if r <= 0 or a <= 0:
        return
    if mid is None:
        sh = rad(x, y, r, [(c, a), (c, a * .35), (c, 0)], [0, .4, 1])
    else:
        sh = rad(x, y, r, [(c, a), (c, 0)])
    cv.drawCircle(x, y, r, paint(shader=sh))


def shaded(cv, path, base, shade=None, dx=-6, dy=-6, hi=None):
    """Fill path with base colour and a soft-edged crescent of shade on the lower-right."""
    shade = shade or dark(base, .22)
    cv.save()
    cv.clipPath(path, skia.ClipOp.kIntersect, True)
    cv.drawPath(path, paint(shade))
    cv.translate(dx, dy)
    cv.drawPath(path, paint(base))
    if hi:
        cv.translate(dx * .9, dy * .9)
        cv.drawPath(path, paint(hi[0], hi[1]))
    cv.restore()


def text(cv, s, x, y, f, c='#ffffff', a=255, anchor='c', track=0, shadow=0):
    """Draw text. y is the visual middle of cap height."""
    w = f.measureText(s) + track * max(0, len(s) - 1)
    if anchor == 'c':
        x0 = x - w / 2
    elif anchor == 'r':
        x0 = x - w
    else:
        x0 = x
    base = y + f.getSize() * 0.35
    if shadow:
        _draw_str(cv, s, x0, base + shadow * .5, f, paint('#0a0820', a * .55, blur=shadow), track)
    _draw_str(cv, s, x0, base, f, paint(c, a), track)
    return w


def _draw_str(cv, s, x, y, f, p, track):
    if not track:
        cv.drawString(s, x, y, f, p)
        return
    for ch in s:
        cv.drawString(ch, x, y, f, p)
        x += f.measureText(ch) + track


# ---------------------------------------------------------------- subtitles
def parse(s):
    lines = []
    for ln in s.split('\n'):
        toks, i = [], 0
        for m in re.finditer(r'\{(\w+):([^}]*)\}', ln):
            if m.start() > i:
                toks.append((ln[i:m.start()], 'n'))
            toks.append((m.group(2), m.group(1)))
            i = m.end()
        if i < len(ln):
            toks.append((ln[i:], 'n'))
        lines.append(toks)
    return lines


SUBC = {'n': '#FFFFFF', 'hl': '#FFC94A', 'od': '#FFC94A', 'red': '#FF6B6B'}


def subtitle(cv, t, a, b, s, cy=1430, size=58, fade_out=True):
    if not (a <= t < b):
        return
    lines = parse(s)
    if len(lines) >= 3:
        size *= .88
    lh = size * 1.28
    y0 = cy - (len(lines) - 1) * lh / 2
    out = 1 - ein(prog(t, b - .3, b)) if fade_out else 1
    for i, toks in enumerate(lines):
        def fnt(st, sz):
            return font('od', sz * .9) if st == 'od' else font('semi', sz)

        def mw(tx, st, sz):
            f = fnt(st, sz)
            return f.measureText(tx) * (.8 if st == 'od' else 1)
        sz = size
        wtot = sum(mw(tx, st, sz) for tx, st in toks)
        if wtot > 960:
            sz *= 960 / wtot
            wtot = 960
        ap = eout(prog(t, a + .08 * i, a + .08 * i + .45))
        al = 255 * ap * out
        y = y0 + i * lh + (1 - ap) * 26
        x = W / 2 - wtot / 2
        for tx, st in toks:
            f = fnt(st, sz)
            base = y + sz * .35
            if st == 'od':
                xx = x
                for ch in tx:
                    cv.drawString(ch, xx, base + 4, f, paint('#08061a', al * .7, blur=7))
                    cv.drawString(ch, xx, base, f, paint(SUBC['od'], al))
                    xx += f.measureText(ch) * .8
            else:
                cv.drawString(tx, x, base + 4, f, paint('#08061a', al * .7, blur=7))
                cv.drawString(tx, x, base, f, paint(SUBC.get(st, '#fff'), al))
            x += mw(tx, st, sz)


def scrim(cv, top=1150, a=200):
    cv.drawRect(R(0, top, W, H), paint(shader=lin(0, top, 0, H, [('#05031a', 0), ('#05031a', a * .75), ('#05031a', a)], [0, .45, 1])))


def vignette(cv, a=150, cx=W / 2, cy=860):
    cv.drawRect(R(0, 0, W, H), paint(shader=rad(cx, cy, 1250, [('#000000', 0), ('#000000', 0), ('#05031a', a)], [0, .5, 1])))


# ---------------------------------------------------------------- grain
_rng = np.random.default_rng(3)
GRAIN = []
for _i in range(6):
    n = _rng.integers(60, 196, (H // 2, W // 2), dtype=np.uint8)
    arr = np.dstack([n, n, n, np.full_like(n, 255)])
    GRAIN.append(skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType))


def grain(cv, f, a=26):
    p = paint('#ffffff', a, blend=skia.BlendMode.kOverlay)
    cv.drawImageRect(GRAIN[f % len(GRAIN)], R(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear), p)


# ---------------------------------------------------------------- characters
INK = (36, 24, 48)


def _arm(cv, pts, sleeve, w):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    cv.save()
    cv.translate(w * .1, w * .12)
    cv.drawPath(p, paint(dark(sleeve, .28), stroke=w))
    cv.restore()
    cv.drawPath(p, paint(sleeve, stroke=w))


def hand(cv, x, y, r, skin):
    shaded(cv, cp(x, y, r), skin, dx=-r * .3, dy=-r * .3)


def face(cv, x, y, r, f, sp):
    lx, ly = f.get('look', (0, 0))
    if f.get('blush', 1):
        for s in (-1, 1):
            glow(cv, x + s * .55 * r, y + .32 * r, .26 * r, f.get('blushc', (255, 120, 140)), 110 * f.get('blush', 1), mid=1)
    if sp.get('freckles'):
        for s in (-1, 1):
            for fx, fy in ((.42, .22), (.53, .30), (.64, .22), (.5, .16)):
                cv.drawCircle(x + s * fx * r, y + fy * r, .025 * r, paint((214, 128, 92), 200))
    ex = .34 * r
    ey = y + .06 * r
    kind = f.get('eyes', 'open')
    brows = f.get('brows', ((0, 0), (0, 0)))
    for i, s in enumerate((-1, 1)):
        cx = x + s * ex + lx * .07 * r
        cy = ey + ly * .07 * r
        if kind == 'happy':
            p = skia.Path()
            p.moveTo(cx - .11 * r, cy + .03 * r)
            p.quadTo(cx, cy - .12 * r, cx + .11 * r, cy + .03 * r)
            cv.drawPath(p, paint(INK, stroke=.06 * r))
        else:
            sz = 1.22 if kind == 'wide' else 1.0
            sq = f.get('squint', 0)
            ow, oh = .095 * r * sz, .125 * r * sz * (1 - .45 * sq)
            cv.drawOval(R(cx - ow, cy - oh, cx + ow, cy + oh), paint(INK))
            cv.drawCircle(cx + .03 * r, cy - .045 * r, .034 * r * sz, paint('#ffffff'))
        ang, rs = brows[i]
        bx = x + s * .36 * r
        by = y - .25 * r - rs * r
        a = math.radians(ang)
        pin = (bx - s * .13 * r * math.cos(a), by + .13 * r * math.sin(a))
        pout = (bx + s * .13 * r * math.cos(a), by - .13 * r * math.sin(a))
        bc = sp.get('brow', dark(sp['hair'], .35))
        cv.drawPath(poly([pin, pout], close=False), paint(bc, stroke=.065 * r))
    my = y + .40 * r
    m = f.get('mouth', .6)
    mo = f.get('mopen', 0)
    w = .17 * r
    if mo > 0.01:
        p = skia.Path()
        p.moveTo(x - w * 1.1, my - .02 * r)
        p.cubicTo(x - w, my + .32 * r * mo, x + w, my + .32 * r * mo, x + w * 1.1, my - .02 * r)
        p.quadTo(x, my + .03 * r, x - w * 1.1, my - .02 * r)
        p.close()
        cv.save()
        cv.clipPath(p, skia.ClipOp.kIntersect, True)
        cv.drawPath(p, paint((132, 36, 62)))
        cv.drawCircle(x, my + .3 * r * mo, .13 * r, paint((240, 110, 120)))
        cv.restore()
    elif f.get('wavy'):
        p = skia.Path()
        p.moveTo(x - w, my)
        n = 4
        for k in range(n):
            x1 = x - w + (k + .5) * 2 * w / n
            x2 = x - w + (k + 1) * 2 * w / n
            p.quadTo(x1, my + (.05 if k % 2 else -.05) * r, x2, my)
        cv.drawPath(p, paint(INK, stroke=.05 * r))
    else:
        if m < 0:
            w *= .85
        p = skia.Path()
        p.moveTo(x - w, my)
        p.quadTo(x, my + m * .17 * r, x + w, my)
        cv.drawPath(p, paint(INK, stroke=.055 * r))
    if sp.get('glasses'):
        for s in (-1, 1):
            cv.drawCircle(x + s * ex, ey, .17 * r, paint(INK, stroke=.04 * r))
        cv.drawPath(poly([(x - ex + .17 * r, ey), (x + ex - .17 * r, ey)], False), paint(INK, stroke=.04 * r))


def _back_hair(cv, x, y, r, sp):
    st, hc = sp['style'], sp['hair']
    if st == 'long':
        p = skia.Path()
        p.moveTo(x - 1.08 * r, y)
        p.arcTo(R(x - 1.08 * r, y - 1.1 * r, x + 1.08 * r, y + 1.06 * r), 180, 180, False)
        p.cubicTo(x + 1.15 * r, y + .9 * r, x + 1.3 * r, y + 1.7 * r, x + 1.2 * r, y + 2.05 * r)
        p.quadTo(x + 1.12 * r, y + 2.3 * r, x + .8 * r, y + 2.25 * r)
        p.lineTo(x - .8 * r, y + 2.25 * r)
        p.quadTo(x - 1.12 * r, y + 2.3 * r, x - 1.2 * r, y + 2.05 * r)
        p.cubicTo(x - 1.3 * r, y + 1.7 * r, x - 1.15 * r, y + .9 * r, x - 1.08 * r, y)
        p.close()
        shaded(cv, p, dark(hc, .12), dark(hc, .3), dx=-.12 * r, dy=0)
    elif st == 'curly':
        p = skia.Path()
        for k in range(15):
            a = math.radians(160 + k * 220 / 14)
            p.addCircle(x + math.cos(a) * 1.05 * r, y - .1 * r + math.sin(a) * 1.05 * r, .38 * r)
        p.addCircle(x, y - .35 * r, 1.1 * r)
        shaded(cv, p, hc, dark(hc, .3), dx=-.1 * r, dy=-.1 * r)
    elif st == 'bob':
        shaded(cv, rrp(x - 1.18 * r, y - 1.15 * r, x + 1.18 * r, y + .75 * r, .95 * r), hc, dark(hc, .3), dx=-.1 * r, dy=-.05 * r)
    elif st == 'bun':
        shaded(cv, cp(x + .05 * r, y - 1.12 * r, .42 * r), hc, dark(hc, .3), dx=-.08 * r, dy=-.08 * r)
    elif st == 'hijab':
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(R(x - 1.25 * r, y - 1.28 * r, x + 1.25 * r, y + 1.9 * r), 1.15 * r, 1.15 * r))
        shaded(cv, p, hc, dark(hc, .3), dx=-.12 * r, dy=-.05 * r)


def _front_hair(cv, x, y, r, sp):
    st, hc = sp['style'], sp['hair']
    head = cp(x, y, r * 1.005)
    if st == 'long':
        cv.save()
        cv.clipPath(cp(x, y, r * 1.06), skia.ClipOp.kIntersect, True)
        p = skia.Path()
        p.addOval(R(x - 1.3 * r, y - 1.4 * r, x + .5 * r, y - .4 * r))
        p.addOval(R(x - .3 * r, y - 1.3 * r, x + 1.25 * r, y - .52 * r))
        shaded(cv, p, hc, dark(hc, .25), dx=-.06 * r, dy=-.08 * r)
        cv.restore()
        for s in (-1, 1):
            q = skia.Path()
            q.moveTo(x + s * .78 * r, y - .55 * r)
            q.cubicTo(x + s * 1.18 * r, y - .1 * r, x + s * 1.12 * r, y + .9 * r, x + s * 1.02 * r, y + 1.75 * r)
            q.quadTo(x + s * .9 * r, y + 1.95 * r, x + s * .78 * r, y + 1.7 * r)
            q.cubicTo(x + s * .86 * r, y + .9 * r, x + s * .9 * r, y + .2 * r, x + s * .78 * r, y - .55 * r)
            q.close()
            shaded(cv, q, hc, dark(hc, .25), dx=-.05 * r * s, dy=-.05 * r)
    elif st in ('short', 'buzz', 'curly', 'bun'):
        p = skia.Path()
        top = {'short': 1.42, 'buzz': 1.3, 'curly': 1.5, 'bun': 1.4}[st]
        p.moveTo(x - 1.03 * r, y + .02 * r)
        p.cubicTo(x - 1.1 * r, y - top * r, x + 1.1 * r, y - top * r, x + 1.03 * r, y + .02 * r)
        if st == 'short':
            p.lineTo(x + .93 * r, y - .22 * r)
            p.quadTo(x + .78 * r, y - .5 * r, x + .45 * r, y - .52 * r)
            p.quadTo(x + .1 * r, y - .44 * r, x - .15 * r, y - .62 * r)
            p.quadTo(x - .62 * r, y - .55 * r, x - .93 * r, y - .22 * r)
        else:
            p.lineTo(x + .92 * r, y - .12 * r)
            p.quadTo(x, y - .72 * r, x - .92 * r, y - .12 * r)
        p.close()
        if st == 'short':
            for k in range(7):
                a = math.radians(205 + k * 21)
                p.addCircle(x + math.cos(a) * .9 * r, y - .05 * r + math.sin(a) * .9 * r, .2 * r)
            p.addOval(R(x - .5 * r, y - 1.18 * r, x + .55 * r, y - .72 * r))
        if st == 'buzz':
            cv.save()
            cv.clipPath(head, skia.ClipOp.kIntersect, True)
        shaded(cv, p, hc, dark(hc, .3), dx=-.08 * r, dy=-.08 * r, hi=(light(hc, .25), 70) if st == 'short' else None)
        if st == 'buzz':
            cv.restore()
        if st == 'short':
            for s in (-1, 1):
                cv.drawPath(poly([(x + s * .96 * r, y - .25 * r), (x + s * 1.0 * r, y - .25 * r), (x + s * .99 * r, y + .02 * r)]), paint(hc))
    elif st == 'bob':
        cv.save()
        cv.clipPath(cp(x, y, r * 1.05), skia.ClipOp.kIntersect, True)
        shaded(cv, rrp(x - 1.2 * r, y - 1.3 * r, x + 1.2 * r, y - .3 * r, .3 * r), hc, dark(hc, .25), dx=-.06 * r, dy=-.06 * r)
        cv.restore()
        for s in (-1, 1):
            cv.drawPath(rrp(x + s * 1.0 * r - .2 * r, y - .4 * r, x + s * 1.0 * r + .2 * r, y + .72 * r, .18 * r), paint(hc))
    elif st == 'hijab':
        cv.drawCircle(x, y, r * .98, paint(sp['hair'], stroke=.2 * r))
    if sp.get('beard'):
        cv.save()
        cv.clipPath(head, skia.ClipOp.kIntersect, True)
        b = skia.Path()
        b.addOval(R(x - 1.05 * r, y - .2 * r, x + 1.05 * r, y + 1.15 * r))
        b2 = skia.Path()
        b2.addOval(R(x - .78 * r, y - .62 * r, x + .78 * r, y + .52 * r))
        b = skia.Op(b, b2, skia.PathOp.kDifference_PathOp)
        cv.drawPath(b, paint(sp.get('beardc', hc)))
        cv.restore()


def head_group(cv, x, y, r, sp, f, tilt=0):
    """Head centred at (x,y), radius r."""
    cv.save()
    cv.rotate(tilt, x, y + 1.1 * r)
    _back_hair(cv, x, y, r, sp)
    skin = sp['skin']
    if sp['style'] not in ('long', 'hijab', 'bob'):
        for s in (-1, 1):
            shaded(cv, cp(x + s * .98 * r, y + .08 * r, .2 * r), skin, dx=-.05 * r, dy=-.05 * r)
    rr = r * (.86 if sp['style'] == 'hijab' else 1)
    shaded(cv, cp(x, y, rr), skin, dark(skin, .16), dx=-.12 * r, dy=-.1 * r)
    _front_hair(cv, x, y, r, sp)
    face(cv, x, y, rr, f, sp)
    cv.restore()


def person(cv, x, yf, r, sp, pose):
    """Front view. yf = floor line, r = head radius.
    pose: arms=[(elbow,hand),(elbow,hand)] in r-units relative to (x,yf) (left then right),
          legs='stand'|'sit'|None, lift (r units), tilt, face{}, held(cv) callback, hands=True"""
    U = lambda p: (x + p[0] * r, yf + p[1] * r)
    lift = pose.get('lift', 0)
    top, pants, shoes, skin = sp['top'], sp.get('pants', '#2E3A6E'), sp.get('shoes', '#1F1A3A'), sp['skin']
    legs = pose.get('legs', 'stand')
    if legs == 'stand':
        for s in (-1, 1):
            shaded(cv, rrp(*U((s * .32 - .2, -1.3)), *U((s * .32 + .2, -.12)), .14 * r), pants, dx=-.06 * r, dy=0)
        for s in (-1, 1):
            shaded(cv, op(*U((s * .34 - .26 + s * .06, -.26)), *U((s * .34 + .26 + s * .06, .02))), shoes, dx=-.05 * r, dy=-.06 * r)
    elif legs == 'sit':
        for s in (-1, 1):
            shaded(cv, rrp(*U((s * .34 - .2, -.95)), *U((s * .34 + .2, -.12)), .14 * r), pants, dx=-.06 * r, dy=0)
            shaded(cv, op(*U((s * .36 - .26 + s * .06, -.26)), *U((s * .36 + .26 + s * .06, .02))), shoes, dx=-.05 * r, dy=-.06 * r)
        shaded(cv, rrp(*U((-.78, -1.25)), *U((.78, -.78)), .22 * r), pants, dx=0, dy=-.08 * r)
    hc = U((0, -3.85 + lift))
    # long back hair sits behind torso
    if sp['style'] in ('long', 'hijab'):
        cv.save()
        cv.rotate(pose.get('tilt', 0), hc[0], hc[1] + 1.1 * r)
        _back_hair(cv, hc[0], hc[1], r, sp)
        cv.restore()
    # neck
    shaded(cv, rrp(*U((-.19, -3.25 + lift)), *U((.19, -2.8 + lift)), .1 * r), skin, dark(skin, .25), dx=.06 * r, dy=0)
    torso = rrp(*U((-.76, -2.98 + lift)), *U((.76, -1.0)), .62 * r)
    cv.save()
    cv.clipPath(torso, skia.ClipOp.kIntersect, True)
    cv.drawPath(torso, paint(dark(top, .22)))
    cv.save()
    cv.translate(-.14 * r, -.1 * r)
    cv.drawPath(torso, paint(top))
    cv.restore()
    if legs:
        cv.drawRect(R(*U((-1, -1.32)), *U((1, -.9))), paint(pants))
    cv.drawOval(R(*U((-.26, -3.12 + lift)), *U((.26, -2.82 + lift))), paint(skin))
    if sp.get('hoodie'):
        for s in (-1, 1):
            cv.drawPath(poly([U((s * .16, -2.82 + lift)), U((s * .19, -2.35 + lift))], False), paint('#ffffff', 220, stroke=.04 * r))
    cv.restore()
    cv.save()
    cv.rotate(pose.get('tilt', 0), hc[0], hc[1] + 1.1 * r)
    if sp['style'] not in ('long', 'hijab'):
        _back_hair(cv, hc[0], hc[1], r, sp)
    if sp['style'] not in ('long', 'hijab', 'bob'):
        for s in (-1, 1):
            shaded(cv, cp(hc[0] + s * .98 * r, hc[1] + .08 * r, .2 * r), skin, dx=-.05 * r, dy=-.05 * r)
    rr = r * (.86 if sp['style'] == 'hijab' else 1)
    shaded(cv, cp(hc[0], hc[1], rr), skin, dark(skin, .16), dx=-.12 * r, dy=-.1 * r)
    _front_hair(cv, hc[0], hc[1], r, sp)
    face(cv, hc[0], hc[1], rr, pose.get('face', {}), sp)
    cv.restore()
    arms = pose.get('arms')
    hands = []
    if arms:
        for s, (el, hd) in zip((-1, 1), arms):
            sh = U((s * .6, -2.7 + lift))
            e, h_ = U(el), U(hd)
            _arm(cv, [sh, e, h_], top, .32 * r)
            hands.append(h_)
    if pose.get('held'):
        pose['held'](cv)
    if pose.get('hands', True):
        for h_ in hands:
            hand(cv, h_[0], h_[1], .18 * r, skin)


def person_back(cv, x, yf, r, sp, t=0, type_=True):
    """Seen from behind, seated at a desk; yf is the seat line."""
    U = lambda p: (x + p[0] * r, yf + p[1] * r)
    top, skin = sp['top'], sp['skin']
    for s in (-1, 1):
        k = math.sin(t * 13 + s) * .04 if type_ else 0
        _arm(cv, [U((s * .62, -2.55)), U((s * 1.02, -1.75)), U((s * .55, -2.05 + k))], dark(top, .1), .32 * r)
    torso = rrp(*U((-.78, -2.95)), *U((.78, -.6)), .62 * r)
    shaded(cv, torso, top, dx=.12 * r, dy=-.06 * r)
    hc = U((0, -3.8))
    hcol = sp['hair']
    p = skia.Path()
    p.moveTo(hc[0] - 1.06 * r, hc[1])
    p.arcTo(R(hc[0] - 1.06 * r, hc[1] - 1.08 * r, hc[0] + 1.06 * r, hc[1] + 1.04 * r), 180, 180, False)
    p.cubicTo(hc[0] + 1.12 * r, hc[1] + .9 * r, hc[0] + 1.2 * r, hc[1] + 1.8 * r, hc[0] + 1.0 * r, hc[1] + 2.25 * r)
    p.quadTo(hc[0], hc[1] + 2.5 * r, hc[0] - 1.0 * r, hc[1] + 2.25 * r)
    p.cubicTo(hc[0] - 1.2 * r, hc[1] + 1.8 * r, hc[0] - 1.12 * r, hc[1] + .9 * r, hc[0] - 1.06 * r, hc[1])
    p.close()
    shaded(cv, p, hcol, dark(hcol, .3), dx=.14 * r, dy=-.1 * r)
    for k in range(5):
        xx = hc[0] + (-.6 + k * .3) * r
        q = skia.Path()
        q.moveTo(xx, hc[1] - .6 * r)
        q.cubicTo(xx + .1 * r, hc[1] + .4 * r, xx - .1 * r, hc[1] + 1.2 * r, xx + .05 * r, hc[1] + 2.0 * r)
        cv.drawPath(q, paint(dark(hcol, .3), 120, stroke=.05 * r))
    # chair back in front of her
    shaded(cv, rrp(*U((-.95, -1.75)), *U((.95, -.35)), .3 * r), '#2B2A4A', dx=.1 * r, dy=-.08 * r)
    cv.drawPath(rrp(*U((-.12, -.4)), *U((.12, .6)), .06 * r), paint('#1E1C38'))


# ---------------------------------------------------------------- recurring cast
CLODAGH = dict(skin=(255, 222, 203), hair='#E36A2C', style='long', top='#2FB59A', pants='#2D3768',
               shoes='#1E1838', freckles=True, brow='#B6501F')
NASTI = dict(skin=(247, 211, 189), hair='#1C1B25', style='short', top='#4C64AE', pants='#2A2E46',
             shoes='#ECECF4', hoodie=True)


# ---------------------------------------------------------------- shared sets
_rs = random.Random(11)
STARS = [(_rs.uniform(0, W), _rs.uniform(0, H), _rs.uniform(1.2, 3.4), _rs.uniform(0, 6.28)) for _ in range(230)]
BOKEH = [(_rs.uniform(0, W), _rs.uniform(0, 1500), _rs.uniform(14, 60), _rs.uniform(0, 6.28), _rs.uniform(.2, .6)) for _ in range(26)]


def stars(cv, t, ymax=1300, a=1.0, n=230, ox=0, oy=0):
    for x, y, s, ph in STARS[:n]:
        if y > ymax:
            continue
        tw = .55 + .45 * math.sin(t * 2.2 + ph * 3)
        cv.drawCircle(x + ox, y + oy, s, paint('#ffffff', 220 * tw * a))
        if s > 2.8:
            glow(cv, x + ox, y + oy, s * 5, '#bcd0ff', 60 * tw * a)


def stage(cv, t, ground=1240, mood=0.0, spot=1.0):
    """Purple 'planet' stage. mood 0..1 shifts toward a threatening red."""
    top = mix('#1A1446', '#2A0E2A', mood)
    midc = mix('#3E2475', '#5A1A3A', mood)
    cv.drawRect(R(0, 0, W, H), paint(shader=lin(0, 0, 0, ground, [top, midc])))
    stars(cv, t, ymax=ground, a=1 - mood * .5)
    for x, y, s, ph, sp_ in BOKEH:
        yy = (y - t * 14 * sp_) % 1500
        glow(cv, x + math.sin(t * .4 + ph) * 20, yy, s, mix('#B89CFF', '#FF6A6A', mood), 36, mid=1)
    sc = mix('#B28CFF', '#FF5A6A', mood)
    glow(cv, W / 2, 760, 700, sc, 95 * spot, mid=1)
    # curved ground
    g = skia.Path()
    g.addOval(R(-900, ground, W + 900, ground + 2200))
    cv.drawPath(g, paint(shader=lin(0, ground, 0, ground + 500, [mix('#4B2C86', '#5E1C3E', mood), mix('#1B1240', '#1A0A1C', mood)])))
    cv.drawPath(g, paint(mix('#9C7BE8', '#FF7A7A', mood), 120, stroke=4))
    glow(cv, W / 2, ground + 20, 420, sc, 50 * spot, mid=1)


def ground_shadow(cv, x, y, w, a=110):
    cv.drawOval(R(x - w, y - w * .13, x + w, y + w * .13), paint('#0a0520', a, blur=10))


# ---------------------------------------------------------------- render loop
def run(name, dur, draw):
    """Render draw(cv, t, frame_index) for dur seconds at 30fps to <KZ_OUT>/<name>.mp4.
    With env STILLS='1.0,4.5' only those times are saved as st_<name>_<t>.png (fast preview)."""
    OUT = os.environ.get('KZ_OUT', os.getcwd())
    os.makedirs(OUT, exist_ok=True)
    stills = os.environ.get('STILLS')
    info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    surf = skia.Surface.MakeRaster(info)
    cv = surf.getCanvas()
    if stills:
        for ts in stills.split(','):
            t = float(ts)
            cv.clear(col('#000000'))
            draw(cv, t, int(t * FPS))
            grain(cv, int(t * FPS))
            surf.makeImageSnapshot().save(os.path.join(OUT, f'st_{name}_{ts}.png'))
        return
    out = os.path.join(OUT, f'{name}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                          '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        cv.clear(col('#000000'))
        draw(cv, t, fi)
        grain(cv, fi)
        p.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
    p.stdin.close()
    p.wait()
