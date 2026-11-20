import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from kz import *
from intern_dyslexia import truck

DUR = 14.5
NX, NF, NR = 540, 1300, 115           # Nasti x, floor, head radius
PHONE_Y = NF - 2.12 * NR


# ------------------------------------------------------------- living room
def living_room(cv, t, glow_on=1.0):
    cv.drawRect(R(0, 0, W, 1190), paint(shader=lin(0, 0, 0, 1190, ['#10153D', '#232860'])))
    # window
    wr = rrp(70, 170, 370, 640, 12)
    cv.drawPath(wr, paint(shader=lin(0, 170, 0, 640, ['#070B2C', '#33236A'])))
    cv.save()
    cv.clipPath(wr, skia.ClipOp.kIntersect, True)
    stars(cv, t)
    glow(cv, 290, 260, 120, '#F6E6C0', 70, mid=1)
    shaded(cv, cp(290, 260, 34), '#F4EBD2', '#D9CDB0', dx=-5, dy=-5)
    for i in range(8):
        bx = 70 + i * 40
        bh = 50 + (i * 53) % 120
        cv.drawRect(R(bx, 640 - bh, bx + 36, 640), paint('#171035'))
        for j in range(int(bh / 28)):
            if (i * 3 + j) % 4:
                cv.drawRect(R(bx + 9, 640 - bh + 12 + j * 26, bx + 16, 640 - bh + 22 + j * 26), paint('#FFC870', 150))
    cv.restore()
    cv.drawPath(wr, paint('#3B3F7A', stroke=14))
    cv.drawPath(poly([(220, 170), (220, 640)], False), paint('#3B3F7A', stroke=9))
    cv.drawPath(poly([(70, 405), (370, 405)], False), paint('#3B3F7A', stroke=9))
    # curtains
    for cx_, sd in ((60, 1), (380, -1)):
        p = skia.Path()
        p.moveTo(cx_ - 34, 140)
        p.lineTo(cx_ + 34, 140)
        p.cubicTo(cx_ + 20 + sd * 10, 360, cx_ + 44 * sd + 10, 560, cx_ + 30, 700)
        p.lineTo(cx_ - 30, 700)
        p.cubicTo(cx_ - 34, 520, cx_ - 30, 300, cx_ - 34, 140)
        p.close()
        shaded(cv, p, '#7A3E7E', dx=-6 * sd, dy=0)
    cv.drawRect(R(20, 132, 420, 146), paint('#2B2350'))
    # frames
    for fx, fy, fw, fh, c in ((640, 330, 130, 160, '#FFC94A'), (800, 380, 110, 90, '#5BC0EB')):
        shaded(cv, rrp(fx, fy, fx + fw, fy + fh, 8), '#3B3F7A', dx=-4, dy=-4)
        cv.drawPath(rrp(fx + 12, fy + 12, fx + fw - 12, fy + fh - 12, 4), paint(c, 200))
        cv.drawCircle(fx + fw / 2, fy + fh / 2, min(fw, fh) * .18, paint('#ffffff', 130))
    # floor lamp (dim)
    cv.drawPath(poly([(960, 1240), (960, 640)], False), paint('#2B2350', stroke=9))
    cv.drawOval(R(915, 1225, 1005, 1250), paint('#2B2350'))
    p = poly([(905, 640), (1015, 640), (990, 560), (930, 560)])
    shaded(cv, p, '#F2C46A', dx=-4, dy=-4)
    glow(cv, 960, 650, 380, '#FFC870', 55, mid=1)
    # floor + rug
    cv.drawRect(R(0, 1190, W, H), paint(shader=lin(0, 1190, 0, H, ['#2A2052', '#140B2A', '#0A0618'])))
    cv.drawRect(R(0, 1186, W, 1196), paint('#3A2D6A'))
    cv.drawOval(R(160, 1270, 920, 1380), paint('#3E2E70'))
    cv.drawOval(R(190, 1280, 890, 1370), paint('#4A3884', stroke=6))
    # plant
    shaded(cv, rrp(100, 1110, 170, 1220, 12), '#E9E4F4', dx=-4, dy=-4)
    for k, (ox, oy, rr_) in enumerate(((-26, -150, 40), (26, -168, 38), (0, -215, 40), (-36, -230, 30), (34, -250, 28))):
        shaded(cv, cp(135 + ox + math.sin(t * .9 + k) * 2, 1125 + oy * .55, rr_), '#4FB874', dx=-5, dy=-5)
    # sofa back + arms
    shaded(cv, rrp(250, 880, 830, 1170, 60), '#6B3E8E', dx=-10, dy=-10)
    for cx_ in (335, 745):
        shaded(cv, rrp(cx_ - 72, 915, cx_ + 72, 1080, 40), '#7D4CA0', dx=-6, dy=-6)


def sofa_front(cv):
    shaded(cv, rrp(255, 1196, 825, 1262, 26), '#7D4CA0', dx=-8, dy=-8)
    for x0 in (200, 790):
        shaded(cv, rrp(x0, 1000, x0 + 90, 1255, 40), '#5E3580', dx=-8, dy=-8)
    for x_ in (280, 800):
        cv.drawPath(rrp(x_ - 8, 1252, x_ + 8, 1290, 4), paint('#2A1840'))


def phone_back(cv, x, y, s=1.0, lit=1.0):
    if lit > 0:
        glow(cv, x, y - 80, 360, '#7FC4FF', 42 * lit, mid=1)
    shaded(cv, rrp(x - 38 * s, y - 70 * s, x + 38 * s, y + 70 * s, 12 * s), '#262A44', dx=-4 * s, dy=-4 * s)
    cv.drawPath(rrp(x - 26 * s, y - 60 * s, x - 6 * s, y - 34 * s, 6 * s), paint('#14162A'))
    cv.drawCircle(x - 16 * s, y - 47 * s, 5 * s, paint('#3A3E66'))


def nasti_seated(cv, t, fc, phone_k=1.0, lit=1.0, thumb=0.0, shake=0.0, tilt=0):
    rest = [((-.95, -1.55), (-.55, -1.2)), ((.95, -1.55), (.55, -1.2))]
    hold = [((-.98, -1.55), (-.38, -2.0)), ((.98, -1.55), (.38, -2.0 + thumb))]
    k = ease(phone_k)
    arms = [(lerp2(rest[i][0], hold[i][0], k), lerp2(rest[i][1], hold[i][1], k)) for i in range(2)]
    py = lerp(NF - 1.2 * NR, PHONE_Y, k)

    def held(cv_):
        phone_back(cv_, NX + shake * 6, py, 1.0, lit * k)
    if lit > 0:
        # screen light on the face
        pass
    person(cv, NX + shake * 6, NF, NR, NASTI, dict(legs='sit', arms=arms, face=fc, held=held, tilt=tilt,
                                                   lift=math.sin(t * 2) * .015))
    if lit * k > 0:
        glow(cv, NX, NF - 3.75 * NR, 1.3 * NR, '#8FD0FF', 26 * lit * k, mid=1)


def steam(cv, t, x, y, r, a=1.0):
    for sd in (-1, 1):
        for i in range(3):
            ph = (t * 1.3 + i / 3) % 1
            px = x + sd * (1.15 * r + ph * .5 * r)
            py = y - .3 * r - ph * 1.2 * r
            cv.drawCircle(px, py, (.12 + .25 * ph) * r, paint('#FFFFFF', 170 * (1 - ph) * a))


# ------------------------------------------------------------- phone UI
PH = (320, 90, 760, 690)          # inset phone screen


def phone_frame(cv, k, draw_content):
    if k <= 0:
        return
    l, tp, r_, b = PH
    cx, cy = (l + r_) / 2, (tp + b) / 2
    cv.save()
    s = eback(k, 1.3)
    cv.translate(cx, cy)
    cv.scale(s, s)
    cv.translate(-cx, -cy)
    glow(cv, cx, cy, 480, '#7FC4FF', 70)
    cv.drawPath(rrp(l - 4, tp + 10, r_ + 4, b + 24, 54), paint('#05031a', 140, blur=22))
    shaded(cv, rrp(l - 16, tp - 16, r_ + 16, b + 16, 56), '#1B1D33', dx=-5, dy=-5)
    scr = rrp(l, tp, r_, b, 44)
    cv.save()
    cv.clipPath(scr, skia.ClipOp.kIntersect, True)
    cv.drawPath(scr, paint('#F3F2FA'))
    draw_content(cv)
    cv.restore()
    cv.drawPath(rrp(cx - 60, tp + 8, cx + 60, tp + 34, 13), paint('#1B1D33'))
    cv.restore()


POST_H = 340
POST_COLS = ['#FFB86B', '#7FD1AE', '#9DB4FF', '#FF8FB1', None, '#FFD66B', '#B49CFF']


def avatar(cv, x, y, r, c):
    cv.drawCircle(x, y, r, paint(c))
    cv.drawCircle(x, y - r * .18, r * .38, paint('#ffffff', 200))
    cv.drawOval(R(x - r * .6, y + r * .25, x + r * .6, y + r * 1.0), paint('#ffffff', 200))


def feed(cv, t, scroll, hi=0.0):
    l, tp, r_, b = PH
    for i, c in enumerate(POST_COLS):
        y = tp + 80 + i * POST_H - scroll
        if y > b or y + POST_H < tp:
            continue
        cv.drawPath(rrp(l + 16, y, r_ - 16, y + POST_H - 16, 20), paint('#FFFFFF'))
        avatar(cv, l + 50, y + 34, 20, c or '#E5484D')
        cv.drawPath(rrp(l + 82, y + 22, l + 220, y + 34, 6), paint('#262448', 200))
        cv.drawPath(rrp(l + 82, y + 40, l + 170, y + 48, 4), paint('#9A98B8', 160))
        img = (l + 30, y + 64, r_ - 30, y + 264)
        if c:
            cv.drawPath(rrp(*img, 14), paint(c, 140))
            cv.drawCircle((img[0] + img[2]) / 2, (img[1] + img[3]) / 2, 40, paint('#ffffff', 120))
        else:
            ir = rrp(*img, 14)
            cv.save()
            cv.clipPath(ir, skia.ClipOp.kIntersect, True)
            cv.drawRect(R(*img), paint(shader=lin(0, img[1], 0, img[3], ['#9FD8FF', '#E6F6FF'])))
            cv.drawRect(R(img[0], img[3] - 26, img[2], img[3]), paint('#7FCB8A'))
            truck(cv, (img[0] + img[2]) / 2 + 20, img[3] - 26, .5, t, label='NASTI')
            cv.restore()
            if hi > 0:
                cv.drawPath(ir, paint('#FF3B3B', 255 * hi, stroke=6))
                glow(cv, (img[0] + img[2]) / 2, (img[1] + img[3]) / 2, 260, '#FF3B3B', 60 * hi)
        for k, ic in enumerate(('#E5484D', '#9A98B8', '#9A98B8')):
            cv.drawCircle(l + 52 + k * 44, y + 292, 11, paint(ic, 200, stroke=4))
    cv.drawRect(R(l, tp, r_, tp + 76), paint('#FFFFFF'))
    cv.drawRect(R(l, tp + 76, r_, tp + 78), paint('#E4E2F0'))
    text(cv, 'Feed', l + 34, tp + 56, font('bold', 30), '#262448', anchor='l')


def scroll_at(t):
    target = 4 * POST_H - 40
    s = 0
    for a, b, frac in ((1.9, 2.5, .3), (2.6, 3.2, .35), (3.3, 4.2, .35)):
        s += frac * ease(prog(t, a, b))
    return target * s


# ------------------------------------------------------------- scenes
def scene_room(cv, t):
    cv.save()
    z = 1 + .05 * ease(t / 8)
    cv.translate(540, 900)
    cv.scale(z, z)
    cv.translate(-540, -900)
    living_room(cv, t)
    phone_k = prog(t, .6, 1.4)
    lit = ease(prog(t, 1.35, 1.6))
    sc = scroll_at(t)
    moving = any(a < t < b for a, b in ((1.9, 2.5), (2.6, 3.2), (3.3, 4.2)))
    thumb = math.sin(t * 20) * .06 if moving else 0
    surprise = prog(t, 4.35, 4.5)
    anger = ease(prog(t, 5.0, 6.2))
    if t < 4.35:
        fc = dict(eyes='open', squint=.35, mouth=.15, look=(0, .8), blush=.4)
    elif t < 5.0:
        fc = dict(eyes='wide', mouth=-.1, look=(0, .8), brows=((-10, .08), (-10, .08)), blush=.5)
    else:
        fc = dict(eyes='open', squint=.25, look=(0, .8), mouth=lerp(-.2, -.7, anger),
                  brows=((lerp(0, 24, anger), lerp(.03, -.04, anger)), (lerp(0, 24, anger), lerp(.03, -.04, anger))),
                  blush=lerp(.5, 1.3, anger), blushc=(255, 70, 70))
    nasti_seated(cv, t, fc, phone_k, lit, thumb, tilt=math.sin(t * .8) * 2 - 3 * anger)
    sofa_front(cv)
    cv.restore()
    ph_k = prog(t, 1.55, 2.0) * (1 - prog(t, 7.6, 8.0))
    phone_frame(cv, ph_k, lambda c: feed(c, t, sc, hi=eout(prog(t, 4.4, 4.8)) * (.75 + .25 * math.sin(t * 8))))


def shrug_pose(t, t0):
    k = ease(prog(t, t0, t0 + .45)) * (1 - ease(prog(t, t0 + 1.9, t0 + 2.4)))
    k2 = ease(prog(t, t0 + 3.0, t0 + 3.45))
    k = max(k, k2)
    rest = [((-.95, -2.0), (-.9, -1.35)), ((.95, -2.0), (.9, -1.35))]
    up = [((-1.12, -1.95), (-1.62, -2.5)), ((1.12, -1.95), (1.62, -2.5))]
    arms = [(lerp2(rest[i][0], up[i][0], k), lerp2(rest[i][1], up[i][1], k)) for i in range(2)]
    return arms, k


def scene_shrug(cv, t):
    cv.save()
    z = 1.02 + .03 * ease(prog(t, 8, 14.5))
    cv.translate(540, 900)
    cv.scale(z, z)
    cv.translate(-540, -900)
    stage(cv, t)
    ground_shadow(cv, 540, 1240, 190)
    arms, k = shrug_pose(t, 8.7)
    fc = dict(eyes='open', look=(.2 * k, 0), brows=((-12 * k, .12 * k), (-12 * k, .12 * k)), mouth=lerp(.5, .25, k))
    person(cv, 540, 1240, 150, CLODAGH, dict(arms=arms, face=fc, lift=-.12 * k, tilt=8 * k))
    cv.restore()


def draw(cv, t, fi):
    wipe = prog(t, 8.0, 8.7)
    if wipe < 1:
        scene_room(cv, t)
    if wipe > 0:
        cv.save()
        if wipe < 1:
            cv.clipPath(cp(540, 760, 1400 * ease(wipe)), skia.ClipOp.kIntersect, True)
        scene_shrug(cv, t)
        cv.restore()
        if wipe < 1:
            cv.drawCircle(540, 760, 1400 * ease(wipe), paint('#FFC94A', 200, stroke=10))
    vignette(cv, 140)
    scrim(cv, 1180, 210)
    subtitle(cv, t, .3, 4.25, "When {hl:N-A-S-T-I} saw this video,")
    subtitle(cv, t, 4.35, 8.0, "he assumed it was {hl:about him}...")
    subtitle(cv, t, 8.4, 15, "...even though Clodagh didn't\nknow {hl:Nasty} existed.", fade_out=False)


if __name__ == '__main__':
    run('v3', DUR, draw)
