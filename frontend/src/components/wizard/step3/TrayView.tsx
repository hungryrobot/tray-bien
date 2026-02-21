import { useDesignStore } from '../../../store/designStore';
import { TrayCanvas } from './TrayCanvas';
import { CompartmentProperties } from './CompartmentProperties';
import { AutoPackButton } from './AutoPackButton';

export function TrayView() {
  const { layouts, editingTrayId, trayStructure, exitTrayView } = useDesignStore();

  const currentLayout = layouts.find(l => l.trayId === editingTrayId);
  const currentTray = trayStructure?.trays.find(t => t.tray_id === editingTrayId);

  if (!currentLayout || !currentTray) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600">Error: No tray selected for editing</p>
        <button
          onClick={exitTrayView}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Back to Box View
        </button>
      </div>
    );
  }

  return (
    <>
      {/* Back to Box View Bar */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <button
          onClick={exitTrayView}
          className="px-4 py-2 bg-white border border-blue-300 rounded hover:bg-blue-50
            text-blue-700 font-medium text-sm transition-colors duration-200"
        >
          ← Back to Box View
        </button>
        <span className="ml-4 text-sm text-blue-800">
          Editing: <strong>{currentTray.name}</strong>
        </span>
      </div>

      {/* Compartment Editing Interface */}
      <div className="flex gap-6">
        {/* Canvas Area */}
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-gray-900">{currentTray.name}</h2>
              <AutoPackButton trayId={currentLayout.trayId} />
            </div>
            <TrayCanvas layout={currentLayout} tray={currentTray} />
          </div>
        </div>

        {/* Properties Panel */}
        <div className="w-80">
          <CompartmentProperties />
        </div>
      </div>
    </>
  );
}
