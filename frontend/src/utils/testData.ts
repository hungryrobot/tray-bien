import type { BoxConfig, Component, QuickDefaults } from '../types';

/**
 * Test data for Qwixx - a quick dice game
 * Use this to skip PDF extraction during development testing
 */

export const QWIXX_BOX_CONFIG: BoxConfig = {
  source: 'custom',
  gameName: 'Qwixx',
  length: 122,
  width: 95,
  height: 30,
};

export const QWIXX_COMPONENTS: Component[] = [
  // Red die
  {
    id: 'test-red-die',
    type: 'Dice',
    name: 'Red Die',
    quantity: 2,
    length: 16,
    width: 16,
    height: 16,
    prefillLength: 16,
    prefillWidth: 16,
    prefillHeight: 16,
    prefillSource: 'Standard 16mm die',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    volume: 16 * 16 * 16, // 4096 mm³
  },
  // Yellow die
  {
    id: 'test-yellow-die',
    type: 'Dice',
    name: 'Yellow Die',
    quantity: 1,
    length: 16,
    width: 16,
    height: 16,
    prefillLength: 16,
    prefillWidth: 16,
    prefillHeight: 16,
    prefillSource: 'Standard 16mm die',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    volume: 16 * 16 * 16,
  },
  // Green die
  {
    id: 'test-green-die',
    type: 'Dice',
    name: 'Green Die',
    quantity: 1,
    length: 16,
    width: 16,
    height: 16,
    prefillLength: 16,
    prefillWidth: 16,
    prefillHeight: 16,
    prefillSource: 'Standard 16mm die',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    volume: 16 * 16 * 16,
  },
  // Blue die
  {
    id: 'test-blue-die',
    type: 'Dice',
    name: 'Blue Die',
    quantity: 1,
    length: 16,
    width: 16,
    height: 16,
    prefillLength: 16,
    prefillWidth: 16,
    prefillHeight: 16,
    prefillSource: 'Standard 16mm die',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    volume: 16 * 16 * 16,
  },
  // White dice
  {
    id: 'test-white-dice',
    type: 'Dice',
    name: 'White Dice',
    quantity: 2,
    length: 16,
    width: 16,
    height: 16,
    prefillLength: 16,
    prefillWidth: 16,
    prefillHeight: 16,
    prefillSource: 'Standard 16mm die',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    volume: 16 * 16 * 16,
  },
  // Score pad
  {
    id: 'test-score-pad',
    type: 'Other',
    name: 'Score Pad',
    quantity: 1,
    length: 120,
    width: 90,
    height: 10,
    prefillLength: 120,
    prefillWidth: 90,
    prefillHeight: 10,
    prefillSource: 'Score pad fits box dimensions',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    notes: 'Stack of score sheets',
    volume: 120 * 90 * 10, // 108000 mm³
  },
  // Rulebook
  {
    id: 'test-rulebook',
    type: 'Rulebook',
    name: 'Rulebook',
    quantity: 1,
    length: 122,
    width: 95,
    height: 3,
    prefillLength: 122,
    prefillWidth: 95,
    prefillHeight: 3,
    prefillSource: 'Matches box dimensions (122×95mm) — rulebook fits box',
    prefillComplete: true,
    needsDimensions: false,
    isExpansion: false,
    playerSpecific: false,
    volume: 122 * 95 * 3, // 34770 mm³
  },
];

export const QWIXX_QUICK_DEFAULTS: QuickDefaults = {
  cardboardQuality: 'standard',
  cardsSleeved: 'unsleeved',
  hasDice: true,
  diceSizeMm: 16,
  hasCubes: false,
  cubeSizeMm: 8,
  hasMinis: false,
  hasExpansionSpace: false,
};
