# Phase 4: Step 3 Layout Editor - Two-Level Refactor Plan

## Overview

Refactor Step 3 to have two levels:
1. **Box View (Level 1)** - Default view showing box footprint with trays as rectangles
2. **Tray View (Level 2)** - Drill-in view showing compartments within a tray (current implementation)

Current compartment arrangement code becomes Tray View. Build new Box View as the primary interface.

---

## Architecture Changes

### Current State (Just Built)
- User lands on Step 3 → sees tabs for each tray
- Click tab → sees compartment arrangement for that tray
- Drag/resize compartments within the tray

### New State (Two-Level)
- User lands on Step 3 → **Box View** (shows all trays in the box)
- Double-click a tray → **Tray View** (drill into compartment arrangement)
- Click "Back to Box View" → return to box overview

---

## Type Changes

### Extend TrayLayout (add box-level positioning)

```typescript
export interface TrayLayout {
  trayId: string;

  // Box-level positioning (NEW - for Box View)
  boxX: number;        // mm from box left edge
  boxY: number;        // mm from box front edge
  boxWidth: number;    // mm - tray footprint width within box
  boxLength: number;   // mm - tray footprint length within box

  // Tray internals (existing - for Tray View)
  compartments: Compartment[];
  outerWallThickness: number;   // mm (default: 1.6mm)
  dividerThickness: number;     // mm (default: 1.2mm)
  floorThickness: number;       // mm (default: 0.8mm)
}
```

**Why boxWidth/boxLength**:
- Trays can be resized to split the box space
- Example: 2 trays side-by-side, each taking half the box width
- Example: 1 tray full-width, 2 trays stacked below splitting the remaining space

---

## Store Changes

### Add View State

```typescript
interface DesignState {
  // ... existing state ...

  // Step 3 - Layout Editor
  layouts: TrayLayout[];
  selectedTrayId: string | null;
  selectedCompartmentId: string | null;

  // NEW: View mode
  layoutViewMode: 'box' | 'tray';        // Which level of the editor
  editingTrayId: string | null;          // Which tray is open in Tray View

  // Actions
  // ... existing actions ...

  // NEW: View mode actions
  setLayoutViewMode: (mode: 'box' | 'tray') => void;
  enterTrayView: (trayId: string) => void;
  exitTrayView: () => void;
}
```

### Update initializeLayouts

Needs to calculate box-level positions for trays:

```typescript
initializeLayouts: () => {
  const { trayStructure, boxConfig } = get();
  if (!trayStructure) return;

  const layouts: TrayLayout[] = trayStructure.trays.map((tray, index) => {
    const outerWall = 1.6;
    const divider = 1.2;

    // Create compartments (existing logic)
    const compartments = tray.components.map(comp => createCompartment(comp));

    // Auto-pack compartments within tray (existing)
    const usableWidth = boxConfig.width - outerWall * 2;
    const usableLength = boxConfig.length - outerWall * 2;
    const packed = autoPackCompartments(compartments, usableWidth, usableLength, divider);

    // NEW: Initial box-level position (simple vertical stack)
    const trayHeight = tray.estimated_height_mm || 20; // From Step 2
    const boxY = index * (boxConfig.length / trayStructure.trays.length); // Divide box evenly

    return {
      trayId: tray.tray_id,

      // NEW: Box positioning (start with simple stacking)
      boxX: 0,
      boxY: boxY,
      boxWidth: boxConfig.width,   // Full width initially
      boxLength: boxConfig.length / trayStructure.trays.length, // Divide height evenly

      // Existing tray internals
      compartments: packed,
      outerWallThickness: outerWall,
      dividerThickness: divider,
      floorThickness: 0.8,
    };
  });

  set({
    layouts,
    layoutViewMode: 'box',           // Start in Box View
    editingTrayId: null,
    selectedTrayId: null,
    selectedCompartmentId: null,
  });
}
```

---

## Component Structure Changes

### Current Structure (Phase 4C)
```
step3/
├── LayoutEditor.tsx          # Main container
├── TrayCanvas.tsx            # Konva canvas for compartments
├── CompartmentRect.tsx       # Draggable compartment
├── CompartmentProperties.tsx # Properties panel
├── TrayTabBar.tsx            # ❌ REMOVE (no longer needed)
├── CanvasGrid.tsx            # Grid background
├── AutoPackButton.tsx        # Auto-pack compartments
└── index.ts
```

### New Structure (Refactored)
```
step3/
├── LayoutEditor.tsx          # Router: renders BoxView or TrayView based on mode
│
├── BoxView.tsx               # NEW: Level 1 - Box footprint with trays
├── TrayRect.tsx              # NEW: Draggable/resizable tray in box view
│
├── TrayView.tsx              # NEW: Level 2 - Compartment arrangement (current LayoutEditor content)
├── TrayCanvas.tsx            # Existing - compartment canvas (used by TrayView)
├── CompartmentRect.tsx       # Existing - draggable compartment
├── CompartmentProperties.tsx # Existing - properties panel
├── CanvasGrid.tsx            # Existing - grid background
├── AutoPackButton.tsx        # Existing - auto-pack compartments
│
└── index.ts
```

---

## New Component Implementations

### A. LayoutEditor.tsx (Refactored - Router)

```tsx
import { useEffect } from 'react';
import { useDesignStore } from '../../../store/designStore';
import { BoxView } from './BoxView';
import { TrayView } from './TrayView';

export function LayoutEditor() {
  const {
    trayStructure,
    layouts,
    layoutViewMode,
    setCurrentStep,
    initializeLayouts,
  } = useDesignStore();

  // Auto-initialize layouts on mount
  useEffect(() => {
    if (!layouts || layouts.length === 0) {
      initializeLayouts();
    }
  }, [layouts, initializeLayouts]);

  if (!trayStructure || !layouts.length) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-600">Initializing layout editor...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Step 3: Layout Editor</h1>
        <p className="mt-2 text-gray-600">
          {layoutViewMode === 'box'
            ? 'Arrange trays within the box. Double-click a tray to edit its compartments.'
            : 'Arrange compartments within the tray. Drag to move, drag edges to resize.'}
        </p>
      </div>

      {/* Conditional Rendering Based on View Mode */}
      {layoutViewMode === 'box' ? <BoxView /> : <TrayView />}

      {/* Navigation (only show in Box View) */}
      {layoutViewMode === 'box' && (
        <div className="flex justify-between items-center pt-6 border-t border-gray-200">
          <button
            onClick={() => setCurrentStep(2)}
            className="px-6 py-3 text-gray-700 hover:text-gray-900 font-medium"
          >
            ← Back: Sort & Plan
          </button>

          <button
            onClick={() => setCurrentStep(4)}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
          >
            Next: Preview & Export →
          </button>
        </div>
      )}
    </div>
  );
}
```

### B. BoxView.tsx (NEW - Primary View)

```tsx
import { Stage, Layer, Rect, Text } from 'react-konva';
import { useDesignStore } from '../../../store/designStore';
import { CanvasGrid } from './CanvasGrid';
import { TrayRect } from './TrayRect';

export function BoxView() {
  const { boxConfig, layouts, trayStructure } = useDesignStore();

  // Scale: fit box into ~800px wide canvas
  const canvasWidth = 800;
  const boxWidthMm = boxConfig.width;
  const boxLengthMm = boxConfig.length;
  const scale = canvasWidth / Math.max(boxWidthMm, boxLengthMm);
  const canvasHeight = (boxLengthMm / boxWidthMm) * canvasWidth;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Box View</h2>
        <p className="text-sm text-gray-600">
          Box dimensions: {boxConfig.width}×{boxConfig.length}×{boxConfig.height}mm
        </p>
      </div>

      <div className="border border-gray-300 rounded inline-block bg-white">
        <Stage width={canvasWidth} height={canvasHeight}>
          <Layer>
            {/* Box outline */}
            <Rect
              x={0}
              y={0}
              width={boxWidthMm * scale}
              height={boxLengthMm * scale}
              stroke="#374151"
              strokeWidth={3}
              fill="#FAFAFA"
              listening={false}
            />

            {/* Grid lines (20mm intervals - larger for box view) */}
            <CanvasGrid
              width={boxWidthMm}
              height={boxLengthMm}
              scale={scale}
              interval={20}
            />

            {/* Tray rectangles */}
            {layouts.map(layout => {
              const tray = trayStructure?.trays.find(t => t.tray_id === layout.trayId);
              return (
                <TrayRect
                  key={layout.trayId}
                  layout={layout}
                  tray={tray}
                  scale={scale}
                  boxWidth={boxWidthMm}
                  boxLength={boxLengthMm}
                />
              );
            })}
          </Layer>
        </Stage>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        💡 Tip: Drag trays to reposition, resize to split box space. Double-click to edit compartments.
      </div>
    </div>
  );
}
```

### C. TrayRect.tsx (NEW - Tray in Box View)

```tsx
import { useRef } from 'react';
import { Rect, Text, Group } from 'react-konva';
import Konva from 'konva';
import type { TrayLayout, Tray } from '../../../types';
import { useDesignStore } from '../../../store/designStore';

interface TrayRectProps {
  layout: TrayLayout;
  tray: Tray | undefined;
  scale: number;
  boxWidth: number;   // mm
  boxLength: number;  // mm
}

export function TrayRect({ layout, tray, scale, boxWidth, boxLength }: TrayRectProps) {
  const { updateCompartment, enterTrayView, selectedTrayId, setSelectedTrayId } = useDesignStore();
  const shapeRef = useRef<Konva.Rect>(null);

  const isSelected = selectedTrayId === layout.trayId;

  // Snap to grid (5mm for box level)
  const snapToGrid = (val: number) => Math.round(val / 5) * 5;

  const handleDragEnd = (e: Konva.KonvaEventObject<DragEvent>) => {
    const newX = snapToGrid(e.target.x() / scale);
    const newY = snapToGrid(e.target.y() / scale);

    // Clamp within box bounds
    const clampedX = Math.max(0, Math.min(newX, boxWidth - layout.boxWidth));
    const clampedY = Math.max(0, Math.min(newY, boxLength - layout.boxLength));

    updateCompartment(layout.trayId, '', { boxX: clampedX, boxY: clampedY } as any);
    // Note: Need to add updateTrayLayout action for box-level updates
  };

  const handleDoubleClick = () => {
    enterTrayView(layout.trayId);
  };

  return (
    <Group>
      <Rect
        ref={shapeRef}
        x={layout.boxX * scale}
        y={layout.boxY * scale}
        width={layout.boxWidth * scale}
        height={layout.boxLength * scale}
        fill="#E0F2FE"
        opacity={0.8}
        stroke={isSelected ? '#2563EB' : '#0369A1'}
        strokeWidth={isSelected ? 3 : 2}
        draggable
        onDragEnd={handleDragEnd}
        onClick={() => setSelectedTrayId(layout.trayId)}
        onDblClick={handleDoubleClick}
        onDblTap={handleDoubleClick}
      />

      {/* Tray name */}
      <Text
        x={layout.boxX * scale + 8}
        y={layout.boxY * scale + 8}
        text={tray?.name || layout.trayId}
        fontSize={14}
        fontStyle="bold"
        fill="#0369A1"
        listening={false}
      />

      {/* Component count + height */}
      <Text
        x={layout.boxX * scale + 8}
        y={layout.boxY * scale + 28}
        text={`${layout.compartments.length} compartments • ${tray?.estimated_height_mm || 0}mm tall`}
        fontSize={11}
        fill="#0C4A6E"
        listening={false}
      />

      {/* Dimensions */}
      <Text
        x={layout.boxX * scale + 8}
        y={layout.boxY * scale + (layout.boxLength * scale) - 24}
        text={`${layout.boxWidth}×${layout.boxLength}mm`}
        fontSize={10}
        fill="#64748B"
        listening={false}
      />
    </Group>
  );
}
```

### D. TrayView.tsx (NEW - Wraps Existing Canvas)

Extracts the compartment editing UI from current LayoutEditor:

```tsx
import { useDesignStore } from '../../../store/designStore';
import { TrayCanvas } from './TrayCanvas';
import { CompartmentProperties } from './CompartmentProperties';
import { AutoPackButton } from './AutoPackButton';

export function TrayView() {
  const { layouts, editingTrayId, trayStructure, exitTrayView } = useDesignStore();

  const currentLayout = layouts.find(l => l.trayId === editingTrayId);
  const currentTray = trayStructure?.trays.find(t => t.tray_id === editingTrayId);

  if (!currentLayout || !currentTray) {
    return <div>Error: No tray selected</div>;
  }

  return (
    <>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <button
          onClick={exitTrayView}
          className="px-4 py-2 bg-white border border-blue-300 rounded hover:bg-blue-50
            text-blue-700 font-medium text-sm"
        >
          ← Back to Box View
        </button>
        <span className="ml-4 text-sm text-blue-800">
          Editing: <strong>{currentTray.name}</strong>
        </span>
      </div>

      <div className="flex gap-6">
        {/* Canvas Area */}
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-gray-900">{currentTray.name}</h2>
              <AutoPackButton trayId={currentLayout.trayId} />
            </div>
            <TrayCanvas layout={currentLayout} tray={currentTray} />
          </div>
        </div>

        {/* Properties Panel */}
        <div className="w-80">
          <CompartmentProperties />
        </div>
      </div>
    </>
  );
}
```

---

## Store Actions to Add/Update

### 1. Add View Mode Actions

```typescript
setLayoutViewMode: (mode) => {
  set({ layoutViewMode: mode });
},

enterTrayView: (trayId) => {
  set({
    layoutViewMode: 'tray',
    editingTrayId: trayId,
    selectedCompartmentId: null,
  });
},

exitTrayView: () => {
  set({
    layoutViewMode: 'box',
    editingTrayId: null,
    selectedCompartmentId: null,
  });
},
```

### 2. Add Box-Level Tray Update

```typescript
updateTrayLayout: (trayId, updates: Partial<TrayLayout>) => {
  set((state) => ({
    layouts: state.layouts.map(layout =>
      layout.trayId === trayId
        ? { ...layout, ...updates }
        : layout
    ),
  }));
},
```

### 3. Update initializeLayouts

Add box-level positioning (boxX, boxY, boxWidth, boxLength) to each layout.

---

## Migration Steps

### Step 1: Update Types
- Add boxX, boxY, boxWidth, boxLength to TrayLayout
- Add layoutViewMode, editingTrayId to DesignState

### Step 2: Update Store
- Add new state fields
- Add 3 new actions (setLayoutViewMode, enterTrayView, exitTrayView, updateTrayLayout)
- Update initializeLayouts to set box positions
- Update partialize to persist new fields

### Step 3: Create New Components
- Create BoxView.tsx
- Create TrayRect.tsx
- Create TrayView.tsx (extract from current LayoutEditor)

### Step 4: Refactor LayoutEditor
- Change to router pattern (render BoxView or TrayView based on mode)
- Remove TrayTabBar usage

### Step 5: Update Existing Components
- TrayCanvas - no changes needed (used by TrayView)
- CompartmentRect - no changes needed
- CompartmentProperties - no changes needed
- Remove TrayTabBar.tsx (no longer used)

### Step 6: Test
- Load test data
- Navigate to Step 3 → should see Box View
- Drag trays around in box
- Double-click tray → should drill into Tray View
- Click "Back to Box View" → should return
- Test persistence

---

## Acceptance Criteria

✅ **Box View renders** - Box outline with tray rectangles
✅ **Trays show info** - Name, compartment count, height
✅ **Drag trays** - Reposition within box (snap to 5mm grid)
✅ **Resize trays** - Split box space (future - v2 feature)
✅ **Double-click drill-in** - Opens Tray View for compartment editing
✅ **Tray View works** - Existing compartment drag/resize still works
✅ **Back to Box View** - Button returns to overview
✅ **Navigation** - Back/Next only visible in Box View
✅ **Persistence** - Both levels saved to localStorage

---

## Estimated Time

- **Step 1-2** (Types + Store): 30 min
- **Step 3** (New Components): 2 hours
- **Step 4** (Refactor LayoutEditor): 30 min
- **Step 5** (Cleanup): 30 min
- **Step 6** (Testing): 1 hour

**Total**: ~4.5 hours

---

## Benefits of Two-Level Approach

1. **Clearer mental model** - See all trays at once, drill down for details
2. **Better for multi-tray designs** - Visualize how trays tile in the box
3. **Future flexibility** - Can add tray rotation, side-by-side layouts, nested trays
4. **No tabs** - More intuitive than switching tabs
5. **Matches physical workflow** - First decide tray positions in box, then design each tray's internals

Ready to implement? 🚀
