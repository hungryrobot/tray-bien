"""
Component Inventory - Step 2 of design wizard

Add and manage game components with smart defaults.
"""

import streamlit as st
import json
from pathlib import Path
import uuid
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ai.pdf_processor import extract_text_from_pdf
from ai.component_extractor import load_ai_settings, extract_components_with_ai


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

    # PDF upload state
    if 'show_pdf_uploader' not in st.session_state:
        st.session_state.show_pdf_uploader = False
    if 'pdf_components' not in st.session_state:
        st.session_state.pdf_components = []

    # Load component standards
    standards = load_component_standards()

    # Add component buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ Add Component", type="primary"):
            # Create a unique ID for this component
            new_component = {
                'id': str(uuid.uuid4()),
                'type': 'Cards',
                'quantity': 1
            }
            st.session_state.components.append(new_component)
            st.rerun()

    with col2:
        if st.button("📄 Upload Rulebook PDF"):
            st.session_state.show_pdf_uploader = True
            st.rerun()

    # PDF Upload UI (if button clicked)
    if st.session_state.get('show_pdf_uploader', False):
        st.markdown("---")
        st.markdown("### 📄 Extract Components from Rulebook PDF")

        st.info("💡 Upload a board game rulebook to automatically extract the component list. You'll still need to enter dimensions manually.")

        pdf_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_upload")

        if pdf_file is not None:
            # Process PDF
            with st.spinner("Extracting text from PDF..."):
                try:
                    pdf_text = extract_text_from_pdf(pdf_file)
                except Exception as e:
                    st.error(f"❌ Could not extract text from PDF: {str(e)}")
                    st.stop()

            # Check AI configuration
            try:
                ai_settings = load_ai_settings()
            except Exception as e:
                st.error(f"❌ Could not load AI settings: {str(e)}")
                st.stop()

            if ai_settings['provider'] == 'none' or not ai_settings['api_key']:
                st.warning("⚠️ AI provider not configured. Please set up an AI provider in Settings to use PDF upload.")
                if st.button("Go to Settings"):
                    st.switch_page("pages/Settings.py")
                st.stop()

            # Extract components with AI
            with st.spinner("Analyzing component list..."):
                try:
                    components = extract_components_with_ai(
                        pdf_text,
                        ai_settings['provider'],
                        ai_settings['api_key']
                    )
                except Exception as e:
                    st.error(f"❌ AI analysis failed: {str(e)}")
                    if st.button("Try Again"):
                        st.rerun()
                    st.stop()

            # Display extracted components for review
            if not components:
                st.info("ℹ️ No components found in the PDF. The component list may be in a different format.")
            else:
                st.success(f"✅ Found {len(components)} component types!")

                # Editable table
                st.markdown("#### Review & Edit Extracted Components")
                st.caption("Edit names, quantities, or types before adding to inventory. You'll enter dimensions next.")

                # Store in session state for editing
                if 'pdf_components' not in st.session_state or not st.session_state.pdf_components:
                    st.session_state.pdf_components = components

                # Display each component with edit controls
                for idx, comp in enumerate(st.session_state.pdf_components):
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    with col1:
                        comp['name'] = st.text_input(
                            "Name",
                            value=comp['name'],
                            key=f"pdf_name_{idx}",
                            label_visibility="collapsed"
                        )
                    with col2:
                        comp['type'] = st.selectbox(
                            "Type",
                            options=['Cards', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Rulebook', 'Custom'],
                            index=['Cards', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Rulebook', 'Custom'].index(comp['type']),
                            key=f"pdf_type_{idx}",
                            label_visibility="collapsed"
                        )
                    with col3:
                        comp['quantity'] = st.number_input(
                            "Qty",
                            value=comp['quantity'],
                            min_value=1,
                            key=f"pdf_qty_{idx}",
                            label_visibility="collapsed"
                        )
                    with col4:
                        if st.button("🗑️", key=f"pdf_remove_{idx}"):
                            st.session_state.pdf_components.pop(idx)
                            st.rerun()

                # Add all button
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("➕ Add All to Inventory", type="primary"):
                        # Create components with default dimensions
                        num_added = len(st.session_state.pdf_components)
                        for comp in st.session_state.pdf_components:
                            new_component = {
                                'id': str(uuid.uuid4()),
                                'type': comp['type'],
                                'quantity': comp['quantity'],
                                'name': comp['name'],
                                'length': 50.0,  # Default - user will edit
                                'width': 50.0,   # Default - user will edit
                                'height': 10.0,  # Default - user will edit
                                '_last_type': comp['type']
                            }
                            st.session_state.components.append(new_component)

                        # Clear PDF upload state
                        st.session_state.show_pdf_uploader = False
                        st.session_state.pdf_components = []
                        st.success(f"✅ Added {num_added} components! Now enter dimensions for each.")
                        st.rerun()

                with col2:
                    if st.button("Cancel"):
                        st.session_state.show_pdf_uploader = False
                        st.session_state.pdf_components = []
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
