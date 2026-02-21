import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Component,
  ComponentGroup,
  BoxConfig,
  QuickDefaults,
  ExtractionResult,
} from '../types';
import { applyQuickDefaultsToComponent } from '../utils/quickDefaultsLogic';
import { calculateComponentVolume } from '../utils/componentCalculations';

interface DesignState {
  // Wizard state
  currentStep: number;
  designName: string;
  createdAt: string;

  // Box config
  boxConfig: BoxConfig;

  // Components
  components: Component[];

  // PDF extraction workflow
  pdfExtractionResult: ExtractionResult | null;
  selectedComponentGroups: ComponentGroup[];
  quickDefaults: QuickDefaults | null;
  quickDefaultsDone: boolean;

  // Actions
  setCurrentStep: (step: number) => void;
  setDesignName: (name: string) => void;
  setBoxConfig: (config: Partial<BoxConfig>) => void;
  setComponents: (components: Component[]) => void;
  addComponent: (component: Component) => void;
  updateComponent: (id: string, updates: Partial<Component>) => void;
  removeComponent: (id: string) => void;
  setPdfExtractionResult: (result: ExtractionResult) => void;
  setSelectedComponentGroups: (groups: ComponentGroup[]) => void;
  setQuickDefaults: (defaults: QuickDefaults) => void;
  applyQuickDefaults: () => void;
  importSelectedComponents: (componentIds: Set<string>) => void;
  resetWizard: () => void;
}

const defaultBoxConfig: BoxConfig = {
  source: 'custom',
  gameName: '',
  length: 300,
  width: 200,
  height: 70,
};

// Removed unused defaultQuickDefaults - defaults are set in QuickDefaults component

export const useDesignStore = create<DesignState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentStep: 1,
      designName: 'My Insert Design',
      createdAt: new Date().toISOString(),
      boxConfig: defaultBoxConfig,
      components: [],
      pdfExtractionResult: null,
      selectedComponentGroups: [],
      quickDefaults: null,
      quickDefaultsDone: false,

      // Actions
      setCurrentStep: (step) => set({ currentStep: step }),

      setDesignName: (name) => set({ designName: name }),

      setBoxConfig: (config) =>
        set((state) => ({
          boxConfig: { ...state.boxConfig, ...config },
        })),

      setComponents: (components) => set({ components }),

      addComponent: (component) =>
        set((state) => ({
          components: [...state.components, component],
        })),

      updateComponent: (id, updates) =>
        set((state) => ({
          components: state.components.map((comp) =>
            comp.id === id
              ? {
                  ...comp,
                  ...updates,
                  volume: calculateComponentVolume({ ...comp, ...updates }),
                }
              : comp
          ),
        })),

      removeComponent: (id) =>
        set((state) => ({
          components: state.components.filter((comp) => comp.id !== id),
        })),

      setPdfExtractionResult: (result) => {
        set({ pdfExtractionResult: result });

        // Convert extraction groups to ComponentGroup format
        const groups: ComponentGroup[] = result.component_groups.map((group) => ({
          groupName: group.group_name,
          groupType: group.group_type as any,
          identicalSets: group.identical_sets ?? false,
          perPlayer: group.per_player,
          notes: group.notes,
          components: group.components.map((comp, index) => ({
            id: `extracted-${Date.now()}-${index}`,
            type: comp.type as any,
            name: comp.name,
            quantity: comp.quantity,
            length: null,
            width: null,
            height: null,
            details: comp.details,
            notes: comp.notes,
            sourceGame: result.game_name,
            isExpansion: false,
            extractionIndex: comp.extraction_index,
            playerSpecific: comp.player_specific ?? false,
            playerIdentifier: comp.player_identifier ?? undefined,
            prefillComplete: false,
            needsDimensions: true,
            volume: 0,
          })),
        }));

        set({ selectedComponentGroups: groups });
      },

      setSelectedComponentGroups: (groups) =>
        set({ selectedComponentGroups: groups }),

      setQuickDefaults: (defaults) => set({ quickDefaults: defaults }),

      applyQuickDefaults: () => {
        const { quickDefaults, selectedComponentGroups, boxConfig } = get();
        if (!quickDefaults) return;

        // Apply defaults to all components in selected groups
        const updatedGroups = selectedComponentGroups.map((group) => ({
          ...group,
          components: group.components.map((comp) =>
            applyQuickDefaultsToComponent(comp, quickDefaults, boxConfig)
          ),
        }));

        set({
          selectedComponentGroups: updatedGroups,
          quickDefaultsDone: true,
        });
      },

      importSelectedComponents: (componentIds) => {
        const { selectedComponentGroups, components } = get();

        // Extract selected components from groups
        const selectedComponents: Component[] = [];
        selectedComponentGroups.forEach((group) => {
          group.components.forEach((comp) => {
            if (componentIds.has(comp.id)) {
              // Calculate volume for the component
              const withVolume = {
                ...comp,
                volume: calculateComponentVolume(comp),
              };
              selectedComponents.push(withVolume);
            }
          });
        });

        set({ components: [...components, ...selectedComponents] });
      },

      resetWizard: () =>
        set({
          currentStep: 1,
          designName: 'My Insert Design',
          createdAt: new Date().toISOString(),
          boxConfig: defaultBoxConfig,
          components: [],
          pdfExtractionResult: null,
          selectedComponentGroups: [],
          quickDefaults: null,
          quickDefaultsDone: false,
        }),
    }),
    {
      name: 'tray-bien-design',
      partialize: (state) => ({
        // Only persist these fields
        currentStep: state.currentStep,
        designName: state.designName,
        createdAt: state.createdAt,
        boxConfig: state.boxConfig,
        components: state.components,
        quickDefaults: state.quickDefaults,
        quickDefaultsDone: state.quickDefaultsDone,
      }),
    }
  )
);
