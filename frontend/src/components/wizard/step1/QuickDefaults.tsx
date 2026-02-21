import { useState } from 'react';
import { useDesignStore } from '../../../store/designStore';
import type { QuickDefaults as QuickDefaultsType, CardboardQuality, SleeveType } from '../../../types';

interface Props {
  onComplete: () => void;
}

export function QuickDefaults({ onComplete }: Props) {
  const { setQuickDefaults, applyQuickDefaults, selectedComponentGroups } = useDesignStore();

  // Auto-detect component types from extraction results
  const detectDefaults = (): QuickDefaultsType => {
    const allComponents = selectedComponentGroups.flatMap(g => g.components);

    const hasDice = allComponents.some(c => c.type === 'Dice');
    const hasCubes = allComponents.some(c => c.type === 'Tokens' &&
      (c.name.toLowerCase().includes('cube') || c.name.toLowerCase().includes('resource')));
    const hasMinis = allComponents.some(c => c.type === 'Meeples/Minis');
    const hasCards = allComponents.some(c => c.type === 'Cards');

    return {
      cardboardQuality: 'standard',
      cardsSleeved: hasCards ? 'unsleeved' : 'unsleeved',
      hasDice,
      diceSizeMm: 16,
      hasCubes,
      cubeSizeMm: 8,
      hasMinis,
      hasExpansionSpace: false,
    };
  };

  const [defaults, setDefaults] = useState<QuickDefaultsType>(detectDefaults());

  const handleSubmit = () => {
    setQuickDefaults(defaults);
    applyQuickDefaults();
    onComplete();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Quick Defaults</h2>
          <p className="text-gray-600 mb-6">
            Set global defaults to pre-fill component dimensions automatically.
            You can edit individual components afterward.
          </p>

          <div className="space-y-6">
            {/* Cardboard Quality */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cardboard Quality (for tokens/tiles)
              </label>
              <select
                value={defaults.cardboardQuality}
                onChange={(e) =>
                  setDefaults({ ...defaults, cardboardQuality: e.target.value as CardboardQuality })
                }
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                  focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="budget">Budget (1.1mm) - Lightweight games</option>
                <option value="standard">Standard (1.5mm) - Most modern games</option>
                <option value="premium">Premium (2.0mm) - Deluxe editions</option>
                <option value="heavy_duty">Heavy Duty (2.5mm) - Player boards</option>
                <option value="luxury">Luxury (3.0mm) - Premium games</option>
              </select>
            </div>

            {/* Cards Sleeved */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Are cards sleeved?
              </label>
              <select
                value={defaults.cardsSleeved}
                onChange={(e) =>
                  setDefaults({ ...defaults, cardsSleeved: e.target.value as SleeveType })
                }
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                  focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="unsleeved">Unsleeved</option>
                <option value="thin">Thin Sleeves (+0.05mm/card)</option>
                <option value="premium">Premium Sleeves (+0.1mm/card)</option>
              </select>
            </div>

            {/* Has Dice */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="has-dice"
                checked={defaults.hasDice}
                onChange={(e) => setDefaults({ ...defaults, hasDice: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="has-dice" className="text-sm font-medium text-gray-700">
                Game has dice?
              </label>
            </div>

            {defaults.hasDice && (
              <div className="ml-7">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dice size (mm)
                </label>
                <input
                  type="number"
                  value={defaults.diceSizeMm}
                  onChange={(e) =>
                    setDefaults({ ...defaults, diceSizeMm: Number(e.target.value) })
                  }
                  className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm
                    focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  min="1"
                />
                <p className="mt-1 text-xs text-gray-500">Common: 16mm (standard), 12mm (small)</p>
              </div>
            )}

            {/* Has Cubes */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="has-cubes"
                checked={defaults.hasCubes}
                onChange={(e) => setDefaults({ ...defaults, hasCubes: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="has-cubes" className="text-sm font-medium text-gray-700">
                Game has resource cubes?
              </label>
            </div>

            {defaults.hasCubes && (
              <div className="ml-7">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cube size (mm)
                </label>
                <input
                  type="number"
                  value={defaults.cubeSizeMm}
                  onChange={(e) =>
                    setDefaults({ ...defaults, cubeSizeMm: Number(e.target.value) })
                  }
                  className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm
                    focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  min="1"
                />
                <p className="mt-1 text-xs text-gray-500">Common: 8mm, 10mm, 12mm</p>
              </div>
            )}

            {/* Has Minis */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="has-minis"
                checked={defaults.hasMinis}
                onChange={(e) => setDefaults({ ...defaults, hasMinis: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="has-minis" className="text-sm font-medium text-gray-700">
                Game has miniatures/figures? (requires manual dimensions)
              </label>
            </div>

            {/* Has Expansion Space */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="has-expansion"
                checked={defaults.hasExpansionSpace}
                onChange={(e) => setDefaults({ ...defaults, hasExpansionSpace: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="has-expansion" className="text-sm font-medium text-gray-700">
                Reserve space for future expansions?
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex justify-end gap-3">
            <button
              onClick={handleSubmit}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Apply Defaults & Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
