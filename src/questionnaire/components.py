"""
Component Inventory - Step 2 of design wizard

Add and manage game components with smart defaults.
"""

import streamlit as st
import json
from pathlib import Path
import uuid


def load_component_standards():
    """Load the component_standards.json data file"""
    data_file = Path(__file__).parent.parent / "data" / "component_standards.json"
    with open(data_file, 'r') as f:
        return json.load(f)


def calculate_component_volume(component):
    """Calculate volume in mm³ for a component"""
    comp_type = component['type']
    quantity = component['quantity']

    if comp_type == 'Cards':
        # Card stack volume
        width = component['width']
        height = component['height']
        thickness = component['thickness_per_card'] * quantity
        return width * height * thickness

    elif comp_type == 'Dice':
        # Dice volume (cube)
        size = component['size']
        return (size ** 3) * quantity

    elif comp_type == 'Tokens':
        # Token volume (cylinder or cuboid)
        if 'diameter' in component:
            # Round token
            radius = component['diameter'] / 2
            volume = 3.14159 * (radius ** 2) * component['thickness']
        else:
            # Square token
            volume = component['width'] * component['height'] * component['thickness']
        return volume * quantity

    elif comp_type == 'Meeples/Minis':
        # Approximate as cuboid
        width = component['width']
        height = component['height']
        depth = component.get('depth', width)  # Default depth = width if not specified
        return width * height * depth * quantity

    elif comp_type == 'Boards':
        # Board volume
        width = component['width']
        height = component['height']
        thickness = component['thickness']
        return width * height * thickness

    elif comp_type == 'Rulebook':
        # Rulebook volume
        width = component['width']
        height = component['height']
        thickness = component['thickness']
        return width * height * thickness

    elif comp_type == 'Custom':
        # Custom component
        return component['length'] * component['width'] * component['height'] * quantity

    return 0


def render_components_inventory():
    """Render the components inventory UI"""

    st.markdown("### 🎲 Step 2: Component Inventory")
    st.markdown("Add all components that need storage in the insert.")

    # Initialize session state
    if 'components' not in st.session_state:
        st.session_state.components = []

    # Load component standards
    standards = load_component_standards()

    # Add component button
    if st.button("➕ Add Component", type="primary"):
        # Create a unique ID for this component
        new_component = {
            'id': str(uuid.uuid4()),
            'type': 'Cards',
            'quantity': 1
        }
        st.session_state.components.append(new_component)
        st.rerun()

    # Display existing components
    if st.session_state.components:
        st.markdown("---")
        st.markdown("#### Current Components")

        components_to_remove = []

        for idx, component in enumerate(st.session_state.components):
            with st.expander(f"**{component.get('name', component['type'])}** ({component['quantity']} × {component['type']})", expanded=(idx == len(st.session_state.components) - 1)):

                col1, col2 = st.columns([3, 1])

                with col1:
                    # Component type selector
                    comp_type = st.selectbox(
                        "Component type:",
                        options=['Cards', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Rulebook', 'Custom'],
                        index=['Cards', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Rulebook', 'Custom'].index(component['type']),
                        key=f"type_{component['id']}"
                    )

                    # Detect type change and clear type-specific fields
                    if component.get('_last_type') != comp_type:
                        # Type changed - clear type-specific fields
                        fields_to_clear = ['width', 'height', 'depth', 'diameter', 'thickness',
                                         'thickness_per_card', 'card_count', 'name', 'length']
                        for field in fields_to_clear:
                            if field in component:
                                del component[field]
                        # Set name to new type default
                        component['name'] = comp_type
                        component['_last_type'] = comp_type

                    component['type'] = comp_type

                with col2:
                    # Quantity
                    component['quantity'] = st.number_input(
                        "Quantity:",
                        min_value=1,
                        max_value=1000,
                        value=component.get('quantity', 1),
                        key=f"qty_{component['id']}"
                    )

                # Component name
                component['name'] = st.text_input(
                    "Name/Description:",
                    value=component.get('name', f"{comp_type}"),
                    key=f"name_{component['id']}",
                    placeholder=f"e.g., Player cards, Resource tokens, Victory points"
                )

                # Type-specific inputs with presets
                if comp_type == 'Cards':
                    card_standards = standards['cards']
                    preset_options = list(card_standards.keys())
                    preset_labels = [f"{card_standards[k]['name']}" for k in preset_options]

                    preset_choice = st.selectbox(
                        "Card preset:",
                        options=['Custom'] + preset_labels,
                        key=f"preset_{component['id']}"
                    )

                    if preset_choice != 'Custom':
                        # Use preset
                        preset_key = preset_options[preset_labels.index(preset_choice)]
                        preset_data = card_standards[preset_key]
                        component['width'] = preset_data['width']
                        component['height'] = preset_data['height']
                        component['thickness_per_card'] = preset_data['thickness_per_card']
                        st.caption(f"💡 {preset_data['notes']}")
                    else:
                        # Custom card dimensions
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            component['width'] = st.number_input("Width (mm):", value=component.get('width', 63.5), step=0.1, format="%.1f", key=f"cw_{component['id']}")
                        with c2:
                            component['height'] = st.number_input("Height (mm):", value=component.get('height', 88.0), step=0.1, format="%.1f", key=f"ch_{component['id']}")
                        with c3:
                            component['thickness_per_card'] = st.number_input("Thickness/card (mm):", value=component.get('thickness_per_card', 0.3), step=0.1, format="%.2f", key=f"ct_{component['id']}")

                elif comp_type == 'Dice':
                    dice_standards = standards['dice']
                    preset_options = list(dice_standards.keys())
                    preset_labels = [f"{dice_standards[k]['name']} ({dice_standards[k]['size']}mm)" for k in preset_options]

                    preset_choice = st.selectbox(
                        "Dice type:",
                        options=['Custom'] + preset_labels,
                        key=f"preset_{component['id']}"
                    )

                    if preset_choice != 'Custom':
                        preset_key = preset_options[preset_labels.index(preset_choice)]
                        preset_data = dice_standards[preset_key]
                        component['size'] = preset_data['size']
                        st.caption(f"💡 {preset_data['notes']}")
                    else:
                        component['size'] = st.number_input("Die size (mm):", value=component.get('size', 16), key=f"ds_{component['id']}")

                elif comp_type == 'Tokens':
                    token_standards = standards['tokens']
                    preset_options = list(token_standards.keys())
                    preset_labels = [f"{token_standards[k]['name']}" for k in preset_options]

                    preset_choice = st.selectbox(
                        "Token preset:",
                        options=['Custom'] + preset_labels,
                        key=f"preset_{component['id']}"
                    )

                    if preset_choice != 'Custom':
                        preset_key = preset_options[preset_labels.index(preset_choice)]
                        preset_data = token_standards[preset_key]

                        if 'diameter' in preset_data:
                            component['diameter'] = preset_data['diameter']
                            component['thickness'] = preset_data['thickness']
                            if 'width' in component:
                                del component['width']
                                del component['height']
                        else:
                            component['width'] = preset_data['width']
                            component['height'] = preset_data['height']
                            component['thickness'] = preset_data['thickness']
                            if 'diameter' in component:
                                del component['diameter']

                        st.caption(f"💡 {preset_data['notes']}")
                    else:
                        # Custom token
                        token_shape = st.radio("Shape:", ['Round', 'Square'], horizontal=True, key=f"shape_{component['id']}")
                        if token_shape == 'Round':
                            component['diameter'] = st.number_input("Diameter (mm):", value=component.get('diameter', 25.0), step=0.1, format="%.1f", key=f"td_{component['id']}")
                            if 'width' in component:
                                del component['width']
                                del component['height']
                        else:
                            c1, c2 = st.columns(2)
                            with c1:
                                component['width'] = st.number_input("Width (mm):", value=component.get('width', 25.0), step=0.1, format="%.1f", key=f"tw_{component['id']}")
                            with c2:
                                component['height'] = st.number_input("Height (mm):", value=component.get('height', 25.0), step=0.1, format="%.1f", key=f"th_{component['id']}")
                            if 'diameter' in component:
                                del component['diameter']

                        component['thickness'] = st.number_input("Thickness (mm):", value=component.get('thickness', 2.0), step=0.1, format="%.1f", key=f"tt_{component['id']}")

                elif comp_type == 'Meeples/Minis':
                    meeple_standards = standards['meeples']
                    preset_options = list(meeple_standards.keys())
                    preset_labels = [f"{meeple_standards[k]['name']}" for k in preset_options]

                    preset_choice = st.selectbox(
                        "Meeple/Mini preset:",
                        options=['Custom'] + preset_labels,
                        key=f"preset_{component['id']}"
                    )

                    if preset_choice != 'Custom':
                        preset_key = preset_options[preset_labels.index(preset_choice)]
                        preset_data = meeple_standards[preset_key]

                        if 'base_diameter' in preset_data:
                            component['width'] = preset_data['base_diameter']
                            component['depth'] = preset_data['base_diameter']
                        else:
                            component['width'] = preset_data['width']
                            component['depth'] = preset_data.get('depth', preset_data['width'])

                        component['height'] = preset_data['height']
                        st.caption(f"💡 {preset_data['notes']}")
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            component['width'] = st.number_input("Width (mm):", value=component.get('width', 14.0), step=0.1, format="%.1f", key=f"mw_{component['id']}")
                        with c2:
                            component['height'] = st.number_input("Height (mm):", value=component.get('height', 16.0), step=0.1, format="%.1f", key=f"mh_{component['id']}")
                        with c3:
                            component['depth'] = st.number_input("Depth (mm):", value=component.get('depth', 8.0), step=0.1, format="%.1f", key=f"md_{component['id']}")

                elif comp_type == 'Boards':
                    board_standards = standards['boards']
                    preset_options = list(board_standards.keys())
                    preset_labels = [f"{board_standards[k]['name']}" for k in preset_options]

                    preset_choice = st.selectbox(
                        "Board preset:",
                        options=['Custom'] + preset_labels,
                        key=f"preset_{component['id']}"
                    )

                    if preset_choice != 'Custom':
                        preset_key = preset_options[preset_labels.index(preset_choice)]
                        preset_data = board_standards[preset_key]
                        component['width'] = preset_data['width']
                        component['height'] = preset_data['height']
                        component['thickness'] = preset_data.get('thickness_folded', preset_data.get('thickness', 2))
                        st.caption(f"💡 {preset_data['notes']}")
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            component['width'] = st.number_input("Width (mm):", value=component.get('width', 200.0), step=0.5, format="%.1f", key=f"bw_{component['id']}")
                        with c2:
                            component['height'] = st.number_input("Height (mm):", value=component.get('height', 150.0), step=0.5, format="%.1f", key=f"bh_{component['id']}")
                        with c3:
                            component['thickness'] = st.number_input("Thickness (mm):", value=component.get('thickness', 2.5), step=0.5, format="%.1f", key=f"bt_{component['id']}")

                elif comp_type == 'Rulebook':
                    rulebook_standards = standards['other']
                    preset_options = [k for k in rulebook_standards.keys() if 'rulebook' in k]
                    preset_labels = [f"{rulebook_standards[k]['name']}" for k in preset_options]

                    preset_choice = st.selectbox(
                        "Rulebook size:",
                        options=['Custom'] + preset_labels,
                        key=f"preset_{component['id']}"
                    )

                    if preset_choice != 'Custom':
                        preset_key = preset_options[preset_labels.index(preset_choice)]
                        preset_data = rulebook_standards[preset_key]
                        component['width'] = preset_data['width']
                        component['height'] = preset_data['height']
                        component['thickness'] = preset_data['thickness']
                        st.caption(f"💡 {preset_data['notes']}")
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            component['width'] = st.number_input("Width (mm):", value=component.get('width', 140.0), step=0.5, format="%.1f", key=f"rw_{component['id']}")
                        with c2:
                            component['height'] = st.number_input("Height (mm):", value=component.get('height', 210.0), step=0.5, format="%.1f", key=f"rh_{component['id']}")
                        with c3:
                            component['thickness'] = st.number_input("Thickness (mm):", value=component.get('thickness', 5.0), step=0.1, format="%.1f", key=f"rt_{component['id']}")

                elif comp_type == 'Custom':
                    st.markdown("**Custom component dimensions:**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        component['length'] = st.number_input("Length (mm):", value=component.get('length', 50.0), step=0.1, format="%.1f", key=f"cl_{component['id']}")
                    with c2:
                        component['width'] = st.number_input("Width (mm):", value=component.get('width', 50.0), step=0.1, format="%.1f", key=f"cw_{component['id']}")
                    with c3:
                        component['height'] = st.number_input("Height (mm):", value=component.get('height', 10.0), step=0.1, format="%.1f", key=f"ch_{component['id']}")

                # Delete button
                if st.button(f"🗑️ Remove", key=f"remove_{component['id']}"):
                    components_to_remove.append(component['id'])

        # Remove marked components
        if components_to_remove:
            st.session_state.components = [c for c in st.session_state.components if c['id'] not in components_to_remove]
            st.rerun()

    # Summary sidebar
    st.markdown("---")
    st.markdown("### 📊 Component Summary")

    if st.session_state.components:
        total_volume = sum(calculate_component_volume(c) for c in st.session_state.components)
        total_volume_cm3 = total_volume / 1000

        # Get box volume for comparison
        if 'box_config' in st.session_state:
            box_config = st.session_state.box_config
            available_height = box_config['height'] - box_config['lid_clearance']
            box_volume_cm3 = (box_config['length'] * box_config['width'] * available_height) / 1000

            percentage = (total_volume_cm3 / box_volume_cm3) * 100

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Components", len(st.session_state.components))
            with col2:
                st.metric("Total Volume", f"{total_volume_cm3:.1f} cm³")
            with col3:
                st.metric("Box Fill", f"{percentage:.1f}%")

            # Warnings
            if percentage > 90:
                st.error("🚨 **Components exceed box capacity!** Remove some components or use a larger box.")
            elif percentage > 70:
                st.warning("⚠️ **Tight fit** - Components use >70% of box volume. Consider clearances and wall thickness.")
            elif percentage < 30:
                st.info("💡 **Lots of space available** - Consider multi-tray stacking or expansion storage.")

        # Component list
        with st.expander("📋 Full Component List"):
            for comp in st.session_state.components:
                volume = calculate_component_volume(comp)
                st.markdown(f"- **{comp['name']}**: {comp['quantity']}× {comp['type']} ({volume/1000:.1f} cm³)")

    else:
        st.info("➕ Click **Add Component** to start building your inventory")

    return st.session_state.components
