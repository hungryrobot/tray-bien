/**
 * TypeScript type definitions for Tray Bien API.
 */

export interface Component {
  name: string;
  type: string;
  quantity: number;
  notes: string;
  extraction_index: number;
  details?: string;
  player_specific?: boolean;
  player_identifier?: string | null;
}

export interface ComponentGroup {
  group_name: string;
  group_type: string;
  per_player: boolean;
  identical_sets?: boolean;
  notes: string;
  components: Component[];
}

export interface ExtractionResult {
  component_groups: ComponentGroup[];
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
