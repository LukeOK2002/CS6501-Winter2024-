# kz.py API reference

`from kz import *` gives everything below plus `skia`, `math`, `random`. Canvas `cv` is a
`skia.Canvas` 1080×1920; use `cv.save() / cv.translate / cv.scale / cv.rotate(deg, px, py) /
cv.clipPath(path, skia.ClipOp.kIntersect, True) / cv.restore()` directly for transforms.

## Constants
`W, H, FPS` = 1080, 1920, 30. `INK` face-ink colour. `CLODAGH`, `NASTI` character specs.
`STARS`, `BOKEH` precomputed particle lists.

## Colour
- Colours are `'#RRGGBB'` strings or `(r,g,b)` tuples; with alpha as `(colour, alpha)` inside
  gradient lists.
- `mix(a, b, t)`, `dark(c, f=.2)`, `light(c, f=.2)` → rgb tuple.

## Easing / timing
`clamp(x,a,b)`, `prog(t, a, b)` (0→1 across [a,b]), `ease` (in-out cubic), `eout`, `ein`,
`eback(x, s=1.7)` (overshoot), `lerp(a,b,t)`, `lerp2(p,q,t)` for points.

## Paint and paths
- `paint(c, a=255, stroke=0, blur=0, shader=None, blend=None, cap='round')`
- `lin(x0,y0,x1,y1, cols, pos=None)`, `rad(x,y,r, cols, pos=None)` gradient shaders
- `R(l,t,r,b)` rect; paths: `rrp(l,t,r,b,radius)`, `cp(x,y,r)`, `op(l,t,r,b)` oval, `poly(pts, close=True)`
- `fill(cv, path, c, a)`; `glow(cv, x, y, r, c, a, mid=None)` radial light (mid=1 → softer, wider)
- `shaded(cv, path, base, shade=None, dx=-6, dy=-6, hi=None)` flat fill + crescent shadow;
  `hi=(colour, alpha)` adds a top-left highlight

## Text
- `font(kind, size)` kind ∈ `med semi bold od` (od = OpenDyslexic)
- `text(cv, s, x, y, f, c='#fff', a=255, anchor='c'|'l'|'r', track=0, shadow=0)` → width.
  y is the visual centre of the caps.
- `subtitle(cv, t, start, end, s, cy=1430, size=58, fade_out=True)` lines split on `\n`;
  inline `{hl:...}` gold, `{red:...}` red, `{od:...}` OpenDyslexic gold. Auto-shrinks lines wider than 960 px,
  3+ lines get 88 % size. Lines rise and fade in, staggered.
- `scrim(cv, top=1150, a=200)` bottom darkening; `vignette(cv, a=150)`.

## Backgrounds
- `stars(cv, t, ymax=1300, a=1.0, n=230, ox=0, oy=0)` twinkling stars with glow on big ones
- `stage(cv, t, ground=1240, mood=0.0, spot=1.0)` purple planet stage with spotlight and bokeh;
  mood→1 shifts to red menace
- `ground_shadow(cv, x, y, half_width, a=110)`

## Characters
`spec` dict: `skin` (rgb), `hair`, `style` (`long short buzz curly bun bob hijab`), `top`,
optional `pants`, `shoes`, `freckles`, `glasses`, `beard`, `beardc`, `hoodie`, `brow`.

`person(cv, x, floor_y, r, spec, pose)` — front view, r = head radius (whole figure ≈ 4.9r tall).
pose keys:
- `arms=[(elbowL, handL), (elbowR, handR)]` points in r-units relative to (x, floor_y),
  e.g. relaxed `[((-.95,-2.0),(-.9,-1.35)), ((.95,-2.0),(.9,-1.35))]`;
  wave R: elbow `(1.25,-3.0)`, hand orbiting it at radius .9; shrug: hands `(±1.62,-2.5)`;
  hold object at chest: hands `(±.38,-2.0)` (seated) / `(±1.12,-2.25)` (book)
- `legs='stand'|'sit'|None` (None = hidden behind a desk: put floor_y = desk_top + 1.6r)
- `face={...}` (see `face` below), `tilt` degrees, `lift` (r-units, negative = up; shoulders/head)
- `held=callable(cv)` draws a prop after arms, before hands; `hands=False` to skip hands

`face` dict: `eyes` (`open happy wide`), `squint` 0..1, `look` (dx, dy) −1..1,
`brows` ((angle, raise), (angle, raise)) — angle>0 angry, <0 worried, raise in r-units,
`mouth` −1..1, `mopen` 0..1 open smile, `wavy` bool, `blush` intensity, `blushc` rgb.

`person_back(cv, x, seat_y, r, spec, t, type_=True)` — seen from behind at a desk (typing arms,
long hair, chair back in front).

## Render
`run(name, dur, draw)` — calls `draw(cv, t, frame_index)` per frame, adds grain, writes
`$KZ_OUT/<name>.mp4` (default cwd). Env `STILLS=1.0,4.5` saves `st_<name>_<t>.png` only.

## Props in examples
- `intern_dyslexia.py`: `truck(cv, x, ground_y, s, t, label, cursor, squiggle)`,
  `takeaway(cv, x, ground_y, s, t)`, `badge(cv, x, y, s, good, a)`, `screen()` animation-app UI
- `phone_misunderstanding.py`: `living_room(cv, t)`, `sofa_front(cv)`, `phone_back()`,
  `nasti_seated(cv, t, face, phone_k, lit, thumb, shake, tilt)`, `steam()`,
  `phone_frame(cv, k, draw_content)` pop-out phone, `feed()`, `avatar()`
- `onslaught_network.py`: `network()` follower graph, `post_card()`, `bubble()` comment
- `newsroom_meteors.py`: `meteor_flight()`, `impact_back()/impact_front()`, `flame()`,
  `worker()` seated desk worker, `lamp()`, `building()` cross-section
