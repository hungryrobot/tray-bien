# Tray Bien 🎲

**Très bon inserts for every game in your collection**

A visual web application that guides you through designing custom 3D-printable board game inserts. Design in your browser, export STL files, print on any 3D printer.

## Features

- 🎨 **Visual Design Wizard** - Browser-based UI with dropdowns, sliders, and live previews
- 🤖 **AI Chat Refinement** - Handle edge cases with natural language requests
- 📏 **Smart Defaults** - Component-specific tolerances and clearances
- 🔧 **Nozzle-Aware** - Per-tray print recommendations with reasons
- 💰 **Efficiency Scoring** - Live filament waste detection with concrete savings
- 📊 **Visual Explainers** - SVG diagrams for every design concept
- 🖨️ **Universal Export** - STL files work on any 3D printer

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenSCAD (for rendering and STL export)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/hungryrobot/tray-bien.git
cd tray-bien

# Install Python dependencies
pip3.10 install -r requirements.txt

# Launch the app
streamlit run app.py
```

Your browser will open to `http://localhost:8501`

### First-Time Setup

1. **Configure Nozzle Diameter** - Settings page will prompt you on first use
2. **Choose AI Provider** (optional) - For chat refinement and layout optimization:
   - Anthropic Claude (requires API key)
   - OpenAI (requires API key)
   - Google Gemini (free tier available)
   - Local Ollama (runs on your machine)
   - None (uses templates only, no AI)

## How It Works

1. **Select Box** - Choose from 20+ popular board games or enter custom dimensions
2. **Add Components** - Cards, tokens, dice, meeples, boards, rulebooks
3. **Set Preferences** - Lids, walls, corners, cutouts, labels
4. **Preview & Refine** - View 3D render, chat with AI to tweak details
5. **Export** - Download STL files and print settings guide
6. **Print** - Use any 3D printer (optional: send directly to Bambu Lab printers)

## Project Status

**Current Phase:** 1 - Project Setup ✅

- [x] Prerequisites check
- [x] Python project structure
- [ ] Boardgame Insert Toolkit integration
- [ ] Streamlit app skeleton
- [ ] Data files (boxes, components)
- [ ] Launch verification

See [tray-bien-project-guide.md](tray-bien-project-guide.md) for full roadmap.

## Design Philosophy

Every UI element, default value, and suggestion follows the principles in [tray-bien-design-philosophy.md](tray-bien-design-philosophy.md):

**Priority Hierarchy:**
1. Setup Speed (< 2 min unpack-to-play)
2. Compact Fit (maximize usable space)
3. Aesthetics (clean organization)
4. Durability (100+ game nights)

**Golden Rules:**
- Smart per-tray lid logic (not blanket on/off)
- Nozzle-aware wall thickness with proactive suggestions
- Nested sub-trays for shared resources
- Filament efficiency first

## Technology Stack

- **UI:** Streamlit (Python web framework)
- **3D Engine:** OpenSCAD (via subprocess)
- **Insert Library:** [The Boardgame Insert Toolkit](https://github.com/dppdppd/The-Boardgame-Insert-Toolkit)
- **AI:** Provider-agnostic (Claude, OpenAI, Gemini, Ollama, or None)
- **Image Processing:** Pillow
- **Printer Integration:** bambulabs-api (optional)

## Contributing

This project is in active development. Issues and pull requests welcome!

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [The Boardgame Insert Toolkit](https://github.com/dppdppd/The-Boardgame-Insert-Toolkit) by dppdppd
- Inspired by the board game community's amazing insert designs

---

**Cost to run:** $0 (use free Gemini API or local Ollama)
**Works with:** Any 3D printer (STL files are universal)
**Perfect for:** Streamers, game cafés, board game enthusiasts, makers
