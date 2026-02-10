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
    """Calculate volume in mm³ for a component.

    All components use length × width × height (simplified cuboid model).
    For cards, height represents thickness per card and is multiplied by quantity.
    """
    quantity = component.get('quantity', 1)
    length = component.get('length', 0)
    width = component.get('width', 0)
    height = component.get('height', 0)

    # Simple cuboid volume for all types
    volume_per_item = length * width * height

    # Special handling for card stacks (multiply height by quantity)
    if component['type'] == 'Cards':
        # For cards, height represents thickness per card
        total_volume = length * width * (height * quantity)
    else:
        # For all other types, standard volume × quantity
        total_volume = volume_per_item * quantity

    return total_volume


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

                    # Detect type change and clear dimension fields
                    if component.get('_last_type') != comp_type:
                        # Type changed - clear dimension fields
                        fields_to_clear = ['length', 'width', 'height']
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

                # Unified dimension inputs - same for ALL component types
                st.markdown("#### 📏 Dimensions")
                c1, c2, c3 = st.columns(3)
                with c1:
                    component['length'] = st.number_input(
                        "Length (mm):",
                        value=component.get('length', 50.0),
                        step=0.1,
                        format="%.1f",
                        key=f"len_{component['id']}"
                    )
                with c2:
                    component['width'] = st.number_input(
                        "Width (mm):",
                        value=component.get('width', 50.0),
                        step=0.1,
                        format="%.1f",
                        key=f"wid_{component['id']}"
                    )
                with c3:
                    component['height'] = st.number_input(
                        "Height/Thickness (mm):",
                        value=component.get('height', 10.0),
                        step=0.1,
                        format="%.1f",
                        key=f"hgt_{component['id']}"
                    )

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
            available_height = box_config['height']
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
