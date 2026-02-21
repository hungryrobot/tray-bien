"""Design storage utilities for saving and loading insert designs"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional


def get_saved_designs_dir() -> Path:
    """Get the saved_designs directory path"""
    # Assume this module is in src/storage/
    return Path(__file__).parent.parent.parent / "saved_designs"


def sanitize_filename(design_name: str) -> str:
    """
    Convert design name to safe filename
    - Replace spaces with underscores
    - Remove special characters (keep only alphanumeric, underscore, hyphen)
    - Lowercase
    - Add .json extension

    Args:
        design_name: Original design name

    Returns:
        Sanitized filename with .json extension
    """
    # Replace spaces with underscores
    filename = design_name.replace(' ', '_')

    # Remove special characters (keep only alphanumeric, underscore, hyphen)
    filename = re.sub(r'[^a-zA-Z0-9_-]', '', filename)

    # Convert to lowercase
    filename = filename.lower()

    # Add .json extension
    return f"{filename}.json"


def validate_design(design_data: dict) -> bool:
    """
    Validate design has required fields

    Args:
        design_data: Design data dict

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails with specific error message
    """
    # Check metadata exists
    if 'metadata' not in design_data:
        raise ValueError("Design missing required 'metadata' section")

    metadata = design_data['metadata']
    if 'name' not in metadata:
        raise ValueError("Design metadata missing 'name' field")

    # Check box_config exists
    if 'box_config' not in design_data:
        raise ValueError("Design missing required 'box_config' section")

    box_config = design_data['box_config']
    required_box_fields = ['length', 'width', 'height']
    for field in required_box_fields:
        if field not in box_config:
            raise ValueError(f"Box config missing required field: {field}")

    # Check components is a list
    if 'components' not in design_data:
        raise ValueError("Design missing required 'components' section")

    if not isinstance(design_data['components'], list):
        raise ValueError("Components must be a list")

    return True


def clean_component_data(components: List[dict]) -> List[dict]:
    """
    Remove ephemeral fields from components before saving

    Args:
        components: List of component dicts

    Returns:
        Cleaned list of components
    """
    cleaned = []
    for comp in components:
        # Remove any keys starting with underscore (internal tracking)
        clean_comp = {k: v for k, v in comp.items() if not k.startswith('_')}
        cleaned.append(clean_comp)
    return cleaned


def save_design(design_data: dict, filename: Optional[str] = None) -> str:
    """
    Save design to saved_designs/{filename}.json

    Args:
        design_data: Design data dict with metadata, box_config, components, layout_preferences
        filename: Optional filename. If None, generate from design_name + timestamp

    Returns:
        Saved filename

    Raises:
        ValueError: If validation fails
    """
    # Validate design data
    validate_design(design_data)

    # Clean component data (remove ephemeral fields)
    if 'components' in design_data:
        design_data['components'] = clean_component_data(design_data['components'])

    # Update modified_at timestamp
    design_data['metadata']['modified_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    # Ensure version field
    if 'version' not in design_data['metadata']:
        design_data['metadata']['version'] = 1

    # Generate filename if not provided
    if filename is None:
        design_name = design_data['metadata']['name']
        filename = sanitize_filename(design_name)

    # Get saved_designs directory
    saved_dir = get_saved_designs_dir()
    saved_dir.mkdir(exist_ok=True)

    # Save to file
    file_path = saved_dir / filename
    with open(file_path, 'w') as f:
        json.dump(design_data, f, indent=2)

    return filename


def load_design(filename: str) -> dict:
    """
    Load design from saved_designs/{filename}.json

    Args:
        filename: Design filename

    Returns:
        Design data dict

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid or validation fails
    """
    # Get file path
    saved_dir = get_saved_designs_dir()
    file_path = saved_dir / filename

    # Check file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Design file not found: {filename}")

    # Load JSON
    with open(file_path, 'r') as f:
        design_data = json.load(f)

    # Validate loaded data
    validate_design(design_data)

    return design_data


def list_designs() -> List[Dict]:
    """
    Return list of all saved designs with metadata

    - Exclude files starting with . or _
    - Sort by modified_at descending (most recent first)

    Returns:
        List of design metadata dicts: [
            {
                'filename': 'catan.json',
                'name': 'Catan',
                'modified_at': '2025-02-11T15:30:45Z',
                'box': '296×296×71mm',
                'component_count': 15
            },
            ...
        ]
    """
    saved_dir = get_saved_designs_dir()

    if not saved_dir.exists():
        return []

    designs = []

    # Find all .json files
    for file_path in saved_dir.glob('*.json'):
        # Skip hidden files (starting with . or _)
        if file_path.name.startswith('.') or file_path.name.startswith('_'):
            continue

        try:
            # Load design
            with open(file_path, 'r') as f:
                design_data = json.load(f)

            # Extract metadata
            metadata = design_data.get('metadata', {})
            box_config = design_data.get('box_config', {})
            components = design_data.get('components', [])

            # Format box dimensions
            length = box_config.get('length', 0)
            width = box_config.get('width', 0)
            height = box_config.get('height', 0)
            box_str = f"{int(length)}×{int(width)}×{int(height)}mm"

            designs.append({
                'filename': file_path.name,
                'name': metadata.get('name', file_path.stem),
                'modified_at': metadata.get('modified_at', ''),
                'box': box_str,
                'component_count': len(components)
            })

        except Exception as e:
            # Skip corrupted files but log the error
            print(f"Error loading {file_path.name}: {str(e)}")
            continue

    # Sort by modified_at descending (most recent first)
    designs.sort(key=lambda d: d['modified_at'], reverse=True)

    return designs


def delete_design(filename: str) -> bool:
    """
    Delete design file

    Args:
        filename: Design filename

    Returns:
        True if deleted, False if not found
    """
    saved_dir = get_saved_designs_dir()
    file_path = saved_dir / filename

    if file_path.exists():
        file_path.unlink()
        return True
    return False


def duplicate_design(filename: str, new_name: str) -> str:
    """
    Create copy of design with new name

    Args:
        filename: Original design filename
        new_name: New design name

    Returns:
        New filename

    Raises:
        FileNotFoundError: If original file doesn't exist
    """
    # Load original design
    design_data = load_design(filename)

    # Update metadata
    design_data['metadata']['name'] = new_name
    design_data['metadata']['created_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    design_data['metadata']['modified_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    # Generate new filename
    new_filename = sanitize_filename(new_name)

    # Save with new filename
    return save_design(design_data, filename=new_filename)


def format_timestamp(iso_timestamp: str) -> str:
    """
    Convert ISO timestamp to friendly format

    Args:
        iso_timestamp: ISO format timestamp (e.g., '2025-02-11T15:30:45Z')

    Returns:
        Formatted string (e.g., '2025-02-11 03:30 PM')
    """
    if not iso_timestamp:
        return "Unknown"

    try:
        # Parse ISO timestamp (handle both Z and +00:00 formats)
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %I:%M %p')
    except Exception:
        return iso_timestamp
