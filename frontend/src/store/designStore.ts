import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Component,
  ComponentGroup,
  BoxConfig,
  QuickDefaults,
  ExtractionResult,
  TrayStructure,
  Tray,
} from '../types';
import { applyQuickDefaultsToComponent } from '../utils/quickDefaultsLogic';
import { calculateComponentVolume } from '../utils/componentCalculations';
import { generateTrayStructure } from '../utils/trayAutoGeneration';
import { estimateTrayHeight } from '../utils/trayEstimation';

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

  // Tray structure (Step 2)
  trayStructure: TrayStructure | null;

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

  // Tray structure actions
  initializeTrayStructure: () => void;
  addTray: (tray: Tray) => void;
  updateTray: (tray_id: string, updates: Partial<Tray>) => void;
  removeTray: (tray_id: string) => void;
  moveComponentBetweenTrays: (componentId: string, fromTrayId: string, toTrayId: string) => void;
  reorderTrays: (from_index: number, to_index: number) => void;
  setTrayStructure: (structure: TrayStructure) => void;

  // Dev utilities
  loadTestData: () => void;
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
      trayStructure: null,

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
          trayStructure: null,
        }),

      // Tray structure actions
      initializeTrayStructure: () => {
        const { selectedComponentGroups, components, boxConfig } = get();

        const structure = generateTrayStructure(
          selectedComponentGroups,
          components,
          boxConfig
        );

        set({ trayStructure: structure });
      },

      addTray: (tray) => {
        set((state) => {
          if (!state.trayStructure) return state;

          return {
            trayStructure: {
              ...state.trayStructure,
              trays: [...state.trayStructure.trays, tray],
              stack_order: [...state.trayStructure.stack_order, tray.tray_id],
            },
          };
        });
      },

      updateTray: (tray_id, updates) => {
        set((state) => {
          if (!state.trayStructure) return state;

          return {
            trayStructure: {
              ...state.trayStructure,
              trays: state.trayStructure.trays.map((t) =>
                t.tray_id === tray_id
                  ? {
                      ...t,
                      ...updates,
                      estimated_height_mm: updates.components
                        ? estimateTrayHeight(updates.components)
                        : t.estimated_height_mm,
                    }
                  : t
              ),
            },
          };
        });
      },

      removeTray: (tray_id) => {
        set((state) => {
          if (!state.trayStructure) return state;

          const tray = state.trayStructure.trays.find((t) => t.tray_id === tray_id);
          const unassigned = [...(state.trayStructure.unassigned || [])];

          if (tray && tray.components.length) {
            unassigned.push(...tray.components);
          }

          return {
            trayStructure: {
              ...state.trayStructure,
              trays: state.trayStructure.trays.filter((t) => t.tray_id !== tray_id),
              stack_order: state.trayStructure.stack_order.filter((id) => id !== tray_id),
              unassigned,
            },
          };
        });
      },

      moveComponentBetweenTrays: (componentId, fromTrayId, toTrayId) => {
        set((state) => {
          if (!state.trayStructure) return state;

          let component: Component | null = null;
          const trays = state.trayStructure.trays.map((tray) => {
            if (fromTrayId === 'unassigned') {
              // From unassigned to tray
              if (tray.tray_id === toTrayId || tray.name === toTrayId) {
                const unassignedComp = state.trayStructure!.unassigned?.find((c) => c.id === componentId);
                if (unassignedComp) {
                  return {
                    ...tray,
                    components: [...tray.components, unassignedComp],
                    estimated_height_mm: estimateTrayHeight([...tray.components, unassignedComp]),
                  };
                }
              }
              return tray;
            }

            if (tray.tray_id === fromTrayId) {
              component = tray.components.find((c) => c.id === componentId) || null;
              const newComponents = tray.components.filter((c) => c.id !== componentId);
              return {
                ...tray,
                components: newComponents,
                estimated_height_mm: estimateTrayHeight(newComponents),
              };
            }

            if (toTrayId !== 'Unassigned' && (tray.tray_id === toTrayId || tray.name === toTrayId) && component) {
              const newComponents = [...tray.components, component];
              return {
                ...tray,
                components: newComponents,
                estimated_height_mm: estimateTrayHeight(newComponents),
              };
            }

            return tray;
          });

          let unassigned = state.trayStructure.unassigned || [];

          if (fromTrayId === 'unassigned') {
            unassigned = unassigned.filter((c) => c.id !== componentId);
          } else if (toTrayId === 'Unassigned' && component) {
            unassigned = [...unassigned, component];
          }

          return {
            trayStructure: {
              ...state.trayStructure,
              trays,
              unassigned,
            },
          };
        });
      },

      reorderTrays: (fromIndex, toIndex) => {
        set((state) => {
          if (!state.trayStructure) return state;

          const trays = [...state.trayStructure.trays];
          const stackOrder = [...state.trayStructure.stack_order];

          // Swap in trays array
          [trays[fromIndex], trays[toIndex]] = [trays[toIndex], trays[fromIndex]];

          // Swap in stack_order array
          [stackOrder[fromIndex], stackOrder[toIndex]] = [stackOrder[toIndex], stackOrder[fromIndex]];

          return {
            trayStructure: {
              ...state.trayStructure,
              trays,
              stack_order: stackOrder,
            },
          };
        });
      },

      setTrayStructure: (structure) => {
        set({ trayStructure: structure });
      },

      // Dev utilities
      loadTestData: () => {
        // Import test data dynamically to avoid bundling in production
        import('../utils/testData').then(({ QWIXX_BOX_CONFIG, QWIXX_COMPONENTS, QWIXX_QUICK_DEFAULTS }) => {
          set({
            designName: 'Qwixx (Test Data)',
            boxConfig: QWIXX_BOX_CONFIG,
            components: QWIXX_COMPONENTS,
            quickDefaults: QWIXX_QUICK_DEFAULTS,
            quickDefaultsDone: true,
            currentStep: 1,
            pdfExtractionResult: null,
            selectedComponentGroups: [],
            trayStructure: null,
          });
        });
      },
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
        trayStructure: state.trayStructure,
      }),
    }
  )
);
