/**
 * TypeScript type definitions for Tray Bien API and wizard state.
 */

// Component type literal
export type ComponentType =
  | 'Cards'
  | 'Tokens'
  | 'Tiles'
  | 'Dice'
  | 'Meeples/Minis'
  | 'Boards'
  | 'Rulebook'
  | 'Other'
  | 'Custom';

export type MaterialCategory = 'cards' | 'cardboard' | 'wood' | 'plastic' | '';
export type CardStock = 'standard' | 'premium' | 'tarot' | 'custom';
export type SleeveType = 'unsleeved' | 'thin' | 'premium';
export type CardboardQuality = 'budget' | 'standard' | 'premium' | 'heavy_duty' | 'luxury';

// Enhanced Component interface for wizard
export interface Component {
  id: string;
  type: ComponentType;
  name: string;
  quantity: number;
  length: number | null;
  width: number | null;
  height: number | null;

  // Material properties
  material?: string;
  materialCategory?: MaterialCategory;
  cardStock?: CardStock;
  sleeveType?: SleeveType;
  stackQuantity?: number;
  stackHeight?: number;
  calculatedPerCard?: number;

  // Prefill metadata
  prefillLength?: number;
  prefillWidth?: number;
  prefillHeight?: number;
  prefillSource?: string;
  prefillComplete: boolean;
  clearanceMm?: number;
  clearanceNote?: string;
  needsDimensions: boolean;

  // Extraction metadata
  details?: string;
  notes?: string;
  sourceGame?: string;
  isExpansion: boolean;
  extractionIndex?: number;
  playerSpecific: boolean;
  playerIdentifier?: string;

  // Calculated
  volume?: number;
}

// Component group from extraction
export interface ComponentGroup {
  groupName: string;
  groupType: 'player' | 'shared' | 'setup' | 'board_and_rules';
  identicalSets: boolean;
  perPlayer: boolean;
  notes: string;
  components: Component[];
}

// Box configuration
export interface BoxConfig {
  source: 'custom' | string;
  gameName: string;
  length: number;
  width: number;
  height: number;
}

// Quick Defaults configuration
export interface QuickDefaults {
  cardboardQuality: CardboardQuality;
  cardsSleeved: SleeveType;
  hasDice: boolean;
  diceSizeMm: number;
  hasCubes: boolean;
  cubeSizeMm: number;
  hasMinis: boolean;
  hasExpansionSpace: boolean;
}

// PDF Extraction result from API
export interface ExtractionResult {
  component_groups: {
    group_name: string;
    group_type: string;
    per_player: boolean;
    identical_sets?: boolean;
    notes: string;
    components: Array<{
      name: string;
      type: string;
      quantity: number;
      notes: string;
      extraction_index: number;
      details?: string;
      player_specific?: boolean;
      player_identifier?: string | null;
    }>;
  }[];
  game_name: string;
  player_count: { min?: number; max?: number };
  factions_or_colors: string[];
  extraction_notes: string;
  components: any[];
  metadata: {
    tokens_used?: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
    provider: string;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
