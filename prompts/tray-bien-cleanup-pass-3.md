# Tray Bien — UI Cleanup Pass 3

## Context

Quick Defaults panel is working. Three bugs found in the flow after it, plus refinements to Quick Defaults itself.

Read `src/questionnaire/components.py` before making changes. Plan first.

---

## 1. Remove the Material Defaults Screen

The Material Defaults screen (shows "Cardboard quality for all tokens" / "Cardboard quality for all tiles" dropdowns) is now **redundant**. The Quick Defaults panel already collects cardboard quality, and that answer should apply to all tokens and tiles.

**Action:** Remove or bypass the Material Defaults screen entirely when Quick Defaults has already been completed.

After the user selects components and clicks "Continue →", if `st.session_state.quick_defaults_done` is `True`, skip the Material Defaults screen and go directly to the "Add to Inventory" step (game name + add button). Apply the Quick Defaults cardboard quality to all tokens and tiles automatically during the import.

The Material Defaults screen should ONLY appear if Quick Defaults was skipped (e.g., manual component entry without PDF extraction).

**Implementation:**

In the flow after "Continue →" is clicked:
```python
if st.session_state.get('quick_defaults_done'):
    # Skip material defaults — already answered in Quick Defaults
    # Apply quick_defaults['cardboard_quality'] to all token/tile components
    # Go directly to Add to Inventory (game name + import button)
    render_add_to_inventory()
else:
    # No Quick Defaults — show the old Material Defaults screen
    render_material_defaults_and_expansion_workflow()
```

Apply the cardboard quality using this thickness mapping:
```python
thickness_map = {
    'budget': 1.1,
    'standard': 1.5,
    'premium': 2.0,
    'luxury': 2.75,
}
```

---

## 2. Fix "Add to Inventory" Loop Bug

After clicking "Add to Inventory →", the wizard resets back to the component upload/extraction flow instead of showing the populated inventory or advancing to Sort & Plan.

**Root cause (likely):** The `add_to_inventory` handler resets session state flags (`show_material_defaults`, `pdf_extraction_result`, etc.) as cleanup, which causes the component inventory section to re-render in its initial "upload PDF" state.

**Debug steps:**
1. Print `st.session_state.confirmed_components` immediately after the handler runs. Is it populated?
2. Print `st.session_state.wizard_step` after the handler. Is it still 1?
3. Check what session state keys the handler clears. Does it clear something the inventory display needs?

**Expected behavior after "Add to Inventory →":**
- Components are added to `st.session_state.confirmed_components`
- Step 1 re-renders showing the populated inventory list (not the upload flow)
- "Next: Sort & Plan →" button visible at bottom
- Clicking it sets `wizard_step = 2`

**The key branching logic:**
```python
if st.session_state.get('confirmed_components'):
    # Show the populated inventory list with dimension editors
    render_inventory_list()
    # Show "Next: Sort & Plan →" button
else:
    # Show the upload/extraction/quick defaults flow
    render_extraction_flow()
```

If this branching doesn't exist, add it. If it exists but `confirmed_components` is being cleared by the add handler, stop clearing it.

---

## 3. Refine Quick Defaults — Cubes, Dice, Miniatures

The Quick Defaults form needs corrections. Key principle: **Quick Defaults sets size defaults and flags, not quantities.** The PDF extraction handles quantities. Quick Defaults just tells the auto-fill system what sizes to apply.

### Add cubes toggle

Place after the dice toggle, before the miniatures toggle:

```python
has_cubes = st.toggle("Game has resource cubes?",
                       help="Sets default dimensions for cube components")
if has_cubes:
    cube_size = st.selectbox("Default cube size",
        options=['8mm', '10mm', 'Custom'],
        index=0,
        help="Override per-component in the review if needed")
    if cube_size == 'Custom':
        cube_size_mm = st.number_input("Cube size (mm)", min_value=3, max_value=30, value=8, step=1)
    else:
        cube_size_mm = int(cube_size.replace('mm', ''))
else:
    cube_size_mm = 8
```

Add to `quick_defaults` dict:
```python
'has_cubes': has_cubes,
'cube_size_mm': cube_size_mm if has_cubes else 8,
```

### Fix dice toggle — remove quantity, add Custom option

The dice toggle currently asks for quantity. Remove it — the PDF extraction detects quantities. Only ask for size, with a Custom escape hatch:

```python
has_dice = st.toggle("Game has dice?",
                      help="Sets default dimensions for dice components")
if has_dice:
    dice_size = st.selectbox("Default dice size",
        options=['12mm (small)', '16mm (standard)', '19mm (large)', 'Custom'],
        index=1,
        help="Standard d6 is 16mm")
    if dice_size == 'Custom':
        dice_size_mm = st.number_input("Dice size (mm)", min_value=8, max_value=30, value=16, step=1)
    else:
        dice_size_mm = int(dice_size.split('mm')[0])
else:
    dice_size_mm = 16
```

Update `quick_defaults` dict — remove `dice_qty`, keep only:
```python
'has_dice': has_dice,
'dice_size_mm': dice_size_mm if has_dice else 16,
```

Remove `_inject_dice_component()` calls that depend on quantity. Dice injection from Quick Defaults should only happen if the AI detected zero dice components AND the user toggled dice on — in that case, inject a single placeholder component with quantity 1 that the user can edit in the review.

### Miniatures toggle — clearance flag only, no size selector

The miniatures toggle should NOT ask for sizes — minis are too varied. Just set a clearance flag:

```python
has_minis = st.toggle("Game has miniatures or large figures?",
                       help="Applies wider clearance (+2mm per dimension) to mini components. "
                            "Enter actual dimensions per component in the review.")
```

No size dropdown, no quantity input. The toggle sets `quick_defaults['has_minis'] = True`, and the auto-fill applies +2mm clearance to anything tagged as minis.

### Updated Quick Defaults form order:

1. Cardboard quality (dropdown)
2. Cards sleeved? (radio)
3. Game has dice? (toggle → size selector with Custom)
4. Game has resource cubes? (toggle → size selector with Custom)
5. Game has miniatures? (toggle — clearance flag only)
6. Include expansion space? (toggle)
7. [Apply & Review Components] button

---

## 4. Pre-fill Game Name from Extraction

If the extraction result contains a detected game name, pre-fill the "Design name" input in the box dimensions section.

In the Quick Defaults submit handler, before `st.rerun()`:
```python
game_name = st.session_state.get('pdf_extraction_result', {}).get('game_name')
if game_name:
    st.session_state.setdefault('design_name', game_name)
```

---

## 5. Auto-Fill — Use Quick Defaults Sizes

Update `_get_dimension_prefill()` to use the refined Quick Defaults values:

**Cubes** — match on name containing "cube":
```python
if any(kw in name_lower for kw in ['cube', 'cubes']):
    size = quick_defaults.get('cube_size_mm', 8)
    return (size, size, size, f"Resource cube — {size}mm")
```

**Dice** — match on name containing "dice"/"die" or type "Dice":
```python
if comp_type == 'Dice' or any(kw in name_lower for kw in ['dice', 'die', 'd6', 'd8', 'd10', 'd12', 'd20']):
    size = quick_defaults.get('dice_size_mm', 16)
    return (size, size, size, f"Standard {size}mm die")
```

**Miniatures** — flag for clearance, don't prefill dimensions:
```python
if has_minis and (comp_type == 'Meeples/Minis' or any(kw in name_lower for kw in ['miniature', 'figure', 'model', 'sculpt'])):
    comp['_clearance_mm'] = 2.0
    comp['_clearance_note'] = "Miniature — wider clearance applied (+2mm)"
    return None  # No dimension prefill — too varied
```

**Standard meeples** — separate from miniatures, these ARE predictable:
```python
if any(kw in name_lower for kw in ['meeple', 'worker']) and not has_minis:
    return (16, 16, 10, "Standard meeple — 16×16×10mm")
```

If `has_minis` is True, don't auto-fill meeple dimensions — the user probably has non-standard figures.

---

## Verification

Test with a PDF:

1. Upload PDF → extraction → Quick Defaults appears
2. Quick Defaults: Standard cardboard, unsleeved, no dice, no cubes, no minis
3. "Apply & Review Components" → component review appears
4. Select all → "Continue →" → **goes to Add to Inventory directly** (NO material defaults screen)
5. Game name pre-filled from extraction
6. "Add to Inventory →" → **shows populated inventory list, NOT the upload flow**
7. "Next: Sort & Plan →" → arrives at Step 2 with populated trays

Test cubes:
1. Toggle cubes ON → size selector: 8mm / 10mm / Custom
2. Select Custom → number input, enter 12
3. Apply → cube components prefilled with 12×12×12mm

Test dice:
1. Toggle dice ON → size selector (NO quantity field): 12mm / 16mm / 19mm / Custom
2. Select 16mm
3. Apply → dice components prefilled with 16×16×16mm

Test minis:
1. Toggle minis ON → no size or quantity selector
2. Apply → mini components show no dimension prefill, clearance note visible
