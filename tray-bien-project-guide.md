# Tray Bien — Board Game Insert Generator

### *Très bon inserts for every game in your collection*

---

## Project Summary

**Tray Bien** is a visual web application that walks you through designing custom 3D-printable board game inserts. It runs in your browser with a full graphical interface — dropdowns, sliders, image uploads, live 3D previews, and an AI chat panel for handling tricky edge cases. The output is universal STL files printable on any 3D printer.

**Total ongoing cost after the program is built: $0**

---

## Table of Contents

1. [What You're Building](#1-what-youre-building)
2. [Cost Breakdown](#2-cost-breakdown)
3. [Printer Recommendation](#3-printer-recommendation)
4. [Setting Up Your Development Environment](#4-setting-up-your-development-environment)
5. [The Starter Prompt for Claude Code](#5-the-starter-prompt-for-claude-code)
6. [How Development Works Day-to-Day](#6-how-development-works-day-to-day)
7. [Sharing With Friends](#7-sharing-with-friends)
8. [Key Technical Notes](#8-key-technical-notes)
9. [Useful References](#9-useful-references)

---

## 1. What You're Building

A Streamlit web app with this user flow:

### Step 1 — Box Setup
Dropdown to pick a known game box ("Catan," "Ticket to Ride," "Wingspan," etc.) or enter custom inner dimensions. A live diagram shows the box outline and available space.

### Step 2 — Add Components
Click buttons like "Add Cards," "Add Tokens," "Add Dice," "Add Miniatures." Each opens a form with size presets (e.g., standard poker cards sleeved/unsleeved) and quantity fields. A sidebar tracks everything you've added.

### Step 3 — Layout Preferences
Toggle switches for lids (smart per-tray recommendations with reasons), radio buttons for horizontal vs. vertical storage, auto-calculated wall thickness based on your nozzle, checkboxes for finger cutouts and rounded corners. Every design concept — pedestal bases, nested sub-trays, angled card wells — has an **inline diagram** you can expand to see what it actually looks like before you choose it.

### Step 4 — Customization
Drag-and-drop image upload for logos/graphics, text fields for compartment labels, positioning controls for where the logo goes (lid, bottom, side wall).

### Step 5 — Preview + AI Chat Refinement
A rendered 3D image of your insert displayed in the browser, with a **live efficiency meter** showing filament usage and flagging waste (oversized compartments, unnecessary lids, thick walls). Per-tray print recommendations appear as info cards suggesting the best nozzle and wall thickness with a plain-English reason for each.

Below the preview is a **chat panel** where you can type freeform requests to handle anything the wizard didn't anticipate:

- *"The Catan hex tiles need to stack in a honeycomb pattern, not a grid"*
- *"Add a narrow slot along the left wall for the score track — it's 280mm × 40mm × 2mm"*
- *"The miniatures are too tall, split this into two stacking trays"*
- *"Make the card compartment angled so I can thumb through the cards"*
- *"I have a weird L-shaped board piece, here are the dimensions..."*

The AI sees your current insert configuration, modifies the OpenSCAD code, and re-renders the preview. You keep chatting until it looks right.

### Step 6 — Export
Download buttons for STL files (one per tray if multi-tray), plus a **per-tray print settings guide** with nozzle, wall thickness, filament weight, estimated print time, and cost — each with a reason. Trays grouped by recommended nozzle so you can batch prints efficiently.

### Optional Step 7 — Send to Printer
If you've configured your Bambu printer, one-click send to print.

**No terminal interaction needed for day-to-day use.** The only time you touch a terminal is during initial setup.

---

## 2. Cost Breakdown

### To BUILD the program (one-time)

| Item | Cost | Notes |
|------|------|-------|
| Claude Pro subscription | $20/month | You already have this |
| GSD framework | Free | Open-source workflow enhancer for Claude Code |

You'll likely need 1-2 months of Pro. Claude Code on the Pro plan uses **Sonnet 4.5**, which is the right model for this project — fast, capable, and won't burn through your usage limits. You don't need to upgrade to Max or use Opus.

Use **Opus 4.6 here in claude.ai chat** (which you already have) for planning, brainstorming, and thinking through architecture. Use **Sonnet 4.5 in Claude Code** for actually writing the code.

### To RUN the program (ongoing)

| Item | Cost |
|------|------|
| Streamlit | Free (open-source) |
| Streamlit Community Cloud (hosting) | Free |
| OpenSCAD | Free (open-source) |
| Boardgame Insert Toolkit | Free (open-source) |
| Python | Free |
| AI for code gen + chat refinement | Free (Gemini API free tier, or local Ollama model) |

### To PRINT inserts

| Item | Cost |
|------|------|
| Bambu Lab P1S Combo (recommended) | ~$400-$600 (watch for sales) |
| PLA filament | ~$15-20 per 1kg spool (prints dozens of inserts) |

---

## 3. Printer Recommendation: Bambu Lab P1S Combo

For board game inserts specifically, the **P1S Combo** is the best value in Bambu's lineup:

- **Enclosed chamber** — consistent temperatures mean no warping on large flat insert trays
- **AMS (Auto Material System)** — print in multiple colors (color-code compartments, contrasting logos)
- **Build volume (256×256×256mm)** — fits most standard board game box dimensions in one print
- **Speed (~500mm/s)** — a typical insert tray prints in 2-4 hours vs. 8-12 on budget printers
- **Reliability** — critical when printing 4-6 trays per game
- **Software** — Bambu Studio slicer is excellent, and the bambulabs-api Python package supports P-series well

The A1 Combo ($399) is a solid budget option but lacks the enclosure. The X1 Carbon is overkill for PLA/PETG inserts.

**Your friend's different Bambu printer works too.** STL files are universal — every printer model uses them.

---

## 4. Setting Up Your Development Environment

### Step 1: Install the Basics

You only need to manually install two things. Claude Code will check for and help install everything else.

**Node.js 18+** (required to install Claude Code):
- Download from https://nodejs.org (LTS version)
- Verify: `node --version`

**Claude Code:**
```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

On first run it will prompt you to authenticate with your Claude Pro account.

For the latest installation details: https://docs.claude.com/en/docs/claude-code/overview

### Step 2: Create the GitHub Repo

Go to https://github.com/new and create a repo called `tray-bien`. Then:

```bash
mkdir tray-bien
cd tray-bien
git init
git remote add origin https://github.com/hungryrobot/tray-bien.git
```

### Step 3: Set Up the GSD Framework

GSD (Get Shit Done) is a workflow framework that sits on top of Claude Code. It enforces a structured approach — Idea → Roadmap → Phase Plan → Atomic Execution — preventing "context rot" where AI quality degrades in long sessions.

```bash
cd tray-bien
git clone https://github.com/glittercowboy/get-shit-done.git .gsd
```

Follow GSD's README for setup — it adds custom slash commands to Claude Code (like `/gsd-research`, `/gsd-plan`, `/gsd-execute`).

### Step 4: Launch Claude Code

```bash
cd tray-bien
claude
```

Then paste the starter prompt from Section 5 below. **Claude Code will automatically check for all remaining prerequisites** (Python, OpenSCAD, Git, pip packages) and either install what's missing or give you exact instructions. You don't need to manually install anything else before starting.

---

## 5. The Starter Prompt for Claude Code

Use GSD's workflow to feed this in at the appropriate stage. If you're not using GSD, you can paste this directly into Claude Code.

---

```
PROJECT: Tray Bien — Board Game Insert Generator
REPO: https://github.com/hungryrobot/tray-bien

SUMMARY:
A Streamlit web application that guides users through designing custom
3D-printable board game inserts via a visual browser UI, generates OpenSCAD
code using The Boardgame Insert Toolkit library, provides an AI chat panel
for freeform refinement, renders live previews, and exports print-ready
STL files. Designed to be shared — runs locally or hosted free on Streamlit
Community Cloud.

## PHASE 0: Prerequisites Check (DO THIS FIRST)

Before writing any project code, check that all required tools are installed.
Run shell commands to verify each one and report the results:

1. Python 3.10+ — check `python --version` or `python3 --version`
2. pip — check `pip --version`
3. OpenSCAD — check `openscad --version`
4. Git — check `git --version`
5. Node.js 18+ — check `node --version` (should already be installed)

For anything missing:
- Python packages: install automatically with pip
- OpenSCAD: provide the download link (https://openscad.org/downloads.html)
  and pause for the user to install manually, since it's a desktop application
- Git: provide install instructions for the user's OS

Do NOT proceed to Phase 1 until all prerequisites pass. Show a clear
checklist with ✓ and ✗ marks.

## Tech Stack

- **UI**: Streamlit (Python web framework — visual browser interface, NOT CLI)
- **3D Engine**: OpenSCAD (called via subprocess for rendering and STL export)
- **Insert Library**: The Boardgame Insert Toolkit
  (https://github.com/dppdppd/The-Boardgame-Insert-Toolkit)
- **AI Code Generation**: Provider-agnostic — supports Claude API, OpenAI,
  Google Gemini, or local Ollama models (selectable in settings)
- **Image Processing**: Pillow (for logo → heightmap conversion for embossing)
- **SVG Diagrams**: Inline SVG generation for visual explainers in the UI
- **Printer Integration** (optional future): bambulabs-api for direct Bambu
  Lab printer control

## CRITICAL: Design Philosophy Document

The companion file `tray-bien-design-philosophy.md` defines HOW the app
should behave — all defaults, tolerances, design rules, and UI guidance.
READ IT BEFORE CODING. It specifies:
- The priority hierarchy (setup speed > compact fit > aesthetics > durability)
- Smart per-tray lid logic (not blanket on/off)
- Nozzle-aware wall thickness with proactive per-tray suggestions
- Nested sub-tray patterns for shared resources
- Visual explainer SVG diagrams for every design concept
- Live filament efficiency scoring with waste detection
- Component-specific clearance/tolerance rules
- All default values and when to override them

Every UI element, default value, warning, and suggestion in the app should
trace back to a principle in that document.

## CRITICAL DESIGN REQUIREMENT: Multi-Provider AI

The AI integration layer MUST be provider-agnostic. Create an abstract
interface that any LLM provider can plug into. Implement these providers:
- Anthropic Claude (via anthropic Python SDK)
- OpenAI (via openai Python SDK)
- Google Gemini (via google-generativeai Python SDK)
- Local Ollama (via REST API to localhost:11434)
- "None" mode — uses pre-built templates only, no AI calls

Users select their provider and enter their API key in a Settings page.
The "None" mode ensures the app works even with zero AI budget by using
parameterized OpenSCAD templates for common insert patterns.

## PHASE 1: Project Setup & Streamlit Skeleton

1. Initialize Python project with pyproject.toml and requirements.txt
2. Clone The Boardgame Insert Toolkit as a git submodule into lib/BIT/
3. Create Streamlit app skeleton with page navigation:
   - Home / New Insert (the design wizard)
   - My Designs (saved configurations)
   - Settings (AI provider selection, API key entry, nozzle diameter
     with first-use prompt, printer config)
4. Create common_boxes.json with INNER dimensions for ~20 popular board
   game boxes:
   - Catan, Ticket to Ride, Wingspan, Pandemic, Azul, Splendor,
     7 Wonders, Everdell, Terraforming Mars, Spirit Island, Gloomhaven,
     Arkham Horror LCG, Dominion, Codenames, Root, Scythe,
     Brass Birmingham, Viticulture, Parks, Cascadia
5. Create component_standards.json with standard sizes:
   - Cards: poker standard, poker sleeved, mini, mini sleeved, tarot,
     bridge, bridge sleeved
   - Dice: d4, d6, d8, d10, d12, d20 (with dimensions for each)
   - Common token sizes (small round, large round, square)
6. Verify the Streamlit app launches in the browser with working navigation

## PHASE 2: Interactive Questionnaire UI

Build the Streamlit visual interface for the insert design wizard:

**Page 1 — Box Setup:**
- Searchable dropdown to select known box OR manual dimension entry
  (L × W × H in mm)
- Visual box outline diagram (use Streamlit's plotting or SVG)
- "Lid clearance" slider (how much vertical space the lid needs)
- Display available interior volume

**Page 2 — Component Inventory:**
- "Add Component" button that expands a form section
- Component type selector (Cards, Tokens, Dice, Meeples/Minis, Boards,
  Rulebook, Custom)
- Each type has smart defaults and presets from component_standards.json
- Running summary sidebar showing all added components with total volume
- Visual warning indicator if components exceed box volume
- Ability to remove or edit any added component

**Page 3 — Layout Preferences:**
- Horizontal vs. vertical storage (radio buttons with visual diagrams)
- **Smart lid recommendations per tray** — app evaluates each tray's position
  in the stack and pre-selects lid on/off with a reason shown. User can
  override. (See Design Philosophy: Smart Lid Logic)
- Single tray vs. stacking multi-tray (radio)
- Finger cutouts for easy removal (toggle + size slider)
- Wall thickness — auto-calculated from nozzle diameter, shown as mm and
  perimeter count. App suggests per-tray overrides when warranted.
- Corner style (sharp / rounded + radius slider)
- Label areas (toggle)
- **Visual explainers**: every design concept (pedestal bases, finger cutouts,
  inset vs. cap lids, nested sub-trays, angled card wells, bottom holes)
  gets an inline SVG cross-section diagram in an expandable "What's this?"
  section next to its toggle/option. Generated programmatically in Python,
  not stored image files. ~200×120px per diagram.

**Page 4 — Customization:**
- Image upload widget for logos/graphics (PNG, SVG) via st.file_uploader
- Emboss vs. deboss radio button
- Depth slider (0.3mm to 1.5mm)
- Position selector (lid center, bottom center, side wall)
- Text labels for compartments (text inputs per compartment)
- Font size slider for labels

**Summary Page:**
- Full specification review in a clean layout
- Edit buttons to jump back to any section
- "Generate Insert" button
- Save configuration as JSON / Load previous configuration
- Configuration files saved to saved_designs/ directory

## PHASE 3A: OpenSCAD Code Generation

Generate OpenSCAD code using The Boardgame Insert Toolkit's functions:

- Import the BIT library correctly (study the BIT repo's examples first)
- Define box dimensions and compartment layout using BIT's data structures
- Include finger cutouts, rounded corners, lids as specified
- Well-commented output code so users can hand-edit in OpenSCAD if desired
- Text labels via OpenSCAD's text() function
- For complex layouts, use the configured AI provider to optimize
  compartment arrangement (bin-packing) within box constraints
- "None" AI mode uses simple grid-based layout without optimization
- Save generated .scad file to output/ directory

## PHASE 3B: AI Chat Refinement Panel

Add a chat interface on the preview page using Streamlit's chat components
(st.chat_input, st.chat_message):

- Chat panel appears below the 3D preview
- User types freeform modification requests in natural language
- System prompt includes:
  - The current insert configuration as JSON
  - The current OpenSCAD code
  - The full Design Philosophy document (tolerances, rules, golden rules)
  - Instructions: "You are a board game insert designer following the Tray
    Bien design philosophy. Modify the OpenSCAD code based on the user's
    request. Return the complete updated code. Explain what you changed
    and reference the relevant visual diagram if applicable (e.g., 'I added
    a pedestal base — this is a raised bump on the floor...')."
- On receiving AI response, extract the updated OpenSCAD code
- Re-render the preview automatically
- Conversation history persists so the user can iterate
- Works with whichever AI provider is configured in Settings
- If AI provider is "None", show a message suggesting the user configure
  one for chat refinement, or allow manual .scad code editing in a
  text area instead

## PHASE 4: Preview & Export

- Run OpenSCAD in command-line mode to render PNG preview:
  `openscad --render --camera=0,0,0,55,0,25,400 -o preview.png insert.scad`
- Display preview image in Streamlit
- Provide multiple camera angle buttons (top, front, isometric, side)
- **Live filament efficiency meter** on the preview page:
  - Calculate total filament weight from wall/floor/lid/infill volumes
    × PLA density (1.24 g/cm³)
  - Compare against efficient baseline (optimal clearances, default walls,
    15% infill, smart lids)
  - Show efficiency score: 🟢 90-100%, 🟡 70-89%, 🔴 below 70%
  - Expandable waste suggestions with concrete numbers: grams saved,
    dollars saved (~$0.02/g PLA), minutes saved
  - Updates live as user makes changes in the questionnaire or chat
  - Flag specific issues: oversized compartments (>1.5× component volume),
    unnecessary lids, walls above default, infill >20%
- **Per-tray nozzle/print recommendations** — info card for each tray:
  - Recommended nozzle diameter with one-line reason
  - Wall thickness as mm AND perimeter count
  - Flag when a tray benefits from a different nozzle than user's default
  - Present two options with tradeoffs when nozzle change is suggested
- Export STL files — one per tray if multi-tray design
- Generate **per-tray print_settings.md** with:
  - Each tray gets its own section with nozzle, walls, layer height
  - One-line reason for each recommendation
  - Per-tray filament weight estimate and print time estimate
  - Overall totals and approximate cost
  - Trays grouped by nozzle for efficient batching
  - Material: PLA recommended, PETG for durability
  - Supports: typically not needed for inserts
  - Color suggestions matched to game palette
  - Recommended print order (bottom tray first, test a lid fit)
  - Tolerance test piece suggestion for first-time printers
- Download buttons in Streamlit for all output files (STL + settings)
- Option to download the raw .scad file for manual editing

## PHASE 5: Image/Logo Embedding

- Accept PNG/SVG uploads via Streamlit file_uploader
- Convert to grayscale heightmap using Pillow
- Auto-resize to fit target surface area
- Generate OpenSCAD surface() call for emboss/deboss
- Support positioning on lid, bottom, or side walls
- Show warning if image detail is finer than 0.4mm (one nozzle width)
  with suggestion to simplify the image
- Preview the logo placement before final generation

## PHASE 6 (Future): Bambu Labs Printer Integration

- Settings page fields for: Printer IP, Serial Number, Access Code
- Connection test button with status indicator
- Using bambulabs-api (pip install bambulabs-api):
  - Upload STL to printer
  - Monitor print status with progress bar in Streamlit
  - Show printer state (idle, printing, error)
- Works with any Bambu Lab printer (A1, P1S, X1C, etc.) — user just
  enters their own printer's credentials
- This phase only activates when printer settings are configured

## Project Structure

```
tray-bien/
├── README.md
├── pyproject.toml
├── requirements.txt
├── tray-bien-design-philosophy.md  # Design rules — fed to AI + Claude Code
├── app.py                        # Streamlit entry point
├── .gsd/                         # GSD framework (cloned)
├── src/
│   ├── __init__.py
│   ├── pages/
│   │   ├── 01_new_insert.py      # Main wizard flow
│   │   ├── 02_my_designs.py      # Saved configurations
│   │   └── 03_settings.py        # AI provider, nozzle, printer config
│   ├── questionnaire/
│   │   ├── box_setup.py          # Box selection/dimensions UI
│   │   ├── components.py         # Component inventory UI
│   │   ├── layout_prefs.py       # Layout preference controls
│   │   └── customization.py      # Logo upload, labels, styling
│   ├── ui/
│   │   ├── visual_explainers.py  # Inline SVG diagram generators
│   │   └── efficiency_meter.py   # Live filament waste scoring
│   ├── ai/
│   │   ├── provider.py           # Abstract AI provider interface
│   │   ├── claude_provider.py    # Anthropic Claude implementation
│   │   ├── openai_provider.py    # OpenAI implementation
│   │   ├── gemini_provider.py    # Google Gemini implementation
│   │   ├── ollama_provider.py    # Local Ollama implementation
│   │   └── none_provider.py      # Template-only, no AI calls
│   ├── chat/
│   │   └── refinement.py         # AI chat refinement panel
│   ├── generator/
│   │   ├── scad_generator.py     # OpenSCAD code generation
│   │   ├── layout_engine.py      # Bin-packing / compartment layout
│   │   ├── image_processor.py    # Logo → heightmap conversion
│   │   ├── nozzle_advisor.py     # Per-tray nozzle/wall recommendations
│   │   └── templates/            # Pre-built OpenSCAD templates
│   ├── preview/
│   │   ├── renderer.py           # OpenSCAD CLI rendering
│   │   └── exporter.py           # STL export & per-tray print settings
│   ├── printer/
│   │   └── bambu.py              # Bambu Labs API integration
│   └── data/
│       ├── common_boxes.json     # Known board game box dimensions
│       └── component_standards.json  # Standard component sizes
├── lib/
│   └── BIT/                      # Git submodule: Boardgame Insert Toolkit
├── output/                       # Generated .scad, .stl, .png files
├── saved_designs/                # User's saved insert configurations
└── tests/
```

## Getting Started

Run Phase 0 first (prerequisites check). Then build Phase 1 (project
skeleton). Get the Streamlit app launching in the browser with working
navigation before moving on. We'll iterate phase by phase.
```

---

## 6. How Development Works Day-to-Day

### The GSD Workflow

Instead of dumping the entire prompt above at once, GSD structures your work:

1. **Research Phase** — Feed GSD the project idea. It researches the tools, checks feasibility, identifies risks.

2. **Roadmap Phase** — GSD creates a phased roadmap with clear milestones.

3. **Planning Phase** — For each phase, GSD creates an atomic plan: exactly what files to create, what functions to write, what to test.

4. **Execution Phase** — Claude Code writes the actual code, one atomic task at a time. Each task is small enough to complete without context degradation.

5. **Verification Phase** — Test what was built, document it, commit to git.

Then repeat steps 3-5 for the next phase.

### What a typical session looks like

```
You: [launch Claude Code in your tray-bien directory]
You: /gsd-plan phase-2
GSD: [creates detailed plan for the questionnaire UI]

You: /gsd-execute task-1
Claude Code: [creates box_setup.py with the dropdown and dimension inputs]

You: streamlit run app.py
[browser opens, you test the box selection page]

You: "The dropdown works but I want it to also show the box dimensions
      next to each game name"
Claude Code: [updates the code]

You: [test again, looks good]
You: git add -A && git commit -m "Phase 2 task 1: box setup page"
You: /gsd-execute task-2
[...continues through the phase]
```

### Tips

- **Test with a real game first.** Once Phases 2-3 work, try designing an insert for a game you own. You know exactly what components it has, so you'll immediately spot issues.
- **Opus for thinking, Sonnet for building.** If you hit a tricky design question, come back to this claude.ai chat (Opus 4.6) to think it through, then take the solution back to Claude Code (Sonnet 4.5).
- **Save configurations as JSON.** The app saves/loads designs, so you don't re-enter everything when iterating on a design.
- **Use git.** Commit after each working task. GSD auto-generates commit messages.
- **One phase at a time.** Don't skip ahead. Each phase builds on the last.
- **Your first test insert** could be for one of the games in your collection — you know the components intimately and can validate the output against the real box.

---

## 7. Sharing With Friends

### Option A: Share the Code (for tech-comfortable friends)

Your friend clones your repo and runs:

```bash
git clone https://github.com/hungryrobot/tray-bien.git
cd tray-bien
pip install -r requirements.txt
streamlit run app.py
```

Browser opens, they design inserts, download STL files. For AI chat refinement, they add their own free Gemini API key in Settings. Without an API key, "None" mode still works using templates.

To connect their Bambu printer (any model), they enter their printer's IP, serial, and access code in Settings.

### Option B: Host It Online (for non-technical friends)

Deploy to Streamlit Community Cloud (free):

1. Push your code to the `hungryrobot/tray-bien` GitHub repo
2. Go to https://streamlit.io/cloud
3. Connect your repo
4. Deploy — you get a URL like `tray-bien.streamlit.app`

Anyone with the link designs inserts and downloads STL files in their browser. No installation needed.

Note: The hosted version wouldn't include direct-to-printer (requires local network access), but the core workflow — design → download STL → slice in Bambu Studio → print — works perfectly.

### Printer Compatibility

STL files work on **every** 3D printer, not just Bambu. Your friend could have a Prusa, Creality, Elegoo, anything. The only Bambu-specific feature is the optional direct-send in Phase 6.

---

## 8. Key Technical Notes

### The Boardgame Insert Toolkit does the heavy lifting
BIT already handles lids, finger cutouts, stacking trays, label areas, and wall parameters. Tray Bien is a smart visual front-end that produces BIT configuration code.

### Image embedding has physical limits
Detail smaller than ~0.4mm (one nozzle width) won't print. Logos work best as simple, bold designs embossed 0.5-1mm deep. The program warns users about this.

### The AI is optional, not required
"None" mode works without any AI — using parameterized templates for common insert patterns (grid layouts, card rows, etc.). AI helps with complex optimization and the chat refinement feature, but simple inserts don't need it.

### The chat refinement panel is what makes this special
This is the feature that handles the long tail of weird board game components that no questionnaire can anticipate. The AI sees the current design context and makes targeted modifications. This is also where a smarter AI provider (Claude, GPT-4o) pays off versus a small local model.

### OpenSCAD runs as a background process
The app calls OpenSCAD via command line. Users never see OpenSCAD directly — it's behind the Streamlit UI.

### Bambu printer connection
The bambulabs-api package communicates over MQTT on local WiFi. You need the printer's IP, serial number, and access code (found in printer network settings). Phase 6 concern only.

---

## 9. Useful References

| Resource | URL |
|----------|-----|
| Claude Code docs | https://docs.claude.com/en/docs/claude-code/overview |
| GSD Framework | https://github.com/glittercowboy/get-shit-done |
| OpenSCAD | https://openscad.org/documentation.html |
| Boardgame Insert Toolkit | https://github.com/dppdppd/The-Boardgame-Insert-Toolkit |
| Streamlit docs | https://docs.streamlit.io |
| Streamlit Community Cloud | https://streamlit.io/cloud |
| Bambu Labs Python API | https://bambutools.github.io/bambulabs_api/ |
| Bambu Lab Wiki | https://wiki.bambulab.com/en/home |
| Bambu Lab Printer Comparison | https://bambulab.com/en-us/compare |
| Blog post inspiration | https://jdsalmonson.github.io/openscad-ai-3d-print |
| Google Gemini free API | https://ai.google.dev |
| Ollama (local AI) | https://ollama.com |
