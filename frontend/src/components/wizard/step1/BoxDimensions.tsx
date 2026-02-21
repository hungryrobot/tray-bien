import { useDesignStore } from '../../../store/designStore';
import { getBoxVolumeCm3 } from '../../../utils/componentCalculations';

export function BoxDimensions() {
  const { designName, boxConfig, setDesignName, setBoxConfig } = useDesignStore();

  const boxVolume = getBoxVolumeCm3(boxConfig);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Box Configuration</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Design Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Design Name
          </label>
          <input
            type="text"
            value={designName}
            onChange={(e) => setDesignName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="My Insert Design"
          />
        </div>

        {/* Length */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Length (mm)
          </label>
          <input
            type="number"
            value={boxConfig.length}
            onChange={(e) => setBoxConfig({ length: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            min="1"
          />
        </div>

        {/* Width */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Width (mm)
          </label>
          <input
            type="number"
            value={boxConfig.width}
            onChange={(e) => setBoxConfig({ width: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            min="1"
          />
        </div>

        {/* Height */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Height (mm)
          </label>
          <input
            type="number"
            value={boxConfig.height}
            onChange={(e) => setBoxConfig({ height: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            min="1"
          />
        </div>
      </div>

      {/* Volume Display */}
      <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
        <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>
          Box volume: <strong>{boxVolume.toFixed(0)} cm³</strong>
          {' '}({boxConfig.length} × {boxConfig.width} × {boxConfig.height} mm)
        </span>
      </div>

      {boxVolume < 100 && (
        <p className="mt-2 text-sm text-orange-600">
          ⚠️ Warning: Very small box volume. Double-check dimensions.
        </p>
      )}
    </div>
  );
}
