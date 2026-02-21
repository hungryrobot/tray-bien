import type { Component, ComponentType } from '../types';

// Height estimation constants (mm) - rough batch estimates for stack summary
const HEIGHT_ESTIMATES: Record<ComponentType, [number, number]> = {
  'Cards': [60, 20],        // 60 cards per deck ≈ 20mm
  'Tokens': [30, 10],       // 30 tokens ≈ 10mm
  'Tiles': [20, 15],        // 20 tiles ≈ 15mm
  'Meeples/Minis': [5, 15], // 5 minis ≈ 15mm
  'Boards': [1, 4],         // 1 board ≈ 4mm
  'Dice': [6, 15],          // 6 dice ≈ 15mm
  'Rulebook': [1, 3],       // 1 rulebook ≈ 3mm
  'Other': [1, 5],          // 1 item ≈ 5mm
  'Custom': [1, 5],
};

const WALL_ALLOWANCE_MM = 5;
const MIN_TRAY_HEIGHT_MM = 15;
const MAX_TRAY_HEIGHT_MM = 60;

export function estimateComponentHeight(component: Component): number {
  const type = component.type;
  const quantity = Math.max(1, component.quantity);
  const [batchSize, mmPerBatch] = HEIGHT_ESTIMATES[type] || [1, 5];
  return Math.ceil(quantity / batchSize) * mmPerBatch;
}

export function estimateTrayHeight(components: Component[]): number {
  if (!components.length) return MIN_TRAY_HEIGHT_MM;

  const maxHeight = Math.max(...components.map(estimateComponentHeight));
  const withWalls = maxHeight + WALL_ALLOWANCE_MM;
  return Math.max(MIN_TRAY_HEIGHT_MM, Math.min(MAX_TRAY_HEIGHT_MM, withWalls));
}

export function estimateBoardLayerThickness(components: Component[]): number {
  let total = 0;
  for (const comp of components) {
    const quantity = Math.max(1, comp.quantity);
    if (comp.type === 'Boards') {
      total += 4 * quantity;  // 4mm per board
    } else {
      total += 4 * quantity;  // 4mm per other flat item (rulebook, ref cards)
    }
  }
  return Math.max(total, 0);
}
