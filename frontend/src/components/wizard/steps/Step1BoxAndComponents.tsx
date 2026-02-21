import { useState } from 'react';
import { useDesignStore } from '../../../store/designStore';
import { BoxDimensions } from '../step1/BoxDimensions';
import { PDFExtraction } from '../step1/PDFExtraction';
import { QuickDefaults } from '../step1/QuickDefaults';
import { ComponentReview } from '../step1/ComponentReview';
import { ComponentEditor } from '../step1/ComponentEditor';
import { ComponentSummary } from '../step1/ComponentSummary';

interface Props {
  onOpenSettings: () => void;
}

export function Step1BoxAndComponents({ onOpenSettings }: Props) {
  const {
    quickDefaultsDone,
    pdfExtractionResult,
    components,
    setCurrentStep,
  } = useDesignStore();

  const [showQuickDefaults, setShowQuickDefaults] = useState(false);

  // Trigger Quick Defaults modal when PDF extraction completes
  const handleExtractionComplete = () => {
    setShowQuickDefaults(true);
  };

  const handleQuickDefaultsComplete = () => {
    setShowQuickDefaults(false);
  };

  const canProceed = components.length > 0 && !components.some((c) => c.needsDimensions);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Step 1: Box & Components</h1>
        <p className="mt-2 text-gray-600">
          Define your box dimensions and add components from PDF extraction or manually.
        </p>
      </div>

      {/* Box Dimensions */}
      <BoxDimensions />

      {/* PDF Extraction */}
      <PDFExtraction
        onExtractionComplete={handleExtractionComplete}
        onOpenSettings={onOpenSettings}
      />

      {/* Quick Defaults Modal (blocking) */}
      {showQuickDefaults && !quickDefaultsDone && (
        <QuickDefaults onComplete={handleQuickDefaultsComplete} />
      )}

      {/* Component Review (after Quick Defaults) */}
      {quickDefaultsDone && pdfExtractionResult && (
        <ComponentReview />
      )}

      {/* Component Editor (after import) */}
      {components.length > 0 && (
        <>
          <ComponentEditor />
          <ComponentSummary />
        </>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 text-gray-700 hover:text-gray-900"
        >
          ← Reset Wizard
        </button>

        <button
          onClick={() => setCurrentStep(2)}
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
          Next: Sort & Plan →
        </button>
      </div>

      {!canProceed && components.length > 0 && (
        <p className="text-sm text-orange-600 text-right -mt-6">
          ⚠️ Some components need dimensions before proceeding
        </p>
      )}
    </div>
  );
}
