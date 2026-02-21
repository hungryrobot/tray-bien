"""
My Designs - View and manage saved insert configurations
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from storage.design_storage import (
    list_designs,
    load_design,
    delete_design,
    duplicate_design,
    format_timestamp
)

st.set_page_config(
    page_title="My Designs - Tray Bien",
    page_icon="📁",
    layout="wide",
)

st.title("📁 My Designs")

st.markdown("""
View, load, and manage your saved insert configurations. Designs are automatically saved
during the design process and can be loaded to continue editing.
""")

# Get list of saved designs using the new utility
try:
    designs = list_designs()
except Exception as e:
    st.error(f"Error loading designs: {str(e)}")
    designs = []

if not designs:
    st.info("""
    📂 **No saved designs yet**

    Once you create and save an insert design, it will appear here.
    Start by visiting the **New Insert** page to create your first design!
    """)
else:
    st.success(f"Found {len(designs)} saved design(s)")

    # Display saved designs
    for design_meta in designs:
        with st.expander(f"📦 {design_meta['name']} — {design_meta['box']} — {design_meta['component_count']} components"):
            try:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.caption(f"**Modified:** {format_timestamp(design_meta['modified_at'])}")
                    st.caption(f"**Box:** {design_meta['box']}")
                    st.caption(f"**Components:** {design_meta['component_count']}")

                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)

                with btn_col1:
                    if st.button("📂 Load Design", key=f"load_{design_meta['filename']}", use_container_width=True):
                        # Load design and populate session state
                        design_data = load_design(design_meta['filename'])

                        # Populate all session state keys
                        st.session_state.box_config = design_data.get('box_config', {})
                        st.session_state.components = design_data.get('components', [])
                        st.session_state.design_name = design_data['metadata']['name']
                        st.session_state.created_at = design_data['metadata']['created_at']

                        # Populate layout preferences
                        layout = design_data.get('layout_preferences', {})
                        st.session_state.layout_storage_orientation = layout.get('storage_orientation', 'vertical')
                        st.session_state.layout_tray_config = layout.get('tray_config', 'multi')
                        st.session_state.layout_tray_count = layout.get('tray_count', 2)
                        st.session_state.layout_per_tray_lids = layout.get('per_tray_lids', {})
                        st.session_state.layout_finger_cutouts_enabled = layout.get('finger_cutouts_enabled', True)
                        st.session_state.layout_finger_cutout_size_pct = layout.get('finger_cutout_size_pct', 60)
                        st.session_state.layout_corner_style = layout.get('corner_style', 'rounded')
                        st.session_state.layout_corner_radius_mm = layout.get('corner_radius_mm', 2.0)
                        st.session_state.layout_labels_enabled = layout.get('labels_enabled', True)

                        # Navigate to Step 2 (Component Inventory)
                        st.session_state.wizard_step = 2
                        st.switch_page("pages/New_Insert.py")

                with btn_col2:
                    if st.button("📋 Duplicate", key=f"dup_{design_meta['filename']}", use_container_width=True):
                        new_name = f"{design_meta['name']} (Copy)"
                        try:
                            duplicate_design(design_meta['filename'], new_name)
                            st.success(f"✅ Duplicated as '{new_name}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to duplicate: {str(e)}")

                with btn_col3:
                    if st.button("🗑️ Delete", key=f"del_{design_meta['filename']}", use_container_width=True):
                        if delete_design(design_meta['filename']):
                            st.success("✅ Design deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete design")

                # Show design details
                with st.expander("View JSON"):
                    design_full = load_design(design_meta['filename'])
                    st.json(design_full)

            except Exception as e:
                st.error(f"Error loading design: {str(e)}")

# Upload design from file
st.markdown("---")
st.markdown("### 📤 Import Design")

uploaded_file = st.file_uploader(
    "Upload a saved design configuration (JSON)",
    type=['json'],
    help="Upload a previously exported design configuration to continue editing"
)

if uploaded_file:
    try:
        import json
        design_data = json.load(uploaded_file)

        # Optionally save to saved_designs folder
        if st.button("💾 Save to My Designs"):
            from storage.design_storage import save_design
            filename = save_design(design_data)
            st.success(f"✅ Saved as '{design_data['metadata']['name']}'")
            st.rerun()

        # Show preview
        st.json(design_data)

    except Exception as e:
        st.error(f"❌ Error importing design: {str(e)}")
