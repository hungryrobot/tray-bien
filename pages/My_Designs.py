"""
My Designs - View and manage saved insert configurations
"""

import streamlit as st
from pathlib import Path
import json

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

# Path to saved designs
saved_designs_dir = Path(__file__).parent.parent.parent / "saved_designs"
saved_designs_dir.mkdir(exist_ok=True)

# Check for existing designs
design_files = list(saved_designs_dir.glob("*.json"))

if not design_files:
    st.info("""
    📂 **No saved designs yet**

    Once you create and save an insert design, it will appear here.
    Start by visiting the **New Insert** page to create your first design!
    """)
else:
    st.success(f"Found {len(design_files)} saved design(s)")

    # Display saved designs
    for design_file in design_files:
        with st.expander(f"📄 {design_file.stem}"):
            try:
                with open(design_file, 'r') as f:
                    design_data = json.load(f)

                # Display design summary
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Game:** {design_data.get('game', 'Unknown')}")
                    st.markdown(f"**Components:** {len(design_data.get('components', []))}")
                    st.markdown(f"**Created:** {design_data.get('created_at', 'Unknown')}")

                with col2:
                    if st.button(f"Load Design", key=f"load_{design_file.stem}"):
                        st.session_state.design_config = design_data
                        st.success("✅ Design loaded! Go to New Insert to continue editing.")

                    if st.button(f"Delete", key=f"delete_{design_file.stem}"):
                        design_file.unlink()
                        st.rerun()

                # Show full JSON (collapsed)
                with st.expander("View JSON"):
                    st.json(design_data)

            except Exception as e:
                st.error(f"Error loading design: {e}")

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
        design_data = json.load(uploaded_file)
        st.session_state.design_config = design_data
        st.success("✅ Design imported successfully! Go to New Insert to view.")

        # Optionally save to saved_designs folder
        if st.button("Save to My Designs"):
            save_path = saved_designs_dir / uploaded_file.name
            with open(save_path, 'w') as f:
                json.dump(design_data, f, indent=2)
            st.success(f"Saved to {save_path.name}")
            st.rerun()

    except Exception as e:
        st.error(f"Error importing design: {e}")
