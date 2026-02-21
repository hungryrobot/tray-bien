import { useEffect } from 'react';
import { useDesignStore } from '../../../store/designStore';
import { BoxView } from './BoxView';
import { TrayView } from './TrayView';

export function LayoutEditor() {
  const {
    trayStructure,
    layouts,
    layoutViewMode,
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Step 3: Layout Editor</h1>
        <p className="mt-2 text-gray-600">
          {layoutViewMode === 'box'
            ? 'Arrange trays within the box. Double-click a tray to edit its compartments.'
            : 'Arrange compartments within the tray. Drag to move, drag edges to resize.'}
        </p>
      </div>

      {/* Conditional Rendering Based on View Mode */}
      {layoutViewMode === 'box' ? <BoxView /> : <TrayView />}

      {/* Navigation (only show in Box View) */}
      {layoutViewMode === 'box' && (
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
      )}
    </div>
  );
}
