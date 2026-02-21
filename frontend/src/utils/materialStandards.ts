import materialStandardsData from '../data/material_standards.json';

export const MATERIAL_STANDARDS = materialStandardsData;

// Material thickness constants
export const MATERIAL_THICKNESS: Record<string, number> = {
  budget: 1.1,
  standard: 1.5,
  premium: 2.0,
  heavy_duty: 2.5,
  luxury: 3.0,
};

// Sleeve thickness additions (mm per card)
export const SLEEVE_THICKNESS: Record<string, number> = {
  unsleeved: 0,
  thin: 0.05,
  premium: 0.1,
};

/**
 * Helper functions to identify component types from names
 */

export function isRulebook(name: string): boolean {
  const keywords = ['rulebook', 'rules', 'manual', 'instructions', 'guide'];
  const lowerName = name.toLowerCase();
  return keywords.some((keyword) => lowerName.includes(keyword));
}

export function isCube(name: string): boolean {
  const keywords = ['cube', 'cubes'];
  const lowerName = name.toLowerCase();
  return keywords.some((keyword) => lowerName.includes(keyword));
}

export function isMini(name: string): boolean {
  const keywords = ['miniature', 'mini', 'minis', 'figure', 'standee', 'standees'];
  const lowerName = name.toLowerCase();
  return keywords.some((keyword) => lowerName.includes(keyword));
}

export function isDice(name: string): boolean {
  const keywords = ['dice', 'die', 'd6', 'd8', 'd10', 'd12', 'd20'];
  const lowerName = name.toLowerCase();
  return keywords.some((keyword) => lowerName.includes(keyword));
}

export function isMeeple(name: string): boolean {
  const keywords = ['meeple', 'meeples', 'worker'];
  const lowerName = name.toLowerCase();
  return keywords.some((keyword) => lowerName.includes(keyword));
}

/**
 * Get material clearance for a given material category and type
 */
export function getMaterialClearance(
  category: string,
  material: string
): { clearance: number; note: string } {
  const standards = MATERIAL_STANDARDS as any;
  const categoryData = standards[category];

  if (!categoryData || !categoryData[material]) {
    return { clearance: 0, note: 'No clearance data' };
  }

  const materialData = categoryData[material];
  const clearance = materialData.clearance_mm || 0;
  const reason = materialData.clearance_reason || 'standard clearance';

  return { clearance, note: reason };
}
