import type { Component, BoxConfig } from '../types';
import { getMaterialClearance } from './materialStandards';

/**
 * Calculate the volume of a component in cubic millimeters
 */
export function calculateComponentVolume(component: Component): number {
  const { type, quantity, length, width, height, materialCategory, material } = component;

  if (!length || !width || !height) return 0;

  // Get clearance from material standards
  let clearance = 0;
  if (materialCategory && material) {
    const { clearance: matClearance } = getMaterialClearance(materialCategory, material);
    clearance = matClearance;
  }

  const lengthWithClearance = length + clearance;
  const widthWithClearance = width + clearance;

  // For cards, use per-card thickness if available
  if (type === 'Cards' && component.calculatedPerCard) {
    const perCardThickness = component.calculatedPerCard;
    const totalHeight = perCardThickness * quantity;
    return lengthWithClearance * widthWithClearance * totalHeight;
  }

  // Standard volume calculation
  const volumePerItem = lengthWithClearance * widthWithClearance * height;
  return volumePerItem * quantity;
}

/**
 * Calculate box fill percentage
 */
export function calculateBoxFillPercentage(
  components: Component[],
  boxConfig: BoxConfig
): number {
  const totalVolume = components.reduce((sum, c) => sum + (c.volume || 0), 0);
  const boxVolume = boxConfig.length * boxConfig.width * boxConfig.height;

  if (boxVolume === 0) return 0;

  return (totalVolume / boxVolume) * 100;
}

/**
 * Get box volume in cubic centimeters
 */
export function getBoxVolumeCm3(boxConfig: BoxConfig): number {
  return (boxConfig.length * boxConfig.width * boxConfig.height) / 1000;
}

/**
 * Get total component volume in cubic centimeters
 */
export function getTotalComponentVolumeCm3(components: Component[]): number {
  const totalVolumeMm3 = components.reduce((sum, c) => sum + (c.volume || 0), 0);
  return totalVolumeMm3 / 1000;
}

/**
 * Validate if components fit in the box
 */
export function validateBoxFit(
  components: Component[],
  boxConfig: BoxConfig
): {
  fits: boolean;
  fillPercentage: number;
  warning?: string;
} {
  const fillPercentage = calculateBoxFillPercentage(components, boxConfig);

  if (fillPercentage > 100) {
    return {
      fits: false,
      fillPercentage,
      warning: 'Components exceed box capacity!',
    };
  }

  if (fillPercentage > 90) {
    return {
      fits: true,
      fillPercentage,
      warning: 'Very tight fit - components may not fit comfortably',
    };
  }

  if (fillPercentage > 70) {
    return {
      fits: true,
      fillPercentage,
      warning: 'Tight fit - limited space for arrangement',
    };
  }

  return {
    fits: true,
    fillPercentage,
  };
}
