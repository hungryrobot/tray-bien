import { useEffect } from 'react';
import { useDesignStore } from '../../../store/designStore';
import { StackSummary } from '../step2/StackSummary';
import { TrayCard } from '../step2/TrayCard';
import { BoardLayerCard } from '../step2/BoardLayerCard';
import { UnassignedSection } from '../step2/UnassignedSection';

export function Step2SortAndPlan() {
  const {
    setCurrentStep,
    trayStructure,
    initializeTrayStructure,
    addTray,
  } = useDesignStore();

  // Auto-initialize tray structure on mount if not already done
  useEffect(() => {
    if (!trayStructure) {
      initializeTrayStructure();
    }
  }, [trayStructure, initializeTrayStructure]);

  if (!trayStructure) {
    return <div className="text-center py-8">Initializing tray structure...</div>;
  }

  const { trays, unassigned = [] } = trayStructure;
  const canProceed = unassigned.length === 0;  // All components must be assigned

  const handleAddTray = () => {
    const newId = `tray_${trays.length + 1}`;
    addTray({
      tray_id: newId,
      name: `New Tray ${trays.length + 1}`,
      tray_type: 'shared',
      components: [],
      player_sets: null,
      player_names: null,
      needs_lid: false,
      parent_tray_id: null,
      notes: '',
      estimated_height_mm: 15,
    });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Step 2: Sort & Plan</h1>
        <p className="mt-2 text-gray-600">
          Organize components into trays and review the stack layout.
        </p>
      </div>

      {/* Stack Summary */}
      <StackSummary />

      {/* Board Layer */}
      <BoardLayerCard />

      {/* Tray Cards */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Trays (Bottom to Top)</h2>
        {trays.map((tray, index) => (
          <TrayCard
            key={tray.tray_id}
            tray={tray}
            trayIndex={index}
            allTrays={trays}
          />
        ))}
      </div>

      {/* Add Tray Button */}
      <button
        onClick={handleAddTray}
        className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg
          hover:border-blue-500 hover:bg-blue-50 text-gray-600 hover:text-blue-600
          transition-colors duration-200"
      >
        + Add New Tray
      </button>

      {/* Unassigned Section */}
      <UnassignedSection />

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={() => setCurrentStep(1)}
          className="px-6 py-3 text-gray-700 hover:text-gray-900 font-medium"
        >
          ← Back: Box & Components
        </button>

        <button
          onClick={() => setCurrentStep(3)}
          disabled={!canProceed}
          className={`
            px-6 py-3 rounded-lg font-medium
            ${
              canProceed
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          Next: Layout Editor →
        </button>
      </div>

      {!canProceed && (
        <p className="text-sm text-orange-600 text-right -mt-4">
          ⚠️ Assign all unassigned components before proceeding
        </p>
      )}
    </div>
  );
}
