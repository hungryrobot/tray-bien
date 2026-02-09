# 🚀 Tray Bien - Quick Launch Guide

## Launch the App

### Step 1: Open Terminal
```bash
cd /Users/avrom/Documents/Work/Programs/tray-bien
```

### Step 2: Start Streamlit
```bash
streamlit run app.py
```

**Your browser will automatically open to:** `http://localhost:8501`

---

## 🧪 Test Phase 2 (Steps 1-2)

### Quick Test Flow:

1. **Home Page**
   - See feature overview
   - Click sidebar → **New Insert**

2. **Settings** (optional first-time setup)
   - Set nozzle diameter: **0.4mm** (standard)
   - Save settings

3. **New Insert → Step 1: Box Setup**
   - Select **"Wingspan"** from dropdown
   - See dimensions: 296×296×71mm
   - Adjust lid clearance: **3mm**
   - Expand **"What's a clearance zone?"** → See diagram
   - Click **"Next: Components →"**

4. **Step 2: Component Inventory**
   - Click **"➕ Add Component"**
   - Type: **Cards**
   - Preset: **Poker (Sleeved - Standard)**
   - Name: **Bird Cards**
   - Quantity: **170**

   - Click **"➕ Add Component"** again
   - Type: **Tokens**
   - Preset: **Small Round Token**
   - Name: **Eggs**
   - Quantity: **75**

   - Click **"➕ Add Component"** again
   - Type: **Dice**
   - Preset: **d6 (16mm)**
   - Name: **Dice**
   - Quantity: **5**

   - Check **Component Summary**:
     - Total Volume: ~XX cm³
     - Box Fill: ~XX%

   - Expand **"What's a finger cutout?"** → See diagram
   - Expand **"What's a pedestal base?"** → See diagram

   - Click **"Next: Layout →"**

5. **Steps 3-5** (Placeholders)
   - See visual diagram previews:
     - Lid comparison
     - Wall thickness
     - Nested sub-trays
     - Bottom holes
     - Angled card well

   - Navigate to **Step 5: Preview**
   - See **Current Configuration** summary
   - Verify box config and components listed

6. **Test Navigation**
   - Click step buttons (1-5) in header
   - Use Back/Next buttons
   - Verify data persists when navigating

7. **Sidebar Features**
   - Check **"Show All Diagrams"**
   - Expand each of 8 diagrams
   - Verify all SVGs render

---

## ✅ What Should Work (Phase 2 Partial)

### Fully Functional:
- ✅ **Step 1: Box Setup**
  - 20 game presets
  - Custom dimensions
  - Lid clearance
  - Volume calculator
  - Box diagram
  - Clearance zone diagram

- ✅ **Step 2: Component Inventory**
  - Add/remove components
  - 7 component types
  - 30+ smart presets
  - Volume calculations
  - Box fill percentage
  - Warnings for over/under-filling
  - Finger cutout diagram
  - Pedestal base diagram

- ✅ **Visual Explainers**
  - All 8 SVG diagrams
  - Embedded in steps
  - Sidebar reference panel

- ✅ **Navigation**
  - Step buttons
  - Back/Next buttons
  - Session state persistence

### Placeholders (Coming Soon):
- ⏳ Step 3: Layout Preferences
- ⏳ Step 4: Customization
- ⏳ Step 5: Preview & Export
- ⏳ OpenSCAD code generation
- ⏳ AI chat refinement
- ⏳ STL export

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill existing Streamlit processes
lsof -ti:8501 | xargs kill -9

# Restart
streamlit run app.py
```

### Import Errors
```bash
# Verify you're in the right directory
pwd
# Should show: /Users/avrom/Documents/Work/Programs/tray-bien

# Check Python path
python3.10 --version
# Should show: Python 3.10.x

# Reinstall dependencies if needed
pip3.10 install -r requirements.txt
```

### Page Not Loading
- Check terminal for Python errors
- Try refreshing browser (Cmd+R)
- Try different browser
- Check browser console (F12) for JavaScript errors

### Diagrams Not Showing
- Check that SVG syntax is correct
- Try different browser (Chrome works best)
- Check browser console for errors

---

## 📸 What You Should See

### Home Page
- Large "Tray Bien" header with 🎲
- Three feature boxes (Visual Design, AI Refinement, Smart Optimization)
- Quick start guide
- Design process expandable section

### New Insert - Step 1
- Box selection dropdown (20 games)
- Dimension inputs or preset values
- Lid clearance slider
- Metrics: Length, Width, Available Height, Volume
- Box outline SVG diagram
- Clearance zone diagram in expander

### New Insert - Step 2
- "Add Component" button
- Component cards with expandable details
- Type selector with presets
- Volume summary metrics
- Box fill percentage with color coding
- Component list in expander
- Finger cutout & pedestal base diagrams

### Visual Explainers
- 8 clean SVG diagrams (~200×120px each)
- Labels and annotations
- Consistent color scheme (grays, blues)

---

## 🎯 Success Criteria

Phase 2 (Partial) test is **successful** if:

1. ✅ App launches without errors
2. ✅ All navigation works (home, settings, new insert, my designs)
3. ✅ Step 1 box setup fully functional
4. ✅ Step 2 component inventory fully functional
5. ✅ All 8 SVG diagrams display correctly
6. ✅ Data persists when navigating between steps
7. ✅ No errors in terminal or browser console

---

## 📊 Test Results Template

After testing, record:

**✅ Working:**
-

**🐛 Broken:**
-

**💡 Observations:**
-

**🚀 Ready for Phase 2 Completion:**
- [ ] Yes, continue with Layout Preferences
- [ ] No, fix issues first

---

## Next Steps

After verifying Steps 1-2 work correctly:
1. Build **Step 3: Layout Preferences** (smart lid logic, walls, cutouts)
2. Build **Step 4: Customization** (logo upload, labels)
3. Build **Step 5: Summary Page** (review, save, load)
4. Move to **Phase 3: OpenSCAD Code Generation**

---

## 🛑 Stop the App

Press **Ctrl+C** in the terminal where Streamlit is running.

Or force kill:
```bash
lsof -ti:8501 | xargs kill -9
```
