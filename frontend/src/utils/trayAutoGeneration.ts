import type { ComponentGroup, Component, Tray, BoardLayer, TrayStructure, BoxConfig } from '../types';
import { estimateTrayHeight, estimateBoardLayerThickness } from './trayEstimation';

export function generateTrayStructure(
  componentGroups: ComponentGroup[],
  components: Component[],
  boxConfig: BoxConfig
): TrayStructure {
  const trays: Tray[] = [];
  const boardLayer: BoardLayer = { components: [], estimated_thickness_mm: 0 };
  const stackOrder: string[] = [];

  for (const group of componentGroups) {
    const { groupType, groupName, components: groupComps, identicalSets } = group;

    if (!groupComps.length) continue;

    // Board & rules go to non-printed top layer
    if (groupType === 'board_and_rules') {
      boardLayer.components.push(...groupComps);
      boardLayer.estimated_thickness_mm = estimateBoardLayerThickness(boardLayer.components);
      continue;
    }

    const trayId = `tray_${trays.length + 1}`;

    if (groupType === 'player') {
      const tray: Tray = {
        tray_id: trayId,
        name: identicalSets ? 'Player Components' : groupName,
        tray_type: 'player',
        components: groupComps,
        player_sets: identicalSets ? 4 : null,  // TODO: Get from user config
        player_names: null,
        needs_lid: shouldHaveLid(groupComps),
        lid_reason: getLidReason(groupComps),
        parent_tray_id: null,
        notes: '',
        estimated_height_mm: estimateTrayHeight(groupComps),
      };

      trays.push(tray);
      stackOrder.push(trayId);

    } else if (groupType === 'shared') {
      const tray: Tray = {
        tray_id: trayId,
        name: groupName === 'Shared Supply' || groupName === 'Shared Components'
          ? 'Shared Resources'
          : groupName,
        tray_type: 'shared',
        components: groupComps,
        player_sets: null,
        player_names: null,
        needs_lid: shouldHaveLid(groupComps),
        lid_reason: getLidReason(groupComps),
        parent_tray_id: null,
        notes: '',
        estimated_height_mm: estimateTrayHeight(groupComps),
      };

      trays.push(tray);
      stackOrder.push(trayId);

    } else if (groupType === 'setup') {
      const tray: Tray = {
        tray_id: trayId,
        name: groupName || 'Setup Components',
        tray_type: 'setup',
        components: groupComps,
        player_sets: null,
        player_names: null,
        needs_lid: shouldHaveLid(groupComps),
        lid_reason: getLidReason(groupComps),
        parent_tray_id: null,
        notes: '',
        estimated_height_mm: estimateTrayHeight(groupComps),
      };

      trays.push(tray);
      stackOrder.push(trayId);
    }
  }

  // Fallback: if no trays created (manual component entry), create one tray
  if (!trays.length && components.length) {
    const boardComps = components.filter(c => c.type === 'Boards');
    const otherComps = components.filter(c => c.type !== 'Boards');

    if (otherComps.length) {
      const trayId = 'tray_1';
      trays.push({
        tray_id: trayId,
        name: 'All Components',
        tray_type: 'shared',
        components: otherComps,
        player_sets: null,
        player_names: null,
        needs_lid: false,
        lid_reason: undefined,
        parent_tray_id: null,
        notes: 'All components (add via PDF extraction for better organization)',
        estimated_height_mm: estimateTrayHeight(otherComps),
      });
      stackOrder.push(trayId);
    }

    if (boardComps.length) {
      boardLayer.components = boardComps;
      boardLayer.estimated_thickness_mm = estimateBoardLayerThickness(boardComps);
    }
  }

  return {
    trays,
    board_layer: boardLayer,
    stack_order: stackOrder,
    box_height_mm: boxConfig.height,
    unassigned: [],
  };
}

// Lid recommendation logic
function shouldHaveLid(components: Component[]): boolean {
  // Recommend lid if:
  // - Has loose small pieces (tokens, dice, cubes)
  // - Has cards without sleeves
  // - Has miniatures

  const hasLoosePieces = components.some(c =>
    ['Tokens', 'Tiles', 'Dice'].includes(c.type) && c.quantity > 10
  );

  const hasUnsleevedCards = components.some(c =>
    c.type === 'Cards' && c.sleeveType === 'unsleeved'
  );

  const hasMinis = components.some(c => c.type === 'Meeples/Minis');

  return hasLoosePieces || hasUnsleevedCards || hasMinis;
}

function getLidReason(components: Component[]): string {
  const reasons: string[] = [];

  const hasLoosePieces = components.some(c =>
    ['Tokens', 'Tiles', 'Dice'].includes(c.type) && c.quantity > 10
  );
  if (hasLoosePieces) reasons.push('many loose pieces');

  const hasUnsleevedCards = components.some(c =>
    c.type === 'Cards' && c.sleeveType === 'unsleeved'
  );
  if (hasUnsleevedCards) reasons.push('unsleeved cards');

  const hasMinis = components.some(c => c.type === 'Meeples/Minis');
  if (hasMinis) reasons.push('miniatures');

  return reasons.length ? `Recommended due to: ${reasons.join(', ')}` : '';
}
