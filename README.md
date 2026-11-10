# Osmdesát let — Dad's 80th birthday

An illustrated story for November 10, 2026. Thirteen pages, told to Dad in the second person, in English and Czech, with a French line at the end.

**[Open the card](https://dzajic.github.io/dad-80th-birthday-card/)**

Arrow keys, the buttons along the bottom, or a horizontal swipe. The address `#7` opens a specific page.

## The pictures

The plates are painted in one modernist voice: geometric planes, dry brush, and a mineral palette of ivory, sandstone, ochre, terracotta, sage, and ink. Subjects stay recognizable and correctly proportioned. Prague is Prague. The Aztek keeps its cladding, grille, and stance, and sits in a gallery. The chalet has a steep roof and broad eaves. Hockey is a shot on a goalie. Mount Washington is the Cog Railway on a trestle, and the canoe is a real open canoe with two adults and two children.

The Atlantic map is not a drawing of a map. `scripts/build_map.py` builds it from Natural Earth 1:50m coastlines. Sources and licenses are in [ATTRIBUTION.md](ATTRIBUTION.md).

There are no caption bars on the artwork. The only word painted into a plate is **Florida**, set in type over the travel picture.

## A few facts, held lightly

- Photography **possibly** around McGill is marked as uncertain in the story.
- The idea that his father may already have been in Canada with Hydro-Québec is left out. It was never confirmed.
- The return to Prague is "around 1990."
- His father having been Canadian president of Sokol is included as "for a time."
- The iPad is described as arriving in about two weeks.
- Nothing here is a photograph of Dad or the family.

## Running it

The site is static: `index.html`, `css/`, `js/`, `fonts/`, and `images/`. GitHub Pages serves the repository root. A `.nojekyll` file keeps Pages from filtering the font files.

```bash
python3 -m http.server 8765
```

## Privacy

Anyone with the link can open the card. It does not include addresses, health details, or family photographs.
