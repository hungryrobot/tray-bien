"""
Tray Bien - Board Game Insert Generator
Main Streamlit application entry point
"""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Tray Bien - Board Game Insert Generator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e7f3ff;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🎲 Tray Bien</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Très bon inserts for every game in your collection</div>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
Welcome to **Tray Bien**, your visual board game insert designer! This app guides you through
creating custom 3D-printable inserts with smart defaults, live previews, and AI-powered refinement.
""")

# Feature highlights
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 🎨 Visual Design")
    st.markdown("""
    - Browser-based wizard
    - Searchable game database
    - Live 3D preview
    - Smart component presets
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Refinement")
    st.markdown("""
    - Natural language chat
    - Provider-agnostic
    - Context-aware suggestions
    - Iterative improvements
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 📊 Smart Optimization")
    st.markdown("""
    - Nozzle-aware walls
    - Efficiency scoring
    - Per-tray recommendations
    - Waste detection
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Quick start guide
st.markdown("## 🚀 Quick Start")

st.markdown('<div class="info-box">', unsafe_allow_html=True)
st.markdown("""
**First time using Tray Bien?** Here's what to do:

1. **Visit Settings** (sidebar) → Configure your nozzle diameter (usually 0.4mm)
2. **New Insert** (sidebar) → Start designing with the visual wizard
3. **Preview & Refine** → See your design, chat with AI to perfect it
4. **Export** → Download STL files and print settings guide

**Optional:** Configure an AI provider in Settings for chat refinement (or use "None" mode with templates only)
""")
st.markdown('</div>', unsafe_allow_html=True)

# How it works
st.markdown("## 📋 Design Process")

with st.expander("See the step-by-step workflow"):
    st.markdown("""
    ### Step 1: Box Setup
    Choose from 20+ popular board games or enter custom dimensions. See available interior volume.

    ### Step 2: Component Inventory
    Add cards, tokens, dice, meeples, boards, and rulebooks. Use smart presets or custom sizes.

    ### Step 3: Layout Preferences
    Configure lids (smart per-tray recommendations), storage orientation, cutouts, walls, and corners.

    ### Step 4: Customization
    Upload logos, add embossed labels, choose positioning and styling.

    ### Step 5: Preview & AI Chat
    View rendered 3D preview, see efficiency score, chat with AI for complex modifications.

    ### Step 6: Export
    Download STL files (one per tray), plus detailed print settings with per-tray recommendations.
    """)

# Design philosophy teaser
st.markdown("## 🎯 Design Philosophy")

st.markdown("""
Every design decision in Tray Bien follows a clear priority hierarchy:

1. **Setup Speed** — Open box → trays on table → play (< 2 minutes)
2. **Compact Fit** — Maximize usable space, minimize waste
3. **Aesthetics** — Clean organization, satisfying design
4. **Durability** — Built for 100+ game nights

**Golden Rules:**
- Smart lid logic (per-tray evaluation, not blanket on/off)
- Nozzle-aware wall thickness with proactive suggestions
- Nested sub-trays for shared resources
- Filament efficiency first
""")

# Navigation guide
st.markdown("---")
st.markdown("### 👈 Use the sidebar to navigate:")
st.markdown("""
- **New Insert** — Start designing a new board game insert
- **My Designs** — View and load previously saved configurations
- **Settings** — Configure AI provider, nozzle diameter, and printer
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    Made with ❤️ for board game enthusiasts • Open source • Works with any 3D printer
</div>
""", unsafe_allow_html=True)
