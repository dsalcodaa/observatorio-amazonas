---
name: Observatório Amazonas
description: State-monitoring console for Amazonas; every number carries source, unit and reference year.
colors:
  negro-950: "#0b1716"
  negro-900: "#102220"
  negro-800: "#18302d"
  negro-700: "#24423e"
  negro-300: "#9fb7b2"
  negro-200: "#c7d6d3"
  clay: "#c98a3d"
  clay-600: "#a86b25"
  clay-50: "#fbf3e8"
  canvas: "#f2f4f3"
  surface: "#ffffff"
  surface-2: "#f7f8f8"
  line: "#e3e7e6"
  line-strong: "#cfd6d4"
  ink: "#15201f"
  ink-2: "#4a5654"
  ink-3: "#5f6a68"
  seq-1: "#cde2fb"
  seq-2: "#9ec5f4"
  seq-3: "#6da7ec"
  seq-4: "#3987e5"
  seq-5: "#256abf"
  seq-6: "#104281"
  s1: "#2a78d6"
  s2: "#eb6834"
  s3: "#1baf7a"
  s4: "#eda100"
  good: "#0ca30c"
  warn: "#fab219"
  serious: "#ec835a"
  crit: "#d03b3b"
  nodata: "#b9c1bf"
  good-ink: "#08700a"
  warn-ink: "#8a5d00"
  crit-ink: "#a52a2a"
typography:
  headline:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    letterSpacing: "-0.01em"
  kpi-value:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  title:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 600
  stat:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    fontFeature: "tnum"
  body:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.45
  table:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
  label:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    letterSpacing: "0.03em"
  caption:
    fontFamily: "Figtree, Segoe UI, system-ui, sans-serif"
    fontSize: "11.5px"
    fontWeight: 400
rounded:
  xs: "4px"
  sm: "5px"
  md: "6px"
  pill: "10px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  card: "18px"
  gutter: "20px"
  page: "24px"
components:
  sidebar:
    backgroundColor: "{colors.negro-900}"
    textColor: "{colors.negro-200}"
    width: "252px"
  menu-item:
    textColor: "{colors.negro-200}"
    rounded: "{rounded.md}"
    padding: "9px 10px"
  menu-item-active:
    backgroundColor: "{colors.negro-800}"
    textColor: "{colors.surface}"
  topbar:
    backgroundColor: "{colors.surface}"
    height: "70px"
    padding: "0 24px"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
  card-head:
    typography: "{typography.title}"
    padding: "14px 18px"
    height: "54px"
  kpi-card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "16px 18px 14px"
  button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0 14px"
    height: "36px"
  button-ghost:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.md}"
  button-ghost-hover:
    backgroundColor: "{colors.surface-2}"
  search-input:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "40px"
    padding: "0 12px 0 38px"
  select:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "32px"
  segment:
    backgroundColor: "{colors.surface-2}"
    rounded: "{rounded.md}"
    padding: "3px"
  segment-active:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xs}"
  tag:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    height: "20px"
    padding: "0 7px"
  table-header:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink-2}"
    padding: "8px 12px"
  tooltip:
    backgroundColor: "{colors.negro-950}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: "8px 10px"
  note:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
---

# Design System: Observatório Amazonas

## Overview

**Creative North Star: "Encontro das Águas"**

Two rivers meet without mixing. The dark Rio Negro water holds the navigation: a near-black teal-green sidebar that frames the console and never carries data. The Solimões clay-ochre appears only as a thin thread where the user has put a hand: the current page icon, the focus ring, the selected municipality on the map, the text selection, the brand mark. Everything that measures the State is blue, on a quiet grey-green canvas, so magnitude never competes with identity.

The structure is a dense admin console (Velzon pattern: collapsible dark sidebar, 70px white top bar, light canvas, white cards with a soft shadow, sortable tables) built for a meeting room. Few strong numbers per row, read from across a table; detail sits one click down in tables, notes and card footers. Every card states reference year and source; no figure stands alone.

The surface is flat and calm. Depth is one soft ambient shadow under cards and nothing else at rest. Color in the content area belongs to data and to status, and status always comes with an icon and a word.

**Key Characteristics:**
- Rio Negro sidebar, white top bar, grey-green canvas, white cards.
- Clay accent reserved for selection, focus and the active place; never for data.
- Blue sequential ramp for magnitude; a fixed four-color categorical order for parts of a whole.
- Figtree throughout, tabular numerals on every figure.
- Gently rounded (6px) and flat; one ambient card shadow.

## Colors

A cool, near-neutral console where the only warm color is the hand of the user, and data speaks in blue.

### Primary
- **Rio Negro Ink** (negro-900): sidebar background. Its family covers the sidebar hover/active fill (negro-800), sidebar scrollbar and dividers (negro-700, negro-800), inactive menu text (negro-200), group headings and footer text (negro-300), and the tooltip ground (negro-950).

### Secondary
- **Solimões Clay** (clay): focus ring (2px outline, 2px offset), focused search border, active menu icon stroke, selected/hovered municipality outline on the map (2.4px stroke), located-municipality fill, `::selection` ground, brand mark lower wave and dot. Clay-600 and clay-50 are defined deep and pale steps; the shipped build does not yet use them.

### Tertiary (data)
- **Magnitude Blues** (seq-1 to seq-6): choropleth classes by quantile, light to dark = less to more. seq-2 marks partial-year bars, seq-3 fills inline table bars.
- **Categorical Order** (s1 blue, s2 orange, s3 green, s4 amber): series and composition, always in this order. s1 is the single-series line, area (8% opacity) and bar color.
- **Status** (good, warn, crit, nodata, plus serious): PPA goal state only. Icon strokes use the bright tone, labels use the darker ink pair (good-ink, warn-ink, crit-ink) for legibility.

### Neutral
- **Canvas** (canvas): page ground behind cards.
- **Surface** (surface) / **Surface Tint** (surface-2): card ground; tinted fills for table headers, row hover, segmented controls, tags, notes, search field.
- **Line** (line) / **Strong Line** (line-strong): card dividers, table rules, chart grid; control borders, chart axis, "not applicable" status.
- **Ink** (ink, ink-2, ink-3): primary text; secondary text and labels; metadata, axes, placeholders.

### Named Rules
**The Two Rivers Rule.** Clay never encodes data. It marks only where the user is or what the user picked; a clay pixel in a chart is a selection, never a value.

**The Magnitude Is Not Judgment Rule.** Choropleths and rankings use the blue sequential ramp, never red/green. Status colors appear only for PPA goal state.

**The Gap Stays Visible Rule.** Missing data is a diagonal hatch of nodata on white, labelled "sem dado"; it is never filled as zero or as the lightest class.

## Typography

**Display Font:** Figtree (variable 300–900, self-hosted woff2, with Segoe UI, system-ui fallback)
**Body Font:** Figtree

**Character:** One humanist workhorse sans for the whole console; hierarchy comes from weight and size, and every figure uses tabular numerals so columns align.

### Hierarchy
- **Headline** (700, 22px, -0.01em): page title, one per view, with a 80ch-max ink-2 lead below.
- **KPI Value** (700, 28px, 1.1, -0.02em, tabular): the headline number on KPI cards, unit in a 13px/500 ink-3 suffix.
- **Stat** (600, 17px, tabular): counter strips and municipality stat grids; status-bar totals at 20px.
- **Title** (600, 15px): card headings, with a 12px ink-3 sub line (year · source) on the same row.
- **Body** (400, 14px, 1.45): base text; menu items at 500.
- **Table** (400, 13px): table cells; headers 12px/600 ink-2.
- **Label** (600, 12.5px, 0.03em, uppercase): KPI metric name. Sidebar group headings use 11px/600, 0.06em, uppercase in negro-300.
- **Caption** (11.5–12.5px): card footers, legends, KPI meta, crumbs, stamp.

### Named Rules
**The Tabular Rule.** Every number shown as data uses `tabular-nums` and right-aligns in tables.

## Layout

A two-column app grid: sidebar (252px; 72px icon-only when collapsed, animated 0.2s ease-out) plus a main column with a sticky 70px top bar. Content sits in a page with 24px padding and a 1680px max width.

Cards live in a 12-column grid with 20px gaps and 20px row spacing; spans used are 3, 4, 5, 6, 7, 8 and 12. KPI rows are four span-3 cards; the analysis row pairs span-8 with span-4.

Rhythm: card heads 14px/18px padding, bodies 16px/18px, footers 10px/18px; list rows 10px; table cells 8px/12px.

Responsive:
- At 1280px and below, span-3 becomes 6, everything else becomes 12.
- At 900px and below, the sidebar becomes an off-canvas drawer (270px, slides from the left, page dimmed by a 45% negro-950 scrim). Page padding drops to 16px, grid gaps to 14px, KPI cards pair two per row, the search fills the bar, and filters stack full-width.
- Print hides sidebar and top bar and swaps card shadows for 1px line borders.
- Reduced motion removes all transitions.

## Elevation & Depth

Flat with a single ambient layer. Cards float on the canvas by one soft, low shadow; the top bar is separated by a 1px line drawn as shadow. Stronger shadows appear only as response: a hoverable KPI card lifts, and the tooltip and mobile drawer sit above everything.

### Shadow Vocabulary
- **Card** (`box-shadow: 0 1px 2px rgba(16,34,32,.08), 0 2px 8px -2px rgba(16,34,32,.06)`): every card at rest.
- **Card Lift** (`box-shadow: 0 2px 4px rgba(16,34,32,.1), 0 8px 20px -6px rgba(16,34,32,.16)`): hover on a linked KPI card.
- **Top Bar Rule** (`box-shadow: 0 1px 0 #e3e7e6`): top bar bottom edge.
- **Segment Raise** (`box-shadow: 0 1px 2px rgba(16,34,32,.12)`): pressed segment.
- **Tooltip** (`box-shadow: 0 6px 18px rgba(0,0,0,.25)`): floating data tooltip.

### Named Rules
**The One Shadow Rule.** At rest there is one shadow, the card shadow. Anything heavier must be a response to hover or a floating layer.

## Shapes

Gently rounded and rectangular. One radius (6px) for cards, buttons, inputs, selects, menu items, notes and counter strips; 4px for segment buttons and thick stacked bars; 5px for the tooltip; fully rounded ends for tags (10px), tracks (5px) and inline bars (3px). Legend swatches are 22x10px with 2px corners; status dots are 8px circles. Icons are 1.75px stroke line icons with round caps and joins, 17–20px in chrome, 14px in status.

## Components

### Buttons
Quiet and outlined; the console has no filled primary button.
- **Shape:** gently rounded (6px), 36px tall, 14px side padding, icon + label with 7px gap.
- **Default:** white ground, ink text, line-strong border; hover darkens the border to ink-3.
- **Ghost:** transparent border, ink-2 text; hover fills surface-2. Label hides below 900px, icon stays.
- **Icon button:** 38px square, transparent, ink-2; hover surface-2 and ink.

### Chips
- **Tag:** 20px pill, 11px/600, surface-2 ground, ink-2 text, line border. Marks data provenance type ("oficial").
- **Calculated tag:** same pill with transparent ground and a dashed line-strong border, so derived figures read as different from official ones.

### Cards / Containers
- **Corner Style:** 6px.
- **Background:** surface on canvas.
- **Shadow Strategy:** Card shadow (see Elevation).
- **Border:** none; head and foot separated by 1px line rules.
- **Internal Padding:** head 14px 18px (min 54px tall, title left, sub/control right), body 16px 18px, foot 10px 18px in 12px ink-3.

### KPI Card
Label (uppercase), big tabular value with unit suffix, delta line in ink-2, then a meta row pinned to the bottom with a provenance tag and source · year. When linked, the whole card is the link and lifts on hover.

### Inputs / Fields
- **Search:** 40px, surface-2 fill, transparent border, leading 17px icon; focus swaps to white with a clay border.
- **Select / filter input:** 32px, white, line-strong border, 13px text.
- **Segmented control:** surface-2 track with 3px padding; buttons 12.5px/500 ink-2; pressed is white with ink text and the Segment Raise shadow.
- **Focus:** global 2px clay outline with 2px offset; table rows use a -2px inset offset.

### Navigation
Sidebar on Rio Negro ink: brand (wave mark + two-line wordmark) in a 70px block, uppercase group headings, then menu items (18px line icon + 14px/500 label, 9px 10px padding, 6px radius). Hover and current page both fill negro-800 with white text; the current page also turns its icon clay. Collapsed shows icons only; below 900px it is an off-canvas drawer opened from the top bar menu button. Footer carries dataset counts in 11.5px negro-300 above a negro-800 rule.

### Tables
Dense and sortable. 13px cells, 8px 12px padding, 1px line row rules, sticky surface-2 header in 12px/600 ink-2. Numeric columns right-align. Sort buttons carry a 12px chevron at 35% opacity that goes full when active. Row hover is surface-2; clickable rows show a pointer. Inline magnitude bars are 6px seq-3 capsules beside the value.

### Choropleth Map
62 municipalities stroked white at 0.7px, filled from the blue ramp by quantile; hover or selection draws a 2.4px clay outline and raises the shape. Missing values use the hatch pattern. Legend below in 11.5px with range swatches and a "sem dado" swatch when needed.

### PPA Status
Always icon + label: check / warning / cross / dash in 14px at 2.2px stroke, label 12px/600 in the ink-pair color. Stacked tracks (10px tall, 2px gaps, rounded ends) show the status mix in good, warn, crit, nodata order.

### Charts
Hand-drawn SVG. Grid lines in line, axis in line-strong, 11px ink-3 text. Single series: 2px s1 line over an 8% s1 area, white-ringed dots, a dashed ink-3 crosshair, and the last value labeled in ink 600. Tooltip: negro-950 ground, white 12.5px text, 5px radius, sub line in negro-300.

## Do's and Don'ts

### Do:
- **Do** keep clay for focus, selection, the current menu icon and the selected place on the map.
- **Do** encode magnitude with seq-1 to seq-6 and parts of a whole with s1, s2, s3, s4 in that order.
- **Do** pair every status color with an icon and a word, using the ink pair for text.
- **Do** put reference year and source on every card: in the head sub line, the KPI meta row or the card foot.
- **Do** use tabular numerals for every figure and right-align numeric columns.
- **Do** mark derived figures with the dashed calculated tag and missing values with the hatch.

### Don't:
- **Don't** use clay as a data color or a status color.
- **Don't** color choropleths or rankings red/green; magnitude is not a verdict.
- **Don't** draw a missing value as zero or as the lightest ramp class.
- **Don't** add shadows heavier than the card shadow to elements at rest.
- **Don't** put data color in the sidebar; Rio Negro ink carries navigation only.
