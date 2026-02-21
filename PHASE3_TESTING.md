# Phase 3: Step 2 (Sort & Plan) - Testing Guide

## Implementation Complete ✅

All Phase 3 deliverables have been implemented and TypeScript compilation is successful.

## Development Server

**URL:** http://localhost:5175/

## What Was Implemented

### New Files Created

```
frontend/src/utils/
  ├── trayEstimation.ts           ✅ Height estimation logic
  └── trayAutoGeneration.ts       ✅ Auto-generation from component groups

frontend/src/components/wizard/step2/
  ├── StackSummary.tsx            ✅ Stack height visualization
  ├── TrayCard.tsx                ✅ Individual tray editor
  ├── BoardLayerCard.tsx          ✅ Board/rulebook display
  ├── UnassignedSection.tsx       ✅ Unassigned components warning
  └── index.ts                    ✅ Exports
```

### Modified Files

```
frontend/src/types/index.ts              ✅ Added Tray, BoardLayer, TrayStructure types
frontend/src/store/designStore.ts        ✅ Added trayStructure state + 7 actions
frontend/src/components/wizard/steps/
  └── Step2SortAndPlan.tsx               ✅ Full implementation
```

## Testing Workflow

### 1. Initial Setup (Start Fresh)

```bash
# Clear localStorage to start fresh
# In browser console:
localStorage.clear()
location.reload()
```

### 2. Complete Step 1 (Box & Components)

1. **Use PDF Extraction** to get component groups (recommended for best testing)
2. **Configure Quick Defaults**
3. **Import Components** with dimensions
4. Navigate to **Step 2**

### 3. Test Auto-Generation

**Expected Behavior:**
- [ ] Player components → "Player Components" tray (type: player)
- [ ] Shared components → "Shared Resources" tray (type: shared)
- [ ] Setup components → "Setup Components" tray (type: setup)
- [ ] Boards/Rulebooks → Amber "Board Layer" card (not a tray)
- [ ] Stack Summary shows all trays bottom-to-top
- [ ] Total height calculated correctly

### 4. Test Stack Summary

**Check:**
- [ ] Shows total height used vs box height
- [ ] Shows utilization percentage
- [ ] Lists trays in reverse order (visual bottom-to-top)
- [ ] Board layer listed at top (if present)
- [ ] Color-coded headroom:
  - Green: ≥10mm headroom
  - Orange: 0-9mm headroom (tight fit)
  - Red: Negative (overflow warning)
- [ ] Red error box appears if stack exceeds box height

### 5. Test Tray Editing

For each tray:

**Name Editing:**
- [ ] Click tray header to expand
- [ ] Edit "Tray name" field → updates immediately
- [ ] Header text updates with new name

**Type Changing:**
- [ ] Change type dropdown (Player/Shared/Setup)
- [ ] Header updates with new type label
- [ ] Type persists on refresh

**Lid Configuration:**
- [ ] Checkbox shows lid recommendation (if auto-suggested)
- [ ] Blue explanation text appears (e.g., "Recommended due to: many loose pieces")
- [ ] Can toggle lid on/off
- [ ] Toggle persists on refresh

**Player Tray Info:**
- [ ] If type = "player" and has player_sets, shows "Template tray — ×4 identical sets"
- [ ] If type = "player" and no player_sets, shows "Unique faction tray"

### 6. Test Component Movement

**Move Component to Another Tray:**
- [ ] Open a tray with components
- [ ] Select different tray from "Move to..." dropdown
- [ ] Component disappears from current tray
- [ ] Component appears in target tray
- [ ] Both tray heights update in Stack Summary
- [ ] Dropdown resets to "— stay here —"

**Move Component to Unassigned:**
- [ ] Select "Unassigned" from dropdown
- [ ] Component disappears from tray
- [ ] Orange "Unassigned" section appears
- [ ] Next button becomes disabled
- [ ] Warning text appears: "⚠️ Assign all unassigned components before proceeding"

**Move Component from Unassigned:**
- [ ] In Unassigned section, select tray from dropdown
- [ ] Component disappears from Unassigned
- [ ] Component appears in selected tray
- [ ] When last component assigned, Unassigned section disappears
- [ ] Next button becomes enabled

### 7. Test Tray Reordering

**Up/Down Buttons:**
- [ ] Click ↑ on tray (not first) → moves up in list
- [ ] Click ↓ on tray (not last) → moves down in list
- [ ] Stack Summary updates to show new order
- [ ] First tray has no ↑ button
- [ ] Last tray has no ↓ button
- [ ] Order persists on refresh

### 8. Test Remove Tray

**Remove Empty Tray:**
- [ ] Create new tray (should be empty)
- [ ] Click "× Remove tray" button
- [ ] Tray disappears from list
- [ ] No unassigned components created

**Remove Tray with Components:**
- [ ] Click "× Remove tray" on tray with components
- [ ] Tray disappears
- [ ] Orange "Unassigned" section appears
- [ ] All components from removed tray appear in Unassigned
- [ ] Next button disabled until reassigned

### 9. Test Add Tray

**Create New Tray:**
- [ ] Click "+ Add New Tray" button
- [ ] New tray appears at bottom of list
- [ ] Tray is named "New Tray X" (X = tray count)
- [ ] Tray type is "shared" by default
- [ ] Tray is empty (shows "This tray is empty" message)
- [ ] Can move components to it via dropdowns
- [ ] Can rename and configure like any other tray

### 10. Test Board Layer

**If game has boards/rulebooks:**
- [ ] Amber "Board & Rulebook Layer" card appears
- [ ] Header shows item count and thickness
- [ ] Shows explanation: "These items sit on top..."
- [ ] Lists each component with type and quantity
- [ ] Shows individual thickness estimate (~Xmm)
- [ ] Contributes to total stack height in summary
- [ ] Cannot move these components (read-only)

### 11. Test Navigation

**Back Button:**
- [ ] Click "← Back: Box & Components"
- [ ] Returns to Step 1
- [ ] Tray structure preserved (not reset)

**Next Button (Enabled):**
- [ ] When no unassigned components
- [ ] Button is blue and clickable
- [ ] Click → advances to Step 3 (stub page)

**Next Button (Disabled):**
- [ ] When unassigned components exist
- [ ] Button is gray and has cursor-not-allowed
- [ ] Click does nothing
- [ ] Warning text appears below button

### 12. Test Persistence

**After making changes:**
- [ ] Edit tray names
- [ ] Move components between trays
- [ ] Reorder trays
- [ ] Toggle lids
- [ ] Add/remove trays
- [ ] **Refresh page** (F5)
- [ ] All changes preserved
- [ ] Navigate to Step 1 then back to Step 2
- [ ] All changes still preserved

### 13. Test Edge Cases

**Empty State:**
- [ ] If no components imported in Step 1
- [ ] Auto-generation creates single "All Components" tray
- [ ] Note appears: "All components (add via PDF extraction...)"

**Stack Overflow:**
- [ ] If total stack > box height
- [ ] Red error box appears
- [ ] Shows exact overflow amount
- [ ] Lists "OVER by Xmm — trays will not fit"
- [ ] Can still proceed (warning only, not blocking)

**All Components in One Tray:**
- [ ] Move all components to single tray
- [ ] Other trays empty but still exist
- [ ] Can remove empty trays
- [ ] Stack Summary updates correctly

## Known Enhancements (vs Streamlit)

These features are NEW in the React version:

✅ **Smart Lid Recommendations**
- Auto-suggests lids for trays with loose pieces, unsleeved cards, or minis
- Shows reason for recommendation
- User can override

✅ **Real-Time Validation**
- Unassigned component tracking
- Blocks navigation until resolved
- Immediate visual feedback

✅ **Better UX**
- Expandable/collapsible tray cards
- Inline editing (no page refresh)
- Drag-like feel with move-to dropdowns
- Color-coded warnings

## Bug Testing Checklist

Common issues to watch for:

- [ ] Components duplicating when moved
- [ ] Components disappearing when moved
- [ ] Height estimates not updating after changes
- [ ] Stack order not matching visual order
- [ ] Next button state not updating
- [ ] localStorage not persisting
- [ ] TypeScript errors in console
- [ ] React errors/warnings in console
- [ ] Unassigned section not appearing/disappearing
- [ ] Lid checkbox not persisting

## Console Checks

Open browser DevTools (F12) and check:

**Console Tab:**
- [ ] No red errors
- [ ] No React warnings
- [ ] No TypeScript errors

**Application Tab → Local Storage:**
- [ ] Key: `tray-bien-design`
- [ ] Contains `trayStructure` object
- [ ] Updates when changes made

## Success Criteria

Phase 3 is complete when:

✅ All test cases pass
✅ No TypeScript compilation errors
✅ No runtime errors in console
✅ Persistence works across refresh
✅ Navigation validation works
✅ Stack calculations are accurate

## Next Phase

After testing validation:

**Phase 4: Step 3 (Layout Editor)**
- Visual tray design canvas
- Drag-drop compartment placement
- Dimension constraints
- Export to OpenSCAD/STL

---

**Testing Status:** Ready for manual testing ✅
**Development Server:** http://localhost:5175/
