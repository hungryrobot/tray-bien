"""
AI-powered tray structure analysis.

Analyzes board game components and suggests optimal tray layouts based on:
- Player count detection from component patterns
- Per-player vs shared resource grouping
- Card storage requirements
- Setup component identification
- Volume-based layer count recommendations

GAME-SPECIFIC TRAY STRUCTURE PATTERNS - REFERENCE EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

PATTERN 1: GRAB-AND-GO PLAYER TRAYS
When components are described as "starting", "give each player", or "begins with"
Example: Wingspan-style games where each player gets pre-assembled components

Structure:
✓ Individual removable player trays (one per player)
✓ Each tray contains that player's starting resources
✓ Deal one tray to each player at setup and start playing
✓ Trays leave the box during play

Keywords that trigger Pattern 1:
- "starting resources", "give each player", "begins with"
- "initial setup", "player's starting", "each player receives"

═══════════════════════════════════════════════════════════════════════════════

PATTERN 2: STORAGE COMPARTMENTS
When components form decks/pools that are drawn from during gameplay
Example: Cacao - "Shuffle your worker tiles and place them face-down"

Structure:
✓ Per-player storage compartments in one tray (NOT individual trays)
✓ Each compartment holds one player's shuffled deck
✓ Keeps decks separate for organization
✓ Compartments stay in box during play

Keywords that trigger Pattern 2:
- "shuffle", "draw pile", "deck", "face-down"
- "mix", "randomly", "pool", "supply"

EXAMPLE - CACAO:
Components:
* 44 worker tiles (11 red, 11 purple, 11 white, 11 yellow)
* 4 water carriers (meeples, 1 per color)
Setup: "Shuffle your worker tiles and place them face-down..."

Optimal Structure:
✓ Tray 1: Player Storage (4 compartments)
  - Red: 11 tiles + 1 meeple
  - Purple: 11 tiles + 1 meeple
  - White: 11 tiles + 1 meeple
  - Yellow: 11 tiles + 1 meeple
Why: Keeps each player's shuffled deck separate

═══════════════════════════════════════════════════════════════════════════════

PATTERN 3: NO PLAYER COMPONENTS
All shared resources, no player-specific items
Example: Cooperative games or games with no player colors

Structure:
✓ Shared resource trays only
✓ Card storage trays
✓ Setup component trays
✓ No player-specific organization needed

═══════════════════════════════════════════════════════════════════════════════
"""

from typing import List, Dict, Any
import re


def analyze_tray_structure(components: List[dict], box_config: dict) -> dict:
    """
    Main analysis function that coordinates all detection logic.

    Args:
        components: List of component dicts from st.session_state.components
        box_config: Box dimensions from st.session_state.box_config

    Returns:
        Dict with structure:
        {
            'suggested_trays': [
                {
                    'name': 'Player Trays',
                    'type': 'player_tray',
                    'count': 4,
                    'components': [...],
                    'reason': 'Quick setup - deal one tray per player',
                    'icon': '✓'
                },
                ...
            ],
            'player_count': 4,
            'suggested_layer_count': 2,
            'volume_utilization': 0.75
        }
    """
    suggested_trays = []

    # Detect player count
    player_count = detect_player_count(components)

    # Group components by purpose (only if we detected players)
    if player_count > 0:
        player_components = group_player_components(components, player_count)
    else:
        player_components = []

    shared_resources = detect_shared_resources(components, player_components)
    card_analysis = analyze_card_storage(components)
    setup_components = detect_setup_components(components)

    # Build tray suggestions

    # 1. Player trays (if applicable)
    if player_components and player_count > 0:
        # Detect which pattern to use
        tray_pattern = detect_player_tray_pattern(player_components)

        if tray_pattern == 'grab_and_go':
            # Pattern 1: Individual removable player trays
            suggested_trays.append({
                'name': 'Player Trays (Grab-and-Go)',
                'type': 'player_tray_individual',
                'count': player_count,
                'components': player_components,
                'reason': 'Quick setup - deal one tray per player and start playing immediately',
                'icon': '✓',
                'pattern': 'Pattern 1: Grab-and-Go'
            })
        else:
            # Pattern 2: Storage compartments in one tray
            suggested_trays.append({
                'name': 'Player Storage Compartments',
                'type': 'player_tray_storage',
                'count': 1,
                'components': player_components,
                'reason': f'Organized storage for {player_count} players - keeps decks/components separate',
                'icon': '✓',
                'pattern': 'Pattern 2: Storage Compartments'
            })

    # 2. Shared resource bank
    if shared_resources['components']:
        if shared_resources['use_nested']:
            suggested_trays.append({
                'name': 'Resource Bank with Nested Sub-Trays',
                'type': 'nested_resource_bank',
                'count': 1,
                'sub_tray_count': shared_resources['sub_tray_count'],
                'components': shared_resources['components'],
                'reason': 'Both ends of table can access resources without passing',
                'icon': '✓'
            })
        else:
            suggested_trays.append({
                'name': 'Shared Resource Bank',
                'type': 'resource_bank',
                'count': 1,
                'components': shared_resources['components'],
                'reason': 'Centralized storage for shared game components',
                'icon': '✓'
            })

    # 3. Card storage
    if card_analysis['deck_count'] > 0:
        if card_analysis['suggest_angled_wells']:
            suggested_trays.append({
                'name': 'Card Tray with Angled Wells',
                'type': 'angled_card_storage',
                'count': 1,
                'components': card_analysis['components'],
                'reason': 'Angled layout makes thumbing through cards easy during play',
                'icon': '✓'
            })
        else:
            suggested_trays.append({
                'name': 'Card Storage',
                'type': 'card_storage',
                'count': 1,
                'components': card_analysis['components'],
                'reason': 'Keeps cards organized and protected',
                'icon': '✓'
            })

    # 4. Setup components
    if setup_components:
        suggested_trays.append({
            'name': 'Setup/Misc Tray',
            'type': 'setup_tray',
            'count': 1,
            'components': setup_components,
            'reason': 'Everything needed for setup in one place',
            'icon': '✓'
        })

    # Calculate layer recommendation
    layer_count = calculate_layer_recommendation(components, box_config)

    # Calculate volume utilization
    total_component_volume = sum(c.get('volume', 0) for c in components)
    box_volume = box_config['length'] * box_config['width'] * box_config['height']
    volume_utilization = min(total_component_volume / box_volume, 1.0) if box_volume > 0 else 0.5

    return {
        'suggested_trays': suggested_trays,
        'player_count': player_count,
        'suggested_layer_count': layer_count,
        'volume_utilization': volume_utilization
    }


def detect_player_count(components: List[dict]) -> int:
    """
    Detect probable player count from component patterns.

    Logic:
    - Look for quantities like 4, 8, 12, 16 (likely per-player multiples)
    - Look for color variations in names ("red tokens", "blue meeples")
    - Look for "player board" components
    - Return 0 if no player-specific patterns found (Pattern 3)
    - Default to 4 if patterns unclear
    """
    # Check for explicit player boards
    player_board_count = 0
    for comp in components:
        name_lower = comp.get('name', '').lower()
        if 'player board' in name_lower or 'player mat' in name_lower:
            player_board_count = max(player_board_count, comp.get('quantity', 0))

    if player_board_count > 0:
        return player_board_count

    # Look for faction-based components (STRONGEST signal for asymmetric games)
    factions_found = set()

    for comp in components:
        faction = comp.get('faction', '').strip()
        if faction:
            factions_found.add(faction)

    # If we found 2+ factions, this is definitely a faction-based player game
    if len(factions_found) >= 2:
        return len(factions_found)

    # Look for color-coded components (STRONG signal for symmetric games)
    color_keywords = [
        'red', 'blue', 'green', 'yellow', 'purple', 'black', 'white', 'orange',
        'cyan', 'magenta', 'pink', 'brown', 'teal', 'indigo', 'gray', 'grey',
        'crimson', 'scarlet', 'azure', 'turquoise', 'lime', 'navy', 'maroon'
    ]
    colors_found = set()

    for comp in components:
        # Check explicit color field first
        color = comp.get('color', '').strip()
        if color:
            colors_found.add(color)
            continue

        # Fall back to keyword search in text
        name_lower = comp.get('name', '').lower()
        type_lower = comp.get('type', '').lower()
        details_lower = comp.get('details', '').lower() if comp.get('details') else ''
        combined_text = f"{name_lower} {type_lower} {details_lower}"

        for color in color_keywords:
            if color in combined_text:
                colors_found.add(color)
                break

    # If we found 2+ colors, this is definitely a player-component game
    if len(colors_found) >= 2:
        return len(colors_found)

    # If we found NO factions, NO colors, and NO player boards, this is likely Pattern 3 (no players)
    # Don't try to infer from quantities alone - too error-prone
    return 0  # No player components detected


def group_player_components(components: List[dict], player_count: int) -> List[dict]:
    """
    Identify which components are per-player.

    Logic:
    - Quantities divisible by player_count (e.g., 16 tokens / 4 players = 4 per player)
    - Component names containing colors or "player"
    - Return list of component dicts that should go in player trays
    """
    player_components = []

    for comp in components:
        name_lower = comp.get('name', '').lower()
        type_lower = comp.get('type', '').lower()
        details_lower = comp.get('details', '').lower() if comp.get('details') else ''
        combined_text = f"{name_lower} {type_lower} {details_lower}"
        quantity = comp.get('quantity', 0)

        # Check if component is explicitly marked as NOT player-specific
        if comp.get('player_specific') == False:
            continue  # Skip this component, it's shared

        # Check if component has explicit faction or color markers (STRONGEST signal)
        if comp.get('faction') or comp.get('color') or comp.get('player_specific') == True:
            player_components.append(comp)
            continue

        # Check if name/type/details suggests per-player
        per_player_keywords = [
            'player', 'faction', 'red', 'blue', 'green', 'yellow', 'purple',
            'black', 'white', 'orange', 'meeple', 'worker',
            'cyan', 'magenta', 'pink', 'brown', 'teal', 'indigo', 'gray', 'grey',
            'crimson', 'scarlet', 'azure', 'turquoise', 'lime', 'navy', 'maroon'
        ]
        name_suggests_player = any(keyword in combined_text for keyword in per_player_keywords)

        # Check if quantity divides evenly by player count
        if quantity > 0 and quantity % player_count == 0:
            qty_per_player = quantity // player_count
            # Likely per-player if each player gets 1-20 of this item
            quantity_suggests_player = 1 <= qty_per_player <= 20
        else:
            quantity_suggests_player = False

        # Include if either name or quantity suggests per-player
        if name_suggests_player or quantity_suggests_player:
            player_components.append(comp)

    return player_components


def detect_player_tray_pattern(player_components: List[dict]) -> str:
    """
    Determine if components should be grab-and-go trays or storage compartments.

    PATTERN 1 - Grab-and-Go Player Trays:
    Keywords in component names/descriptions: "starting", "begins with", "give each player"
    Components are dealt at setup and used immediately
    Creates: Individual removable player trays (portable, leave the box during play)

    PATTERN 2 - Storage Compartments:
    Keywords: "shuffle", "draw pile", "mix", "face-down", "deck"
    Components form decks/pools that are drawn from during game
    Creates: Per-player storage compartments in one tray (stay in box during play)

    PATTERN 3 - No Player Components:
    All shared resources, no player-specific items
    Creates: Only shared resource/card/setup trays

    Args:
        player_components: List of components identified as per-player

    Returns:
        'grab_and_go' or 'storage_compartments'
    """
    if not player_components:
        return 'storage_compartments'  # Default if no components

    # Keywords that suggest shuffled decks/draw piles (Pattern 2)
    shuffle_keywords = ['shuffle', 'draw', 'pile', 'deck', 'mix', 'face-down',
                       'randomly', 'pool', 'supply']

    # Keywords that suggest starting resources dealt at setup (Pattern 1)
    starting_keywords = ['starting', 'begins', 'initial', 'give each', 'receives',
                        'dealt', 'start with', 'each player gets']

    shuffle_count = 0
    starting_count = 0

    for comp in player_components:
        comp_name_lower = comp.get('name', '').lower()
        comp_type_lower = comp.get('type', '').lower()

        # Check both name and type for keywords
        combined_text = f"{comp_name_lower} {comp_type_lower}"

        if any(kw in combined_text for kw in shuffle_keywords):
            shuffle_count += 1
        if any(kw in combined_text for kw in starting_keywords):
            starting_count += 1

    # Decision logic: If any components mention shuffling/drawing → storage compartments
    if shuffle_count > 0:
        return 'storage_compartments'

    # If components are starting resources → grab-and-go
    if starting_count > 0:
        return 'grab_and_go'

    # Default to storage compartments (safer for organization)
    return 'storage_compartments'


def detect_shared_resources(components: List[dict], player_components: List[dict]) -> dict:
    """
    Identify shared resource components and determine if nested sub-trays recommended.

    Logic:
    - Tokens/tiles not in player_components
    - If 3+ players AND 3+ shared token types → suggest nested sub-trays
    - Return: {'components': [...], 'use_nested': bool, 'sub_tray_count': 2}
    """
    # Get IDs of player components
    player_comp_ids = {comp.get('id') for comp in player_components}

    # Find shared components (tokens, tiles, resources not assigned to players)
    shared_components = []
    shared_resource_types = ['Tokens', 'Tiles', 'Meeples', 'Cubes', 'Dice']

    for comp in components:
        comp_type = comp.get('type', '')
        comp_id = comp.get('id')

        # Not a player component and is a token-like resource
        if comp_id not in player_comp_ids and comp_type in shared_resource_types:
            shared_components.append(comp)

    # Determine if nested sub-trays recommended
    use_nested = len(shared_components) >= 3
    sub_tray_count = 2 if use_nested else 1

    return {
        'components': shared_components,
        'use_nested': use_nested,
        'sub_tray_count': sub_tray_count
    }


def analyze_card_storage(components: List[dict]) -> dict:
    """
    Analyze card components and recommend storage strategy.

    Logic:
    - Count how many card decks (distinct card components)
    - Check if sleeved (from card_stock/sleeve_type fields)
    - Multiple decks → suggest angled wells
    - Single deck → suggest stacked storage
    - Return: {'deck_count': 2, 'suggest_angled_wells': True, 'sleeved': True, 'components': [...]}
    """
    card_components = [comp for comp in components if comp.get('type') == 'Cards']

    deck_count = len(card_components)

    # Check if any are sleeved
    sleeved = any(comp.get('card_stock') and 'sleeve' in comp.get('card_stock', '').lower()
                  for comp in card_components)

    # Suggest angled wells for multiple decks
    suggest_angled_wells = deck_count >= 2

    return {
        'deck_count': deck_count,
        'suggest_angled_wells': suggest_angled_wells,
        'sleeved': sleeved,
        'components': card_components
    }


def detect_setup_components(components: List[dict]) -> List[dict]:
    """
    Identify components used once at setup then set aside.

    Logic:
    - Dice
    - Rulebook
    - Components with "first player" or "setup" in name
    - Return list of these components
    """
    setup_components = []

    for comp in components:
        comp_type = comp.get('type', '')
        name_lower = comp.get('name', '').lower()

        # Check type
        if comp_type in ['Dice', 'Rulebook']:
            setup_components.append(comp)
            continue

        # Check name keywords
        setup_keywords = ['first player', 'setup', 'start player', 'starting',
                         'round marker', 'turn marker', 'instruction']
        if any(keyword in name_lower for keyword in setup_keywords):
            setup_components.append(comp)

    return setup_components


def calculate_layer_recommendation(components: List[dict], box_config: dict) -> int:
    """
    Recommend 1-4 tray layers based on component volume vs box volume.

    Logic:
    - Sum total component volume (use existing volume calculation)
    - Compare to box volume
    - If fill < 30% → 1 layer
    - If fill 30-60% → 2 layers (most common)
    - If fill 60-85% → 3 layers
    - If fill > 85% → 4 layers (rare, warn about tight fit)
    """
    total_component_volume = sum(comp.get('volume', 0) for comp in components)

    box_volume = box_config['length'] * box_config['width'] * box_config['height']

    if box_volume == 0:
        return 2  # Default

    fill_ratio = total_component_volume / box_volume

    if fill_ratio < 0.30:
        return 1
    elif fill_ratio < 0.60:
        return 2
    elif fill_ratio < 0.85:
        return 3
    else:
        return 4


def calculate_tray_volume(components: List[dict]) -> float:
    """Calculate total volume of components in cm³.

    Args:
        components: List of component dicts with 'volume' field in mm³

    Returns:
        Total volume in cm³
    """
    total_mm3 = sum(c.get('volume', 0) for c in components)
    return total_mm3 / 1000  # Convert mm³ to cm³


def calculate_tray_height(components: List[dict], box_width: float, box_length: float) -> float:
    """Estimate tray height from component volume and box footprint.

    Args:
        components: List of component dicts (must have 'volume' field in mm³)
        box_width: Box interior width in mm
        box_length: Box interior length in mm

    Returns:
        Estimated height in mm
    """
    if not components:
        return 20.0  # Minimum tray height

    volume_cm3 = calculate_tray_volume(components)

    if volume_cm3 == 0:
        # No volume data, use type-based heuristic
        return estimate_height_from_types(components)

    # Box footprint in cm²
    footprint_cm2 = (box_width / 10.0) * (box_length / 10.0)

    if footprint_cm2 == 0:
        return 30.0  # Default

    # Height = Volume / Footprint (cm to mm)
    height_cm = volume_cm3 / footprint_cm2
    height_mm = height_cm * 10.0

    # Add walls/floor thickness (~8mm total)
    height_mm += 8.0

    # Clamp to reasonable range
    return max(20.0, min(height_mm, 80.0))


def estimate_height_from_types(components: List[dict]) -> float:
    """Fallback heuristic when volume data missing.

    Args:
        components: List of component dicts with 'type' field

    Returns:
        Estimated height in mm based on component types
    """
    type_heights = {
        'Cards': 60.0,
        'Tokens': 30.0,
        'Tiles': 25.0,
        'Dice': 25.0,
        'Meeples/Minis': 40.0,
        'Boards': 15.0,
        'Rulebook': 15.0
    }

    max_height = 30.0  # Default
    for comp in components:
        comp_type = comp.get('type', 'Tokens')
        height = type_heights.get(comp_type, 30.0)
        max_height = max(max_height, height)

    return max_height
