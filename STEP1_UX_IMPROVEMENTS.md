# Step 1 UX Improvements Plan

## Issues to Fix

2. **Player component grouping** - Group identical player sets, single form with player count adjuster
3. **Single Save button** - One "Save All Changes" instead of per-component Save/Cancel
4. **Meeple auto-detect** - Auto-fill standard meeples to 16×16×10mm in Quick Defaults
5. **Board & Rulebook simplified** - Only thickness needed, L×W from box, mark as non-printed layer

---

## Implementation Order

### 1. Issue 5: Boards & Rulebooks Simplified (Easiest)

**Changes Needed:**

**A. Quick Defaults Logic (`utils/quickDefaultsLogic.ts`)**
- Boards/Rulebooks already auto-fill L×W from box
- Change: Set `needsDimensions = false` for these types
- Change: Set `prefillComplete = true` even with just thickness

```typescript
// In applyQuickDefaultsToComponent()
if (component.type === 'Boards' || component.type === 'Rulebook') {
  return {
    ...component,
    length: boxConfig.length,
    width: boxConfig.width,
    height: component.height || 3, // Use existing or default
    prefillLength: boxConfig.length,
    prefillWidth: boxConfig.width,
    prefillHeight: component.height || 3,
    prefillSource: 'Matches box dimensions — non-printed layer',
    prefillComplete: true,   // ✅ Mark complete
    needsDimensions: false,  // ✅ No warning
  };
}
```

**B. Component Editor (`components/wizard/step1/ComponentEditor.tsx`)**
- For Boards/Rulebooks, show simplified UI
- Only thickness input visible
- Show "Non-printed layer" badge
- Show L×W as read-only (from box dimensions)

```tsx
{/* Special UI for Boards/Rulebooks */}
{(localState.type === 'Boards' || localState.type === 'Rulebook') && (
  <div className="p-3 bg-amber-50 border border-amber-200 rounded">
    <p className="text-sm text-amber-800 mb-2">
      📦 Non-printed layer — sits on top of insert stack
    </p>
    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="text-xs text-gray-500">Footprint (from box)</label>
        <p className="text-sm font-medium text-gray-700">
          {boxConfig.length}×{boxConfig.width}mm
        </p>
      </div>
      <div>
        <label className="block text-xs text-gray-500 mb-1">Thickness (mm)</label>
        <input
          type="number"
          value={localState.height || ''}
          onChange={(e) => update({ height: Number(e.target.value) || null })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
          placeholder="e.g., 3"
        />
      </div>
    </div>
  </div>
)}
```

**C. Component Review (`components/wizard/step1/ComponentReview.tsx`)**
- Show visual distinction for Boards/Rulebooks
- Amber background or icon
- Don't show "Needs dimensions" warning

---

### 2. Issue 4: Meeple Auto-Detect (Simple)

**Changes Needed:**

**A. Quick Defaults (`components/wizard/step1/QuickDefaults.tsx`)**
- Detect meeples in component groups
- No need for user toggle (auto-detect is enough)

```typescript
const detectDefaults = (): QuickDefaultsType => {
  const allComponents = selectedComponentGroups.flatMap(g => g.components);

  const hasDice = allComponents.some(c => c.type === 'Dice');
  const hasCubes = allComponents.some(c =>
    c.type === 'Tokens' &&
    (c.name.toLowerCase().includes('cube') || c.name.toLowerCase().includes('resource'))
  );
  const hasMinis = allComponents.some(c =>
    c.type === 'Meeples/Minis' &&
    !c.name.toLowerCase().includes('meeple')  // Minis but NOT meeples
  );

  return {
    cardboardQuality: 'standard',
    cardsSleeved: hasCards ? 'unsleeved' : 'unsleeved',
    hasDice,
    diceSizeMm: 16,
    hasCubes,
    cubeSizeMm: 8,
    hasMinis,
    hasExpansionSpace: false,
  };
};
```

**B. Quick Defaults Logic (`utils/quickDefaultsLogic.ts`)**
- Standard meeples (16×16×10mm) should be detected

```typescript
// In getDimensionPrefill()

// Standard meeples (NOT large minis)
if (type === 'Meeples/Minis' && isMeeple(name)) {
  return {
    length: 16,
    width: 16,
    height: 10,
    source: 'Standard meeple (16×16×10mm)',
  };
}

// Large miniatures (flagged by user)
if (hasMinis && (type === 'Meeples/Minis' || isMini(name))) {
  return {
    length: null,
    width: null,
    height: null,
    source: 'Miniature — requires manual measurement',
    clearanceMm: 2.0,
    clearanceNote: 'Miniature — wider clearance applied (+2mm)',
  };
}
```

Current logic already has meeple detection but the order might be wrong. Fix the order:
1. Check for standard meeples first (isMeeple())
2. Then check for large minis (hasMinis flag)

---

### 3. Issue 3: Single Save Button (Medium)

**Current Flow:**
- Each component has expand/collapse
- When expanded, local state + Save/Cancel buttons
- Save commits to store

**New Flow:**
- Each component always editable (no collapse/expand, or keep collapse but remove save buttons)
- Changes update local state
- One "Save All Changes" button at bottom
- Track dirty state globally
- Commit all changes at once

**Changes Needed:**

**A. Component Editor State**
```typescript
// ComponentEditor.tsx
const [localComponents, setLocalComponents] = useState<Component[]>(components);
const [isDirty, setIsDirty] = useState(false);

useEffect(() => {
  setLocalComponents(components);
  setIsDirty(false);
}, [components]);

const updateLocal = (id: string, updates: Partial<Component>) => {
  setLocalComponents(prev =>
    prev.map(c => c.id === id ? { ...c, ...updates } : c)
  );
  setIsDirty(true);
};

const handleSaveAll = () => {
  localComponents.forEach(comp => {
    updateComponent(comp.id, comp);
  });
  setIsDirty(false);
};
```

**B. Remove Save/Cancel from Items**
```tsx
// ComponentEditorItem - remove action buttons
// Just have inputs that call updateLocal on change

{/* No more Save/Cancel buttons here */}
```

**C. Add Save All at Bottom**
```tsx
{/* At bottom of ComponentEditor */}
{isDirty && (
  <div className="sticky bottom-0 bg-white border-t-2 border-blue-500 p-4 shadow-lg">
    <div className="flex items-center justify-between">
      <p className="text-sm text-gray-600">
        You have unsaved changes
      </p>
      <button
        onClick={handleSaveAll}
        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
      >
        💾 Save All Changes
      </button>
    </div>
  </div>
)}
```

---

### 4. Issue 2: Player Component Grouping (Complex)

**Current:** Each player component (e.g., "Player 1 Cards", "Player 2 Cards") gets separate form

**New:** Group identical player components, show one form with player count adjuster

**Detection Logic:**
```typescript
// In ComponentEditor
const groupPlayerComponents = (components: Component[]): ComponentGroup[] => {
  const groups: Map<string, Component[]> = new Map();

  components.forEach(comp => {
    if (comp.playerSpecific && comp.playerIdentifier) {
      // Group by component type/name (strip player identifier)
      const baseKey = comp.name.replace(/Player \d+/i, 'Player').trim();
      if (!groups.has(baseKey)) {
        groups.set(baseKey, []);
      }
      groups.get(baseKey)!.push(comp);
    }
  });

  return Array.from(groups.entries()).map(([key, comps]) => ({
    groupKey: key,
    components: comps,
    isPlayerGroup: comps.length > 1,
    playerCount: comps.length,
  }));
};
```

**UI Component:**
```tsx
// PlayerComponentGroup.tsx
interface PlayerComponentGroupProps {
  groupKey: string;
  components: Component[];
  playerCount: number;
}

function PlayerComponentGroup({ groupKey, components, playerCount }: PlayerComponentGroupProps) {
  const [count, setCount] = useState(playerCount);
  const representative = components[0]; // Use first as template

  return (
    <div className="border-2 border-blue-200 rounded-lg bg-blue-50 p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-blue-900">
          {groupKey} (per player, identical sets)
        </h4>
        <div className="flex items-center gap-2">
          <span className="text-sm text-blue-700">Player count:</span>
          {[2, 3, 4, 5].map(n => (
            <button
              key={n}
              onClick={() => setCount(n)}
              className={`px-3 py-1 rounded ${
                count === n
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-blue-600 border border-blue-300'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      {/* Single dimension form */}
      <div className="grid grid-cols-3 gap-4 bg-white p-3 rounded">
        <input type="number" placeholder="Length" ... />
        <input type="number" placeholder="Width" ... />
        <input type="number" placeholder="Height" ... />
      </div>

      <p className="text-xs text-blue-600 mt-2">
        These dimensions will apply to all {count} player sets
      </p>
    </div>
  );
}
```

**Store Action:**
```typescript
// Update all components in a player group
updatePlayerGroup: (componentIds: string[], updates: Partial<Component>) => {
  set((state) => ({
    components: state.components.map(comp =>
      componentIds.includes(comp.id)
        ? { ...comp, ...updates, needsDimensions: false }
        : comp
    ),
  }));
}
```

---

## Implementation Steps

### Step 1: Issue 5 (Boards/Rulebooks) - 1 hour
1. Update `quickDefaultsLogic.ts` to mark Boards/Rulebooks complete
2. Add special UI in `ComponentEditor.tsx` for these types
3. Add visual distinction in `ComponentReview.tsx`
4. Test with Qwixx (has rulebook)

### Step 2: Issue 4 (Meeple detect) - 30 min
1. Fix order in `getDimensionPrefill()` (meeples before minis)
2. Verify meeple detection in Quick Defaults
3. Test with game that has meeples

### Step 3: Issue 3 (Single Save) - 2 hours
1. Refactor ComponentEditor to use local state array
2. Remove Save/Cancel from ComponentEditorItem
3. Add "Save All Changes" sticky button
4. Add dirty state tracking
5. Test workflow

### Step 4: Issue 2 (Player grouping) - 3 hours
1. Create grouping logic in ComponentEditor
2. Create PlayerComponentGroup component
3. Add `updatePlayerGroup` store action
4. Wire up player count adjuster
5. Test with multi-player game

**Total Estimate: 6.5 hours**

---

## Testing Checklist

After implementation:

**Issue 5 (Boards/Rulebooks):**
- [ ] Board auto-fills L×W from box
- [ ] Only thickness input shown
- [ ] No "Needs dimensions" warning
- [ ] Shows "Non-printed layer" badge
- [ ] Amber styling distinguishes from tray components

**Issue 4 (Meeple detect):**
- [ ] Meeples auto-fill to 16×16×10mm
- [ ] Minis (if flagged) still show manual measurement needed
- [ ] Quick Defaults summary shows detected types

**Issue 3 (Single Save):**
- [ ] Can edit multiple components inline
- [ ] Changes not saved until "Save All Changes" clicked
- [ ] Dirty indicator appears when changes made
- [ ] Save button is sticky at bottom
- [ ] After save, dirty state clears

**Issue 2 (Player grouping):**
- [ ] Player components grouped together
- [ ] Shows "4 player sets" or similar
- [ ] Player count adjuster buttons work
- [ ] Entering dimensions applies to all player components
- [ ] Can adjust from 2-5 players
- [ ] Save applies dimensions to correct components

Ready to implement? I'll go in order: 5 → 4 → 3 → 2
