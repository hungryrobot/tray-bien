"""
CSS overrides for Tray Bien.

All st.markdown(unsafe_allow_html=True) CSS injections live here.
Call inject_custom_css() once at the top of each page.
"""

import streamlit as st


def inject_custom_css():
    """Inject all custom CSS overrides. Call once per page load."""
    st.markdown("""
    <style>
    /* Step bar buttons: allow labels to wrap rather than truncate */
    [data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
        font-size: 0.78rem;
        white-space: normal;
        word-break: break-word;
        height: auto;
        min-height: 2.5rem;
        line-height: 1.2;
    }

    /* Reduce top padding on the main content area */
    .main .block-container {
        padding-top: 1.5rem;
    }

    /* Tighter vertical gaps between block elements */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.25rem;
    }

    /* Even tighter spacing inside expanders */
    [data-testid="stExpander"] div[data-testid="stVerticalBlock"] > div {
        gap: 0.1rem;
    }

    /* Reduce h3 (st.subheader) bottom margin */
    h3 { margin-bottom: 0.2rem; }

    /* Compact form elements — remove extra bottom margin */
    .stNumberInput, .stSelectbox, .stTextInput { margin-bottom: 0; }

    /* Thinner horizontal rules */
    hr { margin-top: 0.4rem; margin-bottom: 0.4rem; }
    </style>
    """, unsafe_allow_html=True)
