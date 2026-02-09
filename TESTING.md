# Testing Guide - Tray Bien Phase 2

## 🚀 Launch Instructions

### 1. Navigate to project directory
```bash
cd /Users/avrom/Documents/Work/Programs/tray-bien
```

### 2. Verify dependencies are installed
```bash
pip3.10 list | grep -E "streamlit|pillow"
```

Should show:
- streamlit (>= 1.29.0)
- Pillow (>= 10.0.0)

If missing, install:
```bash
pip3.10 install -r requirements.txt
```

### 3. Launch Streamlit app
```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

---

## ✅ Test Checklist - Phase 2 (Partial)

### Home Page
- [ ] Page loads without errors
- [ ] Feature boxes display
- [ ] Navigation sidebar visible

### Settings Page
- [ ] Nozzle diameter selector works
- [ ] Wall thickness calculations shown
- [ ] AI provider dropdown works
- [ ] Settings save/load

### New Insert - Step 1: Box Setup
- [ ] Page loads without errors
- [ ] **Known Game** dropdown shows 20 games
- [ ] Selecting a game updates dimensions
- [ ] Game notes display
- [ ] **Custom Dimensions** radio button works
- [ ] Manual dimension inputs update
- [ ] Lid clearance slider works
- [ ] Available volume calculates correctly
- [ ] Box outline SVG diagram displays
- [ ] Validation warnings show for edge cases
- [ ] "What's a clearance zone?" expander shows SVG diagram
- [ ] "Next: Components →" button advances to step 2

### New Insert - Step 2: Component Inventory
- [ ] Page loads without errors
- [ ] "➕ Add Component" button creates new component
- [ ] Component type dropdown works (Cards, Tokens, Dice, etc.)
- [ ] **Cards presets** load correctly (poker, mini, sleeved, etc.)
- [ ] **Dice presets** load correctly (d4, d6, d8, d10, d12, d20)
- [ ] **Token presets** load correctly (round, square, wooden cubes, poker chips)
- [ ] **Meeples/Minis presets** load correctly
- [ ] **Boards presets** load correctly
- [ ] **Rulebook presets** load correctly
- [ ] Custom dimensions work for each type
- [ ] Quantity input works
- [ ] Component name input works
- [ ] Volume calculations appear
- [ ] Total volume summary shows
- [ ] Box fill percentage calculates
- [ ] Warnings show when >90% or <30% fill
- [ ] Component list expander shows all added items
- [ ] "🗑️ Remove" button deletes components
- [ ] Visual explainer diagrams show in expanders
- [ ] "← Back: Box Setup" returns to step 1
- [ ] "Next: Layout →" advances to step 3
- [ ] Error shows if no components added

### New Insert - Step 3: Layout (Placeholder)
- [ ] Placeholder message displays
- [ ] Visual explainer previews show:
  - [ ] Lid comparison diagram
  - [ ] Wall thickness diagram
  - [ ] Nested sub-trays diagram
  - [ ] Bottom holes diagram
- [ ] Navigation buttons work

### New Insert - Step 4: Customization (Placeholder)
- [ ] Placeholder message displays
- [ ] Angled card well diagram shows
- [ ] Navigation buttons work

### New Insert - Step 5: Preview (Placeholder)
- [ ] Placeholder message displays
- [ ] Box configuration JSON shows
- [ ] Components list shows
- [ ] "Start Over" button clears state
- [ ] "Generate Insert" button (disabled) displays

### Visual Explainers (All 8 Diagrams)
Test in sidebar "Show All Diagrams" checkbox:
- [ ] Pedestal Base SVG renders
- [ ] Finger Cutout SVG renders
- [ ] Bottom Hole SVG renders
- [ ] Lid Comparison SVG renders
- [ ] Nested Sub-Trays SVG renders
- [ ] Angled Card Well SVG renders
- [ ] Wall Thickness SVG renders
- [ ] Clearance Zones SVG renders

### Navigation
- [ ] Step buttons (1-5) jump to correct step
- [ ] Active step highlights in primary color
- [ ] Sidebar shows current step number
- [ ] Sidebar checkbox "Show All Diagrams" works

### Session State
- [ ] Data persists between step changes
- [ ] Refreshing page preserves data
- [ ] Multiple components can be added
- [ ] Start Over clears everything

---

## 🐛 Known Issues / Expected Behavior

1. **Steps 3-5 are placeholders** - This is expected. We're testing Steps 1-2 only.
2. **OpenSCAD not required yet** - Code generation is Phase 3.
3. **No AI calls yet** - Chat refinement is Phase 3B.
4. **No STL export yet** - Preview/export is Phase 4.

---

## 🧪 Test Scenarios

### Scenario 1: Design insert for Wingspan
1. Settings → Set nozzle to 0.4mm → Save
2. New Insert → Step 1 → Select "Wingspan" from dropdown
3. Verify dimensions: 296×296×71mm
4. Set lid clearance: 3mm
5. Click "Next: Components"
6. Add component: Cards → Poker (Sleeved) → Name: "Bird Cards" → Quantity: 170
7. Add component: Tokens → Small Round Token → Name: "Eggs" → Quantity: 75
8. Add component: Dice → d6 (16mm) → Name: "Dice" → Quantity: 5
9. Verify total volume and box fill percentage
10. Click expanders to view diagrams
11. Navigate forward to see placeholders
12. Navigate back to verify data persists

### Scenario 2: Custom box with many components
1. New Insert → Step 1 → Select "Custom Dimensions"
2. Enter: 200×150×60mm
3. Lid clearance: 5mm
4. Add 10 different components (mix of types)
5. Verify volume warnings trigger correctly
6. Remove some components
7. Check that totals update

### Scenario 3: Visual explainers tour
1. Sidebar → Check "Show All Diagrams"
2. Expand each diagram
3. Verify all 8 SVGs render correctly
4. Click through step 1-5 and view embedded diagrams

---

## 📊 Success Criteria

Phase 2 (Partial) is successful if:
- ✅ All Step 1 (Box Setup) features work
- ✅ All Step 2 (Component Inventory) features work
- ✅ All 8 SVG diagrams display correctly
- ✅ Navigation between steps works
- ✅ Session state persists
- ✅ No JavaScript errors in browser console
- ✅ No Python errors in terminal

---

## 📝 Feedback Template

After testing, note:
- **What worked well:**
- **What broke:**
- **Confusing UI elements:**
- **Missing features:**
- **Performance issues:**

---

## 🔧 Troubleshooting

### App won't start
```bash
# Check if port is in use
lsof -ti:8501 | xargs kill -9

# Restart
streamlit run app.py
```

### Import errors
```bash
# Reinstall dependencies
pip3.10 install --upgrade streamlit pillow
```

### Diagrams not showing
- Check browser console for errors
- Verify SVG syntax in visual_explainers.py
- Try different browser (Chrome/Safari/Firefox)

### State not persisting
- This is normal on page refresh (Streamlit limitation)
- State persists between step navigation only
