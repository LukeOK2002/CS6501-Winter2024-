import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from kz import *
from intern_dyslexia import truck
from phone_misunderstanding import living_room, sofa_front, nasti_seated, steam, phone_frame, PH, avatar, NX, NF, NR, PHONE_Y

DUR = 17.5
ORIG = (NX, PHONE_Y)

# ------------------------------------------------------------- follower network
rn = random.Random(21)
NODES = []
for i in range(240):
    a = i * 2.39996 + rn.uniform(-.2, .2)
    d = (70 + 66 * math.sqrt(i)) * rn.uniform(.9, 1.1)
    x = ORIG[0] + math.cos(a) * d
    y = ORIG[1] + math.sin(a) * d * 1.25
    if not (30 < x < W - 30 and 60 < y < 1300):
        continue
    NODES.append([x, y, d, rn.uniform(13, 22), rn.choice(['#FFB86B', '#7FD1AE', '#9DB4FF', '#FF8FB1', '#FFD66B', '#B49CFF']), rn.random()])
NODES.sort(key=lambda n: n[2])
for i, n in enumerate(NODES):
    # parent = nearest earlier node closer to origin (or the origin itself)
    best, bd = None, 1e9
    for m in NODES[:i]:
        dd = math.hypot(m[0] - n[0], m[1] - n[1])
        if dd < bd and m[2] < n[2]:
            best, bd = m, dd
    n.append(best if best and bd < 260 else None)


def network(cv, t, a):
    if a <= 0:
        return
    front = lerp(0, 1400, ease(prog(t, 2.3, 4.7)))
    red = prog(t, 7.6, 9.6)
    cv.drawRect(R(0, 0, W, H), paint('#070520', 200 * a))
    # edges
    for n in NODES:
        if n[2] > front:
            continue
        p = n[6] or (ORIG[0], ORIG[1], 0)
        rk = clamp((red * 1500 - n[2]) / 200)
        c = mix('#8C7CFF', '#FF4A5A', rk)
        cv.drawPath(poly([(p[0], p[1]), (n[0], n[1])], False), paint(c, 110 * a, stroke=2.5))
        ph = (t * .9 + n[5]) % 1
        px, py = lerp(p[0], n[0], ph), lerp(p[1], n[1], ph)
        cv.drawCircle(px, py, 3.5, paint(c, 220 * a))
    for n in NODES:
        k = eback(clamp((front - n[2]) / 120))
        if k <= 0:
            continue
        rk = clamp((red * 1500 - n[2]) / 200)
        c = mix(n[4], '#E5484D', rk)
        if rk > 0:
            glow(cv, n[0], n[1], n[3] * 3.2, '#FF3B3B', 90 * rk * a)
        cv.save()
        cv.translate(n[0], n[1])
        cv.scale(k, k)
        avatar(cv, 0, 0, n[3], c)
        if rk > .5:
            for sd in (-1, 1):
                cv.drawPath(poly([(sd * n[3] * .55, -n[3] * .5), (sd * n[3] * .15, -n[3] * .3)], False), paint('#2A0A14', 220, stroke=2.5))
        cv.restore()
    # hub (his phone)
    glow(cv, ORIG[0], ORIG[1], 160, '#7FC4FF', 140 * a)
    cv.drawCircle(ORIG[0], ORIG[1], 34, paint('#262A44', 255 * a))
    cv.drawCircle(ORIG[0], ORIG[1], 34, paint('#7FC4FF', 255 * a, stroke=4))
    # counter
    k = eout(prog(t, 2.3, 2.7)) * a
    if k > 0:
        n = int(round(300000 * ease(prog(t, 2.4, 4.8)) / 10) * 10)
        f = font('bold', 52)
        s_ = f'{n:,}'
        w = f.measureText(s_) + font('semi', 34).measureText(' followers') + 70
        cv.save()
        cv.translate(W / 2, 150)
        cv.scale(k, k)
        cv.drawPath(rrp(-w / 2, -48, w / 2, 48, 48), paint('#FFFFFF'))
        x0 = -w / 2 + 35
        x0 += text(cv, s_, x0, 0, f, '#272448', anchor='l')
        text(cv, ' followers', x0, 2, font('semi', 34), '#7A78A0', anchor='l')
        cv.restore()


def share_ui(cv, t):
    l, tp, r_, b = PH
    cv.drawRect(R(l, tp, r_, b), paint('#F3F2FA'))
    img = (l + 30, tp + 120, r_ - 30, tp + 380)
    cv.drawPath(rrp(l + 16, tp + 60, r_ - 16, tp + 470, 20), paint('#FFFFFF'))
    avatar(cv, l + 50, tp + 92, 20, '#E5484D')
    cv.drawPath(rrp(l + 82, tp + 80, l + 220, tp + 92, 6), paint('#262448', 200))
    ir = rrp(*img, 14)
    cv.save()
    cv.clipPath(ir, skia.ClipOp.kIntersect, True)
    cv.drawRect(R(*img), paint(shader=lin(0, img[1], 0, img[3], ['#9FD8FF', '#E6F6FF'])))
    cv.drawRect(R(img[0], img[3] - 30, img[2], img[3]), paint('#7FCB8A'))
    truck(cv, (img[0] + img[2]) / 2 + 20, img[3] - 30, .55, t, label='NASTI')
    cv.restore()
    # share sheet
    k = eout(prog(t, .6, 1.1))
    sy = lerp(b + 10, b - 230, k)
    cv.drawRect(R(l, tp, r_, b), paint('#000000', 80 * k))
    cv.drawPath(rrp(l, sy, r_, b + 60, 34), paint('#FFFFFF'))
    cv.drawPath(rrp((l + r_) / 2 - 30, sy + 12, (l + r_) / 2 + 30, sy + 18, 3), paint('#D0CEE0'))
    text(cv, 'Share to', l + 36, sy + 54, font('semi', 26), '#7A78A0', anchor='l')
    press = prog(t, 1.55, 1.75)
    done = t > 1.8
    bs = 1 - .08 * math.sin(math.pi * press)
    cx, cy = (l + r_) / 2, sy + 140
    cv.save()
    cv.translate(cx, cy)
    cv.scale(bs, bs)
    cv.drawPath(rrp(-170, -44, 170, 44, 44), paint('#38C172' if done else '#4C6BFF'))
    if done:
        cv.drawPath(poly([(-92, 0), (-80, 12), (-58, -12)], False), paint('#ffffff', stroke=6))
        text(cv, 'Shared', 15, 0, font('bold', 32), '#FFFFFF')
    else:
        text(cv, 'All followers', 0, 0, font('bold', 30), '#FFFFFF')
    cv.restore()
    if 1.55 < t < 2.3:
        q = prog(t, 1.55, 2.3)
        cv.drawCircle(cx + 40, cy, 30 + 160 * eout(q), paint('#4C6BFF', 160 * (1 - q), stroke=6))
        cv.drawCircle(cx + 40, cy + 6 * (1 - prog(t, 1.4, 1.6)), 26, paint('#F7D3BD', 200 * (1 - prog(t, 1.8, 2.0))))


def post_card(cv, t):
    k = eback(prog(t, 5.6, 6.1), 1.2) * (1 - ease(prog(t, 9.7, 10.0)))
    if k <= 0:
        return
    cv.save()
    cv.translate(W / 2, 520)
    cv.scale(k, k)
    cv.drawPath(rrp(-430, -170, 430, 200, 40), paint('#05031a', 150, blur=26))
    shaded(cv, rrp(-430, -190, 430, 180, 40), '#FFFFFF', '#E8E6F4', dx=-8, dy=-8)
    # avatar = Nasti
    ax, ay = -350, -110
    cv.save()
    cv.clipPath(cp(ax, ay, 44), skia.ClipOp.kIntersect, True)
    cv.drawCircle(ax, ay, 44, paint('#4C64AE'))
    from kz import _front_hair, face as _face
    shaded(cv, cp(ax, ay + 8, 30), NASTI['skin'], dx=-4, dy=-4)
    _front_hair(cv, ax, ay + 8, 30, NASTI)
    _face(cv, ax, ay + 8, 30, dict(brows=((25, 0), (25, 0)), mouth=-.6, blush=.8, blushc=(255, 70, 70)), NASTI)
    cv.restore()
    text(cv, 'Nasti', -285, -126, font('bold', 38), '#272448', anchor='l')
    text(cv, '@nasti  ·  300K followers', -285, -84, font('med', 26), '#8A88AA', anchor='l')
    full = [('Lads, I need your ', '#272448'), ('“help”', '#E5484D'), (' with this.', '#272448')]
    total = sum(len(s) for s, _ in full)
    n = int(total * prog(t, 6.2, 7.5))
    f = font('semi', 44)
    x, y = -370, 10
    shown = 0
    for s, c in full:
        part = s[:max(0, n - shown)]
        shown += len(s)
        if part:
            x += text(cv, part, x, y, f, c, anchor='l')
    if prog(t, 6.2, 7.5) < 1 and int(t * 3) % 2 == 0:
        cv.drawRect(R(x + 4, y - 26, x + 8, y + 26), paint('#272448'))
    # reactions counter
    likes = int(12400 * ease(prog(t, 7.6, 9.6)))
    shares = int(3100 * ease(prog(t, 7.8, 9.6)))
    cv.drawRect(R(-390, 88, 390, 90), paint('#E6E4F0'))
    hp = skia.Path()
    hx_, hy_ = -358, 132
    hp.moveTo(hx_, hy_ + 12)
    hp.cubicTo(hx_ - 22, hy_ - 2, hx_ - 12, hy_ - 20, hx_, hy_ - 8)
    hp.cubicTo(hx_ + 12, hy_ - 20, hx_ + 22, hy_ - 2, hx_, hy_ + 12)
    cv.drawPath(hp, paint('#E5484D'))
    text(cv, f'{likes:,}', -330, 132, font('semi', 30), '#E5484D', anchor='l')
    text(cv, f'{shares:,} shares', -120, 132, font('semi', 30), '#8A88AA', anchor='l')
    cv.restore()


def scene_room(cv, t):
    cv.save()
    z = 1.03 + .03 * ease(t / 5)
    cv.translate(540, 900)
    cv.scale(z, z)
    cv.translate(-540, -900)
    living_room(cv, t)
    fury = .85 + .15 * math.sin(t * 6)
    fc = dict(eyes='open', squint=.35, look=(0, .8), mouth=-.85, mopen=0,
              brows=((30, -.06), (30, -.06)), blush=1.6 * fury, blushc=(255, 60, 60))
    shake = math.sin(t * 40) * .6
    tap = -.18 * math.sin(math.pi * prog(t, 1.45, 1.75))
    nasti_seated(cv, t, fc, 1.0, 1.0, tap, shake=shake, tilt=-3)
    steam(cv, t, NX + shake * 6, NF - 3.85 * NR, NR, 1)
    glow(cv, NX, NF - 3.85 * NR, 2.2 * NR, '#FF3B3B', 40 * fury, mid=1)
    sofa_front(cv)
    cv.restore()
    phone_frame(cv, prog(t, .15, .55) * (1 - prog(t, 2.2, 2.5)), lambda c: share_ui(c, t))


# ------------------------------------------------------------- onslaught
COMMENTS = ['ur a joke', 'DELETE THIS', 'disgraceful', 'who hired u??', 'learn to spell', 'get her fired',
            'pathetic', 'embarrassing', 'clown', 'just quit', 'unemployable', 'shameful', 'state of this',
            'cringe', 'do better', 'sack her']
rc = random.Random(5)
DROPS = []
tt = 11.0
buckets = {}
while tt < 16.6:
    x = rc.choice([rc.uniform(90, 360), rc.uniform(720, 990), rc.uniform(380, 700)])
    txt = rc.choice(COMMENTS)
    b = int(x // 170)
    st = buckets.get(b, 0)
    buckets[b] = st + 1
    behind = 360 < x < 720
    land = (1180 - st * 40) if behind else 1240 - 34 - st * 58
    DROPS.append(dict(t=tt, x=x, txt=txt, land=land, behind=behind, rot=rc.uniform(-12, 12), dur=rc.uniform(.6, .85)))
    tt += max(.12, .55 - (tt - 11) * .09)


def bubble(cv, x, y, txt, rot, a=255, s=1.0):
    f = font('bold', 32)
    w = f.measureText(txt) + 50
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    cv.scale(s, s)
    cv.drawPath(rrp(-w / 2, -30, w / 2, 34, 30), paint('#05031a', 90 * a / 255, blur=8))
    p = rrp(-w / 2, -34, w / 2, 30, 30)
    p.addPath(poly([(-w / 2 + 26, 20), (-w / 2 + 14, 52), (-w / 2 + 52, 24)]))
    cv.drawPath(p, paint('#FFFFFF', a))
    text(cv, txt, 0, -2, f, '#D7263D', a)
    cv.restore()


def drop_pos(d, t):
    a = t - d['t']
    tx = d['x']
    ty = d['land'] if d['land'] else (lerp(560, 1150, (d['x'] - 380) / 320) if False else None)
    if d['land'] is None:
        # falls past her, off the bottom
        ty = 2100
    q = clamp(a / d['dur'])
    sx, sy = tx + 520, -220
    x = lerp(sx, tx, ein(q) * .7 + q * .3)
    y = lerp(sy, ty, ein(q) * .7 + q * .3)
    return x, y, q


def scene_onslaught(cv, t):
    mood = ease(prog(t, 10.6, 14))
    hits = 0
    for d in DROPS:
        a = t - d['t'] - d['dur']
        if 0 < a < .25 and d['land']:
            hits += (1 - a / .25)
    sx, sy = math.sin(t * 70) * 6 * hits, math.cos(t * 63) * 6 * hits
    cv.save()
    cv.translate(sx, sy)
    z = 1.02 + .05 * ease(prog(t, 10, 17.5))
    cv.translate(540, 900)
    cv.scale(z, z)
    cv.translate(-540, -900)
    stage(cv, t, mood=mood, spot=1 - .4 * mood)
    ground_shadow(cv, 540, 1240, 190)
    worry = ease(prog(t, 11.3, 12.0))
    trem = math.sin(t * 30) * .01 * worry
    rest = [((-.95, -2.0), (-.9, -1.35)), ((.95, -2.0), (.9, -1.35))]
    hug = [((-1.0, -1.75), (.3, -2.35)), ((1.0, -1.75), (-.3, -2.3))]
    k = ease(prog(t, 12.4, 13.0))
    arms = [(lerp2(rest[i][0], hug[i][0], k), lerp2(rest[i][1], hug[i][1], k)) for i in range(2)]
    if t < 11.3:
        fc = dict(eyes='open', mouth=.6, look=(.5, -.6))
    else:
        fc = dict(eyes='wide' if t < 12.2 else 'open', look=(lerp(.5, .1, worry), lerp(-.6, -.2, worry)),
                  brows=((-22 * worry, .1 * worry), (-22 * worry, .1 * worry)), mouth=lerp(.3, -.55, worry),
                  wavy=t > 13.5, blush=.6)
    for d in DROPS:
        if d['behind'] and t >= d['t'] + d['dur']:
            x, y, q = drop_pos(d, t)
            bubble(cv, x, y, d['txt'], d['rot'], 255, 1.0)
    person(cv, 540 + trem * 150, 1240, 150, CLODAGH, dict(arms=arms, face=fc, tilt=-4 * worry, lift=-.03 * k))
    # landed bubbles + falling ones
    for d in DROPS:
        if t < d['t']:
            continue
        x, y, q = drop_pos(d, t)
        if q < 1:
            dx, dy = x - (d['x'] + 520), y + 220
            n_ = math.hypot(dx, dy) or 1
            ux, uy = dx / n_, dy / n_
            tl = 260
            p = poly([(x - uy * 30, y + ux * 30), (x - ux * tl, y - uy * tl), (x + uy * 30, y - ux * 30)])
            cv.drawPath(p, paint(shader=lin(x, y, x - ux * tl, y - uy * tl, [('#FF4A5A', 170), ('#FF4A5A', 0)])))
            glow(cv, x, y, 120, '#FF3B3B', 90)
            bubble(cv, x, y, d['txt'], d['rot'] * q, 255, 1.0)
        elif not d['behind']:
            a = t - d['t'] - d['dur']
            sq = 1 + .15 * math.sin(min(a, .3) / .3 * math.pi) * (1 - clamp(a / .3))
            if a < .4:
                glow(cv, x, y + 20, 160 * eout(a / .4), '#FF6A5A', 140 * (1 - a / .4))
            bubble(cv, x, y, d['txt'], d['rot'], 255, sq)
    cv.restore()
    # notification bell
    kb = eback(prog(t, 11.2, 11.6))
    if kb > 0:
        n = sum(1 for d in DROPS if t > d['t']) * 61
        lbl = '999+' if n > 999 else str(n)
        cv.save()
        cv.translate(W - 140, 170)
        cv.scale(kb, kb)
        cv.rotate(math.sin(t * 25) * 10 * (1 if int(t * 2) % 2 == 0 else 0))
        glow(cv, 0, 0, 110, '#FF3B3B', 90)
        p = skia.Path()
        p.moveTo(-34, 22)
        p.cubicTo(-30, 10, -32, -38, 0, -40)
        p.cubicTo(32, -38, 30, 10, 34, 22)
        p.close()
        shaded(cv, p, '#FFC94A', dx=-4, dy=-4)
        cv.drawCircle(0, 30, 9, paint('#FFC94A'))
        f = font('bold', 26)
        w = max(44, f.measureText(lbl) + 24)
        cv.drawPath(rrp(14, -54, 14 + w, -16, 19), paint('#E5484D'))
        text(cv, lbl, 14 + w / 2, -35, f, '#FFFFFF')
        cv.restore()


def draw(cv, t, fi):
    wipe = prog(t, 10.0, 10.7)
    if wipe < 1:
        scene_room(cv, t)
        network(cv, t, prog(t, 2.2, 2.6))
        post_card(cv, t)
    if wipe > 0:
        cv.save()
        if wipe < 1:
            cv.clipPath(cp(540, 760, 1400 * ease(wipe)), skia.ClipOp.kIntersect, True)
        scene_onslaught(cv, t)
        cv.restore()
        if wipe < 1:
            cv.drawCircle(540, 760, 1400 * ease(wipe), paint('#FF5A6A', 200, stroke=10))
    vignette(cv, 150 + 60 * prog(t, 12, 17))
    scrim(cv, 1180, 215)
    subtitle(cv, t, .3, 5.5, "Nasti was furious, and shared the video\nwith his {hl:300,000 followers}.")
    subtitle(cv, t, 5.6, 10.0, "He asked his followers for {red:“help”}.")
    subtitle(cv, t, 10.5, 18, "Shortly after that,\nthe {red:onslaught} began.", fade_out=False)


if __name__ == '__main__':
    run('v4', DUR, draw)
