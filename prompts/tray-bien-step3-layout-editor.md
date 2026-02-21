# Tray Bien v3 — Step 3: Layout Editor

## Overview

Build the interactive layout editor for Step 3 of the wizard. The user sees a top-down 2D view of each tray with draggable, resizable compartments inside it. This is the core feature that motivated the React migration — it needs native canvas interaction, not iframe hacks.

Read these files before starting:
- `frontend/src/store/designStore.ts` (current state model)
- `frontend/src/types/index.ts` (current type definitions)
- `tray-bien-design-philosophy.md` (tolerances, clearances, wall thickness rules)
- `frontend/src/components/wizard/steps/Step2SortAndPlan.tsx` (Step 2 output — tray structure)

Plan first. List all files you'll create/modify.

---

## Dependencies

Install these before starting:

```bash
cd frontend
npm install react-konva konva
```

- **Konva.js** — 2D canvas library with built-in drag, resize, hit detection, snap-to-grid
- **react-konva** — React bindings for Konva

---

## Data Model

### Extend Types (frontend/src/types/index.ts)

Add these interfaces:

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
  outerWallThickness: number;   // mm — from nozzle settings
  dividerThickness: number;     // mm — inner walls
  floorThickness: number;       // mm
}
```

### Extend Zustand Store

Add to `DesignState`:

```typescript
// Step 3
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

---

## Compartment Sizing Logic

When initializing layouts from the tray structure, calculate each compartment's size from its component:

```typescript
function createCompartment(component: Component, index: number): Compartment {
  const clearance = getClearance(component);
  
  const width = (component.width || 30) + clearance * 2;
  const length = (component.length || 30) + clearance * 2;
  const depth = calculateStackDepth(component);
  
  return {
    id: `comp_${component.id}`,
    componentId: component.id,
    name: component.name,
    x: 0,   // Will be set by auto-pack
    y: 0,   // Will be set by auto-pack
    width,
    length,
    depth,
    minWidth: width,    // Can't go smaller than component + clearance
    minLength: length,
    color: getComponentColor(component.type),
  };
}
```

### Clearance rules (from design philosophy):
- Cardboard tokens/tiles: +1mm per side
- Wooden/plastic: +0.5mm per side  
- Cards (unsleeved): +0.5mm per side
- Cards (sleeved): +0.75mm per side
- Dice: +1mm per side
- Miniatures: +1mm per side (or +2mm if hasMinis flagged)

### Stack depth calculation:
- Cards: stack height (quantity × per-card thickness) + 5mm finger room
- Tokens stacked: quantity × thickness + 3mm finger room
- Dice: single die height + 2mm (dice don't stack well)
- Meeples: component height + 2mm
- Everything else: component height + 2mm

### Component colors (for visual distinction):
- Cards: #93C5FD (light blue)
- Tokens: #FCD34D (yellow)
- Tiles: #86EFAC (green)
- Dice: #F87171 (red)
- Meeples/Minis: #C4B5FD (purple)
- Boards: #FDBA74 (orange)
- Other: #D1D5DB (gray)

---

## Auto-Pack Algorithm

Implement a bottom-left shelf packing algorithm:

```typescript
function autoPackCompartments(
  compartments: Compartment[],
  trayWidth: number,    // box inner width - 2 * outerWallThickness
  trayLength: number,   // box inner length - 2 * outerWallThickness
  wallThickness: number // divider thickness between compartments
): Compartment[] {
  // Sort by area (largest first) for better packing
  const sorted = [...compartments].sort(
    (a, b) => (b.width * b.length) - (a.width * a.length)
  );
  
  let currentX = 0;
  let currentY = 0;
  let rowHeight = 0;
  
  return sorted.map(comp => {
    // Try to place in current row
    if (currentX + comp.width > trayWidth) {
      // Start new row
      currentX = 0;
      currentY += rowHeight + wallThickness;
      rowHeight = 0;
    }
    
    const placed = {
      ...comp,
      x: currentX,
      y: currentY,
    };
    
    currentX += comp.width + wallThickness;
    rowHeight = Math.max(rowHeight, comp.length);
    
    return placed;
  });
}
```

---

## Component Structure

```
frontend/src/components/wizard/step3/
├── LayoutEditor.tsx          # Main container — tab bar + canvas + properties
├── TrayCanvas.tsx            # Konva Stage/Layer — renders one tray
├── CompartmentRect.tsx       # Single draggable/resizable compartment
├── CompartmentProperties.tsx # Selected compartment detail panel
├── TrayTabBar.tsx            # Tab switcher between trays
├── AutoPackButton.tsx        # Trigger auto-pack for current tray
├── CanvasGrid.tsx            # Background grid lines
└── index.ts
```

---

## Component Implementations

### A. LayoutEditor.tsx (Main Container)

```tsx
export function LayoutEditor() {
  const { 
    trayStructure, layouts, selectedTrayId, 
    setSelectedTrayId, setCurrentStep, initializeLayouts 
  } = useDesignStore();
  
  useEffect(() => {
    if (!layouts || layouts.length === 0) {
      initializeLayouts();
    }
  }, []);
  
  if (!trayStructure || !layouts.length) {
    return <div>Loading layout editor...</div>;
  }
  
  const currentTrayId = selectedTrayId || layouts[0]?.trayId;
  const currentLayout = layouts.find(l => l.trayId === currentTrayId);
  const currentTray = trayStructure.trays.find(t => t.tray_id === currentTrayId);
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Step 3: Layout Editor</h1>
        <p className="text-gray-600">Arrange compartments within each tray. Drag to move, drag edges to resize.</p>
      </div>
      
      {/* Tray tab bar */}
      <TrayTabBar 
        layouts={layouts}
        trays={trayStructure.trays}
        selectedTrayId={currentTrayId}
        onSelect={setSelectedTrayId}
      />
      
      {/* Canvas + Properties side by side */}
      <div className="flex gap-6">
        {/* Canvas area — takes most of the width */}
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold">{currentTray?.name}</h2>
              <AutoPackButton trayId={currentTrayId} />
            </div>
            <TrayCanvas 
              layout={currentLayout}
              tray={currentTray}
            />
          </div>
        </div>
        
        {/* Properties panel — right sidebar */}
        <div className="w-80">
          <CompartmentProperties />
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t">
        <button onClick={() => setCurrentStep(2)} className="...">
          ← Back: Sort & Plan
        </button>
        <button onClick={() => setCurrentStep(4)} className="...">
          Next: Preview & Export →
        </button>
      </div>
    </div>
  );
}
```

### B. TrayCanvas.tsx (Konva Canvas)

This is the core interactive component.

```tsx
import { Stage, Layer, Rect, Text, Line } from 'react-konva';

interface TrayCanvasProps {
  layout: TrayLayout;
  tray: Tray;
}

export function TrayCanvas({ layout, tray }: TrayCanvasProps) {
  const { boxConfig } = useDesignStore();
  
  // Scale: convert mm to pixels
  // Fit the tray into ~700px wide canvas
  const canvasWidth = 700;
  const trayWidthMm = boxConfig.width - layout.outerWallThickness * 2;
  const trayLengthMm = boxConfig.length - layout.outerWallThickness * 2;
  const scale = canvasWidth / Math.max(trayWidthMm, trayLengthMm);
  const canvasHeight = (trayLengthMm / trayWidthMm) * canvasWidth;
  
  return (
    <Stage width={canvasWidth} height={canvasHeight}>
      <Layer>
        {/* Tray outline */}
        <Rect
          x={0} y={0}
          width={trayWidthMm * scale}
          height={trayLengthMm * scale}
          stroke="#9CA3AF"
          strokeWidth={2}
          fill="#F9FAFB"
        />
        
        {/* Grid lines (10mm intervals) */}
        <CanvasGrid 
          width={trayWidthMm} 
          height={trayLengthMm} 
          scale={scale} 
          interval={10} 
        />
        
        {/* Compartments */}
        {layout.compartments.map(comp => (
          <CompartmentRect
            key={comp.id}
            compartment={comp}
            scale={scale}
            trayId={layout.trayId}
            trayWidth={trayWidthMm}
            trayLength={trayLengthMm}
          />
        ))}
      </Layer>
    </Stage>
  );
}
```

### C. CompartmentRect.tsx (Draggable + Resizable)

```tsx
import { Rect, Text, Group, Transformer } from 'react-konva';

interface CompartmentRectProps {
  compartment: Compartment;
  scale: number;
  trayId: string;
  trayWidth: number;   // mm — inner usable width
  trayLength: number;  // mm — inner usable length
}

export function CompartmentRect({ compartment, scale, trayId, trayWidth, trayLength }: CompartmentRectProps) {
  const { updateCompartment, selectedCompartmentId, setSelectedCompartmentId } = useDesignStore();
  const shapeRef = useRef<any>(null);
  const trRef = useRef<any>(null);
  
  const isSelected = selectedCompartmentId === compartment.id;
  
  // Snap to 1mm grid
  const snapToGrid = (val: number) => Math.round(val);
  
  const handleDragEnd = (e: any) => {
    const newX = snapToGrid(e.target.x() / scale);
    const newY = snapToGrid(e.target.y() / scale);
    
    // Clamp within tray bounds
    const clampedX = Math.max(0, Math.min(newX, trayWidth - compartment.width));
    const clampedY = Math.max(0, Math.min(newY, trayLength - compartment.length));
    
    updateCompartment(trayId, compartment.id, { x: clampedX, y: clampedY });
  };
  
  const handleTransformEnd = () => {
    const node = shapeRef.current;
    const scaleX = node.scaleX();
    const scaleY = node.scaleY();
    
    // Reset scale and apply to width/length
    node.scaleX(1);
    node.scaleY(1);
    
    const newWidth = snapToGrid(Math.max(compartment.minWidth, (node.width() * scaleX) / scale));
    const newLength = snapToGrid(Math.max(compartment.minLength, (node.height() * scaleY) / scale));
    
    updateCompartment(trayId, compartment.id, {
      x: snapToGrid(node.x() / scale),
      y: snapToGrid(node.y() / scale),
      width: newWidth,
      length: newLength,
    });
  };
  
  useEffect(() => {
    if (isSelected && trRef.current && shapeRef.current) {
      trRef.current.nodes([shapeRef.current]);
      trRef.current.getLayer().batchDraw();
    }
  }, [isSelected]);
  
  return (
    <>
      <Group>
        <Rect
          ref={shapeRef}
          x={compartment.x * scale}
          y={compartment.y * scale}
          width={compartment.width * scale}
          height={compartment.length * scale}
          fill={compartment.color}
          opacity={0.7}
          stroke={isSelected ? '#2563EB' : '#374151'}
          strokeWidth={isSelected ? 2 : 1}
          draggable
          onDragEnd={handleDragEnd}
          onClick={() => setSelectedCompartmentId(compartment.id)}
          onTap={() => setSelectedCompartmentId(compartment.id)}
        />
        
        {/* Component name label */}
        <Text
          x={compartment.x * scale + 4}
          y={compartment.y * scale + 4}
          text={compartment.name}
          fontSize={11}
          fill="#1F2937"
          width={(compartment.width * scale) - 8}
          wrap="word"
          listening={false}
        />
        
        {/* Dimensions label */}
        <Text
          x={compartment.x * scale + 4}
          y={compartment.y * scale + (compartment.length * scale) - 18}
          text={`${compartment.width}×${compartment.length}mm`}
          fontSize={9}
          fill="#6B7280"
          listening={false}
        />
      </Group>
      
      {/* Resize transformer (when selected) */}
      {isSelected && (
        <Transformer
          ref={trRef}
          boundBoxFunc={(oldBox, newBox) => {
            // Enforce minimum size
            if (newBox.width < compartment.minWidth * scale || 
                newBox.height < compartment.minLength * scale) {
              return oldBox;
            }
            return newBox;
          }}
          onTransformEnd={handleTransformEnd}
          rotateEnabled={false}
          keepRatio={false}
        />
      )}
    </>
  );
}
```

### D. CompartmentProperties.tsx (Side Panel)

```tsx
export function CompartmentProperties() {
  const { selectedCompartmentId, layouts, selectedTrayId, updateCompartment } = useDesignStore();
  
  if (!selectedCompartmentId || !selectedTrayId) {
    return (
      <div className="bg-white rounded-lg shadow p-4 text-gray-500 text-sm">
        Click a compartment to view and edit its properties.
      </div>
    );
  }
  
  const layout = layouts.find(l => l.trayId === selectedTrayId);
  const compartment = layout?.compartments.find(c => c.id === selectedCompartmentId);
  
  if (!compartment) return null;
  
  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <h3 className="font-semibold">{compartment.name}</h3>
      
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-500">X (mm)</label>
          <input type="number" value={compartment.x}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { x: Number(e.target.value) })}
            className="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Y (mm)</label>
          <input type="number" value={compartment.y}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { y: Number(e.target.value) })}
            className="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Width (mm)</label>
          <input type="number" value={compartment.width}
            min={compartment.minWidth}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { width: Math.max(compartment.minWidth, Number(e.target.value)) })}
            className="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Length (mm)</label>
          <input type="number" value={compartment.length}
            min={compartment.minLength}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { length: Math.max(compartment.minLength, Number(e.target.value)) })}
            className="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Depth (mm)</label>
          <input type="number" value={compartment.depth}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { depth: Number(e.target.value) })}
            className="w-full border rounded px-2 py-1 text-sm" />
        </div>
      </div>
      
      <div className="text-xs text-gray-500 space-y-1">
        <p>Min size: {compartment.minWidth}×{compartment.minLength}mm</p>
        <p>Volume: {((compartment.width * compartment.length * compartment.depth) / 1000).toFixed(1)} cm³</p>
      </div>
      
      <div className="pt-2 border-t">
        <div className="w-4 h-4 rounded inline-block mr-2" style={{ backgroundColor: compartment.color }} />
        <span className="text-sm text-gray-600">Component type color</span>
      </div>
    </div>
  );
}
```

### E. TrayTabBar.tsx

```tsx
export function TrayTabBar({ layouts, trays, selectedTrayId, onSelect }) {
  return (
    <div className="flex gap-2 border-b pb-2">
      {layouts.map(layout => {
        const tray = trays.find(t => t.tray_id === layout.trayId);
        const isActive = layout.trayId === selectedTrayId;
        return (
          <button
            key={layout.trayId}
            onClick={() => onSelect(layout.trayId)}
            className={`px-4 py-2 rounded-t text-sm font-medium ${
              isActive 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tray?.name || layout.trayId}
            <span className="ml-2 text-xs opacity-75">
              ({layout.compartments.length})
            </span>
          </button>
        );
      })}
    </div>
  );
}
```

### F. CanvasGrid.tsx

```tsx
import { Line } from 'react-konva';

export function CanvasGrid({ width, height, scale, interval = 10 }) {
  const lines = [];
  
  // Vertical lines
  for (let x = 0; x <= width; x += interval) {
    lines.push(
      <Line
        key={`v-${x}`}
        points={[x * scale, 0, x * scale, height * scale]}
        stroke="#E5E7EB"
        strokeWidth={0.5}
        dash={[2, 4]}
      />
    );
  }
  
  // Horizontal lines
  for (let y = 0; y <= height; y += interval) {
    lines.push(
      <Line
        key={`h-${y}`}
        points={[0, y * scale, width * scale, y * scale]}
        stroke="#E5E7EB"
        strokeWidth={0.5}
        dash={[2, 4]}
      />
    );
  }
  
  return <>{lines}</>;
}
```

### G. AutoPackButton.tsx

```tsx
export function AutoPackButton({ trayId }: { trayId: string }) {
  const { autoPackTray } = useDesignStore();
  
  return (
    <button
      onClick={() => autoPackTray(trayId)}
      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium"
    >
      Auto-Pack
    </button>
  );
}
```

---

## Wall Thickness Defaults

Use these for initial layout (from design philosophy, 0.4mm nozzle):
- `outerWallThickness`: 1.6mm
- `dividerThickness`: 1.2mm  
- `floorThickness`: 0.8mm

---

## Store Action: initializeLayouts

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

---

## Verification

Step 3 is complete when:

1. **Canvas renders** — Tray outline visible with grid lines
2. **Compartments display** — Colored rectangles with names and dimensions
3. **Auto-pack works** — Compartments arranged within tray bounds on load
4. **Drag works** — Click and drag compartments to reposition, snaps to 1mm grid
5. **Resize works** — Drag edges/corners to resize, minimum size enforced
6. **Selection works** — Click compartment to select, shows blue border + transformer handles
7. **Properties panel** — Shows/edits X, Y, width, length, depth for selected compartment
8. **Tab switching** — Can switch between trays
9. **Bounds enforcement** — Can't drag outside tray, can't resize beyond tray edges
10. **Navigation** — Back to Step 2, Next to Step 4 (stub is fine)
11. **State persistence** — Refresh preserves layout positions

---

## Known Limitations (acceptable for v1)

- No collision detection between compartments (future enhancement)
- No wall thickness color-coding (future — green/yellow/red based on nozzle multiples)
- No undo/redo
- No rotation of compartments
- Auto-pack is basic shelf algorithm (not optimal bin-packing)
- Canvas doesn't zoom/pan (future — for large trays)

These can all be added iteratively. Get the core drag-and-drop canvas working first.
