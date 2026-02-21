"""
Step 2.5: Tray Structure

Organizes selected components into a proposed tray layout based on V2 extraction
group types (player/shared/setup/board_and_rules). The user reviews and modifies
the proposal before proceeding to Step 3 (Layout).

Data source:
  - st.session_state.selected_component_groups  (set by Step 2 form submit)
  - st.session_state.player_set_count            (set by player count adjuster)
  - st.session_state.player_set_names            (set by editable name inputs)
  - st.session_state.box_config                  (set by Step 1)

Output:
  - st.session_state.tray_structure              (consumed by Step 3)
"""

import math
import streamlit as st
import uuid


# ─── Height estimation constants ──────────────────────────────────────────────

# Rough mm estimates per batch size — used for stack summary only, NOT for layout
_HEIGHT_ESTIMATES = {
    'Cards':        (60,  20),   # 60 cards per deck ≈ 20mm
    'Tokens':       (30,  10),   # 30 tokens ≈ 10mm
    'Tiles':        (20,  15),   # 20 tiles ≈ 15mm
    'Meeples/Minis': (5,  15),   # 5 minis ≈ 15mm
    'Boards':       (1,    4),   # 1 board ≈ 4mm
    'Dice':         (6,   15),   # 6 dice ≈ 15mm
    'Other':        (1,    5),   # 1 item ≈ 5mm
}

_WALL_ALLOWANCE_MM = 5    # Added to largest component estimate per tray
_MIN_TRAY_HEIGHT_MM = 15
_MAX_TRAY_HEIGHT_MM = 60


def _estimate_component_height(comp: dict) -> int:
    """Estimate the storage height (mm) needed for a single component entry."""
    comp_type = comp.get('type', 'Other')
    quantity = max(1, int(comp.get('quantity', 1)))
    batch_size, mm_per_batch = _HEIGHT_ESTIMATES.get(comp_type, (1, 5))
    return math.ceil(quantity / batch_size) * mm_per_batch


def _estimate_tray_height(components: list) -> int:
    """Estimate tray height from its components (compartments are side-by-side, not stacked).

    Takes the max component height + wall allowance, clamped to [15, 60] mm.
    """
    if not components:
        return _MIN_TRAY_HEIGHT_MM
    max_height = max(_estimate_component_height(c) for c in components)
    return max(_MIN_TRAY_HEIGHT_MM, min(_MAX_TRAY_HEIGHT_MM, max_height + _WALL_ALLOWANCE_MM))


def _estimate_board_layer_thickness(components: list) -> int:
    """Estimate thickness of the board + rulebook layer (sits on top, not a printed tray)."""
    total = 0
    for comp in components:
        comp_type = comp.get('type', 'Other')
        quantity = max(1, int(comp.get('quantity', 1)))
        if comp_type == 'Boards':
            total += 4 * quantity   # 4mm per board
        else:
            total += 4 * quantity   # 4mm per other flat item (rulebook, reference cards)
    return max(total, 0)


# ─── Auto-suggestion ───────────────────────────────────────────────────────────

def _suggest_from_flat_components(box_height: int) -> tuple:
    """Fallback: build tray structure from st.session_state.components (manual entry).

    Returns (trays, board_layer, stack_order).
    """
    components = st.session_state.get('components', [])
    board_comps = [c for c in components if c.get('type') == 'Boards']
    other_comps = [c for c in components if c.get('type') != 'Boards']

    trays = []
    stack_order = []

    if other_comps:
        tray_id = 'tray_1'
        trays.append({
            'tray_id': tray_id,
            'name': 'All Components',
            'tray_type': 'shared',
            'components': other_comps,
            'player_sets': None,
            'player_names': None,
            'parent_tray_id': None,
            'notes': 'All components (add via PDF extraction for better organization)',
        })
        stack_order.append(tray_id)

    board_layer = {
        'components': board_comps,
        'estimated_thickness_mm': _estimate_board_layer_thickness(board_comps),
    }

    return trays, board_layer, stack_order


def _suggest_tray_structure() -> dict:
    """Build the initial tray structure from selected_component_groups.

    Called once on first render. Reads from session state:
      - selected_component_groups (set by Step 2 form submit)
      - player_set_count + player_set_names (set by player count adjuster)
      - box_config (set by Step 1)
    """
    groups = st.session_state.get('selected_component_groups', [])
    box_height = st.session_state.get('box_config', {}).get('height', 71)
    player_sets = st.session_state.get('player_set_count', 4)
    player_names = st.session_state.get('player_set_names', [])

    trays = []
    board_layer = {'components': [], 'estimated_thickness_mm': 0}
    stack_order = []

    for group in groups:
        group_type = group.get('group_type', 'shared')
        group_name = group.get('group_name', 'Components')
        comps = group.get('components', [])
        is_identical = group.get('identical_sets', False)

        if not comps:
            continue

        if group_type == 'board_and_rules':
            board_layer['components'].extend(comps)
            board_layer['estimated_thickness_mm'] = _estimate_board_layer_thickness(
                board_layer['components']
            )
            continue

        tray_id = f"tray_{len(trays) + 1}"

        if group_type == 'player':
            if is_identical:
                # All players get identical components — one template tray
                tray = {
                    'tray_id': tray_id,
                    'name': 'Player Components',
                    'tray_type': 'player',
                    'components': comps,
                    'player_sets': player_sets,
                    'player_names': list(player_names) if player_names else None,
                    'parent_tray_id': None,
                    'notes': '',
                }
            else:
                # Asymmetric faction — each group is its own unique player tray
                tray = {
                    'tray_id': tray_id,
                    'name': group_name,
                    'tray_type': 'player',
                    'components': comps,
                    'player_sets': None,    # Unique faction, not duplicated
                    'player_names': None,
                    'parent_tray_id': None,
                    'notes': '',
                }

        elif group_type == 'shared':
            tray = {
                'tray_id': tray_id,
                'name': group_name if group_name not in ('Shared Supply', 'Shared Components')
                        else 'Shared Resources',
                'tray_type': 'shared',
                'components': comps,
                'player_sets': None,
                'player_names': None,
                'parent_tray_id': None,
                'notes': '',
            }

        elif group_type == 'setup':
            tray = {
                'tray_id': tray_id,
                'name': group_name if group_name else 'Setup Components',
                'tray_type': 'setup',
                'components': comps,
                'player_sets': None,
                'player_names': None,
                'parent_tray_id': None,
                'notes': '',
            }

        else:
            continue

        trays.append(tray)
        stack_order.append(tray_id)

    # Fallback if no extraction groups (manually entered components)
    if not trays and not board_layer['components']:
        trays, board_layer, stack_order = _suggest_from_flat_components(box_height)

    return {
        'trays': trays,
        'board_layer': board_layer,
        'stack_order': stack_order,
        'box_height_mm': box_height,
    }


# ─── Stack summary ─────────────────────────────────────────────────────────────

def _render_stack_summary(tray_structure: dict):
    """Render the stack summary panel at the top of Sort & Plan."""
    box_height = tray_structure['box_height_mm']
    board_layer = tray_structure['board_layer']
    trays = tray_structure['trays']
    stack_order = tray_structure['stack_order']

    board_thickness = board_layer['estimated_thickness_mm']

    # Calculate per-tray estimated heights
    tray_by_id = {t['tray_id']: t for t in trays}
    tray_heights = {}
    for tray_id in stack_order:
        tray = tray_by_id.get(tray_id)
        if tray:
            tray_heights[tray_id] = _estimate_tray_height(tray['components'])

    total_tray_height = sum(tray_heights.values())
    total_used = total_tray_height + board_thickness
    remaining = box_height - total_used
    pct = int((total_used / box_height) * 100) if box_height > 0 else 0

    st.subheader("Stack summary")

    # Compact text summary
    lines = [f"{total_used}mm used of {box_height}mm ({pct}%)"]
    if board_thickness > 0:
        lines.append(f"  Board & rulebook (top, not printed) — ~{board_thickness}mm")
    for tray_id in reversed(stack_order):
        tray = tray_by_id.get(tray_id)
        if not tray:
            continue
        h = tray_heights.get(tray_id, 0)
        label = tray['name']
        if tray.get('player_sets'):
            label += f" ×{tray['player_sets']}"
        lines.append(f"  {label} — ~{h}mm")

    if remaining < 0:
        lines.append(f"  OVER by {abs(remaining)}mm — trays will not fit")
    elif remaining < 10:
        lines.append(f"  {remaining}mm headroom (tight fit)")
    else:
        lines.append(f"  {remaining}mm headroom")

    st.text("\n".join(lines))

    if total_used > box_height:
        st.error(
            f"Estimated stack height (~{total_used}mm) exceeds box height ({box_height}mm) "
            f"by ~{total_used - box_height}mm. Reduce tray count or use shallower compartments."
        )


# ─── Tray card rendering ───────────────────────────────────────────────────────

_TRAY_TYPE_LABELS = {
    'player': 'Player',
    'shared': 'Shared',
    'setup':  'Setup',
}

_TRAY_TYPE_OPTIONS = ['player', 'shared', 'setup']


def _render_tray_card(tray: dict, tray_idx: int, all_trays: list, tray_structure: dict):
    """Render a single tray card with rename, type change, component list, and controls."""
    tray_id = tray['tray_id']
    tray_type = tray.get('tray_type', 'shared')
    type_label = _TRAY_TYPE_LABELS.get(tray_type, tray_type)
    player_sets = tray.get('player_sets')
    player_names = tray.get('player_names') or []
    comps = tray.get('components', [])

    est_height = _estimate_tray_height(comps)

    # Header label
    if tray_type == 'player' and player_sets:
        names_display = ', '.join(player_names[:4])
        if len(player_names) > 4:
            names_display += f', +{len(player_names) - 4} more'
        header = f"**{type_label} ×{player_sets}** — {tray['name']} ({len(comps)} items, ~{est_height}mm)"
    elif tray_type == 'player':
        header = f"**{type_label}** — {tray['name']} ({len(comps)} items, ~{est_height}mm)"
    else:
        header = f"**{type_label}** — {tray['name']} ({len(comps)} items, ~{est_height}mm)"

    with st.expander(header, expanded=True):

        # ── Name + Type row
        name_col, type_col = st.columns([3, 2])
        with name_col:
            new_name = st.text_input("Tray name", value=tray['name'],
                                     key=f"tray_name_{tray_id}")
            tray['name'] = new_name
        with type_col:
            type_idx = _TRAY_TYPE_OPTIONS.index(tray_type) if tray_type in _TRAY_TYPE_OPTIONS else 1
            new_type = st.selectbox(
                "Type",
                options=_TRAY_TYPE_OPTIONS,
                index=type_idx,
                format_func=lambda t: _TRAY_TYPE_LABELS.get(t, t),
                key=f"tray_type_{tray_id}",
            )
            tray['tray_type'] = new_type

        # ── Player sets info for player trays
        if tray_type == 'player' and player_sets:
            st.caption(
                f"Template tray — ×{player_sets} identical sets "
                f"({', '.join(player_names) if player_names else 'unnamed'})"
            )
        elif tray_type == 'player' and not player_sets:
            st.caption("Unique faction tray (asymmetric game)")

        # ── Component list
        if comps:
            other_tray_names = [t['name'] for t in all_trays if t['tray_id'] != tray_id]
            move_options = ['— stay here —'] + other_tray_names + ['Unassigned']

            st.markdown(f"**Components** ({len(comps)} items):")
            comps_to_remove = []
            comps_to_move = []   # (comp, target_tray_name)

            for comp_idx, comp in enumerate(comps):
                c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
                with c1:
                    st.markdown(f"`{comp.get('name', '?')}`")
                with c2:
                    st.caption(comp.get('type', ''))
                with c3:
                    st.caption(f"×{comp.get('quantity', 1)}")
                with c4:
                    move_key = f"move_{tray_id}_{comp.get('extraction_index', comp_idx)}"
                    move_to = st.selectbox(
                        "Move to",
                        options=move_options,
                        index=0,
                        key=move_key,
                        label_visibility="collapsed",
                    )
                    if move_to != '— stay here —':
                        comps_to_move.append((comp, move_to))

            # Process moves (outside the loop to avoid mutation during iteration)
            moved_any = False
            for comp, target_name in comps_to_move:
                comps.remove(comp)
                if target_name == 'Unassigned':
                    tray_structure.setdefault('unassigned', []).append(comp)
                else:
                    for t in all_trays:
                        if t['name'] == target_name:
                            t['components'].append(comp)
                            break
                moved_any = True

            if moved_any:
                st.rerun()
        else:
            st.caption("This tray is empty — move components here from other trays.")

        # ── Stack order controls + Remove
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1, 1, 1, 3])
        with ctrl_col1:
            if tray_idx > 0:
                if st.button("↑ Up", key=f"up_{tray_id}"):
                    trays = tray_structure['trays']
                    order = tray_structure['stack_order']
                    # Swap in both lists
                    i = tray_idx
                    trays[i], trays[i - 1] = trays[i - 1], trays[i]
                    order_i = order.index(tray_id)
                    if order_i > 0:
                        order[order_i], order[order_i - 1] = order[order_i - 1], order[order_i]
                    st.rerun()
        with ctrl_col2:
            if tray_idx < len(all_trays) - 1:
                if st.button("↓ Down", key=f"down_{tray_id}"):
                    trays = tray_structure['trays']
                    order = tray_structure['stack_order']
                    i = tray_idx
                    trays[i], trays[i + 1] = trays[i + 1], trays[i]
                    order_i = order.index(tray_id)
                    if order_i < len(order) - 1:
                        order[order_i], order[order_i + 1] = order[order_i + 1], order[order_i]
                    st.rerun()
        with ctrl_col3:
            if st.button("× Remove tray", key=f"remove_tray_{tray_id}"):
                # Move components to unassigned before removing
                if comps:
                    tray_structure.setdefault('unassigned', []).extend(comps)
                tray_structure['trays'] = [
                    t for t in tray_structure['trays'] if t['tray_id'] != tray_id
                ]
                if tray_id in tray_structure['stack_order']:
                    tray_structure['stack_order'].remove(tray_id)
                st.rerun()


def _render_board_layer_card(board_layer: dict):
    """Render the Board & Rulebook layer card (read-only, not a printed tray)."""
    comps = board_layer.get('components', [])
    thickness = board_layer.get('estimated_thickness_mm', 0)

    with st.expander(f"Board & Rulebook Layer — On Top ({len(comps)} items, ~{thickness}mm)", expanded=True):
        st.caption(
            "These items sit on top of the insert stack. "
            "They don't need printed tray compartments but contribute to the total stack height."
        )
        if comps:
            for comp in comps:
                comp_type = comp.get('type', '')
                qty = comp.get('quantity', 1)
                est = _estimate_component_height(comp)
                c1, c2, c3 = st.columns([4, 2, 1])
                with c1:
                    st.markdown(f"`{comp.get('name', '?')}`")
                with c2:
                    st.caption(comp_type)
                with c3:
                    st.caption(f"×{qty} (~{est}mm)")
        else:
            st.caption("No boards or rulebook detected.")


def _render_unassigned_section(tray_structure: dict, all_trays: list):
    """Show unassigned components (removed from trays) with 'Move to...' options."""
    unassigned = tray_structure.get('unassigned', [])
    if not unassigned:
        return

    st.markdown("---")
    st.warning(f"Unassigned components ({len(unassigned)}) — assign these to a tray before continuing.")

    tray_names = [t['name'] for t in all_trays]
    move_options = ['— leave unassigned —'] + tray_names

    comps_to_assign = []
    for idx, comp in enumerate(unassigned):
        c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
        with c1:
            st.markdown(f"`{comp.get('name', '?')}`")
        with c2:
            st.caption(comp.get('type', ''))
        with c3:
            st.caption(f"×{comp.get('quantity', 1)}")
        with c4:
            target = st.selectbox(
                "Move to",
                options=move_options,
                index=0,
                key=f"unassigned_move_{comp.get('extraction_index', idx)}",
                label_visibility="collapsed",
            )
            if target != '— leave unassigned —':
                comps_to_assign.append((comp, target))

    assigned_any = False
    for comp, target_name in comps_to_assign:
        unassigned.remove(comp)
        for t in all_trays:
            if t['name'] == target_name:
                t['components'].append(comp)
                break
        assigned_any = True

    if assigned_any:
        tray_structure['unassigned'] = unassigned
        st.rerun()


# ─── Main render function ──────────────────────────────────────────────────────

def render_tray_structure():
    """Step 2.5: Tray Structure — called from the wizard (New_Insert.py)."""

    st.subheader("Sort & Plan")
    st.caption(
        "Your components have been organized into trays based on how they're used during gameplay. "
        "Review and adjust as needed."
    )

    # ── Check for data source
    has_extraction = 'selected_component_groups' in st.session_state
    has_components = bool(st.session_state.get('components'))

    if not has_extraction and not has_components:
        st.warning("No components found. Please go back to Step 2 and add or import components.")
        return

    if not has_extraction and has_components:
        st.caption(
            "Components were added manually (no PDF extraction). "
            "Tray suggestions are based on your component list."
        )

    # ── Initialize tray_structure on first render
    if 'tray_structure' not in st.session_state:
        st.session_state.tray_structure = _suggest_tray_structure()

    tray_structure = st.session_state.tray_structure
    trays = tray_structure['trays']
    board_layer = tray_structure['board_layer']

    # ── Stack Summary
    _render_stack_summary(tray_structure)

    st.markdown("---")
    st.subheader("Proposed tray layout")
    st.caption("Adjust names, types, and component assignments as needed.")

    # ── Per-tray cards
    for tray_idx, tray in enumerate(trays):
        _render_tray_card(tray, tray_idx, trays, tray_structure)

    # ── Board layer card
    if board_layer.get('components') or True:  # Always show so users know it exists
        st.markdown("---")
        _render_board_layer_card(board_layer)

    # ── Unassigned components
    _render_unassigned_section(tray_structure, trays)

    # ── Add tray / Auto-suggest buttons
    st.markdown("---")
    add_col, suggest_col, _ = st.columns([1, 1, 2])
    with add_col:
        if st.button("+ Add Tray", use_container_width=True):
            new_id = f"tray_{uuid.uuid4().hex[:8]}"
            tray_structure['trays'].append({
                'tray_id': new_id,
                'name': 'New Tray',
                'tray_type': 'shared',
                'components': [],
                'player_sets': None,
                'player_names': None,
                'parent_tray_id': None,
                'notes': '',
            })
            tray_structure['stack_order'].append(new_id)
            st.rerun()

    with suggest_col:
        if st.button("Auto-Suggest Layout", use_container_width=True):
            del st.session_state.tray_structure
            st.rerun()

    # ── Navigation
    st.markdown("---")
    nav_col1, _, nav_col3 = st.columns([1, 1, 1])

    with nav_col1:
        if st.button("← Back: Components", use_container_width=True):
            # Clear tray_structure so it gets re-suggested next time
            if 'tray_structure' in st.session_state:
                del st.session_state.tray_structure
            st.session_state.wizard_step = 1  # Step 1 = Box & Components (merged)
            st.rerun()

    with nav_col3:
        unassigned_count = len(tray_structure.get('unassigned', []))
        if unassigned_count > 0:
            st.warning(f"{unassigned_count} unassigned component(s) — assign before continuing.")
        if st.button("Next: Layout Editor →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 3  # Step 3 = Layout Editor
            st.rerun()
