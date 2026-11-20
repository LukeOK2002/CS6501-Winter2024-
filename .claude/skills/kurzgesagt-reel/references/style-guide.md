# Style guide

## Palette

Night scenes are the house look. Shading in `kz.dark()` mixes toward deep purple, not black —
shadows should feel cool and coloured.

| role | colours |
|---|---|
| sky / stage top → bottom | `#070A2A` → `#1A1550` → `#4A2272` → `#8A3A72` (horizon) |
| stage (purple planet) | top `#1A1446`, mid `#3E2475`, ground `#4B2C86`→`#1B1240`, rim `#9C7BE8` |
| threatening mood | `stage(mood=1)` → maroon `#2A0E2A` / `#5A1A3A`, red glow `#FF5A6A` |
| warm interior | walls `#F6B48A`→`#E8916E`, lamp light `#FFF4D6` / `#FFE9B5` |
| accents | gold `#FFC94A`, red `#E5484D` / `#FF3B3B`, teal `#3FB6A8`, green `#38C172`, pink neon `#FF5FA0` |
| UI / screens | dark `#15172E` `#23264A`, light `#F3F2FA`, text `#272448`, muted `#8A88AA` |
| subtitles | white, highlight gold `#FFC94A`, menace red `#FF6B6B` |

## Shapes and light

- No outlines. Every solid object is a flat fill plus `shaded()` (a crescent of darker colour
  on the side away from the light, which comes from the top-left). Pass `dx, dy` scaled to
  the object (about 5-12 % of its size).
- Light sources get `glow()` halos (`mid=1` for a soft wide falloff). Use glows for lamps,
  screens (cool blue `#7FC4FF` / `#9FD4FF`), fire (`#FF7A3A`), moons and highlights. Keep screen glow
  on faces subtle (alpha ≤ 30) or faces turn grey.
- Rounded rectangles everywhere (`rrp` radius ≈ 15-40 % of the short side).
- Depth: background layers darker and less saturated (city silhouettes, far meteors at 0.45×
  scale), foreground brighter. Slow parallax/bokeh drifting adds life.
- Grain is added by `run()` automatically. Vignette + scrim every frame.

## Characters

- Proportions (head radius r): head centre 3.85r above the floor, torso 0.76r half-width,
  legs ≈1.2r. Big heads read as friendly; keep them that way.
- Expressions via the `face` dict — eyes `open|happy|wide`, `squint`, `look`, `brows`
  ((angle, raise) per side; positive angle = angry, negative = worried), `mouth` −1..1,
  `mopen`, `wavy` (confused), `blush`/`blushc` (anger = red `(255,70,70)` with blush 1.3-1.6).
- Emotion ramps over ~1 s with `ease(prog(...))`, never pops (except surprise: `eyes='wide'`).
- Arms are strokes from shoulders through elbow to a hand circle; specify elbow/hand points in
  head-radius units relative to (x, floor). Make sure hands meet the objects they hold — the
  `held` callback draws the object between arms and hands.
- Diverse casts: vary skin tone, hair style (`long short buzz curly bun bob hijab`, `beard`,
  `glasses`) and top colour; avoid duplicate looks in one shot.

## Motion and timing

- 30 fps. Scenes 4-8 s. Subtitle segments 3-4.5 s with 0.1-0.4 s gaps; the last one uses
  `fade_out=False` and the video ends ~0.5 s after the final beat lands.
- Entrances: `eback` scale pop (0.4-0.6 s). Exits/fades: `ein`. Moves: `ease`.
- Scene change: circle wipe (clip the new scene to a growing circle, draw a thin gold or red
  ring on its edge) over ~0.7 s.
- Impacts: flash glow + expanding shockwave ellipse + debris with gravity + rising smoke +
  persistent flickering fire, plus `(1 - a/0.5)^2` decaying screen shake.
- Reveals: zoom the camera into the detail (scale 2-2.5 over ~1.2 s), then pop a white card
  with the key word; animate corrections (strike-through, falling letter, red replacement,
  spell-check squiggle).

## Mistakes to check for in every set of stills

These all happened at least once while building the examples:

- Missing glyphs render as empty boxes (♥ ✓ ツ emoji). Draw hearts/ticks as paths.
- Props hiding faces (laptops too tall) or hiding the body the user asked to see. If the user
  says a character must be full-body, draw legs and feet on the ground and add a ground shadow;
  don't leave characters floating.
- Floating hands (no arm connecting) or hands not touching what they hold.
- Text overflowing its card or box; two copies of the same reveal text competing on screen.
- A reveal animation that hasn't finished by the end of the video. Leave 1-1.5 s of hold.
- Decorative items overlapping signs or labels (badges over shop signs, lamps poking into a
  zoomed shot, a moon behind the roof line).
- Smoke or effects in front of the characters thick enough to hide them (keep front-layer
  smoke alpha ≤ 80).
- Objects falling past the bottom edge over the subtitles. Land them on the ground or behind the
  character instead.
- Scene-specific labels/taglines that weren't requested.
- Character name or spelling drift between videos in a series. Keep one spec per character
  and reuse it.
