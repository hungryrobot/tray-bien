import { useState } from 'react';
import { useDesignStore } from '../../../store/designStore';

export function ComponentReview() {
  const { selectedComponentGroups, importSelectedComponents } = useDesignStore();
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set());

  // Initialize all as checked
  useState(() => {
    const allIds = new Set<string>();
    selectedComponentGroups.forEach((group) => {
      group.components.forEach((comp) => allIds.add(comp.id));
    });
    setCheckedIds(allIds);
  });

  const toggleCheck = (id: string) => {
    const newChecked = new Set(checkedIds);
    if (newChecked.has(id)) {
      newChecked.delete(id);
    } else {
      newChecked.add(id);
    }
    setCheckedIds(newChecked);
  };

  const handleSelectAll = () => {
    const allIds = new Set<string>();
    selectedComponentGroups.forEach((group) => {
      group.components.forEach((comp) => allIds.add(comp.id));
    });
    setCheckedIds(allIds);
  };

  const handleDeselectAll = () => {
    setCheckedIds(new Set());
  };

  const handleImport = () => {
    importSelectedComponents(checkedIds);
  };

  if (selectedComponentGroups.length === 0) return null;

  const totalComponents = selectedComponentGroups.reduce(
    (sum, group) => sum + group.components.length,
    0
  );

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Review Extracted Components</h2>
          <p className="text-sm text-gray-600 mt-1">
            Select components to import. Dimensions have been pre-filled based on Quick Defaults.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleSelectAll}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Select All
          </button>
          <button
            onClick={handleDeselectAll}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Deselect All
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {selectedComponentGroups.map((group) => (
          <div key={group.groupName} className="border border-gray-200 rounded-lg overflow-hidden">
            {/* Group Header */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{group.groupName}</h3>
                  <p className="text-sm text-gray-500 mt-0.5">
                    {group.groupType.replace('_', ' ')} •{' '}
                    {group.perPlayer ? 'Per Player' : 'Shared'} •{' '}
                    {group.components.length} component{group.components.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
            </div>

            {/* Components List */}
            <div className="divide-y divide-gray-200">
              {group.components.map((comp) => (
                <label
                  key={comp.id}
                  className="flex items-start gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={checkedIds.has(comp.id)}
                    onChange={() => toggleCheck(comp.id)}
                    className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">{comp.name}</span>
                      <span className="text-xs text-gray-500">({comp.type})</span>
                    </div>

                    <div className="mt-1 flex items-center gap-4 text-sm text-gray-600">
                      <span>Qty: {comp.quantity}</span>

                      {comp.prefillComplete ? (
                        <span className="text-green-600">
                          ✓ {comp.length}×{comp.width}×{comp.height}mm
                        </span>
                      ) : (
                        <span className="text-orange-600">⚠️ Needs dimensions</span>
                      )}
                    </div>

                    {comp.prefillSource && (
                      <p className="mt-1 text-xs text-blue-600">{comp.prefillSource}</p>
                    )}

                    {comp.details && (
                      <p className="mt-1 text-xs text-gray-500">Note: {comp.details}</p>
                    )}
                  </div>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Import Button */}
      <div className="mt-6 flex items-center justify-between">
        <p className="text-sm text-gray-600">
          {checkedIds.size} of {totalComponents} components selected
        </p>

        <button
          onClick={handleImport}
          disabled={checkedIds.size === 0}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg
            hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Import {checkedIds.size} Component{checkedIds.size !== 1 ? 's' : ''} →
        </button>
      </div>
    </div>
  );
}
