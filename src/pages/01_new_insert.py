"""
New Insert - Main design wizard page
"""

import streamlit as st

st.set_page_config(
    page_title="New Insert - Tray Bien",
    page_icon="🎲",
    layout="wide",
)

st.title("🎨 New Insert Design")

st.markdown("""
Welcome to the insert design wizard! Follow the steps below to create your custom insert.
""")

# Design wizard progress tracker
st.markdown("### Design Progress")
progress_cols = st.columns(5)
with progress_cols[0]:
    st.button("1️⃣ Box Setup", type="primary", use_container_width=True)
with progress_cols[1]:
    st.button("2️⃣ Components", use_container_width=True)
with progress_cols[2]:
    st.button("3️⃣ Layout", use_container_width=True)
with progress_cols[3]:
    st.button("4️⃣ Customization", use_container_width=True)
with progress_cols[4]:
    st.button("5️⃣ Preview & Export", use_container_width=True)

st.markdown("---")

# Placeholder content for Phase 1
st.info("""
🚧 **Phase 1 - Coming Soon**

This page will contain the interactive design wizard with:
- Box selection (20+ popular games or custom dimensions)
- Component inventory builder
- Layout preference controls
- Logo upload and customization
- Live 3D preview with AI chat refinement

For now, this is a placeholder to verify navigation works.
""")

# Quick test: Initialize session state for future use
if 'design_config' not in st.session_state:
    st.session_state.design_config = {}
    st.success("✅ Session state initialized - ready for design data")

# Sample interaction to test Streamlit functionality
st.markdown("### Test Area")
test_game = st.selectbox(
    "Select a board game (test):",
    ["Catan", "Wingspan", "Ticket to Ride", "Pandemic", "Custom"]
)

if test_game:
    st.write(f"You selected: **{test_game}**")
    st.session_state.design_config['game'] = test_game
