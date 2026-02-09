"""
Settings - Configure AI provider, nozzle diameter, and printer settings
"""

import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="Settings - Tray Bien",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Settings")

# Settings file path
settings_dir = Path(__file__).parent.parent.parent / "saved_designs"
settings_dir.mkdir(exist_ok=True)
settings_file = settings_dir / ".settings.json"

# Load existing settings
if settings_file.exists():
    with open(settings_file, 'r') as f:
        settings = json.load(f)
else:
    settings = {
        'nozzle_diameter': 0.4,
        'ai_provider': 'none',
        'api_keys': {},
        'printer': {},
        'first_time_setup': True
    }

# Save settings function
def save_settings():
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    st.success("✅ Settings saved successfully!")

# First-time setup banner
if settings.get('first_time_setup', True):
    st.info("""
    👋 **Welcome to Tray Bien!**

    Let's get you set up. The most important setting is your **nozzle diameter** —
    this affects wall thickness calculations. Most printers use 0.4mm nozzles (the standard).
    """)

# ===== PRINTER SETTINGS =====
st.markdown("## 🖨️ Printer Configuration")

with st.expander("Nozzle Diameter", expanded=settings.get('first_time_setup', False)):
    st.markdown("""
    Your nozzle diameter determines wall thickness. Most printers use **0.4mm** (the standard).
    Check your printer's specifications if unsure.
    """)

    nozzle_options = {
        '0.4mm (Standard)': 0.4,
        '0.6mm (Fast prints)': 0.6,
        '0.3mm (Detail)': 0.3,
        '0.2mm (High detail)': 0.2,
        'Custom': None
    }

    nozzle_choice = st.selectbox(
        "Select your nozzle diameter:",
        options=list(nozzle_options.keys()),
        index=0 if settings['nozzle_diameter'] == 0.4 else len(nozzle_options) - 1
    )

    if nozzle_choice == 'Custom':
        nozzle_diameter = st.number_input(
            "Enter custom nozzle diameter (mm):",
            min_value=0.1,
            max_value=2.0,
            value=settings['nozzle_diameter'],
            step=0.1,
            format="%.2f"
        )
    else:
        nozzle_diameter = nozzle_options[nozzle_choice]

    if nozzle_diameter != settings['nozzle_diameter']:
        settings['nozzle_diameter'] = nozzle_diameter
        st.info(f"""
        **Wall thickness calculations:**
        - 2 perimeters: {nozzle_diameter * 2:.1f}mm
        - 3 perimeters: {nozzle_diameter * 3:.1f}mm (default for dividers)
        - 4 perimeters: {nozzle_diameter * 4:.1f}mm (default for outer walls)
        """)

# ===== AI PROVIDER SETTINGS =====
st.markdown("## 🤖 AI Provider Configuration")

st.markdown("""
AI powers the chat refinement panel and layout optimization. Choose a provider below,
or select "None" to use templates only (no AI required).
""")

provider_options = {
    'None (Templates Only)': 'none',
    'Google Gemini (Free tier available)': 'gemini',
    'Anthropic Claude': 'claude',
    'OpenAI': 'openai',
    'Local Ollama': 'ollama'
}

provider_choice = st.selectbox(
    "AI Provider:",
    options=list(provider_options.keys()),
    index=list(provider_options.values()).index(settings.get('ai_provider', 'none'))
)

settings['ai_provider'] = provider_options[provider_choice]

# Provider-specific configuration
if settings['ai_provider'] == 'none':
    st.info("""
    **None mode** uses pre-built templates for common insert patterns.
    No AI calls, no API key needed. Perfect for simple designs!

    To unlock AI chat refinement and layout optimization, configure a provider above.
    """)

elif settings['ai_provider'] == 'gemini':
    with st.expander("Google Gemini Configuration", expanded=True):
        st.markdown("""
        **Free tier available!** Get your API key at: https://ai.google.dev

        The free tier includes generous quotas for personal projects.
        """)

        gemini_key = st.text_input(
            "Gemini API Key:",
            value=settings['api_keys'].get('gemini', ''),
            type='password'
        )
        if gemini_key:
            settings['api_keys']['gemini'] = gemini_key

elif settings['ai_provider'] == 'claude':
    with st.expander("Anthropic Claude Configuration", expanded=True):
        st.markdown("""
        Get your API key at: https://console.anthropic.com

        Recommended for best results in insert design (this app was built with Claude!).
        """)

        claude_key = st.text_input(
            "Claude API Key:",
            value=settings['api_keys'].get('claude', ''),
            type='password'
        )
        if claude_key:
            settings['api_keys']['claude'] = claude_key

elif settings['ai_provider'] == 'openai':
    with st.expander("OpenAI Configuration", expanded=True):
        st.markdown("""
        Get your API key at: https://platform.openai.com

        Uses GPT-4o by default for best reasoning.
        """)

        openai_key = st.text_input(
            "OpenAI API Key:",
            value=settings['api_keys'].get('openai', ''),
            type='password'
        )
        if openai_key:
            settings['api_keys']['openai'] = openai_key

elif settings['ai_provider'] == 'ollama':
    with st.expander("Local Ollama Configuration", expanded=True):
        st.markdown("""
        Ollama runs AI models locally on your machine (free, private, no API key needed).

        Install from: https://ollama.com

        Recommended models: `llama3.1` or `mistral`
        """)

        ollama_url = st.text_input(
            "Ollama URL:",
            value=settings.get('ollama_url', 'http://localhost:11434')
        )
        settings['ollama_url'] = ollama_url

        ollama_model = st.text_input(
            "Model name:",
            value=settings.get('ollama_model', 'llama3.1')
        )
        settings['ollama_model'] = ollama_model

# ===== BAMBU LABS PRINTER INTEGRATION =====
st.markdown("## 🖨️ Bambu Labs Printer Integration (Optional)")

with st.expander("Connect Your Bambu Lab Printer"):
    st.markdown("""
    **Phase 6 feature** — Send STL files directly to your Bambu Lab printer over WiFi.

    Works with: A1, P1S, X1C, and all Bambu models.

    Find your printer's credentials in: Printer Settings → Network → Access Code
    """)

    printer_ip = st.text_input(
        "Printer IP Address:",
        value=settings.get('printer', {}).get('ip', ''),
        placeholder="e.g., 192.168.1.100"
    )

    printer_serial = st.text_input(
        "Printer Serial Number:",
        value=settings.get('printer', {}).get('serial', ''),
        placeholder="e.g., 01S00A123456789"
    )

    printer_access_code = st.text_input(
        "Access Code:",
        value=settings.get('printer', {}).get('access_code', ''),
        type='password',
        placeholder="8-character code from printer"
    )

    if printer_ip and printer_serial and printer_access_code:
        settings['printer'] = {
            'ip': printer_ip,
            'serial': printer_serial,
            'access_code': printer_access_code
        }

        if st.button("🔌 Test Connection"):
            st.info("⏳ Testing connection... (Feature coming in Phase 6)")
            # TODO: Implement actual connection test

# ===== SAVE BUTTON =====
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        settings['first_time_setup'] = False
        save_settings()

with col2:
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        if settings_file.exists():
            settings_file.unlink()
        st.rerun()

with col3:
    st.caption("Settings are saved locally in your project directory")

# ===== CURRENT SETTINGS SUMMARY =====
st.markdown("---")
st.markdown("### 📋 Current Configuration")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.markdown(f"""
    **Printer:**
    - Nozzle: {settings['nozzle_diameter']}mm
    - Connected: {'✅ Yes' if settings.get('printer', {}).get('ip') else '❌ No'}
    """)

with summary_col2:
    st.markdown(f"""
    **AI:**
    - Provider: {settings['ai_provider'].title()}
    - Status: {'✅ Configured' if (settings['ai_provider'] == 'none' or settings['api_keys'].get(settings['ai_provider']) or settings['ai_provider'] == 'ollama') else '⚠️ API key needed'}
    """)
