"""
Box dimensions — compact inline section merged into Step 1 (Box & Components).

Provides render_box_section() which renders a single compact row:
  Design name | Length | Width | Height | Save

The old render_box_setup() measuring guide, SVG diagram, and volume metrics
have been removed. Dimension inputs use help= tooltips instead.

load_common_boxes() is preserved for future preset support.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timezone


def load_common_boxes():
    """Load the common_boxes.json data file (reserved for future preset support)."""
    data_file = Path(__file__).parent.parent / "data" / "common_boxes.json"
    with open(data_file, 'r') as f:
        data = json.load(f)
    return data['boxes']


def _save_design():
    """Save callback — reads current session state and writes to storage."""
    from storage.design_storage import save_design

    design_name = st.session_state.get('design_name', '')
    config = st.session_state.get('box_config', {})

    design_data = {
        'metadata': {
            'name': design_name,
            'created_at': st.session_state.get(
                'created_at',
                datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            ),
            'modified_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'version': 1,
        },
        'box_config': config,
        'components': st.session_state.get('components', []),
        'tray_analysis': st.session_state.get('tray_analysis', None),
        'tray_structure_accepted': st.session_state.get('tray_structure_accepted', False),
        'layout_preferences': {
            'storage_orientation': st.session_state.get('layout_storage_orientation', 'vertical'),
            'tray_config': st.session_state.get('layout_tray_config', 'multi'),
            'tray_count': st.session_state.get('layout_tray_count', 2),
            'per_tray_lids': st.session_state.get('layout_per_tray_lids', {}),
            'per_tray_finger_cutouts': st.session_state.get('layout_per_tray_finger_cutouts', {}),
            'corner_style': st.session_state.get('layout_corner_style', 'rounded'),
            'corner_radius_mm': st.session_state.get('layout_corner_radius_mm', 2.0),
            'per_tray_corner_radius': st.session_state.get('layout_per_tray_corner_radius', {}),
            'labels_enabled': st.session_state.get('layout_labels_enabled', True),
        },
    }

    try:
        filename = save_design(design_data)
        if 'created_at' not in st.session_state:
            st.session_state.created_at = design_data['metadata']['created_at']
        st.session_state._save_success = True
        st.session_state._save_error = None
    except Exception as e:
        st.session_state._save_success = False
        st.session_state._save_error = str(e)


def render_box_section():
    """Compact box dimensions row — merged into Step 1 (Box & Components).

    Renders: Design name | Length | Width | Height | Save button
    All on one row. Volume shown as a caption below.
    """
    # Initialize box_config if missing
    if 'box_config' not in st.session_state:
        st.session_state.box_config = {
            'source': 'custom',
            'game_name': None,
            'length': 296,
            'width': 296,
            'height': 71,
        }
    config = st.session_state.box_config

    st.subheader("Box dimensions")

    name_col, l_col, w_col, h_col, save_col = st.columns([3, 1, 1, 1, 1])

    with name_col:
        design_name = st.text_input(
            "Design name",
            value=st.session_state.get('design_name', config.get('game_name', '')),
            key="design_name_input",
            placeholder="e.g., Wingspan Insert",
            help="Name for this insert design",
        )
        # Keep session state and config in sync
        if design_name:
            st.session_state.design_name = design_name
            config['game_name'] = design_name

    with l_col:
        config['length'] = st.number_input(
            "Length (mm)",
            min_value=50,
            max_value=500,
            value=config['length'],
            step=1,
            help="Interior length — measure inside the box walls at the base, not the outside",
        )

    with w_col:
        config['width'] = st.number_input(
            "Width (mm)",
            min_value=50,
            max_value=500,
            value=config['width'],
            step=1,
            help="Interior width — measure inside the box walls at the base, perpendicular to length",
        )

    with h_col:
        config['height'] = st.number_input(
            "Height (mm)",
            min_value=20,
            max_value=200,
            value=config['height'],
            step=1,
            help="Interior depth — from inside the bottom to where the lid sits. Do not include lid height.",
        )

    with save_col:
        # Align button with the number inputs
        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
        st.button(
            "Save",
            on_click=_save_design,
            disabled=not design_name,
            use_container_width=True,
        )

    # Show save result from previous click (on_click runs before rerender)
    if st.session_state.get('_save_success'):
        st.success(f"Saved as '{design_name}'")
        st.session_state._save_success = False
    elif st.session_state.get('_save_error'):
        st.error(f"Save failed: {st.session_state._save_error}")
        st.session_state._save_error = None

    # Volume caption
    vol_cm3 = config['length'] * config['width'] * config['height'] / 1000
    st.caption(
        f"Interior: {config['length']} × {config['width']} × {config['height']} mm "
        f"— {vol_cm3:.0f} cm³"
    )

    st.divider()

    return config
