import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from kz import *

DUR = 12.0
BL, BR = 80, 1000            # building outer walls
ROOF = 470
FLOORS = [860, 1250]         # floor line of each storey (upper, lower)
CEIL = [500, 890]
GROUND = 1250

WORKERS = [
    (0, 230, dict(skin=(122, 78, 54), hair='#2A1C18', style='curly', top='#F2B33D')),
    (0, 540, dict(skin=(242, 208, 176), hair='#15151C', style='short', top='#5B8DEF', glasses=True)),
    (0, 850, dict(skin=(196, 140, 102), hair='#2E8C8A', style='hijab', top='#E86AA0')),
    (1, 230, dict(skin=(250, 214, 196), hair='#C9C9D6', style='short', top='#5FB878', beard=True, beardc='#D8D8E0')),
    (1, 540, dict(skin=(214, 160, 122), hair='#4A2A1E', style='bun', top='#FF7A5C')),
    (1, 850, dict(skin=(96, 62, 44), hair='#1A1412', style='buzz', top='#8A6CE0', beard=True)),
]

rng = random.Random(7)
METEORS = []
plan = [(1.3, 'roof'), (2.2, 'far'), (2.9, 'groundR'), (3.6, 'far'), (4.2, 'roof'), (4.9, 'front'),
        (5.5, 'far'), (6.0, 'groundL'), (6.6, 'roof'), (7.1, 'front'), (7.6, 'far'), (8.1, 'roof'),
        (8.6, 'groundR'), (9.1, 'front'), (9.5, 'far'), (9.9, 'roof'), (10.4, 'groundL'), (10.9, 'front'), (11.3, 'far')]
for th, kind in plan:
    if kind == 'roof':
        tx, ty, s = rng.uniform(170, 910), ROOF + 4, 1.0
    elif kind == 'far':
        tx, ty, s = rng.uniform(40, 1040), rng.uniform(1150, 1215), .45
    elif kind == 'groundL':
        tx, ty, s = rng.uniform(15, 55), GROUND + 12, 1.0
    elif kind == 'groundR':
        tx, ty, s = rng.uniform(1025, 1065), GROUND + 12, 1.0
    else:
        tx, ty, s = rng.choice([rng.uniform(60, 300), rng.uniform(780, 1020)]), rng.uniform(1310, 1350), 1.1
    METEORS.append(dict(th=th, x=tx, y=ty, s=s, kind=kind, dur=rng.uniform(.75, 1.0),
                        deb=[(rng.uniform(math.pi * 1.05, math.pi * 1.95), rng.uniform(350, 900), rng.uniform(.6, 1.4)) for _ in range(14)],
                        smoke=[(rng.uniform(-40, 40), rng.uniform(.6, 1.4), rng.uniform(0, 1)) for _ in range(7)]))
DIR = (-.5, 1.0)
_n = math.hypot(*DIR)
DIR = (DIR[0] / _n, DIR[1] / _n)

CITY = []
for layer, (base, hmin, hmax, colr) in enumerate([(1250, 120, 300, '#2A1C55'), (1250, 60, 200, '#1E1442')]):
    x = -20
    while x < W + 20:
        w = rng.uniform(50, 120)
        h = rng.uniform(hmin, hmax)
        wins = [(rng.uniform(0, 1), rng.uniform(0, 1)) for _ in range(int(w * h / 1800))]
        CITY.append((layer, x, base - h, w, base, colr, wins))
        x += w + rng.uniform(-6, 14)


def shake_at(t):
    dx = dy = 0
    for m in METEORS:
        a = t - m['th']
        if 0 <= a < .5 and m['kind'] != 'far':
            k = (1 - a / .5) ** 2 * 18 * m['s']
            dx += math.sin(a * 90 + m['x']) * k
            dy += math.cos(a * 77 + m['y']) * k
    return dx, dy


def flame(cv, x, y, s, t, ph):
    for i, (ox, hh) in enumerate(((-18, .8), (0, 1.15), (20, .7))):
        f = .8 + .25 * math.sin(t * 11 + ph + i * 2) + .1 * math.sin(t * 23 + i)
        h = 70 * s * hh * f
        w = 22 * s * hh
        cx = x + ox * s
        p = skia.Path()
        p.moveTo(cx - w, y)
        p.cubicTo(cx - w * 1.1, y - h * .5, cx - w * .2, y - h * .7, cx + math.sin(t * 7 + i) * 6 * s, y - h)
        p.cubicTo(cx + w * .2, y - h * .7, cx + w * 1.1, y - h * .5, cx + w, y)
        p.close()
        cv.drawPath(p, paint(shader=lin(0, y, 0, y - h, ['#FF4D3A', '#FF8A3A', '#FFD36B'])))
    glow(cv, x, y - 30 * s, 150 * s, '#FF7A3A', 90)


def meteor_flight(cv, m, t):
    a = t - m['th']
    if not (-m['dur'] <= a < 0):
        return
    s = m['s']
    q = ein(1 + a / m['dur']) * .85 + (1 + a / m['dur']) * .15
    L = 1700 * s
    x = m['x'] - DIR[0] * L * (1 - q)
    y = m['y'] - DIR[1] * L * (1 - q)
    tl = 420 * s
    tx, ty = x - DIR[0] * tl, y - DIR[1] * tl
    nx, ny = -DIR[1], DIR[0]
    for wmul, al in ((2.6, 70), (1.0, 230)):
        w = 15 * s * wmul
        p = poly([(x + nx * w, y + ny * w), (tx, ty), (x - nx * w, y - ny * w)])
        cv.drawPath(p, paint(shader=lin(x, y, tx, ty, [('#FFE7B0', al), ('#FF7A3A', al * .5), ('#FF4A3A', 0)], [0, .35, 1])))
    glow(cv, x, y, 110 * s, '#FF8A3A', 170)
    cv.drawCircle(x, y, 17 * s, paint('#FFF6DE'))
    cv.drawCircle(x + 4 * s, y - 3 * s, 11 * s, paint('#FFD58A'))


def impact_back(cv, m, t):
    """Smoke + crater + fire (drawn under the flash)."""
    a = t - m['th']
    if a < 0:
        return
    s = m['s']
    if m['kind'] != 'far':
        cv.drawOval(R(m['x'] - 70 * s, m['y'] - 12 * s, m['x'] + 70 * s, m['y'] + 14 * s), paint('#120a24', 200))
    for ox, sp, ph in m['smoke']:
        age = a - ph * .4
        if age <= 0 or age > 4.5:
            continue
        rr = (26 + 70 * eout(age / 3)) * s * sp
        cx = m['x'] + (ox + age * 22) * s
        cy = m['y'] - (age * 70 + 20) * s * sp
        cv.drawCircle(cx, cy, rr * (.75 if m['kind'] == 'front' else 1), paint(mix('#5A4580', '#2C2150', clamp(age / 3)), (80 if m['kind'] == 'front' else 160) * (1 - age / 4.5)))
    if m['kind'] != 'far' and a > .15:
        flame(cv, m['x'], m['y'] + 4 * s, s * eout((a - .15) / .5), t, m['x'])


def impact_front(cv, m, t):
    a = t - m['th']
    if a < 0 or a > 1.6:
        return
    s = m['s']
    if a < .6:
        glow(cv, m['x'], m['y'], (120 + 260 * eout(a / .25)) * s, '#FFD27A', 255 * (1 - a / .6))
        cv.drawCircle(m['x'], m['y'], 60 * s * (1 - a / .6), paint('#FFFBEA', 255 * (1 - a / .6)))
    if a < .8:
        rr = (40 + 420 * eout(a / .8)) * s
        cv.drawOval(R(m['x'] - rr, m['y'] - rr * .45, m['x'] + rr, m['y'] + rr * .45), paint('#FFE2A8', 160 * (1 - a / .8), stroke=6 * s * (1 - a / .8) + 1))
    for ang, sp, sz in m['deb']:
        if a > 1.4:
            break
        x = m['x'] + math.cos(ang) * sp * a * s
        y = m['y'] + math.sin(ang) * sp * a * s + 1500 * a * a * s * .5
        if y > m['y'] + 40 * s:
            continue
        c = mix('#FFE08A', '#6A3A5A', clamp(a / 1.2))
        cv.drawCircle(x, y, 7 * s * sz * (1 - a / 1.5), paint(c))


def city(cv, t):
    for layer, x, y, w, base, colr, wins in CITY:
        cv.drawRect(R(x, y, x + w, base), paint(colr))
        for u, v in wins:
            wx, wy = x + 8 + u * (w - 22), y + 10 + v * (base - y - 30)
            on = math.sin(u * 50 + v * 30) > -.2
            if on:
                cv.drawRect(R(wx, wy, wx + 7, wy + 9), paint('#FFC870' if layer == 0 else '#FFB45E', 150 if layer == 0 else 110))


def worker(cv, fl, x, sp, t, sway):
    floor = FLOORS[fl]
    desk = floor - 122
    r = 44
    yf = desk + 1.6 * r
    ph = x * .013 + fl
    # chair back
    shaded(cv, rrp(x - 46, yf - 3.25 * r, x + 46, desk + 20, 26), '#3B3363', dx=-5, dy=-5)
    bob = math.sin(t * 2.4 + ph) * .03
    tk = [math.sin(t * 15 + ph + k * 1.7) * .05 for k in (0, 1)]
    talk = math.sin(t * .9 + ph * 3)
    look = (clamp(talk * 2, -1, 1) * .8, .4)
    person(cv, x, yf, r, sp, dict(
        legs=None, lift=bob, tilt=math.sin(t * 1.3 + ph) * 4,
        arms=[((-1.1, -1.9), (-.95, -1.55 + tk[0])), ((1.1, -1.9), (.95, -1.55 + tk[1]))],
        face=dict(eyes='happy' if (int(t * .7 + ph) % 3 == 0) else 'open', mouth=.75, look=look,
                  mopen=.45 if (int(t * .7 + ph) % 3 == 0) else 0)))
    # monitor glow on the face
    glow(cv, x, yf - 3.7 * r, 80, '#A9DBFF', 45, mid=1)
    # laptop (back of the screen faces us)
    shaded(cv, rrp(x - 52, desk - 52, x + 52, desk - 4, 9), '#C8CDE0', dx=-5, dy=-5)
    cv.drawCircle(x, desk - 28, 6, paint('#EEF1FA'))
    # desk
    shaded(cv, rrp(x - 128, desk - 4, x + 128, desk + 12, 6), '#F5E9DC', dx=-4, dy=-4)
    shaded(cv, rrp(x - 112, desk + 12, x + 112, floor - 8, 8), '#D2BCAE', dx=-6, dy=-6)
    cv.drawRect(R(x - 112, desk + 12, x + 112, desk + 22), paint('#000000', 30))
    if (fl + x) % 3 == 1:
        shaded(cv, rrp(x + 80, desk - 34, x + 104, desk - 4, 5), '#FFFFFF', dx=-3, dy=-3)
        cv.drawPath(poly([(x + 104, desk - 26), (x + 112, desk - 22), (x + 112, desk - 14), (x + 104, desk - 10)], False), paint('#FFFFFF', stroke=4))
        for k in range(2):
            yy = desk - 44 - k * 12 - (t * 20 % 12)
            cv.drawCircle(x + 92 + math.sin(t * 3 + k) * 3, yy, 3, paint('#ffffff', 90))


def lamp(cv, x, ceil, floor, sway, on=1.0):
    ang = sway
    cv.save()
    cv.rotate(ang, x, ceil)
    cv.drawPath(poly([(x, ceil), (x, ceil + 46)], False), paint('#2B2350', stroke=3))
    cone = poly([(x - 18, ceil + 58), (x + 18, ceil + 58), (x + 150, floor - 10), (x - 150, floor - 10)])
    cv.drawPath(cone, paint(shader=lin(0, ceil + 58, 0, floor, [('#FFF4D6', 60 * on), ('#FFF4D6', 0)])))
    p = skia.Path()
    p.moveTo(x - 30, ceil + 66)
    p.cubicTo(x - 28, ceil + 40, x + 28, ceil + 40, x + 30, ceil + 66)
    p.close()
    shaded(cv, p, '#3A3168', dx=-3, dy=-3)
    glow(cv, x, ceil + 66, 60, '#FFE9B5', 200 * on)
    cv.drawCircle(x, ceil + 64, 8, paint('#FFF8E0'))
    cv.restore()


def building(cv, t, sh):
    sway = (sh[0]) * .5 + math.sin(t * .8) * 1.2
    # outer shell
    shaded(cv, rrp(BL, ROOF - 10, BR, GROUND + 6, 16), '#3B2E6E', dx=-10, dy=-8)
    for fl in range(2):
        top, bot = CEIL[fl], FLOORS[fl]
        wall = ['#F6B48A', '#F2A07E'][fl]
        wall2 = ['#E8916E', '#DC7D66'][fl]
        cv.drawRect(R(BL + 24, top, BR - 24, bot), paint(shader=lin(0, top, 0, bot, [wall, wall2])))
        # skirting
        cv.drawRect(R(BL + 24, bot - 18, BR - 24, bot), paint(dark(wall2, .25)))
        if fl == 0:
            # window strip with night sky
            for wx in (140, 410, 680):
                wr = rrp(wx, 525, wx + 230, 600, 10)
                cv.drawPath(wr, paint(shader=lin(0, 525, 0, 600, ['#1A1448', '#3C2470'])))
                cv.save()
                cv.clipPath(wr, skia.ClipOp.kIntersect, True)
                stars(cv, t, n=230, ox=0, oy=0)
                cv.restore()
                cv.drawPath(wr, paint('#FFFFFF', 140, stroke=6))
                cv.drawPath(poly([(wx + 115, 525), (wx + 115, 600)], False), paint('#FFFFFF', 140, stroke=5))
        else:
            for px, pc in ((385, '#5BC0EB'), (695, '#FDE74C')):
                shaded(cv, rrp(px - 34, 975, px + 34, 1060, 6), pc, dx=-4, dy=-4)
                cv.drawCircle(px, 1005, 14, paint('#ffffff', 160))
                cv.drawRect(R(px - 20, 1030, px + 20, 1036), paint('#ffffff', 160))
        for x in (385, 695):
            lamp(cv, x, top, bot, sway)
        for px in (BL + 60, BR - 60):
            shaded(cv, rrp(px - 24, bot - 70, px + 24, bot - 10, 8), '#F1EEF8', dx=-4, dy=-4)
            for k, (ox, oy, rr) in enumerate(((-14, -88, 26), (14, -96, 24), (0, -120, 26))):
                shaded(cv, cp(px + ox + math.sin(t * 1.5 + k) * 2, bot + oy, rr), '#57C27A', dx=-5, dy=-5)
        for (wf, wx, sp) in WORKERS:
            if wf == fl:
                worker(cv, fl, wx, sp, t, sway)
    # slab between floors
    shaded(cv, rrp(BL, FLOORS[0] - 2, BR, CEIL[1] + 2, 4), '#4A3C80', dx=0, dy=-6)
    # roof
    shaded(cv, rrp(BL - 14, ROOF - 18, BR + 14, CEIL[0] + 2, 8), '#4A3C80', dx=-6, dy=-6)
    cv.drawRect(R(BL - 14, ROOF - 18, BR + 14, ROOF - 12), paint('#7A6AC0', 160))
    # antenna + blinking light
    cv.drawPath(poly([(880, ROOF - 18), (880, ROOF - 120)], False), paint('#2B2350', stroke=6))
    blink = 1 if (t * 1.2) % 1 < .5 else .2
    glow(cv, 880, ROOF - 124, 40, '#FF4A5A', 200 * blink)
    cv.drawCircle(880, ROOF - 124, 7, paint('#FF7A85'))
    for sx in (330, 750):
        cv.drawPath(poly([(sx, ROOF - 18), (sx, ROOF - 70)], False), paint('#2B2350', stroke=8))
    cv.drawPath(poly([(320, ROOF - 52), (760, ROOF - 52)], False), paint('#2B2350', stroke=6))
    fl_ = 1 - .7 * (1 if (int(t * 4) % 13 == 0) else 0)
    glow(cv, 540, ROOF - 95, 330, '#FF5FA0', 70 * fl_, mid=1)
    text(cv, 'NEWSROOM', 540, ROOF - 95, font('bold', 62), '#FF5FA0', 140 * fl_, track=10, shadow=0)
    text(cv, 'NEWSROOM', 540, ROOF - 95, font('bold', 62), '#FFD0E4', 255 * fl_, track=10)
    # ground floor shadow under slab edges
    cv.drawRect(R(BL + 24, CEIL[0], BR - 24, CEIL[0] + 16), paint('#000000', 35))
    cv.drawRect(R(BL + 24, CEIL[1], BR - 24, CEIL[1] + 16), paint('#000000', 35))


def draw(cv, t, fi):
    sh = shake_at(t)
    cv.save()
    z = 1 + .06 * ease(t / DUR)
    cv.translate(540 + sh[0], 860 + sh[1])
    cv.scale(z, z)
    cv.translate(-540, -860)
    # sky
    cv.drawRect(R(-200, -200, W + 200, GROUND + 10), paint(shader=lin(0, 0, 0, GROUND, ['#070A2A', '#1A1550', '#4A2272', '#8A3A72'], [0, .45, .85, 1])))
    stars(cv, t, ymax=1100)
    glow(cv, 190, 200, 300, '#F6E6C0', 60, mid=1)
    shaded(cv, cp(190, 200, 70), '#F4EBD2', '#D9CDB0', dx=-10, dy=-10)
    for cx, cy, cr in ((170, 184, 12), (208, 224, 9), (215, 176, 6)):
        cv.drawCircle(cx, cy, cr, paint('#E2D6B8'))
    for m in METEORS:
        if m['kind'] == 'far':
            meteor_flight(cv, m, t)
    city(cv, t)
    for m in METEORS:
        if m['kind'] == 'far':
            impact_back(cv, m, t)
            impact_front(cv, m, t)
    # ground
    cv.drawRect(R(-200, GROUND, W + 200, H + 200), paint(shader=lin(0, GROUND, 0, H, ['#2A1B52', '#140B2C', '#0A0618'])))
    cv.drawRect(R(-200, GROUND, W + 200, GROUND + 5), paint('#6A4FB0', 150))
    glow(cv, 540, GROUND, 600, '#FFB27A', 40, mid=1)
    building(cv, t, sh)
    for m in METEORS:
        if m['kind'] != 'far':
            impact_back(cv, m, t)
    for m in METEORS:
        if m['kind'] != 'far':
            meteor_flight(cv, m, t)
            impact_front(cv, m, t)
    cv.restore()
    for m in METEORS:
        a = t - m['th']
        if 0 <= a < .35 and m['kind'] != 'far':
            cv.drawRect(R(0, 0, W, H), paint('#FFB070', 70 * (1 - a / .35)))
    vignette(cv, 140)
    scrim(cv, 1200, 210)
    subtitle(cv, t, .2, 3.0, "Every day, journalists across {hl:Ireland}\nwork to keep you informed.")
    subtitle(cv, t, 3.0, 6.0, "But {hl:independent newsrooms}\nare facing mounting pressure.")
    subtitle(cv, t, 6.0, 9.0, "Legal threats. Funding cuts.\nShrinking space to report.")
    subtitle(cv, t, 9.0, 12.5, "If they go quiet,\n{hl:who tells your story?}", fade_out=False)
    a = eout(prog(t, .4, 1.2))
    cv.drawRect(R(W / 2 - 40, 1563, W / 2 + 40, 1566), paint('#FFC94A', 200 * a))
    text(cv, 'INDEPENDENT MEDIA IS UNDER ATTACK IN IRELAND', W / 2, 1596, font('bold', 25), '#FFFFFF', 225 * a, track=2.5)


if __name__ == '__main__':
    run('v1', DUR, draw)
