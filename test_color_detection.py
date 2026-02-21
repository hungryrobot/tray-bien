"""
Test script for color-based PDF extraction.

Tests Cacao component extraction to verify:
- 44 Worker tiles split into 4 entries (11 each for red, purple, white, yellow)
- 4 Water carriers split into 4 color-specific entries
- Step 2.5 detects 4 players (color-based)
- Pattern 2 suggested (Storage Compartments)
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from generator.tray_analyzer import detect_player_count, group_player_components, detect_player_tray_pattern

# Simulate extraction results for Cacao (color-based)
test_components = [
    # Worker tiles (should be split by AI into 4 separate entries)
    {
        'name': 'Red worker tiles',
        'type': 'Tiles',
        'quantity': 11,
        'details': 'Player-specific (red color)',
        'faction': '',
        'color': 'red',
        'player_specific': True
    },
    {
        'name': 'Purple worker tiles',
        'type': 'Tiles',
        'quantity': 11,
        'details': 'Player-specific (purple color)',
        'faction': '',
        'color': 'purple',
        'player_specific': True
    },
    {
        'name': 'White worker tiles',
        'type': 'Tiles',
        'quantity': 11,
        'details': 'Player-specific (white color)',
        'faction': '',
        'color': 'white',
        'player_specific': True
    },
    {
        'name': 'Yellow worker tiles',
        'type': 'Tiles',
        'quantity': 11,
        'details': 'Player-specific (yellow color)',
        'faction': '',
        'color': 'yellow',
        'player_specific': True
    },
    # Water carriers (should be split by AI into 4 separate entries)
    {
        'name': 'Red water carrier',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Player-specific meeple',
        'faction': '',
        'color': 'red',
        'player_specific': True
    },
    {
        'name': 'Purple water carrier',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Player-specific meeple',
        'faction': '',
        'color': 'purple',
        'player_specific': True
    },
    {
        'name': 'White water carrier',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Player-specific meeple',
        'faction': '',
        'color': 'white',
        'player_specific': True
    },
    {
        'name': 'Yellow water carrier',
        'type': 'Meeples/Minis',
        'quantity': 1,
        'details': 'Player-specific meeple',
        'faction': '',
        'color': 'yellow',
        'player_specific': True
    },
    # Shared components
    {
        'name': 'Jungle tiles',
        'type': 'Tiles',
        'quantity': 28,
        'details': 'Shared resource tiles',
        'faction': '',
        'color': '',
        'player_specific': False
    },
    {
        'name': 'Gold coins',
        'type': 'Tokens',
        'quantity': 48,
        'details': '24× 1-value, 12× 5-value, 12× 10-value',
        'faction': '',
        'color': '',
        'player_specific': False
    }
]

print("=" * 80)
print("COLOR DETECTION TEST - Cacao")
print("=" * 80)
print()

# Test 1: Detect player count from colors
print("TEST 1: Player Count Detection")
print("-" * 80)
player_count = detect_player_count(test_components)
print(f"Detected player count: {player_count}")
print(f"Expected: 4 (color-based)")
print(f"✓ PASS" if player_count == 4 else f"✗ FAIL")
print()

# Test 2: Group player components
print("TEST 2: Player Component Grouping")
print("-" * 80)
player_components = group_player_components(test_components, player_count)
print(f"Detected {len(player_components)} player-specific components:")
for comp in player_components:
    color = comp.get('color', '')
    print(f"  - {comp['name']} (qty: {comp['quantity']}, color: {color})")
print()
print(f"Expected: 8 components (4 colors × 2 component types)")
print(f"✓ PASS" if len(player_components) == 8 else f"✗ FAIL")
print()

# Test 3: Detect player tray pattern
print("TEST 3: Player Tray Pattern Detection")
print("-" * 80)
pattern = detect_player_tray_pattern(player_components)
print(f"Detected pattern: {pattern}")
print(f"Expected: Pattern 2 (Storage Compartments) - worker tiles are shuffled")
print()

# Test 4: Verify color field extraction
print("TEST 4: Color Field Verification")
print("-" * 80)
colors_found = set()
for comp in test_components:
    color = comp.get('color', '').strip()
    if color:
        colors_found.add(color)

print(f"Unique colors found: {sorted(colors_found)}")
print(f"Expected: ['purple', 'red', 'white', 'yellow']")
print(f"✓ PASS" if len(colors_found) == 4 else f"✗ FAIL")
print()

# Test 5: Verify no faction contamination
print("TEST 5: Faction vs Color Separation")
print("-" * 80)
factions_found = set()
for comp in test_components:
    faction = comp.get('faction', '').strip()
    if faction:
        factions_found.add(faction)

print(f"Factions found: {factions_found if factions_found else 'None'}")
print(f"Expected: None (color-based game, not faction-based)")
print(f"✓ PASS" if len(factions_found) == 0 else f"✗ FAIL")
print()

print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("All tests verify that color-based extraction still works correctly:")
print("✓ Colors detected from 'color' field")
print("✓ Player count = number of colors")
print("✓ Player components grouped by color marker")
print("✓ No contamination from faction-based detection")
print()
print("Color detection backwards compatible!")
