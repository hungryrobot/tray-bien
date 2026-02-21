# Phase 4: Step 3 (Layout Editor) - Implementation Plan

## Overview

Build an interactive 2D canvas for arranging compartments within trays using react-konva. This is the core feature that motivated the React migration - native drag, resize, and visual feedback without iframe hacks.

---

## Pre-Implementation Checklist

### 1. Install Dependencies

```bash
cd frontend
npm install react-konva konva
```

**Verify**: Check package.json includes:
- `react-konva`: ^18.x
- `konva`: ^9.x

### 2. Read Reference Files

- ✅ `prompts/tray-bien-step3-layout-editor.md` - Complete spec
- ✅ `frontend/src/store/designStore.ts` - Current state model
- ✅ `frontend/src/types/index.ts` - Current types
- □ `tray-bien-design-philosophy.md` - Clearance & wall thickness rules
- □ `frontend/src/components/wizard/steps/Step2SortAndPlan.tsx` - Step 2 output

---

## Data Model Changes

### A. Extend Types (`frontend/src/types/index.ts`)

Add two new interfaces:

```typescript
export interface Compartment {
  id: string;
  componentId: string;       // Links to Component.id
  name: string;              // Display name (from component)
  x: number;                 // mm from tray left inner edge
  y: number;                 // mm from tray front inner edge
  width: number;             // mm — component width + clearance
  length: number;            // mm — component length + clearance
  depth: number;             // mm — stack height + finger room
  minWidth: number;          // mm — cannot resize smaller
  minLength: number;         // mm — cannot resize smaller
  color: string;             // Fill color for the rectangle
}

export interface TrayLayout {
  trayId: string;
  compartments: Compartment[];
  outerWallThickness: number;   // mm — from nozzle settings (default: 1.6mm)
  dividerThickness: number;     // mm — inner walls (default: 1.2mm)
  floorThickness: number;       // mm (default: 0.8mm)
}
```

### B. Extend Store (`frontend/src/store/designStore.ts`)

Add to `DesignState` interface:

```typescript
// Step 3: Layout Editor
layouts: TrayLayout[];
selectedTrayId: string | null;
selectedCompartmentId: string | null;

// Actions
initializeLayouts: () => void;
updateCompartment: (trayId: string, compartmentId: string, updates: Partial<Compartment>) => void;
setSelectedTrayId: (trayId: string | null) => void;
setSelectedCompartmentId: (id: string | null) => void;
autoPackTray: (trayId: string) => void;
```

Add to initial state:

```typescript
layouts: [],
selectedTrayId: null,
selectedCompartmentId: null,
```

Add to `partialize` for persistence:

```typescript
layouts: state.layouts,
selectedTrayId: state.selectedTrayId,
selectedCompartmentId: state.selectedCompartmentId,
```

---

## Utility Functions

### Create: `frontend/src/utils/compartmentSizing.ts`

Contains logic for:
1. **getClearance(component)** - Returns clearance in mm based on component type
2. **calculateStackDepth(component)** - Returns depth in mm based on component type/quantity
3. **getComponentColor(type)** - Returns hex color for component type
4. **createCompartment(component, index)** - Converts Component → Compartment
5. **autoPackCompartments(compartments, trayWidth, trayLength, wallThickness)** - Shelf packing algorithm

**Clearance Rules** (from design philosophy):
- Cardboard (Tokens/Tiles): +1mm per side
- Wooden/Plastic: +0.5mm per side
- Cards (unsleeved): +0.5mm per side
- Cards (sleeved): +0.75mm per side
- Dice: +1mm per side
- Miniatures: +2mm per side (if hasMinis flagged), else +1mm

**Stack Depth Rules**:
- Cards: `stackHeight + 5mm` (finger room)
- Tokens (stacked): `quantity × thickness + 3mm`
- Dice: `singleHeight + 2mm` (don't stack well)
- Meeples: `height + 2mm`
- Everything else: `height + 2mm`

**Component Colors**:
- Cards: `#93C5FD` (light blue)
- Tokens: `#FCD34D` (yellow)
- Tiles: `#86EFAC` (green)
- Dice: `#F87171` (red)
- Meeples/Minis: `#C4B5FD` (purple)
- Boards: `#FDBA74` (orange)
- Other: `#D1D5DB` (gray)

**Auto-Pack Algorithm** (bottom-left shelf packing):
1. Sort compartments by area (largest first)
2. Place left to right in current row
3. When compartment doesn't fit width, start new row below
4. Account for divider wall thickness between compartments
5. Return array with x, y positions set

---

## Component Structure

Create directory: `frontend/src/components/wizard/step3/`

**Files to create**:

1. **LayoutEditor.tsx** - Main container
   - Renders TrayTabBar, TrayCanvas, CompartmentProperties
   - Handles navigation (Back to Step 2, Next to Step 4)
   - Calls `initializeLayouts()` on mount if not initialized

2. **TrayCanvas.tsx** - Konva Stage/Layer
   - Renders tray outline rectangle
   - Renders grid background (10mm intervals)
   - Renders all compartments for selected tray
   - Handles scaling (mm → pixels)

3. **CompartmentRect.tsx** - Single compartment
   - Konva Group with Rect + 2 Text labels (name + dimensions)
   - Draggable with snap-to-grid (1mm)
   - Resizable via Transformer
   - Click to select
   - Bounds checking (can't drag/resize outside tray)
   - Enforces minimum size (minWidth, minLength)

4. **CompartmentProperties.tsx** - Right sidebar panel
   - Shows "Click a compartment..." when none selected
   - When selected, shows editable fields:
     - X, Y position
     - Width, Length, Depth
     - Min size display
     - Volume calculation
     - Color swatch
   - Updates store on input change

5. **TrayTabBar.tsx** - Tab switcher
   - Horizontal tabs for each tray
   - Shows tray name + compartment count
   - Active tab highlighted (blue bg)
   - Inactive tabs gray bg, hoverable

6. **CanvasGrid.tsx** - Background grid lines
   - Renders vertical + horizontal lines
   - 10mm intervals
   - Dashed stroke, light gray (#E5E7EB)

7. **AutoPackButton.tsx** - Trigger auto-pack
   - Gray button above canvas
   - Calls `autoPackTray(currentTrayId)`
   - Rearranges compartments for selected tray

8. **index.ts** - Exports

---

## Store Actions Implementation

### 1. initializeLayouts()

```typescript
initializeLayouts: () => {
  const { trayStructure, boxConfig } = get();
  if (!trayStructure) return;

  const layouts: TrayLayout[] = trayStructure.trays.map(tray => {
    const outerWall = 1.6;
    const divider = 1.2;

    // Create compartments from components
    const compartments = tray.components.map((comp, i) =>
      createCompartment(comp, i)
    );

    // Auto-pack into tray bounds
    const usableWidth = boxConfig.width - outerWall * 2;
    const usableLength = boxConfig.length - outerWall * 2;
    const packed = autoPackCompartments(compartments, usableWidth, usableLength, divider);

    return {
      trayId: tray.tray_id,
      compartments: packed,
      outerWallThickness: outerWall,
      dividerThickness: divider,
      floorThickness: 0.8,
    };
  });

  set({
    layouts,
    selectedTrayId: layouts[0]?.trayId || null,
    selectedCompartmentId: null,
  });
}
```

### 2. updateCompartment()

```typescript
updateCompartment: (trayId, compartmentId, updates) => {
  set((state) => ({
    layouts: state.layouts.map(layout =>
      layout.trayId === trayId
        ? {
            ...layout,
            compartments: layout.compartments.map(comp =>
              comp.id === compartmentId
                ? { ...comp, ...updates }
                : comp
            ),
          }
        : layout
    ),
  }));
}
```

### 3. setSelectedTrayId()

```typescript
setSelectedTrayId: (trayId) => {
  set({ selectedTrayId: trayId, selectedCompartmentId: null });
}
```

### 4. setSelectedCompartmentId()

```typescript
setSelectedCompartmentId: (id) => {
  set({ selectedCompartmentId: id });
}
```

### 5. autoPackTray()

```typescript
autoPackTray: (trayId) => {
  const { layouts, boxConfig } = get();

  const layout = layouts.find(l => l.trayId === trayId);
  if (!layout) return;

  const usableWidth = boxConfig.width - layout.outerWallThickness * 2;
  const usableLength = boxConfig.length - layout.outerWallThickness * 2;

  const packed = autoPackCompartments(
    layout.compartments,
    usableWidth,
    usableLength,
    layout.dividerThickness
  );

  set((state) => ({
    layouts: state.layouts.map(l =>
      l.trayId === trayId ? { ...l, compartments: packed } : l
    ),
  }));
}
```

---

## Implementation Order

### Phase 4A: Foundation (1-2 hours)

1. Install dependencies (`npm install react-konva konva`)
2. Extend types (Compartment, TrayLayout)
3. Create `compartmentSizing.ts` utility
4. Extend store (state + 5 actions)

**Verification**: TypeScript compiles, no errors

### Phase 4B: Basic Canvas (2-3 hours)

1. Create stub Step3 component files
2. Create `TrayCanvas.tsx` with tray outline + grid
3. Create `CanvasGrid.tsx`
4. Create `LayoutEditor.tsx` container
5. Update `Step3LayoutEditor.tsx` to render LayoutEditor

**Verification**: Canvas renders with tray outline and grid

### Phase 4C: Compartments (3-4 hours)

1. Create `CompartmentRect.tsx` (draggable + resizable)
2. Wire up selection state
3. Implement snap-to-grid
4. Implement bounds checking
5. Add component labels (name + dimensions)

**Verification**: Compartments render, drag, resize, snap to grid

### Phase 4D: UI Controls (2 hours)

1. Create `TrayTabBar.tsx`
2. Create `CompartmentProperties.tsx`
3. Create `AutoPackButton.tsx`
4. Wire up all event handlers

**Verification**: Can switch trays, edit properties, auto-pack works

### Phase 4E: Polish & Testing (1-2 hours)

1. Add navigation (Back/Next buttons)
2. Test with Qwixx test data
3. Test multi-tray switching
4. Test drag/resize edge cases
5. Test persistence (refresh preserves layouts)
6. Fix any visual bugs

**Verification**: All acceptance criteria met

---

## Acceptance Criteria

Step 3 is complete when:

✅ **Canvas renders** — Tray outline visible with grid lines
✅ **Compartments display** — Colored rectangles with names and dimensions
✅ **Auto-pack works** — Compartments arranged within tray bounds on load
✅ **Drag works** — Click and drag compartments to reposition, snaps to 1mm grid
✅ **Resize works** — Drag edges/corners to resize, minimum size enforced
✅ **Selection works** — Click compartment to select, shows blue border + transformer handles
✅ **Properties panel** — Shows/edits X, Y, width, length, depth for selected compartment
✅ **Tab switching** — Can switch between trays
✅ **Bounds enforcement** — Can't drag outside tray, can't resize beyond tray edges
✅ **Navigation** — Back to Step 2, Next to Step 4 (stub is fine)
✅ **State persistence** — Refresh preserves layout positions

---

## Known Limitations (Acceptable for v1)

These features are intentionally deferred:

- ❌ No collision detection between compartments (manual adjustment required)
- ❌ No wall thickness color-coding (green/yellow/red based on nozzle multiples)
- ❌ No undo/redo
- ❌ No rotation of compartments
- ❌ Auto-pack is basic shelf algorithm (not optimal bin-packing)
- ❌ Canvas doesn't zoom/pan (for large trays)

These can be added iteratively after core functionality works.

---

## Critical Files Summary

**New files to create** (8 components + 1 utility):
- `/frontend/src/utils/compartmentSizing.ts`
- `/frontend/src/components/wizard/step3/LayoutEditor.tsx`
- `/frontend/src/components/wizard/step3/TrayCanvas.tsx`
- `/frontend/src/components/wizard/step3/CompartmentRect.tsx`
- `/frontend/src/components/wizard/step3/CompartmentProperties.tsx`
- `/frontend/src/components/wizard/step3/TrayTabBar.tsx`
- `/frontend/src/components/wizard/step3/CanvasGrid.tsx`
- `/frontend/src/components/wizard/step3/AutoPackButton.tsx`
- `/frontend/src/components/wizard/step3/index.ts`

**Files to modify** (3):
- `/frontend/src/types/index.ts` - Add Compartment, TrayLayout
- `/frontend/src/store/designStore.ts` - Add layouts state + 5 actions
- `/frontend/src/components/wizard/steps/Step3LayoutEditor.tsx` - Replace stub

**Reference files**:
- `/Users/avrom/Documents/Work/Programs/tray-bien/prompts/tray-bien-step3-layout-editor.md`
- `/Users/avrom/Documents/Work/Programs/tray-bien/tray-bien-design-philosophy.md`

---

## Estimated Time

- **Phase 4A (Foundation)**: 1-2 hours
- **Phase 4B (Basic Canvas)**: 2-3 hours
- **Phase 4C (Compartments)**: 3-4 hours
- **Phase 4D (UI Controls)**: 2 hours
- **Phase 4E (Polish & Testing)**: 1-2 hours

**Total**: 9-13 hours of focused implementation

---

## Next Steps

1. **User approval** of this plan
2. **Install dependencies** (`npm install react-konva konva`)
3. **Begin Phase 4A** (Foundation - types, utilities, store)
4. **Iterate through phases** 4B → 4C → 4D → 4E
5. **Test with Qwixx data** using dev test data loader
6. **Commit and push** when acceptance criteria met

Ready to proceed? 🚀
