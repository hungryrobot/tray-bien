import { useEffect } from 'react';
import { useDesignStore } from '../../../store/designStore';
import { TrayCanvas } from './TrayCanvas';
import { TrayTabBar } from './TrayTabBar';
import { CompartmentProperties } from './CompartmentProperties';
import { AutoPackButton } from './AutoPackButton';

export function LayoutEditor() {
  const {
    trayStructure,
    layouts,
    selectedTrayId,
    setSelectedTrayId,
    setCurrentStep,
    initializeLayouts,
  } = useDesignStore();

  // Auto-initialize layouts on mount if not already done
  useEffect(() => {
    if (!layouts || layouts.length === 0) {
      initializeLayouts();
    }
  }, [layouts, initializeLayouts]);

  if (!trayStructure || !layouts.length) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-600">Initializing layout editor...</p>
      </div>
    );
  }

  const currentTrayId = selectedTrayId || layouts[0]?.trayId;
  const currentLayout = layouts.find(l => l.trayId === currentTrayId);
  const currentTray = trayStructure.trays.find(t => t.tray_id === currentTrayId);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Step 3: Layout Editor</h1>
        <p className="mt-2 text-gray-600">
          Arrange compartments within each tray. Drag to move, drag edges to resize.
        </p>
      </div>

      {/* Tray Tab Bar */}
      <TrayTabBar
        layouts={layouts}
        trays={trayStructure.trays}
        selectedTrayId={currentTrayId || null}
        onSelect={setSelectedTrayId}
      />

      {/* Canvas + Properties Side by Side */}
      <div className="flex gap-6">
        {/* Canvas Area - Takes Most Width */}
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-gray-900">{currentTray?.name}</h2>
              {currentTrayId && <AutoPackButton trayId={currentTrayId} />}
            </div>
            <TrayCanvas layout={currentLayout} tray={currentTray} />
          </div>
        </div>

        {/* Properties Panel - Right Sidebar */}
        <div className="w-80">
          <CompartmentProperties />
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={() => setCurrentStep(2)}
          className="px-6 py-3 text-gray-700 hover:text-gray-900 font-medium"
        >
          ← Back: Sort & Plan
        </button>

        <button
          onClick={() => setCurrentStep(4)}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700
            transition-colors duration-200"
        >
          Next: Preview & Export →
        </button>
      </div>
    </div>
  );
}
