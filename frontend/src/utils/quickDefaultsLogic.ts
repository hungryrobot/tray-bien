import type { Component, BoxConfig, QuickDefaults } from '../types';
import {
  isRulebook,
  isCube,
  isMini,
  isDice,
  isMeeple,
  MATERIAL_THICKNESS,
  SLEEVE_THICKNESS,
} from './materialStandards';

interface Prefill {
  length: number | null;
  width: number | null;
  height: number | null;
  source: string;
  clearanceMm?: number;
  clearanceNote?: string;
}

/**
 * Get dimension prefill for a component based on Quick Defaults
 * Returns null if no prefill is available
 *
 * This is a direct port of the Python _get_dimension_prefill() function.
 */
function getDimensionPrefill(
  component: Component,
  quickDefaults: QuickDefaults,
  boxConfig: BoxConfig
): Prefill | null {
  const { type, name, quantity } = component;
  const {
    cardboardQuality,
    cardsSleeved,
    hasDice,
    diceSizeMm,
    hasCubes,
    cubeSizeMm,
    hasMinis,
  } = quickDefaults;

  const boxL = boxConfig.length;
  const boxW = boxConfig.width;

  // Rulebooks / instructions — fit the box footprint
  if (isRulebook(name) || type === 'Rulebook') {
    return {
      length: boxL,
      width: boxW,
      height: 3,
      source: `Matches box dimensions (${boxL}×${boxW}mm) — rulebook fits box`,
    };
  }

  // Boards
  if (type === 'Boards') {
    return {
      length: boxL,
      width: boxW,
      height: 5,
      source: `Matches box dimensions (${boxL}×${boxW}mm) — bi-fold board default 5mm`,
    };
  }

  // Resource cubes
  if (hasCubes && isCube(name)) {
    return {
      length: cubeSizeMm,
      width: cubeSizeMm,
      height: cubeSizeMm,
      source: `Resource cube — ${cubeSizeMm}mm`,
    };
  }

  // Meeples / Miniatures — separate handling
  const isMiniType = type === 'Meeples/Minis';
  const isMiniName = isMini(name);
  const isMeepleName = isMeeple(name);

  // Large miniatures — dimensions too varied to predict
  if (hasMinis && (isMiniType || isMiniName)) {
    return {
      length: null,
      width: null,
      height: null,
      source: 'Miniature — requires manual measurement',
      clearanceMm: 2.0,
      clearanceNote: 'Miniature — wider clearance applied (+2mm)',
    };
  }

  // Standard meeples
  if (isMeepleName || (isMiniType && !hasMinis)) {
    return {
      length: 16,
      width: 16,
      height: 10,
      source: 'Standard meeple (16×16×10mm)',
    };
  }

  // Dice
  if (hasDice && (type === 'Dice' || isDice(name))) {
    return {
      length: diceSizeMm,
      width: diceSizeMm,
      height: diceSizeMm,
      source: `Standard ${diceSizeMm}mm die`,
    };
  }

  // Cards — poker preset + sleeve clearance
  if (type === 'Cards') {
    const sleeveAdd = SLEEVE_THICKNESS[cardsSleeved] || 0;
    const perCardMm = 0.3 + sleeveAdd; // standard card stock + sleeve
    const stackH = Math.round((quantity * perCardMm + 5) * 10) / 10; // 5mm finger room

    const sleeveLabel: Record<string, string> = {
      unsleeved: 'unsleeved',
      thin: 'thin sleeves',
      premium: 'premium sleeves',
    };

    return {
      length: 63.5, // Poker card width
      width: 88, // Poker card height
      height: stackH,
      source: `Poker card preset (63.5×88mm), ${sleeveLabel[cardsSleeved]}, stack height ${stackH}mm`,
    };
  }

  // Tokens / Tiles — thickness only (footprint varies too much to guess)
  if (type === 'Tokens' || type === 'Tiles') {
    const thickness = MATERIAL_THICKNESS[cardboardQuality] || 1.5;
    return {
      length: null,
      width: null,
      height: thickness,
      source: `Thickness from cardboard quality (${cardboardQuality} = ${thickness}mm)`,
    };
  }

  return null; // No suggestion
}

/**
 * Apply Quick Defaults to a single component
 * Returns a new component with prefill values stamped
 */
export function applyQuickDefaultsToComponent(
  component: Component,
  quickDefaults: QuickDefaults,
  boxConfig: BoxConfig
): Component {
  const prefill = getDimensionPrefill(component, quickDefaults, boxConfig);

  if (!prefill) {
    return {
      ...component,
      prefillComplete: false,
      needsDimensions: true,
    };
  }

  // Apply prefill values
  const updated: Component = {
    ...component,
    prefillSource: prefill.source,
    prefillComplete: prefill.length !== null && prefill.width !== null && prefill.height !== null,
    needsDimensions: !(prefill.length && prefill.width && prefill.height),
  };

  // Apply dimension values if available
  if (prefill.length !== null) {
    updated.prefillLength = prefill.length;
    updated.length = prefill.length;
  }
  if (prefill.width !== null) {
    updated.prefillWidth = prefill.width;
    updated.width = prefill.width;
  }
  if (prefill.height !== null) {
    updated.prefillHeight = prefill.height;
    updated.height = prefill.height;
  }

  // Apply clearance if specified
  if (prefill.clearanceMm !== undefined) {
    updated.clearanceMm = prefill.clearanceMm;
    updated.clearanceNote = prefill.clearanceNote;
  }

  // For cards, calculate per-card thickness
  if (component.type === 'Cards' && prefill.height !== null) {
    const sleeveAdd = SLEEVE_THICKNESS[quickDefaults.cardsSleeved] || 0;
    updated.calculatedPerCard = 0.3 + sleeveAdd;
    updated.sleeveType = quickDefaults.cardsSleeved;
  }

  // For tokens/tiles, set material category
  if (component.type === 'Tokens' || component.type === 'Tiles') {
    updated.materialCategory = 'cardboard';
    updated.material = quickDefaults.cardboardQuality;
  }

  return updated;
}
