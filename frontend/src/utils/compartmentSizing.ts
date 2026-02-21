import type { Component, ComponentType, Compartment } from '../types';

/**
 * Compartment sizing utilities for Step 3: Layout Editor
 * Handles clearances, stack depth, colors, and auto-packing
 */

// Component type colors for visual distinction
const COMPONENT_COLORS: Record<ComponentType, string> = {
  'Cards': '#93C5FD',        // light blue
  'Tokens': '#FCD34D',       // yellow
  'Tiles': '#86EFAC',        // green
  'Dice': '#F87171',         // red
  'Meeples/Minis': '#C4B5FD', // purple
  'Boards': '#FDBA74',       // orange
  'Rulebook': '#FDBA74',     // orange
  'Other': '#D1D5DB',        // gray
  'Custom': '#D1D5DB',       // gray
};

/**
 * Get clearance in mm based on component type and material
 * From design philosophy document
 */
export function getClearance(component: Component): number {
  const { type, sleeveType, materialCategory } = component;

  // Cards - clearance depends on sleeves
  if (type === 'Cards') {
    if (sleeveType === 'premium') return 0.75;
    if (sleeveType === 'thin') return 0.75;
    return 0.5; // unsleeved
  }

  // Dice
  if (type === 'Dice') return 1.0;

  // Miniatures - check if hasMinis was flagged
  // For now, default to 2mm for minis (conservative)
  if (type === 'Meeples/Minis') {
    // If component has clearanceMm set from Quick Defaults, use it
    if (component.clearanceMm !== undefined) {
      return component.clearanceMm;
    }
    return 2.0; // default for miniatures
  }

  // Cardboard tokens/tiles
  if (type === 'Tokens' || type === 'Tiles') {
    if (materialCategory === 'cardboard') return 1.0;
    // Wooden/plastic
    return 0.5;
  }

  // Default for everything else
  return 0.5;
}

/**
 * Calculate stack depth (height) in mm based on component type
 */
export function calculateStackDepth(component: Component): number {
  const { type, height, quantity, stackHeight } = component;

  const baseHeight = height || 10; // fallback if no height

  // Cards - use stack height if available, else estimate
  if (type === 'Cards') {
    if (stackHeight) return stackHeight + 5; // 5mm finger room
    // Fallback calculation if no stackHeight
    const perCard = component.calculatedPerCard || 0.3;
    return quantity * perCard + 5;
  }

  // Tokens - can be stacked
  if (type === 'Tokens' || type === 'Tiles') {
    const thickness = baseHeight;
    // If lots of tokens, assume stacked
    if (quantity > 10) {
      return Math.min(thickness * quantity, 40) + 3; // cap at 40mm, add 3mm finger room
    }
    return thickness + 3;
  }

  // Dice - don't stack well
  if (type === 'Dice') {
    return baseHeight + 2;
  }

  // Meeples/Minis
  if (type === 'Meeples/Minis') {
    return baseHeight + 2;
  }

  // Everything else
  return baseHeight + 2;
}

/**
 * Get component type color
 */
export function getComponentColor(type: ComponentType): string {
  return COMPONENT_COLORS[type] || COMPONENT_COLORS['Other'];
}

/**
 * Create a compartment from a component
 */
export function createCompartment(component: Component): Compartment {
  const clearance = getClearance(component);

  const width = (component.width || 30) + clearance * 2;
  const length = (component.length || 30) + clearance * 2;
  const depth = calculateStackDepth(component);

  return {
    id: `comp_${component.id}`,
    componentId: component.id,
    name: component.name,
    x: 0, // Will be set by auto-pack
    y: 0, // Will be set by auto-pack
    width,
    length,
    depth,
    minWidth: width,    // Can't go smaller than component + clearance
    minLength: length,
    color: getComponentColor(component.type),
  };
}

/**
 * Auto-pack compartments using bottom-left shelf packing algorithm
 * Places largest compartments first, left to right, then row by row
 */
export function autoPackCompartments(
  compartments: Compartment[],
  trayWidth: number,    // box inner width - 2 * outerWallThickness
  _trayLength: number,  // box inner length - 2 * outerWallThickness (not used in simple shelf pack)
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
