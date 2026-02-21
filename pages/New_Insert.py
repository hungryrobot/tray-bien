"""
New Insert — Main design wizard page

Four steps:
  1 — Box & Components  (box dims + component inventory + PDF extraction)
  2 — Sort & Plan       (tray structure, stack ordering)
  3 — Layout Editor     (orientation, tray config, features, finishing)
  4 — Preview & Export  (summary, configuration review, export)
"""

import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from questionnaire.box_setup import render_box_section
from questionnaire.components import render_components_inventory
from questionnaire.tray_structure import render_tray_structure
from ui.visual_explainers import show_diagram
from ui.styles import inject_custom_css
from storage.design_storage import save_design, clean_component_data
import uuid

st.set_page_config(
    page_title="New Insert — Tray Bien",
    page_icon="🎲",
    layout="wide",
)

inject_custom_css()

# Hide sidebar on this page (other pages keep their own sidebar)
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="stSidebarCollapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Wizard state ───────────────────────────────────────────────────────────────

if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1

# Migration: old float step values → new integer mapping
_step_migration = {2.5: 2, 3.0: 3, 4.0: 4, 5.0: 4}
if st.session_state.wizard_step in _step_migration:
    st.session_state.wizard_step = _step_migration[st.session_state.wizard_step]

# ── Step bar ───────────────────────────────────────────────────────────────────

st.title("New Insert Design Wizard")

steps = [
    ("Box & Components", 1),
    ("Sort & Plan", 2),
    ("Layout Editor", 3),
    ("Preview & Export", 4),
]

progress_cols = st.columns(4)
for i, (label, step_num) in enumerate(steps):
    with progress_cols[i]:
        button_type = "primary" if st.session_state.wizard_step == step_num else "secondary"
        if st.button(label, key=f"step_{step_num}", use_container_width=True, type=button_type):
            st.session_state.wizard_step = step_num
            st.rerun()

st.divider()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_nozzle_from_settings():
    settings_file = Path(__file__).parent.parent / "saved_designs" / ".settings.json"
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
            return settings.get('nozzle_diameter', 0.4)
    return 0.4


# ── Step 1: Box & Components ──────────────────────────────────────────────────

if st.session_state.wizard_step == 1:
    render_box_section()
    render_components_inventory()

    st.divider()
    col1, _, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("Next: Sort & Plan →", type="primary", use_container_width=True):
            if not st.session_state.get('components'):
                st.error("Please add at least one component before continuing.")
            else:
                st.session_state.wizard_step = 2
                st.rerun()


# ── Step 2: Sort & Plan ───────────────────────────────────────────────────────

elif st.session_state.wizard_step == 2:
    render_tray_structure()


# ── Step 3: Layout Editor ─────────────────────────────────────────────────────

elif st.session_state.wizard_step == 3:
    st.subheader("Layout Editor")

    # Initialize substep tracking
    if 'layout_substep' not in st.session_state:
        st.session_state.layout_substep = 1

    # Initialize layout preferences
    _layout_defaults = {
        'layout_storage_orientation': 'vertical',
        'layout_tray_config': 'multi',
        'layout_tray_count': 2,
        'layout_per_tray_lids': {},
        'layout_per_tray_finger_cutouts': {},
        'layout_corner_style': 'rounded',
        'layout_corner_radius_mm': 2.0,
        'layout_per_tray_corner_radius': {},
        'layout_labels_enabled': True,
    }
    for key, default in _layout_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Substep pills
    pill_col1, pill_col2, pill_col3 = st.columns(3)
    with pill_col1:
        if st.button(
            "3.1 Storage & Structure",
            type="primary" if st.session_state.layout_substep == 1 else "secondary",
            use_container_width=True, key="pill_31",
        ):
            st.session_state.layout_substep = 1
            st.rerun()
    with pill_col2:
        if st.button(
            "3.2 Tray Features",
            type="primary" if st.session_state.layout_substep == 2 else "secondary",
            use_container_width=True, key="pill_32",
        ):
            st.session_state.layout_substep = 2
            st.rerun()
    with pill_col3:
        if st.button(
            "3.3 Finishing Touches",
            type="primary" if st.session_state.layout_substep == 3 else "secondary",
            use_container_width=True, key="pill_33",
        ):
            st.session_state.layout_substep = 3
            st.rerun()

    st.divider()

    # ── Substep 3.1: Storage & Tray Structure
    if st.session_state.layout_substep == 1:
        st.subheader("Storage & Tray Structure")

        st.caption("Games are typically stored vertically on shelves. Inserts must work when the box is on its side.")

        _orientation_map = {'vertical': 0, 'horizontal': 1, 'both': 2}
        orientation_index = _orientation_map.get(st.session_state.layout_storage_orientation, 0)

        orientation = st.radio(
            "How will this game be stored?",
            options=[
                'Vertical storage (books on shelf)',
                'Horizontal storage (stack flat)',
                'Both orientations (design for worst case)',
            ],
            index=orientation_index,
            key='orientation_radio',
        )

        if orientation.startswith('Vertical'):
            st.session_state.layout_storage_orientation = 'vertical'
        elif orientation.startswith('Horizontal'):
            st.session_state.layout_storage_orientation = 'horizontal'
        else:
            st.session_state.layout_storage_orientation = 'both'

        st.caption("Designing for vertical storage ensures the insert works in both orientations.")

        st.divider()

        st.subheader("Tray Configuration")

        if st.session_state.get('tray_structure_accepted', False):
            analysis = st.session_state.tray_analysis
            st.write(f"Based on your components: {len(analysis['suggested_trays'])} tray types suggested.")
            st.session_state.layout_tray_count = analysis['suggested_layer_count']
            st.write(f"Recommended layers: {analysis['suggested_layer_count']}")
        else:
            st.caption("Multi-tray stacking fills box height and maximises storage efficiency.")

            config_index = 1 if st.session_state.layout_tray_config == 'multi' else 0
            tray_config = st.radio(
                "Tray configuration",
                options=['Single tray (one piece)', 'Stacking multi-tray (2–4 layers)'],
                index=config_index,
                key='tray_config_radio',
            )
            st.session_state.layout_tray_config = 'multi' if tray_config.startswith('Stacking') else 'single'

            if st.session_state.layout_tray_config == 'multi':
                st.session_state.layout_tray_count = st.slider(
                    "Number of tray layers",
                    min_value=2, max_value=4,
                    value=st.session_state.layout_tray_count,
                    key='tray_count_slider',
                )
            else:
                st.session_state.layout_tray_count = 1

    # ── Substep 3.2: Tray Features
    elif st.session_state.layout_substep == 2:
        st.subheader("Tray Features")

        tray_count = st.session_state.layout_tray_count

        st.write("Lid recommendations (top to bottom):")

        for tray_idx in reversed(range(tray_count)):
            position = "Top" if tray_idx == tray_count - 1 else "Middle" if tray_idx > 0 else "Bottom"
            is_top = (tray_idx == tray_count - 1)
            recommended = is_top
            reason = (
                "Top tray — no board covering it" if is_top
                else f"Tray {tray_idx + 2} sits on top and covers this"
            )

            if tray_idx not in st.session_state.layout_per_tray_lids:
                st.session_state.layout_per_tray_lids[tray_idx] = recommended

            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Tray {tray_idx + 1} ({position}):** {reason}")
                with col2:
                    lid_enabled = st.checkbox(
                        "Add lid",
                        value=st.session_state.layout_per_tray_lids[tray_idx],
                        key=f"lid_checkbox_{tray_idx}",
                    )
                    st.session_state.layout_per_tray_lids[tray_idx] = lid_enabled

        st.divider()
        st.subheader("Finger Cutouts")

        with st.expander("What's a finger cutout?"):
            show_diagram('finger_cutout_enhanced', "Cross-section showing scooped wall for easy component access")

        for tray_idx in range(tray_count):
            st.write(f"**Tray {tray_idx + 1}:**")

            if tray_idx not in st.session_state.layout_per_tray_finger_cutouts:
                st.session_state.layout_per_tray_finger_cutouts[tray_idx] = {
                    'enabled': True, 'style': 'Front/Back',
                }

            cutouts_enabled = st.checkbox(
                "Enable finger cutouts",
                value=st.session_state.layout_per_tray_finger_cutouts[tray_idx]['enabled'],
                key=f"cutouts_{tray_idx}",
            )

            if cutouts_enabled:
                cutout_style = st.radio(
                    "Cutout style",
                    options=['Front/Back', 'All sides', 'Front only'],
                    index=['Front/Back', 'All sides', 'Front only'].index(
                        st.session_state.layout_per_tray_finger_cutouts[tray_idx].get('style', 'Front/Back')
                    ),
                    key=f"cutout_style_{tray_idx}",
                    horizontal=True,
                )
                st.session_state.layout_per_tray_finger_cutouts[tray_idx] = {
                    'enabled': True, 'style': cutout_style,
                }
            else:
                st.session_state.layout_per_tray_finger_cutouts[tray_idx] = {
                    'enabled': False, 'style': 'Front/Back',
                }

    # ── Substep 3.3: Finishing Touches
    elif st.session_state.layout_substep == 3:
        st.subheader("Finishing Touches")

        nozzle = _load_nozzle_from_settings()
        outer_walls = nozzle * 4
        inner_dividers = nozzle * 3

        st.write(f"Wall thickness — outer: {outer_walls:.1f}mm (4 perimeters), inner dividers: {inner_dividers:.1f}mm (3 perimeters)")
        st.caption("Based on your nozzle diameter configured in Settings.",)

        with st.expander("How wall thickness works"):
            show_diagram('wall_thickness_enhanced', "Cross-section showing perimeter layers")

        st.divider()
        st.subheader("Corner Style")

        with st.expander("Sharp vs rounded corners"):
            show_diagram('corner_styles', "Visual comparison of corner types")

        style_index = 1 if st.session_state.layout_corner_style == 'rounded' else 0
        corner_style = st.radio(
            "Corner style",
            options=['Sharp corners', 'Rounded corners'],
            index=style_index,
            key='corner_style_radio',
        )
        st.session_state.layout_corner_style = 'rounded' if corner_style.startswith('Rounded') else 'sharp'

        if st.session_state.layout_corner_style == 'rounded':
            st.session_state.layout_corner_radius_mm = st.slider(
                "Corner radius (mm)",
                min_value=1.0, max_value=5.0,
                value=st.session_state.layout_corner_radius_mm,
                step=0.5,
                key='corner_radius_slider',
                help="2–3mm is the recommended sweet spot — strong without wasting compartment space",
            )

        st.divider()
        st.subheader("Compartment Labels")

        st.session_state.layout_labels_enabled = st.toggle(
            "Enable compartment labels",
            value=st.session_state.layout_labels_enabled,
            key='labels_toggle',
            help="Embossed text labels for each compartment. Customise text and placement in Preview & Export.",
        )

    # ── Layout step navigation
    st.divider()
    col1, _, col3 = st.columns(3)
    with col1:
        if st.session_state.layout_substep > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.layout_substep -= 1
                st.rerun()
        else:
            if st.button("← Back: Sort & Plan", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
    with col3:
        if st.session_state.layout_substep < 3:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.layout_substep += 1
                st.rerun()
        else:
            if st.button("Next: Preview & Export →", type="primary", use_container_width=True):
                st.session_state.wizard_step = 4
                st.rerun()


# ── Step 4: Preview & Export ──────────────────────────────────────────────────

elif st.session_state.wizard_step == 4:
    st.subheader("Preview & Export")

    st.write("""
    Coming in Phase 3 & 4 — full design specification review, OpenSCAD generation,
    3D preview, AI refinement, STL export, and print settings guide.
    """)

    # Current configuration summary
    st.subheader("Current configuration")

    if 'box_config' in st.session_state:
        with st.expander("Box configuration"):
            box = st.session_state.box_config
            st.json(box)

    if st.session_state.get('components'):
        with st.expander(f"Components ({len(st.session_state.components)})"):
            for comp in st.session_state.components:
                st.write(f"**{comp['name']}**: {comp['quantity']}x {comp['type']}")

    if st.session_state.get('tray_structure'):
        with st.expander("Tray structure"):
            ts = st.session_state.tray_structure
            for tray in ts.get('trays', []):
                n_comps = len(tray.get('components', []))
                st.write(f"**{tray['name']}** ({tray['tray_type']}) — {n_comps} components")

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back: Layout Editor", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()
    with col2:
        if st.button("Start over", use_container_width=True):
            for key in ['box_config', 'components', 'wizard_step', 'tray_structure',
                        'quick_defaults', 'quick_defaults_done', 'pdf_extraction_result',
                        'last_extracted_pdf_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    with col3:
        st.button("Generate Insert (coming soon)", type="primary",
                  use_container_width=True, disabled=True)
