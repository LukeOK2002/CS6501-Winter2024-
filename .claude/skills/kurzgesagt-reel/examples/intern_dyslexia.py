import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from kz import *

DUR = 22.5
CX, GY, CR = 540, 1240, 150   # Clodagh position, ground, head radius


# ------------------------------------------------------------- props shared with later videos
def truck(cv, x, y, s, t=0, label='', cursor=False, squiggle=0.0):
    """Food truck, (x,y)=centre of the ground line under it."""
    U = lambda px, py: (x + px * s, y + py * s)
    # body
    shaded(cv, rrp(*U(-230, -260), *U(150, -50), 34 * s), '#F4F1EA', dx=-8 * s, dy=-8 * s)
    shaded(cv, rrp(*U(150, -190), *U(250, -50), 26 * s), '#3FB6A8', dx=-6 * s, dy=-6 * s)
    shaded(cv, rrp(*U(168, -175), *U(234, -120), 10 * s), '#BFE8FF', dx=-4 * s, dy=-4 * s)
    cv.drawRect(R(*U(-230, -88), *U(250, -70)), paint('#3FB6A8'))
    # roof sign
    shaded(cv, rrp(*U(-210, -330), *U(120, -270), 14 * s), '#E5484D', dx=-5 * s, dy=-5 * s)
    text(cv, 'SPICE BAG', *U(-45, -300), font('bold', 34 * s), '#FFFFFF', track=2 * s)
    # hatch with awning
    shaded(cv, rrp(*U(-190, -230), *U(90, -150), 8 * s), '#2C2A52', dx=-4 * s, dy=-4 * s)
    glow(cv, *U(-50, -180), 90 * s, '#FFD68A', 110)
    for k in range(7):
        c = '#E5484D' if k % 2 == 0 else '#FFFFFF'
        cv.drawPath(rrp(*U(-200 + k * 42, -245), *U(-200 + (k + 1) * 42, -222), 6 * s), paint(c))
    # paper bag in hatch
    shaded(cv, rrp(*U(-80, -205), *U(-30, -150), 4 * s), '#C9A36B', dx=-3 * s, dy=-3 * s)
    # side panel for text
    shaded(cv, rrp(*U(-190, -138), *U(90, -96), 8 * s), '#FFFFFF', dx=-3 * s, dy=-3 * s)
    if label or cursor:
        f = font('bold', 36 * s)
        w = text(cv, label, *U(-50, -117), f, '#D9433B') if label else 0
        if cursor and int(t * 3) % 2 == 0:
            cx_ = x + (-50) * s + w / 2 + 5 * s
            cv.drawRect(R(cx_, y - 135 * s, cx_ + 3.5 * s, y - 99 * s), paint('#2C2A52'))
        if squiggle > 0 and label:
            x0 = x - 50 * s - w / 2
            p = skia.Path()
            p.moveTo(x0, y - 92 * s)
            n = int(14 * squiggle)
            for k in range(n):
                p.quadTo(x0 + (k + .5) * w / 14, y - (92 + (4 if k % 2 else -4)) * s, x0 + (k + 1) * w / 14, y - 92 * s)
            cv.drawPath(p, paint('#FF3B3B', stroke=3 * s))
    # wheels
    for wx in (-140, 170):
        shaded(cv, cp(*U(wx, -40), 40 * s), '#262440', dx=-5 * s, dy=-5 * s)
        cv.drawCircle(*U(wx, -40), 15 * s, paint('#C9CBDD'))


def takeaway(cv, x, y, s, t=0):
    U = lambda px, py: (x + px * s, y + py * s)
    shaded(cv, rrp(*U(-170, -330), *U(170, 0), 10 * s), '#D9433B', dx=-8 * s, dy=-8 * s)
    shaded(cv, rrp(*U(-185, -360), *U(185, -290), 10 * s), '#F6C445', dx=-5 * s, dy=-5 * s)
    text(cv, 'TAKEAWAY', *U(0, -325), font('bold', 34 * s), '#9A2420', track=3 * s)
    # window + door with warm light
    for l, r_ in ((-140, -10), (20, 140)):
        cv.drawPath(rrp(*U(l, -250), *U(r_, -40), 8 * s), paint(shader=lin(0, y - 250 * s, 0, y - 40 * s, ['#FFE3A0', '#FFB45E'])))
    cv.drawRect(R(*U(-140, -150), *U(-10, -144)), paint('#D9433B'))
    # lanterns
    for lx in (-130, 130):
        sw = math.sin(t * 2 + lx) * 4
        cv.drawPath(poly([U(lx, -290), U(lx + sw, -270)], False), paint('#5A1A16', stroke=3 * s))
        glow(cv, *U(lx + sw, -245), 50 * s, '#FF6A3A', 90)
        shaded(cv, op(*U(lx + sw - 26, -272), *U(lx + sw + 26, -220)), '#F0453A', dx=-4 * s, dy=-4 * s)
        cv.drawRect(R(*U(lx + sw - 12, -276), *U(lx + sw + 12, -268)), paint('#F6C445'))


def badge(cv, x, y, s, good, a=255):
    c = '#38C172' if good else '#E5484D'
    glow(cv, x, y, 60 * s, c, 80 * a / 255)
    cv.drawCircle(x, y, 30 * s, paint(c, a))
    if good:
        cv.drawPath(poly([(x - 13 * s, y), (x - 3 * s, y + 10 * s), (x + 14 * s, y - 10 * s)], False), paint('#ffffff', a, stroke=7 * s))
    else:
        for d in (-1, 1):
            cv.drawPath(poly([(x - 11 * s, y - 11 * s * d), (x + 11 * s, y + 11 * s * d)], False), paint('#ffffff', a, stroke=7 * s))


# ------------------------------------------------------------- scene A/B: stage
POSE_WAVE_L = ((-.95, -2.0), (-.9, -1.35))
POSE_BOOK = [((-1.3, -1.65), (-1.12, -2.25)), ((1.3, -1.65), (1.12, -2.25))]
LETTERS = 'bdpqbdsz96mwbd'
rl = random.Random(4)
LSPAWN = [(5.0 + i * .26, rl.uniform(-1, 1), rl.uniform(-1, 1), LETTERS[i % len(LETTERS)]) for i in range(40)]


def book_cb(cv, t, k):
    def f(cv_):
        if k <= 0:
            return
        s = eback(k) * CR
        bx, by = CX, GY - 2.27 * CR
        cv.save()
        cv.translate(bx, by)
        cv.scale(s / CR, s / CR)
        w, h = 1.16 * CR, .72 * CR
        cv.drawPath(rrp(-w - 6, -h - 14, w + 6, -h + 10, 8), paint('#FFF6E0'))
        for sd in (-1, 1):
            p = poly([(0, -h + 4), (sd * w, -h - 6), (sd * w, h - 6), (0, h + 6)])
            shaded(cv, p, '#E0485A' if sd < 0 else '#EA5A6A', dx=-6, dy=-6)
        cv.drawPath(poly([(0, -h + 4), (0, h + 6)], False), paint('#A32C3C', stroke=8))
        text(cv, 'Aa', -w / 2, -10, font('bold', .42 * CR), '#FFD98A')
        cv.drawPath(rrp(-w * .8, h * .35, -w * .2, h * .35 + 8, 4), paint('#FFD98A', 200))
        cv.restore()
    return f


def clodagh_stage(cv, t):
    ground_shadow(cv, CX, GY, 190)
    rise = eback(prog(t, 0, .8), 1.4)
    k_book = prog(t, 4.4, 5.0)
    kb = ease(k_book)
    wave_a = math.sin(t * 9) * .32
    el = (1.25, -3.0)
    hd = (el[0] + math.sin(-.7 + wave_a) * .95 * -1 + .3, el[1] - math.cos(-.7 + wave_a) * .95)
    hd = (1.25 + .9 * math.sin(.35 + wave_a), -3.0 - .9 * math.cos(.35 + wave_a))
    armL = (lerp2(POSE_WAVE_L[0], POSE_BOOK[0][0], kb), lerp2(POSE_WAVE_L[1], POSE_BOOK[0][1], kb))
    armR = (lerp2(el, POSE_BOOK[1][0], kb), lerp2(hd, POSE_BOOK[1][1], kb))
    conf = ease(prog(t, 5.4, 6.2))
    blink = (t % 3.1) < .12 and t > 5
    if t < 4.6:
        fc = dict(eyes='happy', mouth=.9, mopen=.75, brows=((-8, .04), (-8, .04)))
        tilt = math.sin(t * 2) * 3
    else:
        fc = dict(eyes='open' if not blink else 'happy', look=(lerp(0, .3, conf), lerp(.2, .9, 1 - conf * .5)),
                  brows=((lerp(0, -22, conf), lerp(0, .12, conf)), (lerp(0, 16, conf), lerp(0, -.02, conf))),
                  mouth=lerp(.5, 0, conf), wavy=conf > .5, squint=0)
        tilt = lerp(0, -7, conf) + math.sin(t * 1.3) * 2
    cv.save()
    cv.translate(0, (1 - rise) * 900)
    person(cv, CX, GY, CR, CLODAGH, dict(arms=[armL, armR], face=fc, tilt=tilt, lift=math.sin(t * 2.2) * .02,
                                         held=book_cb(cv, t, k_book)))
    # lanyard badge (visible before the book arrives)
    if kb < .5:
        a = 255 * (1 - kb * 2)
        hx_, hy_ = CX, GY - 2.05 * CR
        cv.drawPath(poly([(CX - .18 * CR, GY - 2.86 * CR), (hx_ - .1 * CR, hy_ - .12 * CR)], False), paint('#2B3A8A', a, stroke=5))
        cv.drawPath(poly([(CX + .18 * CR, GY - 2.86 * CR), (hx_ + .1 * CR, hy_ - .12 * CR)], False), paint('#2B3A8A', a, stroke=5))
        shaded(cv, rrp(hx_ - .26 * CR, hy_ - .14 * CR, hx_ + .26 * CR, hy_ + .2 * CR, 8), '#FFFFFF', dx=-3, dy=-3)
        text(cv, 'INTERN', hx_, hy_ + .03 * CR, font('bold', .11 * CR), '#2B3A8A', a, track=1)
    cv.restore()
    # confusion: letters + question marks + sweat
    if t > 5.0:
        for t0, u, v, ch in LSPAWN:
            age = t - t0
            if age < 0 or age > 2.6:
                continue
            q = age / 2.6
            x = CX + u * .7 * CR + math.sin(age * 2 + v * 3) * 90 * q * (1 if u > 0 else -1) + u * 260 * q
            y = GY - 2.95 * CR - 420 * eout(q)
            al = 255 * math.sin(math.pi * q)
            cv.save()
            cv.translate(x, y)
            cv.rotate(v * 120 * q)
            cv.scale(math.cos(age * 3.5 + v * 3), 1)
            glow(cv, 0, 0, 40, '#B89CFF', 60 * al / 255)
            text(cv, ch, 0, 0, font('bold', 54), '#FFFFFF', al)
            cv.restore()
        for i, (qx, qy, t0) in enumerate(((-1.35, -4.9, 6.0), (1.4, -5.1, 6.35), (1.05, -5.75, 6.8))):
            k = eback(prog(t, t0, t0 + .45))
            if k <= 0:
                continue
            x = CX + qx * CR
            y = GY + qy * CR + math.sin(t * 2.5 + i) * 10
            cv.save()
            cv.translate(x, y)
            cv.rotate(math.sin(t * 2 + i) * 12 + (i - 1) * 10)
            cv.scale(k, k)
            glow(cv, 0, 0, 80, '#FFC94A', 70)
            text(cv, '?', 0, 0, font('bold', 120 - i * 18), '#FFC94A', shadow=6)
            cv.restore()
        k = prog(t, 9.6, 10.0)
        if k > 0:
            sx, sy = CX + .88 * CR, GY - 4.2 * CR + ((t - 9.6) * 12) % 30
            p = skia.Path()
            p.moveTo(sx, sy - 22)
            p.cubicTo(sx + 14, sy - 2, sx + 12, sy + 14, sx, sy + 14)
            p.cubicTo(sx - 12, sy + 14, sx - 14, sy - 2, sx, sy - 22)
            cv.drawPath(p, paint('#9EDCFF', 230 * k))
            cv.drawCircle(sx - 4, sy + 4, 3.5, paint('#ffffff', 220 * k))


def scene_stage(cv, t):
    cv.save()
    z = 1 + .04 * ease(t / 13)
    cv.translate(540, 900)
    cv.scale(z, z)
    cv.translate(-540, -900)
    stage(cv, t)
    clodagh_stage(cv, t)
    cv.restore()


# ------------------------------------------------------------- scene C: office over the shoulder
MON = (170, 270, 910, 760)          # monitor outer rect
VP = (MON[0] + 78, MON[1] + 58, MON[2] - 18, MON[3] - 120)   # viewport


def screen(cv, t):
    l, tp, r_, b = MON
    glow(cv, (l + r_) / 2, (tp + b) / 2, 620, '#7FB8FF', 70, mid=1)
    shaded(cv, rrp(l, tp, r_, b, 22), '#15172E', dx=-6, dy=-6)
    cv.drawPath(rrp(l + 14, tp + 14, r_ - 14, b - 14, 10), paint('#23264A'))
    for i, c in enumerate(('#FF6B6B', '#FFC94A', '#38C172')):
        cv.drawCircle(l + 40 + i * 24, tp + 34, 7, paint(c))
    text(cv, 'spicebag_final_v2.anim', (l + r_) / 2, tp + 34, font('med', 17), '#9AA0D0', anchor='c')
    for i in range(6):
        cv.drawPath(rrp(l + 28, tp + 72 + i * 52, l + 62, tp + 106 + i * 52, 7), paint('#ffffff' if i == 1 else '#3A3E70', 255 if i != 1 else 60))
    # viewport
    vl, vt, vr, vb = VP
    cv.save()
    cv.clipPath(rrp(vl, vt, vr, vb, 6), skia.ClipOp.kIntersect, True)
    cv.drawRect(R(vl, vt, vr, vb), paint(shader=lin(0, vt, 0, vb, ['#9FD8FF', '#E6F6FF'])))
    glow(cv, vl + 80, vt + 70, 90, '#FFF2B0', 200)
    cv.drawCircle(vl + 80, vt + 70, 30, paint('#FFE27A'))
    for cx_, cy_ in ((vl + 330, vt + 70), (vl + 560, vt + 110)):
        for dx, rr_ in ((-30, 22), (0, 30), (32, 22)):
            cv.drawCircle(cx_ + dx + t * 6, cy_, rr_, paint('#ffffff', 230))
    gy = vb - 40
    cv.drawRect(R(vl, gy, vr, vb), paint('#7FCB8A'))
    cv.drawRect(R(vl, gy, vr, gy + 6), paint('#6AB877'))
    s = .62
    takeaway(cv, vl + 150, gy, s, t)
    k = eout(prog(t, 13.5, 14.6))
    tx = lerp(vr + 300, vl + 470, k)
    bounce = math.sin(prog(t, 14.4, 15.0) * math.pi) * 6
    nlet = 0 if t < 17.7 else min(5, int((t - 17.7) / .17) + 1)
    truck(cv, tx, gy - bounce, s, t, label='NASTI'[:nlet], cursor=(17.4 < t < 18.6), squiggle=eout(prog(t, 18.6, 19.0)))
    badge(cv, vl + 150, gy + 20, .62, True, 255 * eback(prog(t, 15.0, 15.4)))
    badge(cv, vl + 470 + 175 * s, gy + 20, .62, False, 255 * eback(prog(t, 15.5, 15.9)))
    if t > 18.7:
        # marker circle around NASTI
        k = eout(prog(t, 18.7, 19.1))
        cxn, cyn = vl + 470 - 50 * s, gy - 117 * s
        p = skia.Path()
        p.addArc(R(cxn - 78, cyn - 32, cxn + 78, cyn + 32), -200, 360 * k)
        cv.drawPath(p, paint('#FF3B3B', stroke=4))
    cv.restore()
    # timeline
    tl = (l + 78, b - 104, r_ - 18, b - 22)
    cv.drawPath(rrp(*tl, 8), paint('#1A1C38'))
    for row in range(3):
        y = tl[1] + 20 + row * 22
        cv.drawRect(R(tl[0] + 10, y - 2, tl[2] - 10, y + 2), paint('#34386A'))
        for kx in (.1 + row * .07, .35, .62 - row * .05, .85):
            x = tl[0] + 10 + kx * (tl[2] - tl[0] - 20)
            cv.drawPath(poly([(x, y - 7), (x + 7, y), (x, y + 7), (x - 7, y)]), paint('#FFC94A'))
    ph = tl[0] + 10 + ((t - 13) / 8.5 % 1) * (tl[2] - tl[0] - 20)
    cv.drawRect(R(ph - 1.5, tl[1] + 4, ph + 1.5, tl[3] - 4), paint('#FF5A5F'))
    cv.drawPath(poly([(ph - 8, tl[1] + 2), (ph + 8, tl[1] + 2), (ph, tl[1] + 12)]), paint('#FF5A5F'))


def scene_office(cv, t):
    # camera: slow drift, then zoom into the truck
    kz_ = ease(prog(t, 17.2, 18.4))
    s = .62
    vl, vt, vr, vb = VP
    gy = vb - 40
    focus = (vl + 470 - 30 * s, gy - 170 * s)
    z = lerp(1.0 + .03 * prog(t, 13, 17.2), 2.35, kz_)
    fx, fy = lerp2((540, 900), focus, kz_)
    tx_, ty_ = lerp2((540, 900), (540, 760), kz_)
    cv.save()
    cv.translate(tx_, ty_)
    cv.scale(z, z)
    cv.translate(-fx, -fy)
    cv.drawRect(R(-100, -100, W + 100, 1000), paint(shader=lin(0, 0, 0, 1000, ['#141842', '#262A62'])))
    # window
    wr = rrp(40, 120, 300, 560, 14)
    cv.drawPath(wr, paint(shader=lin(0, 120, 0, 560, ['#0B0F33', '#3A2468'])))
    cv.save()
    cv.clipPath(wr, skia.ClipOp.kIntersect, True)
    stars(cv, t)
    for i in range(7):
        bx = 40 + i * 40
        bh = 60 + (i * 37) % 110
        cv.drawRect(R(bx, 560 - bh, bx + 34, 560), paint('#1A1440'))
        for j in range(int(bh / 26)):
            if (i + j) % 3:
                cv.drawRect(R(bx + 8, 560 - bh + 10 + j * 24, bx + 15, 560 - bh + 20 + j * 24), paint('#FFC870', 170))
    cv.restore()
    cv.drawPath(wr, paint('#3B3F7A', stroke=12))
    cv.drawPath(poly([(170, 120), (170, 560)], False), paint('#3B3F7A', stroke=8))
    # shelf + plant
    cv.drawRect(R(930, 420, 1080, 434), paint('#3B3F7A'))
    for i, c in enumerate(('#FFC94A', '#5BC0EB', '#E86AA0')):
        shaded(cv, rrp(945 + i * 26, 330 + i * 8, 967 + i * 26, 420, 4), c, dx=-3, dy=-3)
    shaded(cv, rrp(1020, 370, 1060, 420, 8), '#F1EEF8', dx=-3, dy=-3)
    for ox, oy, rr_ in ((-10, -70, 22), (12, -78, 20), (0, -100, 22)):
        shaded(cv, cp(1040 + ox, 420 + oy, rr_), '#57C27A', dx=-4, dy=-4)
    # desk
    cv.drawRect(R(-100, 840, W + 100, 1010), paint(shader=lin(0, 840, 0, 1010, ['#7A5A8E', '#5E4476'])))
    cv.drawRect(R(-100, 1010, W + 100, H + 300), paint(shader=lin(0, 1010, 0, H, ['#2E2250', '#140C2A'])))
    cv.drawRect(R(-100, 1004, W + 100, 1014), paint('#3E2E62'))
    # monitor stand
    shaded(cv, rrp(500, 740, 580, 870, 10), '#2A2C4E', dx=-4, dy=0)
    cv.drawOval(R(420, 852, 660, 892), paint('#2A2C4E'))
    screen(cv, t)
    # keyboard, mouse, mug, lamp
    shaded(cv, rrp(330, 900, 690, 950, 10), '#D9DCEF', dx=-4, dy=-4)
    shaded(cv, op(760, 905, 806, 955), '#D9DCEF', dx=-3, dy=-3)
    shaded(cv, rrp(110, 880, 160, 945, 8), '#FFFFFF', dx=-3, dy=-3)
    cv.drawPath(poly([(160, 895), (176, 905), (176, 925), (160, 932)], False), paint('#ffffff', stroke=6))
    cv.drawPath(poly([(1010, 930), (1030, 780), (1000, 740)], False), paint('#2A2C4E', stroke=10))
    shaded(cv, rrp(955, 712, 1040, 756, 20), '#FFC94A', dx=-4, dy=-4)
    glow(cv, 995, 780, 260, '#FFD68A', 70, mid=1)
    cv.drawOval(R(965, 920, 1055, 950), paint('#2A2C4E'))
    # Clodagh from behind
    person_back(cv, 470, 1470, 125, CLODAGH, t)
    glow(cv, 470, 1000, 330, '#9FC8FF', 40, mid=1)
    cv.restore()


def nasty_card(cv, t):
    t0 = 19.2
    if t < t0:
        return
    k = eback(prog(t, t0, t0 + .45), 1.3)
    cx, cy = 540, 330
    cv.save()
    cv.translate(cx, cy)
    cv.scale(k, k)
    cv.drawPath(rrp(-380, -150, 380, 150, 36), paint('#0a0620', 120, blur=24))
    shaded(cv, rrp(-380, -160, 380, 140, 36), '#FFFFFF', '#E6E4F2', dx=-8, dy=-8)
    f = font('bold', 150)
    wN, wY, wI = f.measureText('NAST'), f.measureText('Y'), f.measureText('I')
    sw = ease(prog(t, t0 + 1.25, t0 + 1.7))
    x0 = lerp(-(wN + wY) / 2, -(wN + wI) / 2, sw)
    text(cv, 'NAST', x0, -5, f, '#272448', anchor='l')
    # Y gets struck out and falls away
    ky = prog(t, t0 + .9, t0 + 1.6)
    if ky < 1:
        cv.save()
        yx = x0 + wN + wY / 2
        cv.translate(yx, -5 + ein(ky) * 140)
        cv.rotate(ky * 40)
        text(cv, 'Y', 0, 0, f, '#272448', 255 * (1 - ein(ky)))
        cv.restore()
    ks = eout(prog(t, t0 + .55, t0 + .85))
    if ks > 0 and ky < 1:
        yx = x0 + wN + wY / 2
        cv.drawPath(poly([(yx - 50, -70), (yx - 50 + 100 * ks, -70 + 130 * ks)], False), paint('#FF3B3B', 255 * (1 - ein(ky)), stroke=12))
    ki = eback(prog(t, t0 + 1.25, t0 + 1.65), 2.2)
    if ki > 0:
        ix = x0 + wN + wI / 2
        cv.save()
        cv.translate(ix, -5 - (1 - ki) * 120)
        text(cv, 'I', 0, 0, f, '#E5484D', 255 * clamp(ki))
        cv.restore()
        kq = eout(prog(t, t0 + 1.7, t0 + 2.1))
        if kq > 0:
            xs, xe = x0, x0 + wN + wI
            p = skia.Path()
            p.moveTo(xs, 72)
            n = 18
            for j in range(int(n * kq)):
                p.quadTo(xs + (j + .5) * (xe - xs) / n, 72 + (9 if j % 2 else -9), xs + (j + 1) * (xe - xs) / n, 72)
            cv.drawPath(p, paint('#FF3B3B', stroke=6))
    cv.restore()


def draw(cv, t, fi):
    wipe = prog(t, 13.0, 13.7)
    if wipe < 1:
        scene_stage(cv, min(t, 13.7))
    if wipe > 0:
        cv.save()
        if wipe < 1:
            cv.clipPath(cp(540, 760, 1400 * ease(wipe)), skia.ClipOp.kIntersect, True)
        scene_office(cv, t)
        cv.restore()
        if 0 < wipe < 1:
            cv.drawCircle(540, 760, 1400 * ease(wipe), paint('#FFC94A', 200, stroke=10))
    nasty_card(cv, t)
    vignette(cv, 140)
    scrim(cv, 1180, 200)
    subtitle(cv, t, .3, 4.5, "This is {hl:Clodagh}.\nShe is one of our interns.")
    subtitle(cv, t, 4.75, 8.9, "Clodagh has {od:dyslexia}.")
    subtitle(cv, t, 9.0, 13.0, "This means she has trouble\n{hl:reading} and {hl:spelling}.")
    subtitle(cv, t, 13.4, 17.4, "For our last video, she made the point that\nfood-truck spice bags aren't as nice\nas the ones from a {hl:Chinese takeaway}.")
    subtitle(cv, t, 17.6, 23, "But while animating the food truck,\nshe spelled {hl:NASTY} as...", fade_out=False)


if __name__ == '__main__':
    run('v2', DUR, draw)
