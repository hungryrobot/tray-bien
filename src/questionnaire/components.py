"""
Component Inventory - Step 2 of design wizard

Add and manage game components with smart defaults.
"""

import streamlit as st
import json
from pathlib import Path
import uuid
import sys
import re
from typing import Dict, List, Set, Tuple, Optional

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ai.pdf_processor import extract_text_from_pdf
from ai.component_extractor import load_ai_settings, extract_components_with_ai, extract_expansion_with_ai


def load_component_standards():
    """Load the component_standards.json data file"""
    data_file = Path(__file__).parent.parent / "data" / "component_standards.json"
    with open(data_file, 'r') as f:
        return json.load(f)


def load_material_standards():
    """Load the material_standards.json data file"""
    data_file = Path(__file__).parent.parent / "data" / "material_standards.json"
    with open(data_file, 'r') as f:
        return json.load(f)


def calculate_component_volume(component):
    """Calculate volume in mm³ for a component, including material clearances.

    All components use length × width × height (simplified cuboid model).
    For cards, height represents thickness per card and is multiplied by quantity.
    Material-based clearances are applied to horizontal dimensions.
    """
    quantity = component.get('quantity', 1)
    length = component.get('length', 0)
    width = component.get('width', 0)
    height = component.get('height', 0)

    # Apply material-based clearances to horizontal dimensions
    material_category = component.get('material_category')
    material = component.get('material')

    clearance = 0
    if material_category and material:
        try:
            material_standards = load_material_standards()
            clearance = material_standards.get(material_category, {}).get(material, {}).get('clearance_mm', 0)
        except:
            clearance = 0

    # Apply clearance to horizontal dimensions
    length_with_clearance = length + clearance
    width_with_clearance = width + clearance

    # Special handling for card stacks (multiply height by quantity)
    if component['type'] == 'Cards':
        # For cards, use calculated per-card thickness if available
        per_card_thickness = component.get('calculated_per_card') or height
        total_volume = length_with_clearance * width_with_clearance * (per_card_thickness * quantity)
    else:
        # For all other types, standard volume × quantity
        volume_per_item = length_with_clearance * width_with_clearance * height
        total_volume = volume_per_item * quantity

    return total_volume


def get_component_breakdown(component):
    """Generate detailed breakdown text for components.

    Analyzes component name for value denominations, colors, or quantity patterns.
    Returns human-readable breakdown like "32× 1-value, 16× 5-value" or None.

    Args:
        component: Component dict with 'name' and 'type' fields

    Returns:
        str or None: Breakdown text if patterns detected, None otherwise
    """
    name_lower = component.get('name', '').lower()

    # Pattern: "32× 1-value, 16× 5-value" or "32 one-value, 16 five-value"
    value_pattern = r'(\d+)\s*(?:×|x)?\s*(\d+)[-\s]*(?:value|point|vp|coin|gold)'
    matches = re.findall(value_pattern, name_lower)

    if matches:
        parts = []
        for qty, value in matches:
            parts.append(f"{qty}× {value}-value")
        return ", ".join(parts)

    # Pattern: Color breakdown "11 red, 11 blue, 11 green"
    color_pattern = r'(\d+)\s+(red|blue|green|yellow|purple|orange|white|black|pink|cyan|brown|teal|magenta|indigo|gray|grey)'
    color_matches = re.findall(color_pattern, name_lower)

    if len(color_matches) > 1:
        return ", ".join(f"{qty} {color}" for qty, color in color_matches)

    return None


def extract_player_identifier(component_name: str) -> Optional[str]:
    """
    Extract player color/faction from component name with priority order.

    Priority order:
    1. "COLOR player X" → COLOR (e.g., "Red player cubes" → "Red")
    2. "Faction NUMBER/LETTER X" → "Faction NUMBER/LETTER" (e.g., "Faction 1 cards" → "Faction 1", "Faction A cards" → "Faction A")
    3. "The NAME X" → NAME (e.g., "The Nobility herald" → "Nobility")
    4. None → Shared component

    Args:
        component_name: Name of the component to parse

    Returns:
        Extracted player identifier or None if shared
    """
    name_lower = component_name.lower()

    # Priority 1: Color + "player" pattern (most specific)
    color_pattern = r'\b(red|blue|green|yellow|purple|white|black|orange|pink|teal)\s+player\b'
    if match := re.search(color_pattern, name_lower):
        return match.group(1).title()

    # Priority 2: "Faction NUMBER" or "Faction LETTER" pattern
    faction_pattern = r'\bfaction\s+([a-d]|\d+)\b'
    if match := re.search(faction_pattern, name_lower):
        identifier = match.group(1).upper()
        return f"Faction {identifier}"

    # Priority 3: "The NAME" pattern (must be at start)
    the_pattern = r'^the\s+([a-z]+(?:\s+[a-z]+)?)\b'
    if match := re.search(the_pattern, name_lower):
        return match.group(1).title()

    # Not player-specific
    return None


def group_components_intelligently(components: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Groups components using AI's player_identifier field.
    Falls back to pattern matching only if AI didn't provide identifier.

    Handles patterns from: The Old King's Crown, Eclipse, Railway Boom, Dune: Imperium,
    Thunder Road, Spirit Island, Brass: Birmingham, Hegemony, and more.
    """

    # Step 1: Separate player-specific from shared (TRUST AI FIRST)
    player_groups = {}
    shared_components = []

    for comp in components:
        name = comp['name']
        name_lower = name.lower()

        # PRIORITY: Trust AI's analysis
        is_player_specific = comp.get('player_specific', False)
        player_id = comp.get('player_identifier')  # NEW: AI provides this directly

        # Fallback: If AI didn't mark it, try pattern matching
        if player_id is None and not is_player_specific:
            player_id = extract_player_identifier(name)

        # Additional fallback patterns for special cases
        if player_id is None and (is_player_specific or 'player' in name_lower or 'faction' in name_lower):
            # Class names (Hegemony-style)
            if any(cls in name_lower for cls in ['working class', 'middle class', 'capitalist', 'state']):
                if 'working class' in name_lower or 'working' in name_lower:
                    player_id = 'Working Class'
                elif 'middle class' in name_lower or 'middle' in name_lower:
                    player_id = 'Middle Class'
                elif 'capitalist' in name_lower:
                    player_id = 'Capitalist Class'
                elif 'state' in name_lower:
                    player_id = 'State'

            # Spirit names (Spirit Island-style)
            elif 'spirit' in name_lower or any(spirit in name_lower for spirit in ['lightning', 'river', 'shadows', 'earth', 'wildfire', 'ocean', 'fangs', 'bringer']):
                if match := re.search(r'(lightning\'s swift strike|river surges in sunlight|shadows flicker like flame|vital strength of the earth|thunderspeaker|ocean\'s hungry grasp|bringer of dreams and nightmares|fangs at the gates?)', name_lower):
                    player_id = match.group(1).title()

        # Group by player identifier
        if player_id:
            # Normalize player identifier
            player_id = player_id.strip()
            # Add "Player" suffix for simple color names if not already present
            if player_id in ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'White', 'Black', 'Orange', 'Pink', 'Teal', 'Brown']:
                player_id = f"{player_id} Player"

            if player_id not in player_groups:
                player_groups[player_id] = []
            player_groups[player_id].append(comp)
        else:
            # Shared component
            shared_components.append(comp)

    # Step 2: Sort player groups intelligently
    def faction_sort_key(faction_name: str) -> Tuple[int, str]:
        """Returns (priority, normalized_name) for sorting"""
        # Extract number if present
        if match := re.search(r'(\d+)', faction_name):
            return (0, f"{int(match.group(1)):03d}")  # Numbered factions first

        # Known faction names (game-specific)
        known_factions = ['clans', 'gathering', 'nobility', 'uprising', 'crown']
        name_lower = faction_name.lower()
        for idx, known in enumerate(known_factions):
            if known in name_lower:
                return (1, f"{idx:03d}")

        # Classes (Hegemony-style)
        classes = ['working class', 'middle class', 'capitalist class', 'state']
        for idx, cls in enumerate(classes):
            if cls in name_lower:
                return (2, f"{idx:03d}")

        # Colors (alphabetically)
        colors = ['black', 'blue', 'brown', 'green', 'orange', 'pink', 'purple', 'red', 'teal', 'white', 'yellow']
        for idx, color in enumerate(colors):
            if color in name_lower:
                return (3, f"{idx:03d}")

        # Everything else alphabetically
        return (4, faction_name.lower())

    sorted_factions = sorted(player_groups.keys(), key=faction_sort_key)

    # Step 3: Group shared components by logical category
    shared_categories = {
        '🃏 Kingdom Cards': ['kingdom card', 'shared deck', 'market card', 'council'],
        '🚂 Train Cards': ['locomotive', 'carriage', 'train car'],
        '🔬 Technology & Upgrades': ['technology', 'tech', 'upgrade', 'ship part', 'research', 'advance'],
        '🗺️ Galaxy Exploration': ['hex', 'sector', 'discovery tile', 'ancient', 'planet', 'wormhole'],
        '🏙️ Map & Cities': ['city', 'map tile', 'location', 'terrain', 'board section'],
        '📋 Strategy & Development': ['objective card', 'route card', 'station card', 'development card',
                                       'agenda', 'contract', 'intrigue', 'event'],
        '💰 Economy & Resources': ['money', 'coin', 'gold', 'resource', 'materials', 'science',
                                    'storage marker', 'influence token', 'lore token', 'wood', 'stone',
                                    'coal', 'food', 'luxury', 'solari', 'spice', 'water'],
        '⚔️ Combat & Conflict': ['dice', 'damage', 'combat', 'weapon', 'ship', 'ancient ship',
                                  'reputation', 'conflict', 'battle'],
        '🏛️ Structures & Buildings': ['orbital', 'monolith', 'building', 'structure', 'starbase',
                                        'colony', 'company'],
        '👤 Leaders & Characters': ['leader', 'spirit panel', 'character', 'panel'],
        '🎭 Optional Modules': ['adversary', 'scenario', 'module', 'expansion', 'choam', 'tech tile'],
        '🎲 Game System': ['marker', 'tracker', 'round marker', 'turn', 'player aid', 'ambassador',
                           'traitor', 'indicator', 'bidding disc', 'vp tracker', 'priority',
                           'rulebook', 'supply board', 'fear', 'blight', 'dahan', 'invader',
                           'first player', 'active player', 'phase', 'season']
    }

    categorized_shared = {}
    uncategorized = []

    for comp in shared_components:
        name_lower = comp['name'].lower()
        categorized = False

        for category, keywords in shared_categories.items():
            if any(keyword in name_lower for keyword in keywords):
                if category not in categorized_shared:
                    categorized_shared[category] = []
                categorized_shared[category].append(comp)
                categorized = True
                break

        if not categorized:
            uncategorized.append(comp)

    # Build final grouped structure
    result = {}

    # Add player-specific groups (sorted)
    for faction in sorted_factions:
        # Choose appropriate emoji
        faction_lower = faction.lower()

        if any(x in faction_lower for x in ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink']):
            emoji = '🎨'
        elif 'spirit' in faction_lower or any(x in faction_lower for x in ['lightning', 'river', 'shadows', 'earth']):
            emoji = '✨'
        elif any(x in faction_lower for x in ['class', 'working', 'middle', 'capitalist', 'state']):
            emoji = '👥'
        elif any(x in faction_lower for x in ['nobility', 'crown', 'clans', 'gathering', 'uprising']):
            emoji = '👑'
        else:
            emoji = '🎨'

        group_name = f"{emoji} {faction} Components"
        result[group_name] = player_groups[faction]

    # Add shared categories (only if they have components)
    for category in shared_categories.keys():
        if category in categorized_shared:
            result[category] = categorized_shared[category]

    # Add uncategorized if any
    if uncategorized:
        result['📦 Other Shared Components'] = uncategorized

    return result


def render_material_defaults_and_expansion_workflow():
    """
    Show material defaults selection and expansion workflow for pending PDF imports.
    This is shown AFTER the user clicks "Continue" in the PDF extraction review form.
    """
    if 'pending_import_components' not in st.session_state or not st.session_state.pending_import_components:
        st.warning("No components selected. Please go back and select components to import.")
        if st.button("← Back to Selection"):
            st.session_state.show_material_defaults = False
            st.rerun()
        return

    selected_components = st.session_state.pending_import_components
    st.success(f"Selected {len(selected_components)} components for import.")

    # Collect unique component types
    component_types = set(comp['type'] for comp in selected_components)

    # Material defaults — skip the UI if Quick Defaults already answered this
    if st.session_state.get('quick_defaults_done'):
        # Quick Defaults collected cardboard quality — apply it automatically
        qd = st.session_state.get('quick_defaults', {})
        cb_quality = qd.get('cardboard_quality', 'standard')
        material_choices = {}
        if 'Cards' in component_types:
            material_choices['Cards'] = 'standard'
        if 'Tokens' in component_types:
            material_choices['Tokens'] = cb_quality
        if 'Tiles' in component_types:
            material_choices['Tiles'] = cb_quality
        st.session_state.pdf_material_defaults = material_choices
        # No material defaults UI shown — cardboard quality already set in Quick Defaults
    else:
        # Quick Defaults was skipped — show the material selection UI
        st.subheader("Material Defaults")
        st.caption("Select default materials for your components. You can adjust individual components later.")

        material_choices = {}

        if 'Cards' in component_types:
            card_stock_options = {
                'standard': 'Standard 300gsm (0.3mm)',
                'premium': 'Premium 350gsm (0.4mm)',
                'tarot': 'Tarot weight (0.5mm)',
            }
            material_choices['Cards'] = st.selectbox(
                "Card stock for all cards:",
                options=list(card_stock_options.keys()),
                format_func=lambda x: card_stock_options[x],
                key="default_card_stock"
            )

        if 'Tokens' in component_types or 'Tiles' in component_types:
            cardboard_options = {
                'budget': 'Budget (1.0-1.2mm) - Lightweight games',
                'standard': 'Standard (1.5mm) - Most modern board games',
                'premium': 'Premium (2.0mm) - Deluxe editions',
                'heavy_duty': 'Heavy-duty (2.5mm) - Player boards, chunky tiles',
            }
            if 'Tokens' in component_types:
                material_choices['Tokens'] = st.selectbox(
                    "Cardboard quality for all tokens:",
                    options=list(cardboard_options.keys()),
                    format_func=lambda x: cardboard_options[x],
                    key="default_token_cardboard"
                )
            if 'Tiles' in component_types:
                material_choices['Tiles'] = st.selectbox(
                    "Cardboard quality for all tiles:",
                    options=list(cardboard_options.keys()),
                    format_func=lambda x: cardboard_options[x],
                    key="default_tile_cardboard"
                )

        st.session_state.pdf_material_defaults = material_choices
        st.markdown("---")

    # Expansion workflow
    st.subheader("Add to Inventory")

    # Check if user has existing games
    existing_games = []
    game_names = set()
    for comp in st.session_state.get('components', []):
        game_name = comp.get('source_game', None)
        if game_name and game_name not in game_names:
            game_names.add(game_name)
            # Count components for this game
            count = sum(1 for c in st.session_state.components if c.get('source_game') == game_name)
            existing_games.append({
                'name': game_name,
                'component_count': count
            })

    # Pre-initialize new_game_name in session state BEFORE any widget renders.
    # Streamlit raises StreamlitAPIException if you assign to a session state key
    # after the widget with that key has already been instantiated on the page.
    # Pre-populate from the extraction result's game_name if available and not already set.
    if 'new_game_name' not in st.session_state or not st.session_state.new_game_name:
        extracted_name = st.session_state.get('pdf_extraction_result', {}).get('game_name', '')
        st.session_state.new_game_name = extracted_name

    if existing_games:
        add_mode = st.radio(
            "How would you like to add these components?",
            options=["As New Game", "Add to Existing Game (Expansion)"],
            key="add_mode_selection"
        )

        if add_mode == "Add to Existing Game (Expansion)":
            selected_game = st.selectbox(
                "Select base game:",
                options=[g['name'] for g in existing_games],
                format_func=lambda name: f"{name} ({next(g['component_count'] for g in existing_games if g['name'] == name)} components)",
                key="expansion_base_game"
            )

            st.caption(f"Components will be added to {selected_game}.")

            # Store expansion info
            st.session_state.is_expansion_import = True
            st.session_state.expansion_base_game = selected_game
        else:
            st.session_state.is_expansion_import = False

            # Widget reads/writes st.session_state.new_game_name automatically via key=
            st.text_input(
                "Game name:",
                placeholder="e.g., Dune: Imperium",
                key="new_game_name"
            )
    else:
        st.caption("This will be added as a new game.")

        # Widget reads/writes st.session_state.new_game_name automatically via key=
        st.text_input(
            "Game name:",
            placeholder="e.g., The Old King's Crown",
            key="new_game_name"
        )
        st.session_state.is_expansion_import = False

    st.markdown("---")

    # Action buttons
    cols = st.columns([1, 1])

    with cols[0]:
        if st.button("← Back to Selection", use_container_width=True):
            st.session_state.show_material_defaults = False
            st.rerun()

    with cols[1]:
        # Validate game name before allowing continue
        can_continue = True
        if not st.session_state.get('is_expansion_import', False):
            can_continue = bool(st.session_state.get('new_game_name', '').strip())

        if st.button("Add to Inventory →", use_container_width=True, type="primary", disabled=not can_continue):
            # Apply material defaults and add components
            material_defaults = st.session_state.get('pdf_material_defaults', {})
            newly_added_ids = []

            for comp in selected_components:
                component_id = str(uuid.uuid4())

                # Apply material defaults if applicable
                material = None
                material_category = None
                if comp['type'] in material_defaults:
                    if comp['type'] == 'Cards':
                        material = material_defaults['Cards']
                        material_category = 'cards'
                    elif comp['type'] in ['Tokens', 'Tiles']:
                        material = material_defaults[comp['type']]
                        material_category = 'cardboard'

                # Add expansion marking if applicable
                component_name = comp['name']
                if st.session_state.get('is_expansion_import', False):
                    component_name = f"[Expansion] {comp['name']}"
                    source_game = st.session_state.expansion_base_game
                    is_expansion = True
                else:
                    source_game = st.session_state.get('new_game_name', 'Unknown')
                    is_expansion = False

                # Carry over prefill dimensions stamped by apply_quick_defaults_to_components()
                _pfill_complete = comp.get('_prefill_complete', False)
                new_component = {
                    'id': component_id,
                    'type': comp['type'],
                    'quantity': comp['quantity'],
                    'name': component_name,
                    'length': comp.get('length', 50.0),   # use prefilled value if available
                    'width':  comp.get('width',  50.0),
                    'height': comp.get('height', 10.0),
                    '_prefill_length':   comp.get('_prefill_length'),
                    '_prefill_width':    comp.get('_prefill_width'),
                    '_prefill_height':   comp.get('_prefill_height'),
                    '_prefill_source':   comp.get('_prefill_source'),
                    '_prefill_complete': _pfill_complete,
                    '_clearance_mm':     comp.get('_clearance_mm'),
                    '_clearance_note':   comp.get('_clearance_note'),
                    '_last_type': comp['type'],
                    '_needs_dimensions': not _pfill_complete,
                    'material': material,
                    'material_category': material_category,
                    'card_stock': material if comp['type'] == 'Cards' else None,
                    'sleeve_type': 'unsleeved' if comp['type'] == 'Cards' else None,
                    'stack_quantity': None,
                    'stack_height': None,
                    'calculated_per_card': None,
                    '_name_manually_edited': False,
                    'details': get_component_breakdown(comp),
                    'source_game': source_game,
                    'is_expansion': is_expansion,
                }

                st.session_state.components.append(new_component)
                newly_added_ids.append(component_id)

            # Store newly added IDs for auto-expand
            st.session_state.newly_added_component_ids = newly_added_ids

            # Clean up
            num_added = len(selected_components)
            st.session_state.pdf_components = []
            st.session_state.selected_pdf_components = set()
            st.session_state.pending_import_components = []
            st.session_state.show_material_defaults = False
            st.session_state.show_pdf_uploader = False
            if 'pdf_material_defaults' in st.session_state:
                del st.session_state.pdf_material_defaults
            # Clear extraction cache and reset the file uploader key so the
            # uploader widget resets (no file selected). This prevents the gate
            # system from re-triggering extraction on the next rerun.
            st.session_state.pop('last_extracted_pdf_name', None)
            st.session_state.pop('pdf_extraction_result', None)
            st.session_state['pdf_upload_counter'] = st.session_state.get('pdf_upload_counter', 0) + 1

            if st.session_state.get('is_expansion_import', False):
                st.success(f"Added {num_added} expansion components to {st.session_state.expansion_base_game}.")
            else:
                st.success(f"Added {num_added} components for {st.session_state.new_game_name}.")

            st.rerun()


def show_material_defaults_dialog(component_types: Set[str]) -> Dict[str, str]:
    """
    DEPRECATED: Use render_material_defaults_and_expansion_workflow() instead.

    Show a dialog for selecting material defaults for each component type.

    Args:
        component_types: Set of component types found in the extracted list

    Returns:
        Dict mapping component type to material choice:
        {
            'Cards': 'standard',
            'Tokens': 'standard',
            'Tiles': 'premium'
        }
    """
    st.subheader("Material Defaults")
    st.caption("Select default materials for your components. You can adjust individual components later.")

    material_choices = {}

    # Card stock defaults
    if 'Cards' in component_types:
        card_stock_options = {
            'standard': 'Standard 300gsm (0.3mm)',
            'premium': 'Premium 350gsm (0.4mm)',
            'tarot': 'Tarot weight (0.5mm)',
        }
        material_choices['Cards'] = st.selectbox(
            "Card stock for all cards:",
            options=list(card_stock_options.keys()),
            format_func=lambda x: card_stock_options[x],
            key="default_card_stock"
        )

    # Cardboard defaults (for Tokens and Tiles)
    if 'Tokens' in component_types or 'Tiles' in component_types:
        cardboard_options = {
            'budget': 'Budget (1.0-1.2mm) - Lightweight games',
            'standard': 'Standard (1.5mm) - Most modern board games',
            'premium': 'Premium (2.0mm) - Deluxe editions',
            'heavy_duty': 'Heavy-duty (2.5mm) - Player boards, chunky tiles',
        }

        if 'Tokens' in component_types:
            material_choices['Tokens'] = st.selectbox(
                "Cardboard quality for all tokens:",
                options=list(cardboard_options.keys()),
                format_func=lambda x: cardboard_options[x],
                key="default_token_cardboard"
            )

        if 'Tiles' in component_types:
            material_choices['Tiles'] = st.selectbox(
                "Cardboard quality for all tiles:",
                options=list(cardboard_options.keys()),
                format_func=lambda x: cardboard_options[x],
                key="default_tile_cardboard"
            )

    return material_choices


# ── Quick Defaults ─────────────────────────────────────────────────────────────

def _get_dimension_prefill(comp: dict, box_config: dict, quick_defaults: dict):
    """Return (length, width, height, source_note) for a component, or None if unknown.

    Called by apply_quick_defaults_to_components() to stamp each component with
    _prefill_* fields so the review form and component editor can pre-fill inputs.
    """
    name_lower = comp.get('name', '').lower()
    comp_type = comp.get('type', 'Other')
    quantity = max(1, int(comp.get('quantity', 1)))
    cardboard_quality = quick_defaults.get('cardboard_quality', 'standard')
    cards_sleeved = quick_defaults.get('cards_sleeved', 'unsleeved')
    dice_size_mm = float(quick_defaults.get('dice_size_mm', 16))
    cube_size_mm = float(quick_defaults.get('cube_size_mm', 8))
    has_minis = quick_defaults.get('has_minis', False)

    box_l = box_config.get('length', 296)
    box_w = box_config.get('width', 296)

    # Rulebooks / instructions — fit the box footprint
    # Match on name keywords regardless of comp_type, OR on bare Rulebook type
    rulebook_keywords = ('rulebook', 'rule book', 'instructions', 'rules', 'manual', 'insert', 'booklet')
    if any(kw in name_lower for kw in rulebook_keywords) or comp_type == 'Rulebook':
        return (float(box_l), float(box_w), 3.0,
                f"Matches box dimensions ({box_l}×{box_w}mm) — rulebook fits box")

    # Boards
    if comp_type == 'Boards':
        return (float(box_l), float(box_w), 5.0,
                f"Matches box dimensions ({box_l}×{box_w}mm) — bi-fold board default 5mm")

    # Resource cubes — use cube_size_mm from Quick Defaults
    if 'cube' in name_lower or 'cubes' in name_lower:
        s = cube_size_mm
        return (s, s, s, f"Resource cube — {s:.0f}mm")

    # Meeples / Miniatures — separate handling
    _is_mini_type  = comp_type == 'Meeples/Minis'
    _is_mini_name  = any(kw in name_lower for kw in ('miniature', 'figure', 'model', 'sculpt', 'mini'))
    _is_meeple_name = any(kw in name_lower for kw in ('meeple', 'worker', 'disc'))

    if has_minis and (_is_mini_type or _is_mini_name):
        # Large figures — dimensions too varied to predict; flag for clearance only
        comp['_clearance_mm'] = 2.0
        comp['_clearance_note'] = "Miniature — wider clearance applied (+2mm)"
        return None  # No dimension prefill

    if _is_meeple_name or (_is_mini_type and not has_minis):
        # Standard meeples — predictable size
        return (16.0, 16.0, 10.0, "Standard meeple (16×16×10mm)")

    # Dice — use dice_size_mm from Quick Defaults; also match on name keywords
    if comp_type == 'Dice' or any(kw in name_lower for kw in ('dice', 'die', 'd6', 'd8', 'd10', 'd12', 'd20')):
        s = dice_size_mm
        return (s, s, s, f"Standard {s:.0f}mm die")

    # Cards — poker preset + sleeve clearance
    if comp_type == 'Cards':
        sleeve_add = {'unsleeved': 0.0, 'thin': 0.05, 'premium': 0.1}.get(cards_sleeved, 0.0)
        per_card_mm = 0.3 + sleeve_add  # standard card stock + sleeve
        stack_h = round(quantity * per_card_mm + 5.0, 1)  # 5mm finger room
        sleeve_label = {'unsleeved': 'unsleeved', 'thin': 'thin sleeves', 'premium': 'premium sleeves'}[cards_sleeved]
        return (63.5, 88.0, stack_h,
                f"Poker card preset (63.5×88mm), {sleeve_label}, stack height {stack_h}mm")

    # Tokens / Tiles — thickness only (footprint varies too much to guess)
    if comp_type in ('Tokens', 'Tiles'):
        thickness = {'budget': 1.1, 'standard': 1.5, 'premium': 2.0, 'luxury': 2.75}.get(cardboard_quality, 1.5)
        # Only height (thickness) pre-filled; length/width left for user
        return (None, None, thickness,
                f"Thickness from cardboard quality ({cardboard_quality} = {thickness}mm)")

    return None  # No suggestion


def apply_quick_defaults_to_components(extraction_result: dict, quick_defaults: dict):
    """Stamp each component in extraction_result with _prefill_* dimension fields.

    Mutates component dicts in-place (inside component_groups AND in the flat
    components list). Called once after Quick Defaults form submit.
    """
    box_config = st.session_state.get('box_config', {})

    for group in extraction_result.get('component_groups', []):
        for comp in group.get('components', []):
            result = _get_dimension_prefill(comp, box_config, quick_defaults)
            if result is not None:
                l, w, h, note = result
                if l is not None:
                    comp['_prefill_length'] = l
                    comp['length'] = l          # write directly so editor reads correct value
                if w is not None:
                    comp['_prefill_width'] = w
                    comp['width'] = w
                if h is not None:
                    comp['_prefill_height'] = h
                    comp['height'] = h
                comp['_prefill_source'] = note
                comp['_prefill_complete'] = (l is not None and w is not None and h is not None)
            else:
                comp.setdefault('_prefill_complete', False)

    # Propagate to flat components list (these are copies from _flatten_groups)
    # Re-stamp by matching extraction_index
    prefill_map = {}
    for group in extraction_result.get('component_groups', []):
        for comp in group.get('components', []):
            idx = comp.get('extraction_index')
            if idx is not None:
                prefill_map[idx] = {
                    k: comp[k] for k in comp if k.startswith('_prefill')
                }

    for comp in extraction_result.get('components', []):
        idx = comp.get('extraction_index')
        if idx in prefill_map:
            pf = prefill_map[idx]
            comp.update(pf)
            # Also write directly to length/width/height so the editor reads them
            if pf.get('_prefill_length') is not None:
                comp['length'] = pf['_prefill_length']
            if pf.get('_prefill_width') is not None:
                comp['width'] = pf['_prefill_width']
            if pf.get('_prefill_height') is not None:
                comp['height'] = pf['_prefill_height']


def _inject_dice_component(size_mm: int):
    """Inject a synthetic dice component into the current extraction result.

    Adds to an existing shared group if present, otherwise creates a new
    'Dice' group with group_type='shared'. Re-indexes all components globally.
    Quantity is set to 1 as a placeholder — user can edit in the review form.
    """
    extraction_result = st.session_state.get('pdf_extraction_result')
    if not extraction_result:
        return

    # Find max existing extraction_index
    max_idx = max(
        (comp.get('extraction_index', -1) for group in extraction_result.get('component_groups', [])
         for comp in group.get('components', [])),
        default=-1,
    )

    dice_comp = {
        'name': f'Dice ({size_mm}mm)',
        'type': 'Dice',
        'quantity': 1,   # placeholder — user edits quantity in the review form
        'extraction_index': max_idx + 1,
        '_group_name': 'Dice',
        '_group_type': 'shared',
        '_per_player': False,
    }

    groups = extraction_result.get('component_groups', [])
    # Try to add to existing shared group
    shared_group = next((g for g in groups if g.get('group_type') == 'shared'), None)
    if shared_group:
        shared_group.setdefault('components', []).append(dice_comp)
    else:
        # Create new dice group
        groups.append({
            'group_name': 'Dice',
            'group_type': 'shared',
            'per_player': False,
            'identical_sets': False,
            'notes': 'Added via Quick Defaults',
            'components': [dice_comp],
        })
        extraction_result['component_groups'] = groups

    # Also add to flat components list
    extraction_result.setdefault('components', []).append(dice_comp)


def render_quick_defaults():
    """Blocking form shown after PDF extraction — sets global defaults before component review.

    Sets st.session_state.quick_defaults and quick_defaults_done on submit,
    then calls apply_quick_defaults_to_components() to stamp prefill data.
    """
    st.subheader("Quick setup")
    st.caption("These apply to all components. You can override individually in the next step.")

    with st.form("quick_defaults_form"):
        cardboard = st.selectbox(
            "Cardboard quality",
            options=['budget', 'standard', 'premium', 'luxury'],
            index=1,
            format_func=lambda x: {
                'budget': 'Budget (1.0–1.2mm) — lightweight games',
                'standard': 'Standard (1.5mm) — most modern games',
                'premium': 'Premium (2.0mm) — deluxe editions',
                'luxury': 'Luxury (2.5–3.0mm) — heavy duty',
            }[x],
            help="Applies to all tokens, tiles, and boards",
        )

        sleeves = st.radio(
            "Cards sleeved?",
            options=['unsleeved', 'thin', 'premium'],
            format_func=lambda x: {
                'unsleeved': 'Unsleeved',
                'thin': 'Thin sleeves (+0.05mm/card)',
                'premium': 'Premium sleeves (+0.1mm/card)',
            }[x],
            horizontal=True,
            help="Sets sleeve clearance for all card stacks",
        )

        # ── Dice ──────────────────────────────────────────────────────────────
        has_dice = st.toggle(
            "Game has dice?",
            help="Sets default dimensions for dice components. "
                 "Toggle on if the AI missed them in the PDF.",
        )

        dice_size_mm = 16
        if has_dice:
            dice_size_label = st.selectbox(
                "Default dice size",
                options=['12mm (small)', '16mm (standard)', '19mm (large)', 'Custom'],
                index=1,
                help="Standard d6 is 16mm. Small/travel dice are 12mm. Casino dice are 19mm.",
            )
            if dice_size_label == 'Custom':
                dice_size_mm = st.number_input(
                    "Dice size (mm)", min_value=8, max_value=30, value=16, step=1
                )
            else:
                dice_size_mm = int(dice_size_label.split('mm')[0])

        # ── Resource cubes ────────────────────────────────────────────────────
        has_cubes = st.toggle(
            "Game has resource cubes?",
            help="Sets default dimensions for cube components",
        )

        cube_size_mm = 8
        if has_cubes:
            cube_size_label = st.selectbox(
                "Default cube size",
                options=['8mm', '10mm', 'Custom'],
                index=0,
                help="8mm is the most common resource cube size",
            )
            if cube_size_label == 'Custom':
                cube_size_mm = st.number_input(
                    "Cube size (mm)", min_value=3, max_value=30, value=8, step=1
                )
            else:
                cube_size_mm = int(cube_size_label.replace('mm', ''))

        # ── Miniatures ────────────────────────────────────────────────────────
        has_minis = st.toggle(
            "Game has miniatures or large figures?",
            help="Applies wider clearance (+2mm per dimension) to miniature components. "
                 "Enter actual dimensions per component in the review.",
        )

        has_expansion = st.toggle(
            "Include expansion space?",
            help="Adds a note to include a flexible compartment for future expansion components",
        )

        submitted = st.form_submit_button("Apply & Review Components", type="primary")

    if submitted:
        qd = {
            'cardboard_quality': cardboard,
            'cards_sleeved': sleeves,
            'has_dice': has_dice,
            'dice_size_mm': dice_size_mm if has_dice else 16,
            'has_cubes': has_cubes,
            'cube_size_mm': cube_size_mm if has_cubes else 8,
            'has_minis': has_minis,
            'has_expansion_space': has_expansion,
        }
        st.session_state.quick_defaults = qd
        st.session_state.quick_defaults_done = True

        # Inject dice placeholder only if AI detected zero dice components
        if has_dice:
            extraction = st.session_state.get('pdf_extraction_result', {})
            has_existing_dice = any(
                comp.get('type') == 'Dice'
                or any(kw in comp.get('name', '').lower() for kw in ('dice', 'die', 'd6'))
                for group in extraction.get('component_groups', [])
                for comp in group.get('components', [])
            )
            if not has_existing_dice:
                _inject_dice_component(dice_size_mm)

        # Stamp all components with prefill data
        if 'pdf_extraction_result' in st.session_state:
            apply_quick_defaults_to_components(st.session_state.pdf_extraction_result, qd)

        # Pre-fill design name from extraction result if not already set
        _extracted_game_name = st.session_state.get('pdf_extraction_result', {}).get('game_name', '')
        if _extracted_game_name and not st.session_state.get('design_name'):
            st.session_state.design_name = _extracted_game_name
            if 'box_config' in st.session_state:
                st.session_state.box_config['game_name'] = _extracted_game_name

        st.rerun()


def render_pdf_extraction_review(extraction_result: dict):
    """
    Render grouped PDF extraction review UI with form-based selection (prevents freeze).

    Args:
        extraction_result: Full extraction result dict from extract_components_with_ai()
                           (has component_groups, game_name, metadata, etc.)
    """
    component_groups = extraction_result.get('component_groups', [])
    flat_components = extraction_result.get('components', [])

    if not component_groups and not flat_components:
        st.caption("No components found in the first 15 pages. If the component list appears later in the rulebook, add components manually below.")
        return

    # Fallback: if no groups but flat components exist, build groups via Python grouping
    if not component_groups and flat_components:
        legacy_grouped = group_components_intelligently(flat_components)
        component_groups = [
            {'group_name': k, 'group_type': 'shared', 'per_player': False, 'notes': '', 'components': v}
            for k, v in legacy_grouped.items()
        ]

    # Game name (read early so it can be used in the success banner)
    game_name = extraction_result.get('game_name', '')

    total_components = sum(len(g.get('components', [])) for g in component_groups)
    is_merged = extraction_result.get('metadata', {}).get('merged', False)
    if is_merged:
        st.success(f"{game_name if game_name else 'Base game + Expansion'} — {total_components} total components across {len(component_groups)} groups")
    else:
        st.success(f"Found {len(component_groups)} component groups, {total_components} total components.")

    # Game name display
    if game_name:
        st.subheader(game_name)

    # Display token usage and extraction details
    metadata = extraction_result.get('metadata', {})

    if 'tokens_used' in metadata and metadata['tokens_used']:
        tokens = metadata['tokens_used']
        provider = metadata.get('provider', 'unknown')

        # Provider-aware pricing table (per million tokens)
        PRICING = {
            'claude': {'input': 3.00,  'output': 15.00, 'label': 'Claude Sonnet 4'},
            'gemini': {'input': 0.075, 'output': 0.30,  'label': 'Gemini Flash'},
            'openai': {'input': 0.150, 'output': 0.600, 'label': 'GPT-4o-mini'},
            'ollama': {'input': 0.0,   'output': 0.0,   'label': 'Local (free)'},
        }
        pricing = PRICING.get(provider, {'input': 0.0, 'output': 0.0, 'label': 'Unknown provider'})

        input_cost = (tokens.get('prompt_tokens', 0) / 1_000_000) * pricing['input']
        output_cost = (tokens.get('completion_tokens', 0) / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost

        with st.expander("Extraction details", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Tokens Used",
                    f"{tokens.get('total_tokens', 0):,}",
                    help="Total tokens: prompt + response"
                )

            with col2:
                st.metric(
                    "Est. Cost",
                    f"${total_cost:.4f}",
                    help=f"Based on {pricing['label']} pricing"
                )

            with col3:
                st.metric(
                    "Provider",
                    pricing['label'],
                    help=f"Input: ${pricing['input']}/1M tokens, Output: ${pricing['output']}/1M tokens"
                )

            st.markdown("**Token Breakdown:**")
            st.caption(f"• Input: {tokens.get('prompt_tokens', 0):,} tokens")
            st.caption(f"• Output: {tokens.get('completion_tokens', 0):,} tokens")

    # Extraction notes (show as warning if present)
    extraction_notes = extraction_result.get('extraction_notes', '')
    if extraction_notes:
        st.caption(f"AI notes: {extraction_notes}")

    # ── Player Count Adjuster (outside form — uses st.button) ───────────────────
    has_player_groups = any(g.get('group_type') == 'player' for g in component_groups)

    if has_player_groups:
        player_count_meta = extraction_result.get('player_count', {})
        factions_or_colors = extraction_result.get('factions_or_colors', [])
        pc_min = player_count_meta.get('min', 2)
        pc_max = player_count_meta.get('max', 4)

        # Initialize session state defaults only on first render
        if 'player_set_count' not in st.session_state:
            default_count = len(factions_or_colors) if factions_or_colors else (pc_max or 4)
            st.session_state.player_set_count = max(1, default_count)

        if 'player_set_names' not in st.session_state:
            base_names = list(factions_or_colors)
            count = st.session_state.player_set_count
            while len(base_names) < count:
                base_names.append(f"Player {len(base_names) + 1}")
            st.session_state.player_set_names = base_names[:count]

        # If expansion added new factions, extend names list
        if len(factions_or_colors) > len(st.session_state.player_set_names):
            existing = st.session_state.player_set_names
            for f in factions_or_colors[len(existing):]:
                existing.append(f)
            st.session_state.player_set_names = existing

        st.subheader("Player sets")
        st.caption(f"AI detected: {pc_min}–{pc_max} players")

        new_count = int(st.number_input(
            "Sets to create",
            min_value=1,
            max_value=12,
            value=st.session_state.player_set_count,
            step=1,
            key="player_set_count_input",
        ))

        # Sync names list when count changes
        if new_count != st.session_state.player_set_count:
            st.session_state.player_set_count = new_count
            names = st.session_state.player_set_names
            while len(names) < new_count:
                names.append(f"Player {len(names) + 1}")
            st.session_state.player_set_names = names[:new_count]

        # Editable name inputs (4 per row)
        st.markdown("**Set names** *(click to rename)*:")
        names = st.session_state.player_set_names
        count = st.session_state.player_set_count
        while len(names) < count:
            names.append(f"Player {len(names) + 1}")
        names = names[:count]

        for row_start in range(0, count, 4):
            cols = st.columns(4)
            for i in range(row_start, min(row_start + 4, count)):
                with cols[i - row_start]:
                    names[i] = st.text_input(
                        f"Set {i + 1}", value=names[i],
                        key=f"player_set_name_{i}",
                        label_visibility="collapsed"
                    )
        st.session_state.player_set_names = names
        st.divider()
    # ─────────────────────────────────────────────────────────────────────────────

    # Initialize selection state
    if 'selected_pdf_components' not in st.session_state:
        st.session_state.selected_pdf_components = set()

    # Group type badge config
    GROUP_BADGES = {
        'player':          ('', 'Player'),
        'shared':          ('', 'Shared'),
        'setup':           ('', 'Setup'),
        'board_and_rules': ('', 'Boards & Rules'),
    }

    st.subheader("Review & Edit Extracted Components")
    st.caption("Select the groups you want to import. Player groups will each get their own tray section.")

    # CRITICAL: Wrap entire UI in form to prevent freeze on checkbox clicks
    with st.form("pdf_component_selection_form", clear_on_submit=False):
        for group_idx, group in enumerate(component_groups):
            group_name = group.get('group_name', f'Group {group_idx + 1}')
            group_comps = group.get('components', [])
            group_type = group.get('group_type', 'shared')
            group_notes = group.get('notes', '')
            is_identical = group.get('identical_sets', False)

            st.markdown("---")

            # Header: badge + name + item count | Select All checkbox
            col1, col2 = st.columns([4, 1])

            with col1:
                _badge_label = GROUP_BADGES.get(group_type, ('', 'Shared'))[1]

                if is_identical and group_type == 'player':
                    # Show consolidated header with set count and editable names
                    set_count = st.session_state.get('player_set_count', 1)
                    set_names = st.session_state.get('player_set_names', [])
                    names_display = ', '.join(set_names) if set_names else f"{set_count} sets"
                    st.markdown(
                        f"**{group_name}** `{_badge_label}` "
                        f"×{set_count} sets ({names_display}) ({len(group_comps)} items)"
                    )
                else:
                    st.markdown(f"**{group_name}** `{_badge_label}` ({len(group_comps)} items)")

                # Group type contextual notes
                if group_type == 'board_and_rules':
                    st.caption("These items sit above the insert stack and are not printed trays — tracked for total stack height only.")
                elif group_type == 'setup':
                    st.caption("Setup-only: placed during game setup, rarely accessed during play.")
                elif group_notes:
                    st.caption(group_notes)

            with col2:
                select_all = st.checkbox(
                    "Select All",
                    key=f"select_all_{group_idx}",
                    label_visibility="visible"
                )

            is_expanded = group_idx < 2

            with st.expander("View components", expanded=is_expanded):
                for idx, comp in enumerate(group_comps):
                    comp_key = comp.get('extraction_index', f"{group_idx}_{idx}")

                    cols = st.columns([0.5, 3, 2, 1, 0.5])

                    with cols[0]:
                        was_selected = comp_key in st.session_state.selected_pdf_components
                        st.checkbox(
                            "☑",
                            value=select_all or was_selected,
                            key=f"check_{comp_key}",
                            label_visibility="collapsed"
                        )

                    with cols[1]:
                        comp['name'] = st.text_input(
                            "Name",
                            value=comp['name'],
                            key=f"name_{comp_key}",
                            label_visibility="collapsed"
                        )

                    with cols[2]:
                        type_options = ['Cards', 'Tokens', 'Tiles', 'Dice', 'Meeples/Minis', 'Boards', 'Other']
                        current_type = comp.get('type', 'Other')
                        if current_type not in type_options:
                            current_type = 'Other'
                        comp['type'] = st.selectbox(
                            "Type",
                            options=type_options,
                            index=type_options.index(current_type),
                            key=f"type_{comp_key}",
                            label_visibility="collapsed"
                        )

                    with cols[3]:
                        comp['quantity'] = st.number_input(
                            "Qty",
                            min_value=1,
                            value=comp.get('quantity', 1),
                            key=f"qty_{comp_key}",
                            label_visibility="collapsed"
                        )

                    with cols[4]:
                        st.checkbox(
                            "Delete",
                            key=f"delete_{comp_key}",
                            label_visibility="collapsed"
                        )

        # Action buttons INSIDE form
        st.markdown("---")
        cols = st.columns([3, 1, 1])

        with cols[1]:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        with cols[2]:
            submit = st.form_submit_button("Continue →", use_container_width=True, type="primary")

    # Process form submission OUTSIDE form
    if submit:
        selected = []
        deleted = []

        for group_idx, group in enumerate(component_groups):
            group_name = group.get('group_name', f'Group {group_idx + 1}')
            # If the group-level "Select All" checkbox was checked, treat every
            # component in the group as selected — even if the user never clicked
            # the individual checkboxes (their session state keys stay False when
            # the checkbox value is driven by `value=select_all` not by user click).
            group_select_all = st.session_state.get(f"select_all_{group_idx}", False)

            for idx, comp in enumerate(group.get('components', [])):
                comp_key = comp.get('extraction_index', f"{group_idx}_{idx}")

                if st.session_state.get(f"delete_{comp_key}", False):
                    deleted.append(comp)
                    continue

                if group_select_all or st.session_state.get(f"check_{comp_key}", False):
                    selected.append(comp)

        # Remove deleted from flat component list
        for comp in deleted:
            if comp in st.session_state.pdf_components:
                st.session_state.pdf_components.remove(comp)

        st.session_state.pending_import_components = selected

        # Store selected components organized by group (for Step 2.5 tray suggestion).
        # Each group entry preserves group_type, identical_sets, player_sets info,
        # with components filtered to only those the user checked.
        selected_keys = {comp.get('extraction_index') for comp in selected}
        selected_groups = []
        for group in component_groups:
            group_comps = [
                c for c in group.get('components', [])
                if c.get('extraction_index') in selected_keys
            ]
            if group_comps:
                selected_groups.append({
                    'group_name': group.get('group_name', ''),
                    'group_type': group.get('group_type', 'shared'),
                    'identical_sets': group.get('identical_sets', False),
                    'per_player': group.get('per_player', False),
                    'notes': group.get('notes', ''),
                    'components': group_comps,
                })
        st.session_state.selected_component_groups = selected_groups

        st.session_state.show_material_defaults = True
        st.rerun()

    if cancel:
        st.session_state.pdf_components = []
        st.session_state.selected_pdf_components = set()
        st.rerun()


def render_expansion_upload_section():
    """Show expansion PDF uploader and merge its components into the existing extraction result.

    Renders after the base game review. Requires pdf_extraction_result to be set in
    session state. Calls extract_expansion_with_ai() and stores the merged result.
    """
    if 'pdf_extraction_result' not in st.session_state:
        return

    base_extraction = st.session_state.pdf_extraction_result

    st.divider()
    st.subheader("Add Expansion")
    st.caption("Upload an expansion rulebook to add its components to the current list.")

    expansion_file = st.file_uploader(
        "Upload Expansion PDF", type=['pdf'],
        key="expansion_pdf_upload",
        label_visibility="collapsed",
    )

    if expansion_file is not None:
        # Guard: don't re-process if this exact file was already merged
        already_merged = base_extraction.get('metadata', {}).get('merged', False)
        last_filename = st.session_state.get('last_expansion_filename')
        if already_merged and last_filename == expansion_file.name:
            total = base_extraction.get('metadata', {}).get('total_component_count', 0)
            st.success(f"Expansion already merged — {total} total components.")
            return

        with st.spinner("Extracting expansion components..."):
            try:
                expansion_text = extract_text_from_pdf(expansion_file)
            except Exception as e:
                st.error(f"Could not extract expansion PDF: {e}")
                return

            try:
                ai_settings = load_ai_settings()
            except Exception as e:
                st.error(f"Could not load AI settings: {e}")
                return

            if ai_settings['provider'] == 'none' or not ai_settings['api_key']:
                st.warning("AI provider not configured. Please set up an AI provider in Settings.")
                return

            try:
                merged = extract_expansion_with_ai(
                    expansion_text,
                    base_extraction,
                    ai_settings['provider'],
                    ai_settings['api_key'],
                )
            except Exception as e:
                st.error(f"Expansion extraction failed: {e}")
                return

        st.session_state.pdf_extraction_result = merged
        st.session_state.pdf_components = merged.get('components', [])
        st.session_state.last_expansion_filename = expansion_file.name

        new_count = merged.get('metadata', {}).get('expansion_component_count', 0)
        total = merged.get('metadata', {}).get('total_component_count', 0)
        st.success(f"Merged: {new_count} new expansion components added. {total} total.")
        st.rerun()


def render_components_inventory():
    """Render the components inventory UI"""

    st.subheader("Component Inventory")
    st.markdown("Add all components that need storage in the insert.")

    # Initialize session state
    if 'components' not in st.session_state:
        st.session_state.components = []

    # PDF upload state
    if 'pdf_components' not in st.session_state:
        st.session_state.pdf_components = []

    # Load component standards
    standards = load_component_standards()

    # Add component button
    if st.button("+ Add component", type="secondary"):
        # Create a unique ID for this component
        new_component = {
            'id': str(uuid.uuid4()),
            'type': 'Cards',
            'quantity': 1,
            'material': None,
            'material_category': None,
            'card_stock': None,
            'sleeve_type': None,
            'stack_quantity': None,
            'stack_height': None,
            'calculated_per_card': None,
            '_name_manually_edited': False
        }
        st.session_state.components.append(new_component)
        st.rerun()

    # PDF Upload UI — always visible
    st.markdown("---")
    st.subheader("Extract Components from Rulebook PDF")

    st.caption("Upload a board game rulebook to automatically extract the component list. Only the first 15 pages are analyzed — component lists are usually near the start.")

    _upload_key = f"pdf_upload_{st.session_state.get('pdf_upload_counter', 0)}"
    pdf_file = st.file_uploader("Choose a PDF file", type=['pdf'], key=_upload_key)

    if pdf_file is not None:
        # Guard: only run the (expensive) AI extraction when the file changes.
        # On reruns caused by checkbox ticks, name edits, player-count changes, etc.
        # the file object is the same — skip the API call and reuse the cached result.
        last_extracted = st.session_state.get('last_extracted_pdf_name')
        needs_extraction = (
            last_extracted != pdf_file.name
            or 'pdf_extraction_result' not in st.session_state
        )

        if needs_extraction:
            # New file uploaded — reset any stale workflow state from a previous extraction
            # so we always show the review form first (not the material-defaults screen).
            st.session_state.show_material_defaults = False
            st.session_state.pending_import_components = []
            st.session_state.selected_pdf_components = set()
            # Reset Quick Defaults so the new file goes through the blocking form again.
            # Reset both the flag AND the dict to prevent stale values leaking into
            # the new extraction's auto-fill.
            st.session_state.quick_defaults_done = False
            st.session_state.quick_defaults = {}

            # Process PDF
            with st.spinner("Extracting text from PDF — this may take up to 60 seconds for scanned PDFs..."):
                try:
                    pdf_text = extract_text_from_pdf(pdf_file)
                except Exception as e:
                    st.error(f"Could not extract text from PDF: {str(e)}")
                    st.stop()

            # Check AI configuration
            try:
                ai_settings = load_ai_settings()
            except Exception as e:
                st.error(f"Could not load AI settings: {str(e)}")
                st.stop()

            if ai_settings['provider'] == 'none' or not ai_settings['api_key']:
                st.warning("AI provider not configured. Please set up an AI provider in Settings to use PDF upload.")
                if st.button("Go to Settings"):
                    st.switch_page("pages/Settings.py")
                st.stop()

            # Extract components with AI
            with st.spinner("Analyzing component list..."):
                try:
                    extraction_result = extract_components_with_ai(
                        pdf_text,
                        ai_settings['provider'],
                        ai_settings['api_key']
                    )
                except Exception as e:
                    _err_str = str(e)
                    if '529' in _err_str or 'overloaded' in _err_str.lower():
                        st.warning("The AI service is currently overloaded. Please wait a moment and try again.")
                    elif '401' in _err_str or 'auth' in _err_str.lower():
                        st.warning("API key invalid or expired. Check your key in Settings.")
                    elif '429' in _err_str or 'rate' in _err_str.lower():
                        st.warning("Rate limit reached. Please wait a few seconds and try again.")
                    else:
                        st.warning(f"Analysis failed: {_err_str}")
                    if st.button("Try Again"):
                        st.rerun()
                    st.stop()

            # Extract flat component list for downstream compat
            flat_components = extraction_result.get('components', [])

            # Store in session state (cache the result + filename so we skip re-extraction on reruns)
            st.session_state.pdf_extraction_result = extraction_result
            st.session_state.last_extracted_pdf_name = pdf_file.name
            if 'pdf_components' not in st.session_state or not st.session_state.pdf_components:
                st.session_state.pdf_components = flat_components

        else:
            # Reuse cached extraction result — no AI call needed
            extraction_result = st.session_state.pdf_extraction_result

        # Gate 1: Quick Defaults — blocking form shown once per PDF before review.
        # Only shown for PDF-extracted components (not manual entry).
        if not st.session_state.get('quick_defaults_done', False):
            render_quick_defaults()
            st.stop()

        # Gate 2: Material defaults workflow (shown after user clicks "Continue →")
        elif st.session_state.get('show_material_defaults', False):
            render_material_defaults_and_expansion_workflow()
            # Stop rendering — don't show Component Summary / nav buttons
            # below while the material-defaults screen is active.
            st.stop()
        else:
            # Display extracted components for review (uses full result for V2 groups)
            render_pdf_extraction_review(extraction_result)
            # Show expansion upload section after base game review
            render_expansion_upload_section()
            # Stop rendering — don't show Component Summary / nav buttons while
            # the review form is active (they'd be confusing and non-functional).
            st.stop()

    # Display existing components
    if st.session_state.components:
        st.markdown("---")
        st.subheader("Current Components")

        # Check if there are newly added components that need dimensions
        newly_added_ids = st.session_state.get('newly_added_component_ids', [])
        if newly_added_ids:
            st.success(f"Added {len(newly_added_ids)} components. Enter dimensions for each component below.")
            st.caption("Click each component to expand it and fill in Length, Width, and Height.")

        components_to_remove = []

        for idx, component in enumerate(st.session_state.components):
            # Auto-expand newly added components, otherwise only expand the last one
            is_newly_added = component['id'] in newly_added_ids
            is_last = (idx == len(st.session_state.components) - 1)
            should_expand = is_newly_added or (is_last and not newly_added_ids)

            # Build dynamic summary header
            comp_type = component.get('type', 'Component')
            comp_name = component.get('name', 'New Component')
            comp_qty = component.get('quantity', 1)
            header_text = f"{comp_type} — \"{comp_name}\" × {comp_qty}"

            with st.expander(header_text, expanded=should_expand):
                # All editable fields are wrapped in a per-component form.
                # This batches all changes until Save is clicked, preventing
                # reruns (and expander collapse) on every dimension edit.
                with st.form(f"comp_form_{component['id']}", clear_on_submit=False):

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Component type selector
                        _type_options = ['Cards', 'Tokens', 'Tiles', 'Dice', 'Meeples/Minis', 'Boards', 'Rulebook', 'Other', 'Custom']
                        _current_type = component.get('type', 'Other')
                        if _current_type not in _type_options:
                            _current_type = 'Other'
                        comp_type = st.selectbox(
                            "Type",
                            options=_type_options,
                            index=_type_options.index(_current_type),
                            key=f"type_{component['id']}"
                        )

                    with col2:
                        # Quantity
                        new_quantity = st.number_input(
                            "Quantity",
                            min_value=1,
                            max_value=1000,
                            value=component.get('quantity', 1),
                            key=f"qty_{component['id']}"
                        )

                    # Component name
                    new_name = st.text_input(
                        "Name",
                        value=component.get('name', f"{comp_type}"),
                        key=f"name_{component['id']}",
                        placeholder=f"e.g., Player cards, Resource tokens, Victory points"
                    )

                    # Show prefill source note when auto-filled
                    if component.get('_needs_dimensions'):
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(f"Suggested: {_prefill_src}. Adjust below if needed.")

                    # Load material standards
                    material_standards = load_material_standards()

                    # MATERIAL SELECTION - varies by component type
                    # Local variables capture the widget values; applied to component on Save.
                    _new_length = component.get('length') or component.get('_prefill_length') or 50.0
                    _new_width  = component.get('width')  or component.get('_prefill_width')  or 50.0
                    _new_height = component.get('height') or component.get('_prefill_height') or 10.0
                    _new_card_stock  = component.get('card_stock', 'standard')
                    _new_sleeve_type = component.get('sleeve_type', 'unsleeved')
                    _new_stack_qty   = component.get('stack_quantity', component.get('quantity', 1))
                    _new_stack_hgt   = component.get('stack_height', 10.0)
                    _new_material    = component.get('material', 'standard')
                    _new_mat_cat     = component.get('material_category', '')
                    _calculated_per_card = component.get('calculated_per_card')
                    _card_validation_msg = None
                    _card_validation_level = None  # 'success', 'caption', 'warning'

                    if comp_type == 'Cards':
                        card_stock_options = {
                            'standard': 'Standard 300gsm (0.3mm)',
                            'premium': 'Premium 350gsm (0.4mm)',
                            'tarot': 'Tarot weight (0.5mm)',
                            'custom': 'Custom thickness'
                        }
                        sleeve_options = {
                            'unsleeved': 'Unsleeved',
                            'thin': 'Thin (+0.1mm)',
                            'premium': 'Premium (+0.15mm)'
                        }
                        preset_sizes = {
                            'Poker': (88.9, 63.5),
                            'Mini': (44.0, 67.0),
                            'Tarot': (120.0, 70.0),
                            'Bridge': (88.0, 56.0),
                            'Custom': None
                        }

                        def format_preset_label(key):
                            if key == 'Custom':
                                return 'Custom'
                            _l, _w = preset_sizes[key]
                            return f"{key} ({_l}×{_w}mm)"

                        current_card_stock = component.get('card_stock') or 'standard'
                        _qd_sleeves = st.session_state.get('quick_defaults', {}).get('cards_sleeved', 'unsleeved')
                        current_sleeve_type = component.get('sleeve_type') or _qd_sleeves

                        # Row 1: Card stock | Sleeves | Card size — all on one line
                        cs_col, sl_col, sz_col = st.columns(3)
                        with cs_col:
                            _new_card_stock = st.selectbox(
                                "Card stock",
                                options=list(card_stock_options.keys()),
                                format_func=lambda x: card_stock_options[x],
                                index=list(card_stock_options.keys()).index(current_card_stock),
                                key=f"card_stock_{component['id']}"
                            )
                        with sl_col:
                            _new_sleeve_type = st.selectbox(
                                "Sleeves",
                                options=list(sleeve_options.keys()),
                                format_func=lambda x: sleeve_options[x],
                                index=list(sleeve_options.keys()).index(current_sleeve_type),
                                key=f"sleeve_{component['id']}"
                            )
                        with sz_col:
                            size_preset = st.selectbox(
                                "Card size",
                                options=list(preset_sizes.keys()),
                                format_func=format_preset_label,
                                key=f"card_preset_{component['id']}"
                            )
                        _new_mat_cat = 'cards'
                        _new_material = _new_card_stock

                        # Apply preset dimensions
                        if size_preset != 'Custom':
                            _preset_l, _preset_w = preset_sizes[size_preset]
                            _new_length = _preset_l
                            _new_width  = _preset_w
                            st.caption(f"{_preset_l}mm × {_preset_w}mm")
                        else:
                            _cl, _cw = st.columns(2)
                            with _cl:
                                _new_length = st.number_input(
                                    "Length (mm)",
                                    value=float(component.get('length') or 50.0),
                                    step=0.1, format="%.1f",
                                    key=f"card_len_{component['id']}"
                                )
                            with _cw:
                                _new_width = st.number_input(
                                    "Width (mm)",
                                    value=float(component.get('width') or 50.0),
                                    step=0.1, format="%.1f",
                                    key=f"card_wid_{component['id']}"
                                )

                        # Row 2: Stack measurement
                        _sc, _sh = st.columns(2)
                        with _sc:
                            _new_stack_qty = st.number_input(
                                "Cards in deck",
                                value=component.get('stack_quantity', component.get('quantity', 1)),
                                min_value=1,
                                key=f"stack_qty_{component['id']}"
                            )
                        with _sh:
                            _new_stack_hgt = st.number_input(
                                "Stack height (mm)",
                                value=float(component.get('stack_height', 10.0)),
                                step=0.1, format="%.1f",
                                key=f"stack_height_{component['id']}"
                            )

                        # Calculate per-card thickness for validation display
                        if _new_stack_qty and _new_stack_hgt:
                            _calculated_per_card = _new_stack_hgt / _new_stack_qty
                            _new_height = _calculated_per_card
                            if 0.28 <= _calculated_per_card <= 0.35:
                                _card_validation_msg = f"{_calculated_per_card:.2f}mm per card — standard thickness"
                                _card_validation_level = 'success'
                            elif 0.35 < _calculated_per_card <= 0.45:
                                _card_validation_msg = f"{_calculated_per_card:.2f}mm per card — premium cards"
                                _card_validation_level = 'caption'
                            elif _calculated_per_card > 0.6:
                                _card_validation_msg = f"{_calculated_per_card:.2f}mm per card — thicker than normal. Premium linen cards or measurement error?"
                                _card_validation_level = 'warning'
                            else:
                                _card_validation_msg = f"{_calculated_per_card:.2f}mm per card — verify measurement"
                                _card_validation_level = 'warning'

                        if _card_validation_msg:
                            if _card_validation_level == 'success':
                                st.success(_card_validation_msg)
                            elif _card_validation_level == 'caption':
                                st.caption(_card_validation_msg)
                            else:
                                st.warning(_card_validation_msg)

                    elif comp_type in ['Tokens', 'Tiles']:
                        cardboard_options = {
                            'budget': 'Budget (1.0-1.2mm) - Lightweight games',
                            'standard': 'Standard (1.5mm) - Most modern board games',
                            'premium': 'Premium (2.0mm) - Deluxe editions',
                            'heavy_duty': 'Heavy-duty (2.5mm) - Player boards, chunky tiles',
                            'luxury': 'Luxury (3.0mm) - Premium games',
                            'custom': 'Custom thickness'
                        }
                        _qd_cardboard = st.session_state.get('quick_defaults', {}).get('cardboard_quality', 'standard')
                        _qd_cardboard = _qd_cardboard if _qd_cardboard in cardboard_options else 'standard'
                        current_material = component.get('material') or _qd_cardboard
                        _new_material = st.selectbox(
                            "Cardboard quality",
                            options=list(cardboard_options.keys()),
                            format_func=lambda x: cardboard_options[x],
                            index=list(cardboard_options.keys()).index(current_material),
                            key=f"material_{component['id']}"
                        )
                        _new_mat_cat = 'cardboard'

                        if _new_material != 'custom':
                            thickness = material_standards['cardboard'][_new_material]['thickness_mm']
                            _new_height = thickness
                            st.number_input(
                                "Height (mm)",
                                value=thickness,
                                disabled=True,
                                key=f"thickness_disabled_{component['id']}"
                            )
                            st.caption(f"Thickness: {thickness}mm (+1mm clearance applied for humidity swell)")
                        else:
                            _new_height = st.number_input(
                                "Height (mm)",
                                value=float(component.get('height') or 1.5),
                                step=0.1, format="%.1f",
                                key=f"thickness_custom_{component['id']}"
                            )

                        _tl, _tw = st.columns(2)
                        with _tl:
                            _new_length = st.number_input(
                                "Length (mm)",
                                value=float(component.get('length') or component.get('_prefill_length') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"len_{component['id']}"
                            )
                        with _tw:
                            _new_width = st.number_input(
                                "Width (mm)",
                                value=float(component.get('width') or component.get('_prefill_width') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"wid_{component['id']}"
                            )
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(_prefill_src)

                    elif comp_type == 'Boards':
                        _b1, _b2, _b3 = st.columns(3)
                        with _b1:
                            _new_length = st.number_input(
                                "Length (mm)",
                                value=float(component.get('length') or component.get('_prefill_length') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"board_len_{component['id']}"
                            )
                        with _b2:
                            _new_width = st.number_input(
                                "Width (mm)",
                                value=float(component.get('width') or component.get('_prefill_width') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"board_wid_{component['id']}"
                            )
                        with _b3:
                            _new_height = st.number_input(
                                "Height (mm)",
                                value=float(component.get('height') or component.get('_prefill_height') or 10.0),
                                step=0.1, format="%.1f",
                                key=f"board_hgt_{component['id']}"
                            )
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(_prefill_src)

                    elif comp_type == 'Meeples/Minis':
                        _m1, _m2, _m3 = st.columns(3)
                        with _m1:
                            _new_length = st.number_input(
                                "Length (mm)",
                                value=float(component.get('length') or component.get('_prefill_length') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"meeple_len_{component['id']}"
                            )
                        with _m2:
                            _new_width = st.number_input(
                                "Width (mm)",
                                value=float(component.get('width') or component.get('_prefill_width') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"meeple_wid_{component['id']}"
                            )
                        with _m3:
                            _new_height = st.number_input(
                                "Height (mm)",
                                value=float(component.get('height') or component.get('_prefill_height') or 10.0),
                                step=0.1, format="%.1f",
                                key=f"meeple_hgt_{component['id']}"
                            )
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(_prefill_src)

                    elif comp_type == 'Dice':
                        dice_presets = {
                            'Standard d6 (16mm)': (16.0, 16.0, 16.0),
                            'Custom': None
                        }
                        dice_preset = st.selectbox(
                            "Dice size",
                            options=list(dice_presets.keys()),
                            key=f"dice_preset_{component['id']}"
                        )
                        if dice_preset != 'Custom':
                            _d_l, _d_w, _d_h = dice_presets[dice_preset]
                            _new_length = _d_l
                            _new_width  = _d_w
                            _new_height = _d_h
                            st.caption(f"{_d_l}mm × {_d_w}mm × {_d_h}mm")
                        else:
                            _d1, _d2, _d3 = st.columns(3)
                            with _d1:
                                _new_length = st.number_input(
                                    "Length (mm)",
                                    value=float(component.get('length') or component.get('_prefill_length') or 16.0),
                                    step=0.1, format="%.1f",
                                    key=f"dice_len_{component['id']}"
                                )
                            with _d2:
                                _new_width = st.number_input(
                                    "Width (mm)",
                                    value=float(component.get('width') or component.get('_prefill_width') or 16.0),
                                    step=0.1, format="%.1f",
                                    key=f"dice_wid_{component['id']}"
                                )
                            with _d3:
                                _new_height = st.number_input(
                                    "Height (mm)",
                                    value=float(component.get('height') or component.get('_prefill_height') or 16.0),
                                    step=0.1, format="%.1f",
                                    key=f"dice_hgt_{component['id']}"
                                )
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(_prefill_src)

                    elif comp_type == 'Rulebook':
                        _r1, _r2, _r3 = st.columns(3)
                        with _r1:
                            _new_length = st.number_input(
                                "Length (mm)",
                                value=float(component.get('length') or component.get('_prefill_length') or 210.0),
                                step=0.1, format="%.1f",
                                key=f"rulebook_len_{component['id']}"
                            )
                        with _r2:
                            _new_width = st.number_input(
                                "Width (mm)",
                                value=float(component.get('width') or component.get('_prefill_width') or 148.0),
                                step=0.1, format="%.1f",
                                key=f"rulebook_wid_{component['id']}"
                            )
                        with _r3:
                            _new_height = st.number_input(
                                "Height (mm)",
                                value=float(component.get('height') or component.get('_prefill_height') or 10.0),
                                step=0.1, format="%.1f",
                                key=f"rulebook_hgt_{component['id']}"
                            )
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(_prefill_src)

                    else:  # Custom / Other
                        _o1, _o2, _o3 = st.columns(3)
                        with _o1:
                            _new_length = st.number_input(
                                "Length (mm)",
                                value=float(component.get('length') or component.get('_prefill_length') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"len_{component['id']}"
                            )
                        with _o2:
                            _new_width = st.number_input(
                                "Width (mm)",
                                value=float(component.get('width') or component.get('_prefill_width') or 50.0),
                                step=0.1, format="%.1f",
                                key=f"wid_{component['id']}"
                            )
                        with _o3:
                            _new_height = st.number_input(
                                "Height (mm)",
                                value=float(component.get('height') or component.get('_prefill_height') or 10.0),
                                step=0.1, format="%.1f",
                                key=f"hgt_{component['id']}"
                            )
                        _prefill_src = component.get('_prefill_source')
                        if _prefill_src:
                            st.caption(_prefill_src)

                    # ── Save button (inside form — batches all changes) ────────────
                    save_clicked = st.form_submit_button("Save", use_container_width=True)

                    if save_clicked:
                        # Apply identity fields
                        component['quantity'] = int(new_quantity)
                        component['name']     = new_name

                        # Detect type change — clear prefill/dimension data on change
                        _prev_type = component.get('type', 'Other')
                        if _prev_type != comp_type:
                            for _fld in ('length', 'width', 'height',
                                         '_prefill_length', '_prefill_width', '_prefill_height',
                                         '_prefill_source', '_prefill_complete'):
                                component.pop(_fld, None)
                            if not component.get('_name_manually_edited', False):
                                component['name'] = comp_type
                            component['_last_type'] = comp_type
                        component['type'] = comp_type

                        # Apply dimension values from local variables
                        component['length'] = float(_new_length)
                        component['width']  = float(_new_width)
                        component['height'] = float(_new_height)

                        # Apply material fields
                        if comp_type == 'Cards':
                            component['card_stock']        = _new_card_stock
                            component['sleeve_type']       = _new_sleeve_type
                            component['material']          = _new_card_stock
                            component['material_category'] = 'cards'
                            component['stack_quantity']    = int(_new_stack_qty)
                            component['stack_height']      = float(_new_stack_hgt)
                            if _calculated_per_card is not None:
                                component['calculated_per_card'] = _calculated_per_card
                        elif comp_type in ['Tokens', 'Tiles']:
                            component['material']          = _new_material
                            component['material_category'] = 'cardboard'

                        # Clear needs_dimensions flag when data is entered
                        if component.get('_needs_dimensions'):
                            if (component['length'] != 50.0 or
                                    component['width'] != 50.0 or
                                    component['height'] != 10.0):
                                component['_needs_dimensions'] = False
                                if 'newly_added_component_ids' in st.session_state:
                                    _newly = st.session_state.newly_added_component_ids
                                    if component['id'] in _newly:
                                        _newly.remove(component['id'])

                        component['details'] = get_component_breakdown(component)
                        st.rerun()

                # Remove button lives OUTSIDE the form (st.button not allowed inside st.form)
                if st.button(f"× Remove", key=f"remove_{component['id']}"):
                    components_to_remove.append(component['id'])

        # Remove marked components
        if components_to_remove:
            st.session_state.components = [c for c in st.session_state.components if c['id'] not in components_to_remove]
            st.rerun()

    # Summary sidebar
    st.markdown("---")
    st.subheader("Component Summary")

    if st.session_state.components:
        total_volume = sum(calculate_component_volume(c) for c in st.session_state.components)

        # Store volume in each component for later use (e.g., tray analyzer)
        for comp in st.session_state.components:
            comp['volume'] = calculate_component_volume(comp)

        total_volume_cm3 = total_volume / 1000

        # Get box volume for comparison
        if 'box_config' in st.session_state:
            box_config = st.session_state.box_config
            available_height = box_config['height']
            box_volume_cm3 = (box_config['length'] * box_config['width'] * available_height) / 1000

            percentage = (total_volume_cm3 / box_volume_cm3) * 100

            # Check if any components have placeholder dimensions
            has_placeholder_dimensions = any(
                c.get('_needs_dimensions', False) for c in st.session_state.components
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Components", len(st.session_state.components))
            with col2:
                st.metric("Total Volume", f"{total_volume_cm3:.1f} cm³")
            with col3:
                if has_placeholder_dimensions:
                    st.metric("Box Fill", "Pending")
                else:
                    st.metric("Box Fill", f"{percentage:.1f}%")

            # Warnings (only show if no placeholder dimensions)
            if not has_placeholder_dimensions:
                if percentage > 90:
                    st.error("Components exceed box capacity. Remove some components or use a larger box.")
                elif percentage > 70:
                    st.warning("Tight fit — components use >70% of box volume. Consider clearances and wall thickness.")
                elif percentage < 30:
                    st.caption("Lots of space available — consider multi-tray stacking or expansion storage.")

        # Component list
        with st.expander("Full component list"):
            for comp in st.session_state.components:
                volume = calculate_component_volume(comp)
                st.markdown(f"- **{comp['name']}**: {comp['quantity']}× {comp['type']} ({volume/1000:.1f} cm³)")

    else:
        st.caption("Click 'Add Component' to start building your inventory.")

    return st.session_state.components
