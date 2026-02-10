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

        provider = settings.get('ai_provider', 'none')

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


def extract_components_with_ai(pdf_text: str, provider: str, api_key: str) -> list:
    """Send PDF text to AI and get structured component list.

    Args:
        pdf_text: Extracted text from PDF
        provider: AI provider ('claude', 'openai', 'gemini', 'ollama')
        api_key: API key for the provider (not needed for Ollama)

    Returns:
        list: List of component dicts [{'name': str, 'type': str, 'quantity': int}, ...]

    Raises:
        Exception: If API call fails or response is invalid
    """
    # Build the prompt
    prompt = _build_extraction_prompt(pdf_text)

    # Call appropriate AI provider
    if provider == 'claude':
        response_text = _call_anthropic_api(prompt, api_key)
    elif provider == 'openai':
        response_text = _call_openai_api(prompt, api_key)
    elif provider == 'gemini':
        response_text = _call_gemini_api(prompt, api_key)
    elif provider == 'ollama':
        response_text = _call_ollama_api(prompt)
    else:
        raise Exception(f"Unsupported AI provider: {provider}")

    # Parse JSON response
    components = _parse_component_response(response_text)

    return components


def _build_extraction_prompt(pdf_text: str) -> str:
    """Build the prompt for component extraction."""
    return f"""You are analyzing a board game rulebook. Extract the list of game components.

INPUT TEXT (from rulebook PDF):
{pdf_text[:15000]}

TASK:
Find the section that lists game components (usually titled "Components", "What's in the Box", "Game Contents", etc.)
Extract ONLY the components that need physical storage in the game box.

RULES:
- Include: Cards, tokens, dice, tiles, meeples, boards, resource cubes, player pieces
- Exclude: Rulebooks (the PDF itself), quick reference sheets, scorepads (unless thick stacks)
- Consolidate similar items (e.g., "50 Gold Tokens" and "30 Silver Tokens" → combine as "Tokens" with quantity 80)
- Classify each component into one of these types: Cards, Tokens, Dice, Meeples/Minis, Boards, Rulebook, Custom

OUTPUT FORMAT (JSON only, no markdown, no code fences):
[
  {{"name": "Bird Cards", "type": "Cards", "quantity": 170}},
  {{"name": "Food Tokens", "type": "Tokens", "quantity": 103}},
  {{"name": "Dice", "type": "Dice", "quantity": 5}}
]

IMPORTANT:
- Return valid JSON only (no markdown formatting, no code fences)
- Use singular or plural naturally (e.g., "Bird Cards" not "Bird Card")
- Combine related items when appropriate
- If you cannot find a component list, return empty array: []
"""


def _call_anthropic_api(prompt: str, api_key: str) -> str:
    """Call Anthropic Claude API with structured output."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    except Exception as e:
        raise Exception(f"Anthropic API error: {str(e)}")


def _call_openai_api(prompt: str, api_key: str) -> str:
    """Call OpenAI API with JSON mode."""
    try:
        import openai

        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective for this task
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


def _call_gemini_api(prompt: str, api_key: str) -> str:
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                max_output_tokens=4096,
            )
        )

        return response.text

    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def _call_ollama_api(prompt: str) -> str:
    """Call local Ollama API."""
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
        return result.get('response', '[]')

    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}. Make sure Ollama is running locally.")


def _parse_component_response(response_text: str) -> list:
    """Parse AI response and extract component list.

    Args:
        response_text: AI response (should be JSON)

    Returns:
        list: Validated list of component dicts

    Raises:
        Exception: If response cannot be parsed
    """
    try:
        # Remove markdown code fences if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()

        # Parse JSON
        components = json.loads(response_text)

        # Validate structure
        if not isinstance(components, list):
            raise ValueError("Response is not a JSON array")

        # Validate and clean each component
        validated_components = []
        valid_types = ['Cards', 'Tokens', 'Dice', 'Meeples/Minis', 'Boards', 'Rulebook', 'Custom']

        for comp in components:
            if not isinstance(comp, dict):
                continue

            # Required fields
            name = comp.get('name', '').strip()
            comp_type = comp.get('type', 'Custom').strip()
            quantity = comp.get('quantity', 1)

            if not name:
                continue

            # Validate type
            if comp_type not in valid_types:
                comp_type = 'Custom'

            # Validate quantity
            try:
                quantity = int(quantity)
                if quantity < 1:
                    quantity = 1
            except (ValueError, TypeError):
                quantity = 1

            validated_components.append({
                'name': name,
                'type': comp_type,
                'quantity': quantity
            })

        return validated_components

    except json.JSONDecodeError as e:
        raise Exception(f"AI returned invalid JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse AI response: {str(e)}")
