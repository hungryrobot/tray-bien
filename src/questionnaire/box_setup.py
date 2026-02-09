"""
Box Setup - Step 1 of design wizard

Select known game box or enter custom dimensions.
"""

import streamlit as st
import json
from pathlib import Path


def load_common_boxes():
    """Load the common_boxes.json data file"""
    data_file = Path(__file__).parent.parent / "data" / "common_boxes.json"
    with open(data_file, 'r') as f:
        data = json.load(f)
    return data['boxes']


def render_box_setup():
    """Render the box setup UI"""

    st.markdown("### 📦 Step 1: Box Setup")
    st.markdown("Choose a known board game box or enter custom dimensions.")

    # Initialize session state
    if 'box_config' not in st.session_state:
        st.session_state.box_config = {
            'source': 'known',  # 'known' or 'custom'
            'game_name': None,
            'length': 296,
            'width': 296,
            'height': 71,
            'lid_clearance': 3
        }

    config = st.session_state.box_config

    # Box source selection
    col1, col2 = st.columns([1, 1])

    with col1:
        source = st.radio(
            "Box dimensions:",
            options=['known', 'custom'],
            format_func=lambda x: "📚 Known Game" if x == 'known' else "📏 Custom Dimensions",
            index=0 if config['source'] == 'known' else 1,
            horizontal=True
        )
        config['source'] = source

    # Load known boxes
    common_boxes = load_common_boxes()
    box_names = list(common_boxes.keys())
    box_options = [f"{name} ({common_boxes[name]['dimensions']['length']}×{common_boxes[name]['dimensions']['width']}×{common_boxes[name]['dimensions']['height']}mm)"
                   for name in box_names]

    if source == 'known':
        # Searchable dropdown for known games
        selected_option = st.selectbox(
            "Select game:",
            options=box_options,
            index=box_options.index(next((opt for opt in box_options if config['game_name'] and config['game_name'] in opt), box_options[0])) if config['game_name'] else 0,
            help="Choose from 20+ popular board games with pre-measured dimensions"
        )

        # Extract game name from selection
        selected_name = selected_option.split(' (')[0]
        config['game_name'] = selected_name

        # Update dimensions from selected game
        box_data = common_boxes[selected_name]
        config['length'] = box_data['dimensions']['length']
        config['width'] = box_data['dimensions']['width']
        config['height'] = box_data['dimensions']['height']

        # Show notes if available
        if 'notes' in box_data:
            st.info(f"💡 **{selected_name}:** {box_data['notes']}")

    else:
        # Custom dimensions input
        config['game_name'] = st.text_input(
            "Game name (optional):",
            value=config.get('game_name', '') if config.get('game_name') not in common_boxes else '',
            placeholder="My Custom Game"
        )

        st.markdown("**Interior box dimensions** (measure with calipers):")

        dim_col1, dim_col2, dim_col3 = st.columns(3)

        with dim_col1:
            config['length'] = st.number_input(
                "Length (mm):",
                min_value=50,
                max_value=500,
                value=config['length'],
                step=1,
                help="Longest interior dimension"
            )

        with dim_col2:
            config['width'] = st.number_input(
                "Width (mm):",
                min_value=50,
                max_value=500,
                value=config['width'],
                step=1,
                help="Shorter interior dimension"
            )

        with dim_col3:
            config['height'] = st.number_input(
                "Height (mm):",
                min_value=20,
                max_value=200,
                value=config['height'],
                step=1,
                help="Interior depth of box"
            )

        st.caption("💡 **Tip:** Measure the INNER dimensions of your box, not the outer. Subtract ~2mm per side from outer dimensions for cardboard thickness.")

    # Lid clearance slider
    st.markdown("---")
    st.markdown("#### 🎩 Lid Clearance")
    st.markdown("""
How much vertical space does the box lid need when closed?

**Typical values:** 3-5mm for most games | **Tight fit:** 2mm | **Deep lid:** 6-10mm
""")

    config['lid_clearance'] = st.slider(
        "Lid clearance (mm):",
        min_value=0,
        max_value=15,
        value=config['lid_clearance'],
        step=1,
        help="Space between top of insert and box lid. Accounts for lid thickness and cardboard compression. Typical: 3-5mm"
    )

    # Calculate available volume
    st.markdown("---")
    st.markdown("#### 📊 Available Interior Volume")

    available_height = config['height'] - config['lid_clearance']
    available_volume_cm3 = (config['length'] * config['width'] * available_height) / 1000

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Length", f"{config['length']} mm")
    with col2:
        st.metric("Width", f"{config['width']} mm")
    with col3:
        st.metric("Available Height", f"{available_height} mm")
    with col4:
        st.metric("Volume", f"{available_volume_cm3:.1f} cm³")

    # Visual box diagram
    st.markdown("---")
    st.markdown("#### 📐 Box Outline")

    # Generate simple SVG box diagram
    svg_scale = 0.5  # Scale down for display
    svg_width = config['length'] * svg_scale
    svg_height = config['width'] * svg_scale

    # Limit SVG size for display
    max_svg_size = 300
    if svg_width > max_svg_size or svg_height > max_svg_size:
        scale_factor = max_svg_size / max(svg_width, svg_height)
        svg_width *= scale_factor
        svg_height *= scale_factor

    box_svg = f"""
    <svg width="{svg_width + 40}" height="{svg_height + 60}" xmlns="http://www.w3.org/2000/svg">
        <!-- Box outline -->
        <rect x="20" y="20" width="{svg_width}" height="{svg_height}"
              fill="#f0f0f0" stroke="#333" stroke-width="2"/>

        <!-- Dimensions -->
        <text x="{svg_width/2 + 20}" y="15" font-size="12" fill="#666" text-anchor="middle">
            {config['length']} mm
        </text>
        <text x="10" y="{svg_height/2 + 20}" font-size="12" fill="#666" text-anchor="middle"
              transform="rotate(-90, 10, {svg_height/2 + 20})">
            {config['width']} mm
        </text>

        <!-- Height indicator -->
        <text x="{svg_width + 25}" y="{svg_height/2 + 20}" font-size="11" fill="#999">
            ↕ {available_height}mm
        </text>
        <text x="{svg_width + 25}" y="{svg_height/2 + 35}" font-size="9" fill="#999">
            available
        </text>
    </svg>
    """

    st.markdown(box_svg.strip(), unsafe_allow_html=True)

    # Validation warnings
    if available_height < 30:
        st.warning("⚠️ Very shallow box - limited space for components. Consider reducing lid clearance if possible.")

    if config['length'] * config['width'] > 400 * 400:
        st.info("💡 Large box footprint - consider multi-tray stacking to fill vertical space efficiently.")

    return config
