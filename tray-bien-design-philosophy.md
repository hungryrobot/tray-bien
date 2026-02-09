# Tray Bien — Design Philosophy & Best Practices

### *The rules that make an insert worth printing*

> **Companion document to the [Tray Bien Project Guide](tray-bien-project-guide.md)**
> The Project Guide tells Claude Code *how to build the app* (tech stack, phases, file structure). This document tells the app *how to behave* — the defaults, rules, tolerances, and UI guidance that make Tray Bien's output genuinely good. Both documents are fed to Claude Code during development; this one is also embedded into the AI chat panel's system prompt so the refinement AI follows these rules too.

---

## Core Design Hierarchy

Every decision in Tray Bien follows this priority order. When two goals conflict, the higher-ranked one wins.

### 1. 🏆 Setup & Teardown Speed (Primary Goal)

The entire reason inserts exist. A great insert means "open box, place trays on table, play." Teardown is "put trays back, close box." If an insert doesn't dramatically reduce setup time, it has failed regardless of how pretty it is.

**What this means in practice:**
- Trays are designed to be **lifted out and placed directly on the table** during play — they double as resource pools, token banks, and card holders. No transferring components from tray to bowl.
- **Player trays** should be a first-class concept: one tray per player containing all their starting components, so setup is "deal one tray per person."
- Components should be **grouped by when they're needed** (setup, during play, end-game scoring), not just by type.
- **"Dump and done" teardown**: at the end of a game, each player sweeps their stuff into their tray, shared resources go back in the shared tray, trays stack into box. Under 2 minutes for any game.
- Card compartments should allow **grabbing the whole deck at once** — not fishing cards out one by one.
- The insert should make it **obvious where everything goes**. Embossed labels, shaped compartments, and color coding all serve this goal.

### 2. 🧊 Compact Fit (Secondary Goal)

Wasted space inside a game box is wasted shelf space. Every cubic millimeter should either hold a component or serve a structural purpose.

**What this means in practice:**
- **Multi-tray stacking is preferred** — use 2-3 layers to fill the box height rather than leaving dead air above a single shallow tray.
- Compartment sizing should be **snug but not tight** — just enough clearance for easy grab-and-go, no more.
- **Shared walls** between adjacent compartments save space vs. separate boxes.
- If the game box has significant unused height after the insert, consider whether the trays could be taller (deeper compartments) rather than wasting vertical space.
- **Expansion awareness**: where practical, leave a compartment or flexible space for one expansion's worth of components. Don't over-engineer for expansions that may never be bought, but don't make it impossible either.

### 3. 🎨 Aesthetics (Tertiary Goal)

A beautiful insert makes opening the box feel like an event. It signals care and craftsmanship. But aesthetics never come at the cost of function.

**Default aesthetic choices:**
- **Rounded/filleted corners** on all compartments (radius 2-3mm). Looks better, feels better in hand, and is actually stronger than sharp corners for 3D prints.
- **Embossed labels** on compartments identifying what goes where. Legible at a glance, tactile, and doubles as a functional aid for setup speed.
- **Game-colored filament** — match the dominant color palette of the game. A Wingspan insert in soft teal, a Scythe insert in dark olive. The app should suggest colors based on the game selected. This is an AMS/multi-color printer feature but even single-color prints benefit from choosing the right filament color.
- **No honeycomb lids by default** — clean, solid lids with an embossed game name or logo. Honeycomb is a stylistic choice users can opt into.
- **Consistent visual language** across trays in the same insert: same corner radius, same wall thickness, same label font size.

---

## Visual Explainers: Show, Don't Just Tell

When the app presents design choices — pedestal bases, finger cutouts, inset lids, nested sub-trays — it should **show a simple line-art cross-section diagram** next to the description. Users shouldn't have to Google what a "pedestal base" is.

### How it works in the UI:
Each design concept gets a small inline SVG (roughly 200×120px) showing a cross-section or isometric sketch. These are generated programmatically (not image files) so they scale cleanly and are easy to maintain.

### Concepts that need visual explainers:

**Pedestal Base**
A raised bump on the compartment floor. Push down on one end of a card stack → other end pops up for grabbing.
```
Diagram: Side cross-section view
┌─────────────────────┐
│  ┌───────────────┐  │
│  │ ▒▒▒▒ cards ▒▒▒│  │  ← cards rest on pedestal
│  │ ▒▒▒▒▒▒▒▒▒▒▒▒▒ │  │
│  └───────────────┘  │
│    ┌───────────┐    │  ← pedestal bump (raised floor)
└────┘           └────┘
  Push here↓      ↑Pops up
```

**Finger Cutout**
A scoop in the compartment wall so you can reach in and grab components.
```
Diagram: Front view of compartment
┌──┐         ┌──┐
│  │         │  │
│  │         │  │
│  │         │  │
│  └─╮     ╭─┘  │  ← cutout curves into floor
│    ╰─────╯    │
└───────────────┘
```

**Bottom Hole (Vacuum Release)**
A hole in the compartment floor lets you push tokens up from below. Also prevents suction.
```
Diagram: Side cross-section view
┌─────────────────────┐
│  ┌───────────────┐  │
│  │ ○ ○ ○ tokens  │  │
│  │ ○ ○ ○ ○ ○ ○ ○ │  │
│  └───────────────┘  │
└───────┘     └───────┘
        ↑ hole ↑
     push up from below
```

**Inset Lid vs. Cap Lid**
Inset sits inside walls (thinner, saves height). Cap sits on top of walls (sturdier, adds height).
```
Inset lid:              Cap lid:
  ┌──────────┐         ┌────────────┐
  │╔════════╗│         │            │
  │║  lid   ║│         ╞════════════╡
  │╚════════╝│         │            │
  │          │         │            │
  └──────────┘         └────────────┘
  No added height      Adds lid thickness
```

**Nested Sub-Trays**
Removable smaller trays inside a parent tray. Lift out and place on table.
```
Diagram: Top-down view of parent tray
┌──────────────────────────┐
│ ┌───────────┐┌──────────┐│
│ │  coins    ││  coins   ││
│ │  (left)   ││  (right) ││
│ │  ↑ lift   ││  ↑ lift  ││
│ └───────────┘└──────────┘│
└──────────────────────────┘
  ← table left   table right →
```

**Angled Card Well**
Tilted compartment for thumbing through cards during play (market rows, display decks).
```
Diagram: Side cross-section view
┌─────────────────────┐
│     ╱▒▒▒▒▒▒▒▒│      │
│    ╱▒▒cards▒▒│      │
│   ╱▒▒▒▒▒▒▒▒▒│      │  ← 5-10° tilt
│  ╱▒▒▒▒▒▒▒▒▒▒│      │
│ ╱────────────┘      │
└─────────────────────┘
  Thumb through easily →
```

### Implementation notes:
- These should be **inline SVGs** generated in Python (not stored image files) so they can be themed/colored dynamically.
- Show the relevant diagram whenever a design choice appears in the questionnaire or is suggested by the AI.
- Tooltip/expandable — don't clutter the UI. Show the diagram on hover, click, or in a "What's this?" expandable section next to each option.
- The AI chat panel should also be able to reference these diagrams when suggesting modifications ("I've added a pedestal base to the card compartment — here's what that looks like: [diagram]").

### 4. 🔧 Durability (Baseline Requirement)

Inserts don't take much abuse, but they do get handled hundreds of times. They need to survive being pulled out, set down, stacked, and slid back in without cracking or warping.

**What this means in practice:**
- Wall thickness and print settings (below) are chosen to be sturdy enough for years of use, not optimized for minimum filament.
- Rounded corners resist cracking at stress points.
- PLA is fine for inserts — they live indoors, don't bear structural loads, and the rigidity is actually desirable for clean compartments.

---

## Vertical Storage: The Non-Negotiable Constraint

Games are stored vertically (like books on a shelf). **Every insert must work when the box is on its side.** This single requirement drives many downstream decisions:

### What vertical storage demands:
- **The total insert stack must fill the box height** so components can't shift vertically. If there's a gap, add a spacer tray or size the top tray to fill it. The board game's own board and rulebook sitting on top of the insert stack can serve this purpose — plan for it.
- **When the stack is tight, the trays themselves become lids.** A well-packed box where tray 2 sits flush on tray 1 doesn't need a separate lid on tray 1 — the tray above holds everything in place. This saves height, filament, and print time.
- **Card compartments need walls tall enough** that cards can't slide out sideways when the box is vertical. Or use lids.
- **Consider which edge faces "up" on the shelf.** The box spine (usually the short edge) faces out. Components should be oriented so gravity pulls them into their compartments, not out of them, when stored this way.
- **No loose components on top of trays.** Everything lives inside a contained space — either a lidded compartment, or trapped by the tray/board/rulebook above it.

### Smart Lid Logic (per-tray, not blanket)

Lids are **optional per tray**, not a global on/off. The app should evaluate each tray in the stack and recommend lids only where they're actually needed:

**Lid NOT needed when:**
- The tray above it sits flush and acts as a lid (tight-stacked trays)
- The game board or rulebook sits directly on top and provides full coverage
- The insert fills the box so completely that nothing can shift — gravity and compression do the work
- The tray contains large, heavy components that won't migrate (thick board tiles, chunky miniatures)

**Lid RECOMMENDED when:**
- It's the **top tray** in the stack with no board/rulebook covering it
- The tray contains **small loose components** (tokens, dice, cubes) that could spill through gaps
- The tray will be **removed and carried to the table** during play — a lid keeps it portable
- The tray above doesn't fully cover this tray's footprint (e.g., two smaller trays sit side-by-side on top of one large tray)
- The tray contains **cards standing vertically** that could fan out sideways

**Lid design when used:**
- Inset lids (sit inside the tray walls) are preferred — thinner, don't add exterior height.
- Tolerance: 0.3mm per side (lid is 0.6mm narrower and shorter than tray interior). Snug enough to hold during vertical storage, loose enough to pop off with one hand.
- **Finger cutouts on lids** (front and back) so you can pop the lid off while the tray is still in the box.
- Solid lids for structural trays (supporting weight above). Decorative/patterned lids only for the top visible tray.
- Lids that double as **component trays during play** — flip them over, and the lid becomes a shallow dish for discards, overflow tokens, etc.

**UI implementation:** Each tray in the design gets a lid toggle (on/off) with the app's recommendation pre-selected and a brief reason shown ("No lid needed — tray 2 covers this" or "Lid recommended — small tokens could shift").

---

## Component-Specific Design Rules

### Cards

- **Always ask: sleeved or unsleeved?** This is a per-design setting, not a global one. Sleeve thickness varies (60-100 micron), so offer presets: unsleeved, thin sleeves (60-80μm), and premium sleeves (80-100μm+).
- **Sleeved card dimensions** add ~1.5mm to width and ~2mm to height over the base card size. For premium sleeves, budget 2mm width and 2.5mm height.
- **Compartment depth for card stacks**: measure the stack height, then add 3-5mm clearance above the stack for finger access. Don't make it so deep that a small deck rattles around — use a pedestal base or spring floor for short stacks.
- **Pedestal bases** (a raised bump on the compartment floor) let you push down on one end of a card stack to pop the other end up for easy grabbing. Excellent for interior compartments where finger cutouts aren't possible.
- **Finger cutouts on at least one short side** of every card compartment. Cut through the full wall height. Width should be ~60% of the compartment width.
- **Angled card wells** (5-10° tilt) make it easy to thumb through cards during play. Great for market rows or display decks. This is a "nice to have" the AI chat can add.
- **Card dividers** for games with multiple decks stored in one compartment. BIT supports these natively.

### Tokens & Chits

- **Round compartments for round tokens** — hex or round shapes in BIT. Prevents tokens from wedging into corners.
- **Slight oversize**: add 1mm per dimension for cardboard tokens (they swell slightly with humidity). Add 0.5mm for wooden/plastic tokens.
- **Scooped/curved walls** at the base make tokens easier to pick up. A finger cutout that goes into the floor of the compartment (BIT's CMP_CUTOUT_DEPTH_PCT) achieves this.
- **Bottom holes** for token stacks: a small hole in the floor lets you push tokens up from below. Especially useful for tightly packed stacks. Also prevents vacuum suction when lifting tokens out.
- **Group tokens by function during play**, not by type. All the "wood" resource tokens in one well, not "all round tokens together."

### Dice

- **Generous clearance** — dice need room to be grabbed. Add 2-3mm per dimension beyond the dice size.
- **Shared dice pools** work fine in a single open compartment with finger cutouts. Don't over-compartmentalize dice unless the game has player-specific dice.
- **Rounded compartments** prevent dice from wedging into corners.

### Miniatures & Meeples

- **Shaped compartments for minis** where possible — a custom cutout that matches the mini's footprint prevents rattling and looks premium.
- **For standard meeples**: slight oversize rectangular compartments with bottom holes work fine. Meeples stack predictably.
- **Height clearance**: measure the tallest mini with any attached accessories (swords, flags). Add 2mm above the tallest point.
- **Padding material**: for painted minis, consider slightly wider compartments (1-2mm extra) so paint doesn't rub against walls. The AI chat panel is ideal for these custom requests.

### Boards, Rulebooks, Player Aids

- **These sit on top of the insert stack**, acting as a "lid" that holds everything in place for vertical storage.
- **Plan the insert stack height** so that boards + rulebook + box lid create gentle pressure on the trays below. No rattling, no crushing.
- **If the game has a folding board**, measure its folded thickness. Two-fold boards are typically 4-6mm thick; tri-fold boards 6-9mm.
- **Player aid cards** can go in the top tray or in individual player trays.

---

## Tray Design Patterns

### Pattern 1: The Player Tray
A small tray that contains everything one player needs to start the game. Pull it out, hand it to a player, done. Contains: starting resources, player tokens, player board (if small enough), reference card. One per player count (e.g., a 4-player game has 4 identical player trays).

**Design notes:**
- Should be liftable with one hand.
- Lid doubles as a personal discard/overflow area during play.
- Consider color-coding per player if using multi-color printing.
- Size these first, then design shared trays to fill the remaining box space.

### Pattern 2: The Shared Resource Tray
A tray that sits in the center of the table during play, holding public resources, market cards, etc. Multiple players reach into it throughout the game.

**Design notes:**
- Wider, shallower compartments for easy access from multiple angles.
- Finger cutouts on all four sides if tokens need to be grabbed from any direction.
- Labels especially important here — "wood," "stone," "gold" etc.
- Consider splitting into two identical half-trays for long tables (put one at each end).

### Pattern 3: The Setup Tray
Components that are placed on the board during setup but not handled much during play (map tiles, event decks, landmark pieces). This tray gets unpacked at the start and repacked at the end.

**Design notes:**
- Organization by setup step is more useful than organization by component type.
- If the game has a specific setup order, arrange compartments in that order.
- Deeper compartments are fine here since speed of access during play is less critical.

### Pattern 4: The Vertical Stack
Multiple trays stacked 2-3 deep inside the box. Each tray has a lid only where needed (see Smart Lid Logic above). The whole stack fills the box height.

**Design notes:**
- Bottom tray = least-accessed components (setup tray, expansion content, rarely-used variants).
- Top tray = most-accessed components (player trays, shared resources).
- All trays the same footprint (box interior dimensions minus ~1mm clearance per side).
- If tray 2 sits flush on tray 1, tray 1 doesn't need a lid — tray 2 IS the lid.
- Lid of bottom tray supports the weight of trays above it only if there's no direct stacking — use solid lids for these, not decorative patterns.

### Pattern 5: The Nested Sub-Tray
A parent tray containing **removable smaller trays** that lift out independently. The parent tray defines the footprint for box fit; the sub-trays are grab-and-go during play.

**Use cases:**
- **The split bank**: A currency/resource tray holds 2-3 identical sub-trays. During play, pull them out and place one at each end of the table so all players have nearby access to the bank. At teardown, drop them back into the parent tray.
- **Player tray carrier**: A parent tray sized to the box footprint holds 4 individual player trays nested inside. Lift the whole carrier out, then deal individual trays to each player.
- **Market row + supply**: A tray where the visible card market is one sub-tray (placed near the board) and the draw deck is another (kept nearby but separate).

**Design notes:**
- Parent tray walls are **outer walls only** — no internal dividers. The sub-trays themselves create the divisions.
- Sub-trays need **0.5mm clearance per side** within the parent tray for easy lift-out.
- Sub-trays should have **finger cutouts or a lip/tab** for grabbing.
- Sub-trays within the same parent should be the **same height** so they stack flush and the tray above (or a lid) sits flat.
- The parent tray floor can have **raised registration ridges** (0.5mm tall) between sub-tray positions to prevent lateral sliding.
- **Label the parent tray floor** with outlines or text showing which sub-tray goes where — makes teardown intuitive.
- This pattern is ideal for components accessed by **multiple people from different table positions** — it solves the "pass the token bowl" problem permanently.

---

## Tolerances & Clearances (The Numbers)

These are the default values Tray Bien should use. All derived from community experience with FDM 3D printing on modern printers (Bambu, Prusa, etc.).

### Box Fit
- **Tray exterior to box interior**: 0.5-1.0mm clearance per side (1-2mm total per dimension). Trays should slide in and out smoothly but not rattle.
- **Measure box INNER dimensions** with calipers. Cardboard boxes vary by ±1mm from published specs.
- **Account for box bulge**: cardboard boxes can bow outward slightly when full. Design to the measured interior, not the theoretical.

### Component Fit
- **Cardboard tokens/tiles**: component size + 1mm per horizontal dimension. Cardboard absorbs humidity and swells.
- **Wooden/plastic components**: component size + 0.5mm per horizontal dimension.
- **Card stacks (unsleeved)**: card width + 1mm, card height + 1mm, stack height + 5mm (finger room).
- **Card stacks (sleeved)**: sleeved width + 1.5mm, sleeved height + 1.5mm, stack height + 5mm.
- **Dice**: die size + 2mm per dimension.
- **Miniatures**: footprint + 1-2mm per dimension, height + 2mm.

### Lid Fit
- **Inset lid tolerance**: 0.3mm per side (lid is 0.6mm narrower and shorter than tray interior). This gives a satisfying snug fit that holds during vertical storage but pops off with a gentle push.
- **Test print a small lid first** if unsure about your printer's tolerance. Tray Bien should offer a "tolerance test" export — a small quick-print tray+lid to calibrate.

### Stacking Fit
- **Tray-on-tray alignment**: add registration bumps/dimples (1mm hemisphere) at the four corners so stacked trays lock together and don't slide apart. BIT doesn't natively support this, but it's a great AI chat modification.

---

## 3D Print Settings (Defaults for Export)

These go in the print_settings.md file exported with every design.

### Material
- **PLA** — the default recommendation. Rigid, easy to print, cheap, plenty durable for inserts that live indoors. No enclosure needed (though P1S has one anyway).
- **PETG** — suggest as alternative for inserts that might live in a car trunk or hot garage. Slightly more flexible, better heat resistance, but stringing can be an issue.
- **Avoid ABS/ASA** for inserts — the fumes, warping risk, and difficulty aren't worth it for parts that experience zero mechanical stress.

### Layer Height
- **0.2mm** — the standard default. Good balance of speed and quality. Layer lines are visible but don't affect function.
- **0.28mm** — "draft mode" for when you want it fast and don't care about looks. Fine for prototype/test prints.
- **0.12mm** — "detail mode" for embossed labels, logos, and surface quality. Only recommend for final prints with decorative elements.
- **Adaptive layer height** — if the slicer supports it, use fine layers only where there's detail (labels, curves) and coarse layers for flat walls. Bambu Studio supports this.

### Walls & Infill (Nozzle-Aware with Proactive Suggestions)

Wall thickness must be a **whole number multiple of the nozzle diameter**. A wall that isn't a clean multiple forces the slicer to leave internal voids or overlap extrusions — both weaken the part and look bad. This is one of the most common mistakes in insert design.

**The rule:** Wall thickness = nozzle diameter × number of perimeters. No exceptions.

| Nozzle | 2 perimeters | 3 perimeters | 4 perimeters | 5 perimeters |
|--------|-------------|-------------|-------------|-------------|
| 0.4mm  | 0.8mm       | **1.2mm** ← dividers | **1.6mm** ← outer walls | 2.0mm |
| 0.6mm  | 1.2mm       | **1.8mm** ← outer walls | 2.4mm | 3.0mm |

#### The App Should Suggest — Not Just Accept

Tray Bien should **not** bury nozzle diameter in a settings page and leave users to figure out the implications. Instead, the app should:

1. **Ask nozzle diameter once during first use** (default 0.4mm, with a brief explainer: "This is the standard nozzle that came with your printer. Check your printer specs if unsure.")

2. **Proactively recommend nozzle + thickness per tray** based on what the tray contains. Show a small info card on the preview page for each tray:

   > **Tray 2: Resource Bank** — Recommended: 0.4mm nozzle, 1.2mm inner dividers, 1.6mm outer walls
   > *This tray has embossed labels and 8 small compartments. The 0.4mm nozzle gives clean label detail, and 1.2mm dividers maximize compartment space in a tray with many divisions.*

   > **Tray 1: Tile Storage** — Recommended: 0.6mm nozzle, 1.8mm outer walls, 1.2mm dividers
   > *This tray is mostly large open compartments with no fine detail. A 0.6mm nozzle prints ~35% faster with no loss in quality. Thicker 1.8mm walls add rigidity for the heavy tile stacks.*

3. **Flag when a tray's needs differ from the user's configured nozzle**, with an explanation and clear options:

   > ⚠️ **Nozzle suggestion for Tray 3 (Player Trays):** Your 0.6mm nozzle will work, but the small embossed player labels won't be as crisp. Two options:
   > - **Keep 0.6mm** — labels will be legible but slightly chunky. Faster print. *(recommended if speed > aesthetics)*
   > - **Switch to 0.4mm for this tray** — sharper labels, ~35% longer print time. *(recommended if this is a display piece)*

4. **Explain WHY when suggesting a change** — always pair the recommendation with a plain-English reason. Users learn over time, and the reasons prevent the app from feeling like a black box.

#### When to recommend each nozzle:

**0.4mm nozzle (standard) — best for:**
- Trays with **embossed labels or logos** — finer detail, cleaner text at small sizes
- Trays with **many small compartments** close together — thinner dividers (1.2mm = 3 perimeters) save space
- **Lids with decorative patterns** (honeycomb, text)
- Any tray where **aesthetics rank high** for the user
- **Nested sub-trays** where tight tolerances matter (0.4mm gives better dimensional accuracy)

**0.6mm nozzle — best for:**
- **Large simple trays** with few compartments — faster print, no detail to lose
- **Tile storage trays** — big open wells, thick walls add rigidity for heavy contents
- **Bottom/structural trays** that nobody sees — speed matters, detail doesn't
- **Prototype/test prints** — get the fit right fast, then reprint with 0.4mm if desired
- Trays with **outer walls only and no labels** — 1.8mm walls in 3 passes instead of 1.6mm in 4 passes

**The app should present this as a recommendation, not a requirement.** Users with only one nozzle (most people) can ignore it. Users with a Bambu AMS or quick-swap nozzle system benefit from per-tray optimization.

#### Default wall thicknesses (auto-calculated from nozzle):

**For 0.4mm nozzle:**
- Outer walls: **1.6mm** (4 perimeters). Sturdy, rigid, will never flex.
- Inner dividers: **1.2mm** (3 perimeters). Saves space between compartments.
- Tray floor: **0.8mm** (4 solid bottom layers at 0.2mm layer height).
- Lid thickness: **0.8-1.2mm.** Thinner for non-structural; thicker if supporting weight above.

**For 0.6mm nozzle:**
- Outer walls: **1.8mm** (3 perimeters). Slightly thicker but prints significantly faster.
- Inner dividers: **1.2mm** (2 perimeters). Same effective thickness, fewer passes.
- Tray floor: **0.6-0.8mm** (3-4 bottom layers at 0.2mm).
- Lid thickness: **1.2mm** (2 perimeters).

**When the app generates the print_settings.md**, it should list per-tray recommendations with wall thicknesses as both mm values AND perimeter counts, nozzle suggestion, and a one-line reason for each choice.

**Infill: 15%** with gyroid or grid pattern. Inserts are mostly walls and floors with minimal infill area anyway. Going above 20% wastes filament with zero perceivable benefit. Wall perimeters contribute far more to strength than infill does — if something feels flimsy, add a perimeter, don't increase infill.

### Speed & Temperature
- **Print speed: whatever your printer's "standard" profile uses.** Modern printers (Bambu P1S at 250-500mm/s) handle inserts trivially. No need to slow down.
- **Nozzle temp: filament manufacturer recommendation** (typically 200-215°C for PLA).
- **Bed temp: 55-60°C for PLA.** Inserts have large flat bases that benefit from good bed adhesion.
- **No supports needed** — inserts are open-top boxes with no overhangs. If the design somehow requires supports, it should be redesigned. The only exception is decorative elements like angled card wells.
- **Brim: optional** for very large flat trays (>200mm). Prevents corner lifting. A 3mm brim is sufficient and peels off easily.

### Orientation
- **Print trays upright** (opening facing up). This is the natural orientation and gives the best quality for the interior surfaces that components touch.
- **Print lids flat.** The bottom surface (bed side) will be the smoothest face — this becomes the top of the lid that you see.

### Filament Usage Estimates
For planning/cost purposes, Tray Bien should estimate filament usage:
- A typical single-tray insert: 50-100g of filament ($0.75-$1.50)
- A full multi-tray system for a big-box game: 150-400g ($2.25-$6.00)
- Most inserts for a standard box game: under $5 in PLA

---

## Filament Efficiency: Detect and Prevent Waste

A wasteful insert is one that uses more plastic than necessary to achieve the same function. Tray Bien should actively watch for waste patterns and alert the user with suggestions — not just after the design is done, but **during the design process** as choices are made.

### What "wasteful" looks like:

**Oversized compartments**
A compartment that's 50% larger than its contents wastes wall material, floor material, and box space. The app knows the component dimensions and the compartment dimensions — if the ratio exceeds a threshold, flag it.
- 🟢 **Efficient**: compartment volume is within 1.2× of component volume (accounting for clearance)
- 🟡 **Loose fit**: compartment volume is 1.2-1.5× component volume → "This compartment has room to spare. Intentional, or should we tighten it up?"
- 🔴 **Wasteful**: compartment volume exceeds 1.5× component volume → "This compartment is significantly oversized. Consider reducing dimensions to save ~Xg of filament."

**Unnecessary thick walls**
If the user manually sets outer walls to 2.4mm (6 perimeters on a 0.4mm nozzle) when the default 1.6mm is more than sufficient, the app should note the cost:
- "Increasing walls from 1.6mm to 2.4mm adds ~Xg of filament across all trays (+X%). The default 1.6mm is already sturdy for insert use — thicker walls are typically only needed for load-bearing mechanical parts."

**Excessive infill**
If the user sets infill above 20%, flag it gently:
- "Infill above 20% has minimal structural benefit for inserts. Reducing from 30% to 15% saves ~Xg of filament and ~X minutes of print time with no noticeable difference in rigidity."

**Lids that aren't needed**
Every lid adds material. The smart lid logic already recommends skipping lids where the tray above covers. But if the user overrides and adds lids to every tray, the app should show the total lid cost:
- "You've added lids to all 4 trays. Trays 1 and 2 are fully covered by the trays above them — removing those lids saves ~Xg of filament and ~X minutes of print time."

**Dead space in the box**
If the insert design leaves significant unused volume in the game box, it's not necessarily waste (you might want room for expansion), but the app should note it:
- "Your insert uses 65% of the available box volume. The remaining 35% is empty space above the top tray. Options: make the top tray taller, add a spacer tray, or leave it for future expansions."

**Duplicate compartments that could be shared**
If two component types could share a compartment (e.g., two types of resource tokens that are never on the table simultaneously), the app could suggest consolidation:
- "The 'wood' and 'food' tokens are similar sizes. Combining them into one compartment with a removable divider saves one set of walls (~Xg)." *(This is an advanced suggestion — only show when the savings are meaningful.)*

### How to calculate waste:

The app already knows:
- Compartment dimensions (from the questionnaire)
- Component dimensions (from the questionnaire + component_standards.json)
- Wall thickness (from nozzle settings)
- Number of trays and lids
- Infill percentage

From these, it can estimate:
- **Total filament weight** = wall volume + floor volume + lid volume + infill volume, multiplied by PLA density (1.24 g/cm³)
- **Efficient baseline** = same design with optimal clearances, default walls, 15% infill, smart lids
- **Waste delta** = user's design minus efficient baseline
- **Cost delta** = waste delta × filament cost per gram (~$0.02/g for PLA)
- **Time delta** = approximate print time difference (from volume and speed estimates)

### UI implementation:

**Efficiency score** — a simple meter or percentage shown on the preview page:
- 🟢 90-100%: "Efficient design — minimal waste"
- 🟡 70-89%: "Good design — some savings possible" (with expandable suggestions)
- 🔴 Below 70%: "This design uses more filament than needed" (with specific recommendations)

Each suggestion includes **concrete numbers**: grams saved, dollars saved, minutes saved. Abstract advice like "consider reducing waste" is useless — "removing 2 unnecessary lids saves 18g ($0.36) and 25 minutes of print time" is actionable.

**The efficiency analysis runs live** as the user makes changes, not just at the end. If they add a lid, the meter updates. If they increase wall thickness, the delta appears immediately.

---

## How This Maps to Tray Bien's UI

### Pre-Program Defaults (baked into the questionnaire)
- Vertical storage mode: **ON** by default (with option to switch to horizontal)
- Lids: **Smart per-tray recommendation** (not blanket on/off). App evaluates each tray's position in the stack and contents, pre-selects on/off with a reason, user can override.
- Finger cutouts: **ON** by default (front and back sides)
- Corner style: **Rounded** by default (2mm radius)
- Nozzle diameter: **Asked once on first use** (default 0.4mm with explainer). App then **proactively suggests per-tray nozzle + wall thickness** with plain-English reasons. Flags when a specific tray would benefit from a different nozzle than the user's default.
- Wall thickness: **Auto-calculated as clean nozzle multiples** (1.6mm outer / 1.2mm dividers for 0.4mm nozzle). Per-tray overrides suggested when tray contents warrant it.
- Compartment labels: **ON** by default (embossed)
- Sleeved cards: **ASK per design** with presets for common sleeve thicknesses
- Clearance values: auto-calculated per component type using the tolerance table above
- Nested sub-trays: **suggested automatically** when shared resources are added for games with 3+ players

### Design-Time Guidance (warnings and suggestions shown to the user)
- ⚠️ Warning if total tray height doesn't fill the box (vertical storage risk)
- ⚠️ Warning if a tray with small loose tokens has no lid AND no tray above it (spill risk)
- ⚠️ Warning if card compartment walls are shorter than card height (spill risk)
- ⚠️ Warning if configured wall thickness isn't a clean multiple of the nozzle diameter
- 🔴 Filament waste alert if any compartment exceeds 1.5× component volume
- 🟡 Efficiency nudge if infill >20%, walls above default, or unnecessary lids are added — with grams, cost, and time saved
- 📊 **Live efficiency meter** on the preview page — updates as the user makes changes
- 🖼️ **Inline SVG visual explainers** shown next to every design concept (pedestal bases, finger cutouts, inset lids, nested sub-trays, angled card wells, bottom holes). Expandable "What's this?" next to each option.
- 💡 Suggestion: "Tray 1 doesn't need a lid — Tray 2 sits directly on top and covers it"
- 💡 Suggestion to create **nested sub-trays** when shared resources are added for 3+ player games ("Split this into two removable half-trays so both ends of the table have access")
- 💡 Suggestion to add **player trays** when the game has per-player starting components
- 💡 Suggestion for **pedestal bases** when card compartments are surrounded by other compartments (no room for finger cutouts)
- 💡 Suggestion for **bottom holes** in token stack compartments to prevent vacuum suction
- 💡 Prompt for filament color suggestion based on selected game
- 📐 Auto-calculate sleeve clearance when "sleeved" is toggled for a card group
- 🔧 If user changes nozzle size in Settings, auto-recalculate and flag any wall thicknesses that are no longer clean multiples

### Print-Time Recommendations (in the exported settings file)
- Full print_settings.md with **per-tray print cards** — each tray gets its own section with:
  - Recommended nozzle + wall thicknesses (mm and perimeter counts)
  - One-line reason for the recommendation ("Large open tray, no labels → 0.6mm nozzle saves 35% print time")
  - Filament weight estimate for that tray
  - Estimated print time for that tray
- Overall filament usage total and approximate cost
- Color suggestions with specific filament brand/color recommendations if game-matched
- Recommended print order (bottom tray first, test a lid fit, then remaining trays)
- Tolerance test piece suggestion for first-time printers
- If mixed nozzle recommendations: grouped by nozzle so the user can batch prints ("Print these 3 trays with 0.6mm, then swap to 0.4mm for these 2")

### AI Chat Intelligence (context the AI uses for suggestions)
- The AI prompt should include this entire design philosophy as context
- When the user describes a component, the AI should apply the correct tolerance rules automatically
- The AI should proactively suggest player trays, resource splitting, and pedestal bases when the game design warrants it
- The AI should warn about vertical storage violations in any modifications it makes

---

## Quick Reference: The Golden Rules

1. **Open box → trays on table → play.** Every design decision serves this flow.
2. **Lid smart, not lid everything.** Use lids where contents would spill; skip them where the tray above does the job.
3. **Fill the box height.** Dead air means shifting components. A tight stack is its own retention system.
4. **Finger cutouts everywhere.** If you can't grab it with one hand, redesign it.
5. **Bottom holes prevent vacuum.** Especially for token stacks and tight-fitting components.
6. **Measure twice, print once.** Use calipers, not published specs. Add clearance per the tolerance table.
7. **Player trays are magic.** One tray per player transforms setup from 10 minutes to 30 seconds.
8. **Split the bank.** Nested sub-trays let both ends of the table reach resources without passing bowls.
9. **Labels aren't decoration — they're function.** They make teardown brainless.
10. **Walls are multiples of your nozzle.** 0.4mm nozzle → 0.8 / 1.2 / 1.6mm walls. The app tells you which and why.
11. **1.6mm walls, 15% infill, 0.2mm layers.** The insert printer's holy trinity.
12. **Print a tolerance test first.** A 10-minute test print saves hours of reprinting.
