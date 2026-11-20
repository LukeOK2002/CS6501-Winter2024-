---
name: kurzgesagt-reel
description: Make polished, Kurzgesagt-style animated cartoon videos as portrait 1080x1920 MP4 reels (Instagram Reels / TikTok / Shorts) with Space Grotesk subtitles, using a bundled skia-python vector toolkit. Flat-vector characters with soft shading, glowing lights, starry gradient skies, cut-away cross-section buildings, phone pop-outs, network graphs, and animated subtitles. Use this skill whenever the user asks for an animated video, explainer, cartoon, reel, short, story video or "Kurzgesagt style" clip — including follow-ups like "make the next video", "another one in the same style", "redo it more polished", or a new scene featuring characters such as Clodagh or Nasti — even if they don't name the style.
---

# Kurzgesagt-style portrait reels

This skill renders short animated videos programmatically: a Python scene script draws every
frame with **skia-python** (anti-aliased vectors, gradients, blur glows) and pipes frames to
**ffmpeg**. A shared toolkit (`scripts/kz.py`) supplies the look — palette helpers, soft
shading, characters, stage/sky backgrounds, subtitles, grain, vignette and the render loop — so
each new video is mostly scene choreography.

The look the user signed off on: deep purple/indigo night palettes with warm accent light,
round-headed characters with a crescent shadow on the lower right, glowing light sources,
subtle film grain, slow camera push-ins, circle-wipe scene changes, and clean white Space
Grotesk subtitles with key words highlighted in gold (or red for menace).

## Setup (once per machine/session)

```bash
SK=<path to this skill>            # e.g. .claude/skills/kurzgesagt-reel
bash $SK/scripts/setup.sh          # installs skia-python, numpy, libEGL, ffmpeg if missing
```

Fonts are bundled in `assets/fonts/` (Space Grotesk Medium/SemiBold/Bold, OpenDyslexic).
Don't download fonts unless the user asks for a different typeface.

## Workflow

1. **Plan the beats before coding.** Write a timeline: for each scene, its time range, what
   moves, the character's expression, and the subtitle text. Reels run 10-25 s; give each
   subtitle 3-4.5 s (about 2 lines, ≤ ~40 characters per line). Use the user's wording for
   subtitles where they gave it, and tell them about any text you wrote yourself.
2. **Write a scene script** in a scratch/working folder (not inside the skill):
   ```python
   import sys; sys.path.insert(0, '<SK>/scripts')
   from kz import *
   DUR = 14.0
   def draw(cv, t, fi):
       ...scene drawing for time t...
       vignette(cv, 140); scrim(cv, 1180, 210)
       subtitle(cv, t, .3, 4.2, "This is {hl:Clodagh}.\nShe is one of our interns.")
   if __name__ == '__main__':
       run('my_reel', DUR, draw)
   ```
   Start from the closest example in `examples/` rather than from scratch (see below).
3. **Preview stills first** — rendering stills takes seconds; a full render takes minutes:
   ```bash
   STILLS=1.0,5.5,9.8 python3 my_reel.py      # -> st_my_reel_1.0.png ...
   ```
   Pick times that cover every scene and the key moments (mid-transition, reveal, end).
   Look at them (downscaled side by side, e.g. a PIL contact sheet) and fix problems before
   the full render. Typical problems found this way are listed in the style guide's
   "Mistakes to check for" — check stills against that list every time.
4. **Full render** in the background (`nohup python3 my_reel.py > log 2>&1 &`); several
   videos can render in parallel (one per core). Output: `<KZ_OUT or cwd>/<name>.mp4`,
   H.264 yuv420p, 30 fps, faststart — uploads directly to Instagram.
5. **Spot-check the real MP4** with ffmpeg (`-ss <t> -frames:v 1`) at a couple of times,
   then deliver. Videos have no audio unless the user asks for it.

## Composition rules (portrait 1080x1920)

- Keep the story in y ≈ 80-1300. Subtitles sit centred at y ≈ 1430 (`subtitle` default).
  Instagram's UI covers roughly the bottom 400 px and a right-hand strip, so nothing
  important below ~1650 or hard against the right edge.
- A small title, if the user wants one, goes just under the subtitles (~y 1600), letter-spaced
  and small (≈25 px). Don't invent chapter taglines or section labels — the user asked for
  them to be removed once already.
- Always finish a frame with `vignette()` + `scrim()` (bottom darkening for legible subtitles),
  then subtitles, outside any camera transform so text doesn't zoom or shake.
- Camera moves: wrap scene drawing in `cv.save(); translate/scale; ...; cv.restore()` —
  a slow 3-6 % push-in per scene, a zoom into a detail for reveals, and shake on impacts.

## Toolkit at a glance

Full reference: `references/api.md`. Style and palette rules plus a checklist of past
mistakes: `references/style-guide.md` — read it before the first scene of a session.

- Drawing: `paint`, `lin`/`rad` gradients, `rrp`/`cp`/`op`/`poly` paths, `shaded()` (base +
  crescent shadow — use it for almost every solid shape), `glow()` for all light.
- Characters: `person(cv, x, floor_y, head_r, spec, pose)` front view (standing, seated or
  legs hidden behind a desk), `person_back()` over-the-shoulder, `face()` expressions.
  Recurring cast: `CLODAGH` (intern; long ginger hair, freckles, teal top, full body, has
  dyslexia) and `NASTI` (white man, short black hair, blue hoodie). Keep their designs
  consistent across videos.
- Sets: `stage()` (purple planet spotlight, `mood` 0→1 turns it threatening red), `stars()`,
  `ground_shadow()`.
- Text: `subtitle()` with inline markup `{hl:gold}`, `{red:red}`, `{od:OpenDyslexic}`;
  `text()` for on-screen labels. Space Grotesk lacks some symbols (♥, ✓, ツ, emoji) — draw
  those as paths instead.
- Easing: `prog(t,a,b)` → 0..1 over [a,b]; `ease`, `eout`, `ein`, `eback` (overshoot pop).

## Examples (copy and adapt)

| file | shows |
|---|---|
| `examples/newsroom_meteors.py` | cut-away 2-storey newsroom with 6 diverse seated workers, meteors with trails, impacts (flash, shockwave, debris, smoke, fires), screen shake, rooftop neon sign, small bottom title |
| `examples/intern_dyslexia.py` | character intro on stage (pop-in, wave), book reading with floating mirrored letters and "?" marks, OpenDyslexic word, circle wipe, over-the-shoulder desk + animation-software UI, zoom into a typo reveal (NASTY→NASTI card); props `truck()`, `takeaway()`, `badge()` |
| `examples/phone_misunderstanding.py` | night living room, seated character lifting and scrolling a phone, pop-out phone screen with a scrolling feed, escalating anger, shrug pose |
| `examples/onslaught_network.py` | share-sheet tap, follower network graph growing from the phone with a counter, social post card with typing text, red mood shift, comment bubbles falling like meteors and piling up, notification bell |

Run any example with `STILLS=<times>` to see it. Reuse their helpers by importing them (the
later examples import `truck` and the living room from the earlier ones).
