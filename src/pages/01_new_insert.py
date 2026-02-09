"""
New Insert - Main design wizard page
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from questionnaire.box_setup import render_box_setup
from questionnaire.components import render_components_inventory
from ui.visual_explainers import show_diagram

st.set_page_config(
    page_title="New Insert - Tray Bien",
    page_icon="🎲",
    layout="wide",
)

st.title("🎨 New Insert Design Wizard")

# Initialize wizard state
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1

# Progress tracker
st.markdown("### Design Progress")
progress_cols = st.columns(5)

steps = [
    ("1️⃣ Box Setup", 1),
    ("2️⃣ Components", 2),
    ("3️⃣ Layout", 3),
    ("4️⃣ Customization", 4),
    ("5️⃣ Preview", 5)
]

for i, (label, step_num) in enumerate(steps):
    with progress_cols[i]:
        button_type = "primary" if st.session_state.wizard_step == step_num else "secondary"
        if st.button(label, key=f"step_{step_num}", use_container_width=True, type=button_type):
            st.session_state.wizard_step = step_num
            st.rerun()

st.markdown("---")

# Render current step
if st.session_state.wizard_step == 1:
    # Box Setup
    box_config = render_box_setup()

    # Example of using visual explainer
    with st.expander("💡 What's a clearance zone?"):
        show_diagram('clearance_zones', "Clearances are extra space added around components for easy access")

    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if st.button("Next: Components →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()

elif st.session_state.wizard_step == 2:
    # Component Inventory
    components = render_components_inventory()

    # Visual explainer examples
    st.markdown("---")
    st.markdown("#### 💡 Design Tips")

    tip_col1, tip_col2 = st.columns(2)

    with tip_col1:
        with st.expander("What's a finger cutout?"):
            show_diagram('finger_cutout', "Scooped walls let you reach in and grab components easily")

    with tip_col2:
        with st.expander("What's a pedestal base?"):
            show_diagram('pedestal_base', "Push down on one end to pop the other end up for grabbing")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back: Box Setup", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with col3:
        if st.button("Next: Layout →", type="primary", use_container_width=True):
            if not st.session_state.components:
                st.error("⚠️ Please add at least one component before continuing")
            else:
                st.session_state.wizard_step = 3
                st.rerun()

elif st.session_state.wizard_step == 3:
    # Layout Preferences (placeholder for now)
    st.markdown("### 🎨 Step 3: Layout Preferences")

    st.info("""
    🚧 **Coming Soon in Phase 2**

    This section will include:
    - Storage orientation (horizontal vs vertical)
    - Smart per-tray lid recommendations
    - Single tray vs multi-tray stacking
    - Finger cutouts configuration
    - Wall thickness (nozzle-aware)
    - Corner style and radius
    - Label areas
    """)

    # Show some visual explainers as preview
    st.markdown("#### 📐 Design Concepts Preview")

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        with st.expander("Lid Types: Inset vs Cap"):
            show_diagram('lid_comparison', "Inset lids save height, cap lids are sturdier")

        with st.expander("Wall Thickness (Perimeters)"):
            show_diagram('wall_thickness', "Walls must be multiples of your nozzle diameter")

    with exp_col2:
        with st.expander("Nested Sub-Trays"):
            show_diagram('nested_subtrays', "Removable trays for shared resources at both ends of table")

        with st.expander("Bottom Holes (Vacuum Release)"):
            show_diagram('bottom_hole', "Push tokens up from below, prevents suction")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back: Components", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()
    with col3:
        if st.button("Next: Customization →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 4
            st.rerun()

elif st.session_state.wizard_step == 4:
    # Customization (placeholder for now)
    st.markdown("### 🎨 Step 4: Customization")

    st.info("""
    🚧 **Coming Soon in Phase 2**

    This section will include:
    - Logo/image upload (PNG, SVG)
    - Emboss vs deboss selection
    - Depth control (0.3mm - 1.5mm)
    - Position selector (lid, bottom, walls)
    - Text labels for compartments
    - Font size control
    """)

    # Show angled card well diagram
    with st.expander("💡 What's an angled card well?"):
        show_diagram('angled_card_well', "Tilted compartments for thumbing through cards during play")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back: Layout", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()
    with col3:
        if st.button("Next: Preview →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 5
            st.rerun()

elif st.session_state.wizard_step == 5:
    # Preview & Summary (placeholder for now)
    st.markdown("### 🎯 Step 5: Preview & Summary")

    st.info("""
    🚧 **Coming in Phase 3 & 4**

    This section will include:
    - Full design specification review
    - Edit buttons to jump back to any section
    - OpenSCAD code generation
    - 3D preview rendering
    - AI chat refinement panel
    - Efficiency scoring
    - STL export
    - Print settings guide
    """)

    # Show current configuration summary
    st.markdown("#### 📋 Current Configuration")

    if 'box_config' in st.session_state:
        with st.expander("📦 Box Configuration"):
            box = st.session_state.box_config
            st.json(box)

    if 'components' in st.session_state and st.session_state.components:
        with st.expander(f"🎲 Components ({len(st.session_state.components)})"):
            for comp in st.session_state.components:
                st.markdown(f"**{comp['name']}**: {comp['quantity']}× {comp['type']}")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back: Customization", use_container_width=True):
            st.session_state.wizard_step = 4
            st.rerun()
    with col2:
        if st.button("🔄 Start Over", use_container_width=True):
            # Clear session state
            for key in ['box_config', 'components', 'wizard_step']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    with col3:
        st.button("🚀 Generate Insert (Phase 3)", type="primary", use_container_width=True, disabled=True)

# Sidebar with helpful info
with st.sidebar:
    st.markdown("### 📖 Quick Guide")
    st.markdown("""
    **Current Step:** Step {step}

    **Tips:**
    - Use presets for common components
    - Check box fill percentage
    - Click on "What's this?" expanders to see diagrams

    **Navigation:**
    - Click step buttons to jump around
    - Use Next/Back buttons to proceed
    - Changes are saved automatically
    """.format(step=st.session_state.wizard_step))

    # Show visual explainers reference
    if st.checkbox("Show All Diagrams"):
        st.markdown("---")
        st.markdown("#### 📐 Design Concepts")

        diagrams = [
            ('pedestal_base', 'Pedestal Base'),
            ('finger_cutout', 'Finger Cutout'),
            ('bottom_hole', 'Bottom Hole'),
            ('lid_comparison', 'Lid Types'),
            ('nested_subtrays', 'Nested Sub-Trays'),
            ('angled_card_well', 'Angled Card Well'),
            ('wall_thickness', 'Wall Thickness'),
            ('clearance_zones', 'Clearance Zones'),
        ]

        for concept, name in diagrams:
            with st.expander(name):
                show_diagram(concept)
