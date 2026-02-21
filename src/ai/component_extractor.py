"""
AI-powered component extraction from rulebook PDFs.
"""

import json
from pathlib import Path
import re


def load_ai_settings() -> dict:
    """Load AI provider and API key from settings.json.

    Returns:
        dict: {'provider': str, 'api_key': str}
              provider is one of: 'none', 'claude', 'openai', 'gemini', 'ollama'
    """
    settings_file = Path(__file__).parent.parent.parent / "saved_designs" / ".settings.json"

    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)

        provider = settings.get('ai_provider', 'claude')

        # Get API key for the selected provider
        api_key = None
        if provider in ['claude', 'openai', 'gemini']:
            api_key = settings.get('api_keys', {}).get(provider)

        return {
            'provider': provider,
            'api_key': api_key
        }

    except FileNotFoundError:
        # Settings file doesn't exist yet
        return {'provider': 'none', 'api_key': None}
    except Exception as e:
        raise Exception(f"Failed to load AI settings: {str(e)}")


def extract_components_with_ai(pdf_text: str, provider: str, api_key: str) -> dict:
    """Send PDF text to AI and get structured component list with metadata.

    Args:
        pdf_text: Extracted text from PDF
        provider: AI provider ('claude', 'openai', 'gemini', 'ollama')
        api_key: API key for the provider (not needed for Ollama)

    Returns:
        dict: {
            'component_groups': List of group dicts (V2 schema),
            'game_name': str,
            'player_count': dict,
            'factions_or_colors': list,
            'extraction_notes': str,
            'components': flat list of all components (for downstream compat),
            'metadata': {
                'tokens_used': {'prompt_tokens': int, 'completion_tokens': int, 'total_tokens': int},
                'provider': str,
            }
        }

    Raises:
        Exception: If API call fails or response is invalid
    """
    # Diagnostic logging for character count
    print(f"📝 PDF text length: {len(pdf_text):,} characters")
    truncated = len(pdf_text) > 75000
    print(f"📤 Sending {min(len(pdf_text), 75000):,} chars to AI (truncated: {truncated})")

    # Build the prompt
    prompt = _build_extraction_prompt(pdf_text)

    # Call appropriate AI provider (returns tuple: response_text, tokens_used)
    response_text, tokens_used = _call_ai_provider(prompt, provider, api_key)

    # Parse JSON response into V2 grouped format
    extraction_result = _parse_extraction_response(response_text)
    num_groups = len(extraction_result.get('component_groups', []))
    flat_components = _flatten_groups_to_components(extraction_result)
    print(f"✅ AI extracted {num_groups} groups, {len(flat_components)} total components")

    return {
        'component_groups': extraction_result.get('component_groups', []),
        'game_name': extraction_result.get('game_name', ''),
        'player_count': extraction_result.get('player_count', {}),
        'factions_or_colors': extraction_result.get('factions_or_colors', []),
        'extraction_notes': extraction_result.get('extraction_notes', ''),
        'components': flat_components,
        'metadata': {
            'tokens_used': tokens_used,
            'provider': provider,
        }
    }


def _build_extraction_prompt(pdf_text: str) -> str:
    """Build the extraction prompt for V2 grouped schema output."""
    return f"""You are an expert board game analyst extracting component inventory from a rulebook.

**YOUR TASK:** Read the rulebook and output a structured component inventory, pre-grouped by how the components are used in the game.

INPUT TEXT (from rulebook PDF):
{pdf_text[:75000]}

---

**STEP 1: Read the SETUP section first**

Before listing any components, find and read the setup instructions to understand:
- How many players does this support?
- What are the actual player identifiers? (real color names like "Red, Blue, Green", faction names like "Atreides, Harkonnen", etc.)
- NEVER use generic placeholders like "Player 1", "Color 1", "Faction A" as group names if the rulebook uses real names
- What components does each player receive? What goes in the shared pool?

**STEP 2: Group components into 4 categories**

- **player** — Components owned by a specific player/faction. Create one group PER player/faction with their actual name. Quantities should be PER PLAYER (not total). Example: if 4 players each get 3 agents, quantity = 3 (not 12).
- **shared** — Components used by all players together (market decks, shared tokens, supply pools)
- **setup** — Components placed on the board during setup and rarely touched during play (starting tiles, preset tokens, terrain)
- **board_and_rules** — The main game board(s), rulebook, player aid cards. These sit ON TOP of the insert stack and do NOT need tray compartments, but are tracked for total stack height.

**STEP 3: Output the following JSON structure exactly**

{{
  "game_name": "Full game name from the rulebook",
  "player_count": {{"min": 1, "max": 4}},
  "factions_or_colors": ["Red", "Blue", "Green", "Yellow"],
  "component_groups": [
    {{
      "group_name": "Red Player Components",
      "group_type": "player",
      "per_player": true,
      "identical_sets": true,
      "components": [
        {{"name": "Agents", "type": "Meeples/Minis", "quantity": 3, "notes": "Wooden meeples, 1 per player action space"}},
        {{"name": "Player board", "type": "Boards", "quantity": 1, "notes": ""}}
      ]
    }},
    {{
      "group_name": "Shared Supply",
      "group_type": "shared",
      "per_player": false,
      "components": [
        {{"name": "Intrigue cards", "type": "Cards", "quantity": 60, "notes": "Shared draw deck"}}
      ]
    }},
    {{
      "group_name": "Board & Rulebook",
      "group_type": "board_and_rules",
      "per_player": false,
      "notes": "These sit on top of the insert stack and do not need tray compartments",
      "components": [
        {{"name": "Main game board", "type": "Boards", "quantity": 1, "notes": ""}}
      ]
    }}
  ],
  "extraction_notes": "Note any ambiguities here, e.g. 'Quantity of damage tokens was unclear, estimated 30'"
}}

---

**COMPONENT TYPE GUIDE:**

- **Cards** — Playing cards meant to be shuffled/drawn (deck cards, hand cards, faction cards)
- **Tokens** — Small punched cardboard pieces, wooden cubes, discs, markers (no notable thickness)
- **Tiles** — Larger punched cardboard pieces with two sides or notable thickness (hex tiles, terrain tiles, location tiles, action tiles, tactic tiles)
- **Dice** — Any dice
- **Meeples/Minis** — Wooden meeples, plastic miniatures, standees, warriors
- **Boards** — Player boards, mats, the main game board, large reference panels
- **Other** — Player aid sheets, reference cards, scoring pads, anything that doesn't fit above

**Type classification examples:**
- "Reference card" or "Player aid" → **Other** (not Cards — these aren't shuffled)
- "Hex tiles", "Terrain tiles", "Location tiles" → **Tiles** (not Tokens)
- "Wooden cubes", "Resource markers" → **Tokens**
- "Player board", "Command board", "Faction mat" → **Boards**
- "Main game board" → **Boards** (and put in board_and_rules group)

---

**IMPORTANT RULES:**

1. Use REAL names from the rulebook for player groups, not generic ones:
   - ✅ "Atreides Player Components" (if rulebook names that faction)
   - ✅ "Red Player Components" (if rulebook uses colors)
   - ❌ "Player Color 1 Components" (too generic)
   - ❌ "Faction A Components" (only OK if rulebook literally names them Faction A)

2. Quantities for player groups = per player, not total:
   - If 4 players each get 3 agents → quantity: 3 (not 12)
   - Include quantity per player in the group's components

3. If a component appears across ALL player groups with equal quantity → it's player-specific
   - "Each player receives 1 player board" → create 1 entry per player group

4. The main game board belongs in a board_and_rules group, NOT shared

5. Return ONLY valid JSON. No markdown, no code fences, no explanation text before or after.

6. If you cannot find a component list, return:
   {{"game_name": "", "player_count": {{}}, "factions_or_colors": [], "component_groups": [], "extraction_notes": "No component list found in the provided text"}}

7. **IDENTICAL vs. ASYMMETRIC PLAYER SETS:**
   If all players/factions receive IDENTICAL components (same items, same quantities):
   - Create only ONE player group named "Player Components"
   - Set "identical_sets": true on the group
   - List all color/faction names in factions_or_colors
   - Quantities are per player (not total)

   Example (4 players, each get the same components):
   {{
     "group_name": "Player Components",
     "group_type": "player",
     "per_player": true,
     "identical_sets": true,
     "components": [
       {{"name": "Agents", "type": "Meeples/Minis", "quantity": 3}},
       {{"name": "Discs", "type": "Tokens", "quantity": 2}},
       {{"name": "Cubes", "type": "Tokens", "quantity": 16}}
     ]
   }}

   If players/factions have DIFFERENT components (asymmetric game like Hegemony, Root, Vast):
   - Create one group PER faction with their unique name
   - Set "identical_sets": false on each group
   - Each group lists that faction's specific components

   When in doubt, lean toward SEPARATE groups — easier for users to merge than split.
"""


def _call_ai_provider(prompt: str, provider: str, api_key: str) -> tuple:
    """Dispatch to the correct AI provider and return (response_text, tokens_used)."""
    if provider == 'claude':
        return _call_anthropic_api(prompt, api_key)
    elif provider == 'openai':
        return _call_openai_api(prompt, api_key)
    elif provider == 'gemini':
        return _call_gemini_api(prompt, api_key)
    elif provider == 'ollama':
        return _call_ollama_api(prompt)
    else:
        raise Exception(f"Unsupported AI provider: {provider}")


def _call_anthropic_api(prompt: str, api_key: str) -> tuple:
    """Call Anthropic Claude API with structured output and return response with token usage.

    Returns:
        tuple: (response_text, tokens_dict)
    """
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16384,  # Increased to handle very long component lists (faction-based games)
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract token usage
        tokens_used = {
            'prompt_tokens': message.usage.input_tokens,
            'completion_tokens': message.usage.output_tokens,
            'total_tokens': message.usage.input_tokens + message.usage.output_tokens
        }

        return message.content[0].text, tokens_used

    except Exception as e:
        raise Exception(f"Anthropic API error: {str(e)}")


def _call_openai_api(prompt: str, api_key: str) -> tuple:
    """Call OpenAI API with JSON mode and return response with token usage.

    Returns:
        tuple: (response_text, tokens_dict)
    """
    try:
        import openai

        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective for this task
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=16384,  # Increased to handle very long component lists (faction-based games)
            response_format={"type": "json_object"}
        )

        # Extract token usage
        tokens_used = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }

        return response.choices[0].message.content, tokens_used

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


def _call_gemini_api(prompt: str, api_key: str) -> tuple:
    """Call Google Gemini API and return response with token usage.

    Returns:
        tuple: (response_text, tokens_dict)
    """
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        # Use Gemini 2.5 Flash (latest fast model as of Feb 2026)
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                max_output_tokens=16384,  # Increased to handle very long component lists (faction-based games)
            )
        )

        # Extract token usage from response
        tokens_used = {
            'prompt_tokens': response.usage_metadata.prompt_token_count,
            'completion_tokens': response.usage_metadata.candidates_token_count,
            'total_tokens': response.usage_metadata.total_token_count
        }

        return response.text, tokens_used

    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def _call_ollama_api(prompt: str) -> tuple:
    """Call local Ollama API and return response (tokens not available for Ollama).

    Returns:
        tuple: (response_text, None)
    """
    try:
        import requests

        # Ollama default endpoint
        url = "http://localhost:11434/api/generate"

        data = {
            "model": "llama2",  # Default model, user can change in settings
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result.get('response', '[]'), None  # Ollama doesn't provide token usage

    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}. Make sure Ollama is running locally.")


def _parse_extraction_response(response_text: str) -> dict:
    """Parse AI response into V2 extraction result dict.

    Handles V2 (component_groups), V1 with metadata wrapper, and raw array formats.

    Returns:
        dict with keys: game_name, player_count, factions_or_colors, component_groups, extraction_notes

    Raises:
        Exception: If response cannot be parsed at all
    """
    try:
        # Remove markdown code fences if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()

        # Find outermost JSON structure
        obj_start = response_text.find('{')
        obj_end = response_text.rfind('}')
        arr_start = response_text.find('[')
        arr_end = response_text.rfind(']')

        # Prefer object over array (V2 format is an object)
        if obj_start != -1 and (arr_start == -1 or obj_start < arr_start):
            response_text = response_text[obj_start:obj_end+1]
        elif arr_start != -1:
            response_text = response_text[arr_start:arr_end+1]

        # Fix trailing commas
        response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)

        # Parse JSON
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error at position {e.pos}: {str(e)}")
            print(f"📝 Attempting recovery by truncating at last complete object...")

            last_complete = max(
                response_text.rfind('},', 0, e.pos),
                response_text.rfind('}', 0, e.pos)
            )

            if last_complete > 0:
                closing = ']' if response_text[0] == '[' else '}'
                response_text = response_text[:last_complete+1] + closing
                print(f"✂️  Truncated at position {last_complete}, retrying...")
                try:
                    parsed_data = json.loads(response_text)
                    print(f"✅ Recovered from truncated response")
                except json.JSONDecodeError as e2:
                    print(f"❌ Recovery failed: {str(e2)}")
                    raise e
            else:
                print(f"❌ No complete objects found before error position")
                raise

        # Route to appropriate format handler
        if isinstance(parsed_data, dict):
            if 'component_groups' in parsed_data:
                print(f"📦 Parsed V2 format (component_groups)")
                return _validate_v2_response(parsed_data)
            elif 'components' in parsed_data:
                print(f"📦 Parsed V1 format (flat components + metadata) — converting to V2")
                return _convert_v1_to_v2(parsed_data)
            else:
                return _convert_v1_to_v2({'components': [], 'metadata': {}})
        elif isinstance(parsed_data, list):
            print(f"📦 Parsed raw array — converting to V2")
            return _convert_v1_to_v2({'components': parsed_data, 'metadata': {}})
        else:
            raise ValueError("Response is not a JSON array or object")

    except json.JSONDecodeError as e:
        preview = response_text[:500] if len(response_text) > 500 else response_text
        raise Exception(f"AI returned invalid JSON: {str(e)}\n\nResponse preview:\n{preview}")
    except Exception as e:
        raise Exception(f"Failed to parse AI response: {str(e)}")


def _validate_v2_response(data: dict) -> dict:
    """Validate and normalize a V2 format response (has component_groups key).

    Normalizes component types and assigns global extraction_index for Streamlit widget keys.
    """
    valid_types = {'Cards', 'Tiles', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Other', 'Custom'}
    valid_group_types = {'player', 'shared', 'setup', 'board_and_rules'}

    validated_groups = []
    extraction_index = 0

    for group in data.get('component_groups', []):
        if not isinstance(group, dict):
            continue

        group_name = str(group.get('group_name', 'Components')).strip()
        group_type = group.get('group_type', 'shared')
        if group_type not in valid_group_types:
            group_type = 'shared'

        validated_comps = []
        for comp in group.get('components', []):
            if not isinstance(comp, dict):
                continue
            name = str(comp.get('name', '')).strip()
            if not name:
                continue
            comp_type = str(comp.get('type', 'Other')).strip()
            if comp_type not in valid_types:
                comp_type = 'Other'
            try:
                quantity = max(1, int(comp.get('quantity', 1)))
            except (ValueError, TypeError):
                quantity = 1

            validated_comps.append({
                'name': name,
                'type': comp_type,
                'quantity': quantity,
                'notes': str(comp.get('notes', '')).strip(),
                'extraction_index': extraction_index,
                # Compatibility fields for downstream code
                'details': str(comp.get('notes', '')).strip(),
                'player_specific': group_type == 'player',
                'player_identifier': None,
            })
            extraction_index += 1

        validated_groups.append({
            'group_name': group_name,
            'group_type': group_type,
            'per_player': bool(group.get('per_player', False)),
            'identical_sets': bool(group.get('identical_sets', False)),
            'notes': str(group.get('notes', '')).strip(),
            'components': validated_comps,
        })

    return {
        'game_name': str(data.get('game_name', '')).strip(),
        'player_count': data.get('player_count', {}),
        'factions_or_colors': list(data.get('factions_or_colors', [])),
        'component_groups': validated_groups,
        'extraction_notes': str(data.get('extraction_notes', '')).strip(),
    }


def _convert_v1_to_v2(v1_data: dict) -> dict:
    """Convert V1 flat component list to V2 grouped format for backward compatibility."""
    components = v1_data.get('components', [])
    valid_types = {'Cards', 'Tiles', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Other', 'Custom'}

    player_groups = {}  # player_id -> list of comps
    shared_comps = []
    extraction_index = 0

    for comp in components:
        if not isinstance(comp, dict):
            continue
        name = str(comp.get('name', '')).strip()
        if not name:
            continue
        comp_type = str(comp.get('type', 'Other')).strip()
        if comp_type not in valid_types:
            comp_type = 'Other'
        try:
            quantity = max(1, int(comp.get('quantity', 1)))
        except (ValueError, TypeError):
            quantity = 1

        validated_comp = {
            'name': name,
            'type': comp_type,
            'quantity': quantity,
            'notes': str(comp.get('details', '')).strip(),
            'details': str(comp.get('details', '')).strip(),
            'extraction_index': extraction_index,
            'player_specific': bool(comp.get('player_specific', False)),
            'player_identifier': comp.get('player_identifier'),
        }
        extraction_index += 1

        player_id = comp.get('player_identifier')
        if player_id and isinstance(player_id, str):
            player_id = player_id.strip()
            if player_id not in player_groups:
                player_groups[player_id] = []
            player_groups[player_id].append(validated_comp)
        else:
            shared_comps.append(validated_comp)

    component_groups = []
    for player_id, comps in player_groups.items():
        component_groups.append({
            'group_name': f"{player_id} Player Components",
            'group_type': 'player',
            'per_player': True,
            'notes': '',
            'components': comps,
        })
    if shared_comps:
        component_groups.append({
            'group_name': 'Shared Components',
            'group_type': 'shared',
            'per_player': False,
            'notes': '',
            'components': shared_comps,
        })

    return {
        'game_name': '',
        'player_count': {},
        'factions_or_colors': [],
        'component_groups': component_groups,
        'extraction_notes': '',
    }


def _flatten_groups_to_components(extraction_result: dict) -> list:
    """Flatten component_groups into a flat list for downstream compatibility.

    Stamps each component with _group_name, _group_type, _per_player from its group.
    """
    flat = []
    for group in extraction_result.get('component_groups', []):
        group_name = group.get('group_name', '')
        group_type = group.get('group_type', 'shared')
        per_player = group.get('per_player', False)
        for comp in group.get('components', []):
            stamped = dict(comp)
            stamped['_group_name'] = group_name
            stamped['_group_type'] = group_type
            stamped['_per_player'] = per_player
            flat.append(stamped)
    return flat


def _build_expansion_prompt(pdf_text: str, base_game_name: str, existing_groups: list) -> str:
    """Build prompt for extracting expansion-only components.

    Lists existing group names so the AI knows what NOT to re-extract.
    Outputs the same V2 JSON schema as the base game prompt.
    """
    existing_summary = '\n'.join(
        f'  - {g.get("group_name", "")}' for g in existing_groups
    )
    return f"""You are analyzing a board game EXPANSION rulebook to extract NEW component information.

BASE GAME: {base_game_name}

EXISTING BASE GAME COMPONENT GROUPS (do NOT re-extract these):
{existing_summary}

Extract ONLY the NEW components added by this expansion. Do not repeat base game components.

EXPANSION RULEBOOK TEXT:
{pdf_text[:75000]}

---

Output the same V2 JSON schema as the base game extraction:

{{
  "game_name": "expansion name only (e.g. 'Wingspan: Oceania Expansion')",
  "player_count": {{"min": 1, "max": 4}},
  "factions_or_colors": ["any NEW factions or colors added by this expansion only"],
  "extraction_notes": "describe what was and was not extracted, any ambiguities",
  "component_groups": [
    {{
      "group_name": "group name",
      "group_type": "player|shared|setup|board_and_rules",
      "per_player": true,
      "identical_sets": true,
      "notes": "",
      "components": [
        {{"name": "component name", "type": "Cards|Tokens|Tiles|Dice|Meeples/Minis|Boards|Other", "quantity": 1, "notes": ""}}
      ]
    }}
  ]
}}

Rules:
1. If the expansion adds identical player sets (same components per player), set identical_sets: true
2. If expansion adds to an existing shared pool, name the group to indicate expansion content (e.g. "Expansion Shared Cards")
3. Return ONLY valid JSON — no markdown, no code fences, no explanation text
4. If no new components are found, return: {{"game_name": "...", "player_count": {{}}, "factions_or_colors": [], "component_groups": [], "extraction_notes": "No new components found"}}
"""


def _merge_expansion(base: dict, expansion: dict) -> dict:
    """Merge expansion extraction into base game extraction.

    Appends expansion groups, extends factions_or_colors, combines game_name
    and extraction_notes, then re-flattens and globally re-indexes all components.

    Note: If both base and expansion have identical player sets, two separate
    'Player Components' groups will result — both visible/editable in the review UI.
    """
    import copy
    merged = copy.deepcopy(base)

    base_name = base.get('game_name', 'Base Game')
    expansion_name = expansion.get('game_name', 'Expansion')
    merged['game_name'] = f"{base_name} + {expansion_name}"

    # Extend factions_or_colors without duplicates, preserving order
    base_factions = list(base.get('factions_or_colors', []))
    for f in expansion.get('factions_or_colors', []):
        if f not in base_factions:
            base_factions.append(f)
    merged['factions_or_colors'] = base_factions

    # Combine extraction notes
    base_notes = base.get('extraction_notes', '').strip()
    exp_notes = expansion.get('extraction_notes', '').strip()
    if exp_notes:
        merged['extraction_notes'] = (
            f"{base_notes}\n\n[{expansion_name}] {exp_notes}" if base_notes
            else f"[{expansion_name}] {exp_notes}"
        )

    # Append expansion groups
    merged['component_groups'] = (
        merged.get('component_groups', []) + expansion.get('component_groups', [])
    )

    # Re-index all components globally and sequentially so Streamlit widget keys
    # (check_{idx}, name_{idx}, etc.) are unique across the merged result.
    # We iterate the groups directly so the same dict objects get updated —
    # _flatten_groups_to_components() creates copies so updating the flat list
    # would leave the group-level dicts with stale (colliding) indices.
    global_idx = 0
    for group in merged.get('component_groups', []):
        for comp in group.get('components', []):
            comp['extraction_index'] = global_idx
            global_idx += 1

    # Re-flatten AFTER re-indexing so the flat list inherits the new indices
    flat = _flatten_groups_to_components(merged)
    merged['components'] = flat

    # Track merge metadata (preserves base provider info)
    base_count = len(base.get('components', []))
    new_count = len(flat) - base_count
    merged['metadata'] = {
        **base.get('metadata', {}),
        'merged': True,
        'base_component_count': base_count,
        'expansion_component_count': new_count,
        'total_component_count': len(flat),
    }
    return merged


def extract_expansion_with_ai(
    pdf_text: str,
    base_extraction: dict,
    provider: str,
    api_key: str,
) -> dict:
    """Extract expansion components and return a merged result with the base game.

    Uses the same AI provider as the base extraction. Returns a dict with the
    same shape as extract_components_with_ai() — compatible with all downstream code.
    """
    base_game_name = base_extraction.get('game_name', 'Unknown Game')
    existing_groups = base_extraction.get('component_groups', [])

    print(f"📦 Building expansion prompt for: {base_game_name}")
    print(f"📝 Expansion PDF text length: {len(pdf_text):,} characters")

    prompt = _build_expansion_prompt(pdf_text, base_game_name, existing_groups)
    response_text, tokens_used = _call_ai_provider(prompt, provider, api_key)

    expansion_result = _parse_extraction_response(response_text)
    expansion_result['metadata'] = {'tokens_used': tokens_used, 'provider': provider}
    # Ensure components flat list exists on expansion result before merge
    expansion_result['components'] = _flatten_groups_to_components(expansion_result)

    num_groups = len(expansion_result.get('component_groups', []))
    print(f"✅ Expansion extracted {num_groups} new groups")

    return _merge_expansion(base_extraction, expansion_result)


