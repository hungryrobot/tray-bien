import { useDesignStore } from '../../../store/designStore';
import { getTotalComponentVolumeCm3, validateBoxFit } from '../../../utils/componentCalculations';

export function ComponentSummary() {
  const { components, boxConfig } = useDesignStore();

  if (components.length === 0) return null;

  const totalVolume = getTotalComponentVolumeCm3(components);
  const { fits, fillPercentage, warning } = validateBoxFit(components, boxConfig);
  const hasPending = components.some((c) => c.needsDimensions);

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Summary</h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Total Components</p>
          <p className="text-2xl font-bold text-gray-900">{components.length}</p>
        </div>

        <div>
          <p className="text-gray-600">Total Volume</p>
          <p className="text-2xl font-bold text-gray-900">{totalVolume.toFixed(1)} cm³</p>
        </div>

        <div>
          <p className="text-gray-600">Box Fill</p>
          <p
            className={`text-2xl font-bold ${
              fillPercentage > 90
                ? 'text-red-600'
                : fillPercentage > 70
                ? 'text-orange-600'
                : 'text-green-600'
            }`}
          >
            {fillPercentage.toFixed(1)}%
          </p>
        </div>

        <div>
          <p className="text-gray-600">Status</p>
          <p className="text-lg font-semibold">
            {hasPending ? (
              <span className="text-orange-600">⚠️ Pending</span>
            ) : fits ? (
              <span className="text-green-600">✓ Ready</span>
            ) : (
              <span className="text-red-600">✗ Too Full</span>
            )}
          </p>
        </div>
      </div>

      {/* Warnings */}
      {hasPending && (
        <div className="mt-4 p-3 bg-orange-100 border border-orange-300 rounded text-sm text-orange-800">
          <strong>⚠️ Action Required:</strong> Some components need dimensions before proceeding.
        </div>
      )}

      {!hasPending && warning && (
        <div
          className={`mt-4 p-3 rounded text-sm ${
            fillPercentage > 90
              ? 'bg-red-100 border border-red-300 text-red-800'
              : 'bg-orange-100 border border-orange-300 text-orange-800'
          }`}
        >
          <strong>⚠️ Warning:</strong> {warning}
        </div>
      )}

      {!hasPending && !warning && (
        <div className="mt-4 p-3 bg-green-100 border border-green-300 rounded text-sm text-green-800">
          <strong>✓ Ready:</strong> All components have dimensions and fit comfortably.
        </div>
      )}
    </div>
  );
}
