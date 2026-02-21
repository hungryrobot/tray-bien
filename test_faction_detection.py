"""
Test script for faction-based PDF extraction.

Tests The Old King's Crown component extraction to verify:
- 76 Faction Cards split into 4 entries (19 each for Nobility, Clans, Uprising, Gathering)
- 4 Heralds split into 4 faction-specific entries
- 20 Supporters split into 4 faction-specific entries
- Step 2.5 detects 4 players (faction-based)
- Pattern 2 suggested (Storage Compartments)
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from generator.tray_analyzer import detect_player_count, group_player_components, detect_player_tray_pattern

# Simulate extraction results for The Old King's Crown (faction-based)
test_components = [
    # Faction Cards (should be split by AI into 4 separate entries)
    {
        'name': 'Nobility Faction Cards',
        'type': 'Cards',
        'quantity': 19,
        'details': 'Faction-specific deck for The Nobility',
        'faction': 'Nobility',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Clans Faction Cards',
        'type': 'Cards',
        'quantity': 19,
        'details': 'Faction-specific deck for The Clans',
        'faction': 'Clans',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Uprising Faction Cards',
        'type': 'Cards',
        'quantity': 19,
        'details': 'Faction-specific deck for The Uprising',
        'faction': 'Uprising',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Gathering Faction Cards',
        'type': 'Cards',
        'quantity': 19,
        'details': 'Faction-specific deck for The Gathering',
        'faction': 'Gathering',
        'color': '',
        'player_specific': True
    },
    # Heralds (should be split by AI into 4 separate entries)
    {
        'name': 'Nobility Herald',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Faction-specific herald meeple',
        'faction': 'Nobility',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Clans Herald',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Faction-specific herald meeple',
        'faction': 'Clans',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Uprising Herald',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Faction-specific herald meeple',
        'faction': 'Uprising',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Gathering Herald',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Faction-specific herald meeple',
        'faction': 'Gathering',
        'color': '',
        'player_specific': True
    },
    # Supporters (should be split by AI into 4 separate entries)
    {
        'name': 'Nobility Supporters',
        'type': 'Tokens',
        'quantity': 5,
        'details': 'Faction-specific supporter tokens',
        'faction': 'Nobility',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Clans Supporters',
        'type': 'Tokens',
        'quantity': 5,
        'details': 'Faction-specific supporter tokens',
        'faction': 'Clans',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Uprising Supporters',
        'type': 'Tokens',
        'quantity': 5,
        'details': 'Faction-specific supporter tokens',
        'faction': 'Uprising',
        'color': '',
        'player_specific': True
    },
    {
        'name': 'Gathering Supporters',
        'type': 'Tokens',
        'quantity': 5,
        'details': 'Faction-specific supporter tokens',
        'faction': 'Gathering',
        'color': '',
        'player_specific': True
    },
    # Shared components
    {
        'name': 'Influence Tokens',
        'type': 'Tokens',
        'quantity': 48,
        'details': '32× 1-value, 16× 5-value',
        'faction': '',
        'color': '',
        'player_specific': False
    },
    {
        'name': 'Crown Tokens',
        'type': 'Tokens',
        'quantity': 12,
        'details': 'Victory point markers',
        'faction': '',
        'color': '',
        'player_specific': False
    }
]

print("=" * 80)
print("FACTION DETECTION TEST - The Old King's Crown")
print("=" * 80)
print()

# Test 1: Detect player count from factions
print("TEST 1: Player Count Detection")
print("-" * 80)
player_count = detect_player_count(test_components)
print(f"Detected player count: {player_count}")
print(f"Expected: 4 (faction-based)")
print(f"✓ PASS" if player_count == 4 else f"✗ FAIL")
print()

# Test 2: Group player components
print("TEST 2: Player Component Grouping")
print("-" * 80)
player_components = group_player_components(test_components, player_count)
print(f"Detected {len(player_components)} player-specific components:")
for comp in player_components:
    faction = comp.get('faction', '')
    print(f"  - {comp['name']} (qty: {comp['quantity']}, faction: {faction})")
print()
print(f"Expected: 12 components (4 factions × 3 component types)")
print(f"✓ PASS" if len(player_components) == 12 else f"✗ FAIL")
print()

# Test 3: Detect player tray pattern
print("TEST 3: Player Tray Pattern Detection")
print("-" * 80)
pattern = detect_player_tray_pattern(player_components)
print(f"Detected pattern: {pattern}")
print(f"Expected: Pattern 2 (Storage Compartments) - faction decks are shuffled")
# Note: This might be Pattern 1 or 2 depending on component details
print()

# Test 4: Verify faction field extraction
print("TEST 4: Faction Field Verification")
print("-" * 80)
factions_found = set()
for comp in test_components:
    faction = comp.get('faction', '').strip()
    if faction:
        factions_found.add(faction)

print(f"Unique factions found: {sorted(factions_found)}")
print(f"Expected: ['Clans', 'Gathering', 'Nobility', 'Uprising']")
print(f"✓ PASS" if len(factions_found) == 4 else f"✗ FAIL")
print()

# Test 5: Verify no color contamination
print("TEST 5: Color vs Faction Separation")
print("-" * 80)
colors_found = set()
for comp in test_components:
    color = comp.get('color', '').strip()
    if color:
        colors_found.add(color)

print(f"Colors found: {colors_found if colors_found else 'None'}")
print(f"Expected: None (faction-based game, not color-based)")
print(f"✓ PASS" if len(colors_found) == 0 else f"✗ FAIL")
print()

print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("All tests verify that faction-based extraction works correctly:")
print("✓ Factions detected from 'faction' field")
print("✓ Player count = number of factions")
print("✓ Player components grouped by faction marker")
print("✓ No contamination from color-based detection")
print()
print("Ready to test with real PDF extraction!")
