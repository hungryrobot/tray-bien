import { useState } from 'react';
import { useDesignStore } from '../../../store/designStore';
import type { Component, ComponentType, CardStock, SleeveType } from '../../../types';

const COMPONENT_TYPES: ComponentType[] = [
  'Cards',
  'Tokens',
  'Tiles',
  'Dice',
  'Meeples/Minis',
  'Boards',
  'Rulebook',
  'Other',
];

interface ComponentEditorItemProps {
  component: Component;
}

function ComponentEditorItem({ component }: ComponentEditorItemProps) {
  const { updateComponent, removeComponent, boxConfig } = useDesignStore();
  const [isExpanded, setIsExpanded] = useState(component.needsDimensions);
  const [localState, setLocalState] = useState(component);

  const handleSave = () => {
    // Recalculate needsDimensions based on current dimensions
    const needsDimensions = !(
      localState.length !== null && localState.length > 0 &&
      localState.width !== null && localState.width > 0 &&
      localState.height !== null && localState.height > 0
    );

    updateComponent(component.id, {
      ...localState,
      needsDimensions,
    });
    setIsExpanded(false);
  };

  const handleCancel = () => {
    setLocalState(component);
    setIsExpanded(false);
  };

  const handleRemove = () => {
    if (confirm(`Remove "${component.name}"?`)) {
      removeComponent(component.id);
    }
  };

  // Update local state helper
  const update = (updates: Partial<Component>) => {
    setLocalState({ ...localState, ...updates });
  };

  return (
    <div className="border border-gray-200 rounded-lg">
      {/* Component Header (collapsed view) */}
      <div
        className="px-4 py-3 bg-gray-50 cursor-pointer hover:bg-gray-100"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">{component.name}</span>
              <span className="text-xs text-gray-500">({component.type})</span>
              {component.needsDimensions && (
                <span className="text-xs text-orange-600 font-semibold">⚠️ Needs dims</span>
              )}
            </div>
            <div className="mt-1 text-sm text-gray-600">
              Qty: {component.quantity} •{' '}
              {component.length && component.width && component.height
                ? `${component.length}×${component.width}×${component.height}mm`
                : 'No dimensions'}
              {component.volume && ` • ${(component.volume / 1000).toFixed(1)} cm³`}
            </div>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg
              className={`w-5 h-5 transform transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Expanded Editor */}
      {isExpanded && (
        <div className="p-4 space-y-4 bg-white">
          {/* Basic Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={localState.name}
                onChange={(e) => update({ name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={localState.type}
                onChange={(e) => update({ type: e.target.value as ComponentType })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                {COMPONENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
            <input
              type="number"
              value={localState.quantity}
              onChange={(e) => update({ quantity: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              min="1"
            />
          </div>

          {/* Type-specific fields */}
          {localState.type === 'Cards' && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Card Stock
                  </label>
                  <select
                    value={localState.cardStock || 'standard'}
                    onChange={(e) => update({ cardStock: e.target.value as CardStock })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="standard">Standard (300gsm)</option>
                    <option value="premium">Premium (350gsm)</option>
                    <option value="tarot">Tarot weight</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sleeve Type
                  </label>
                  <select
                    value={localState.sleeveType || 'unsleeved'}
                    onChange={(e) => update({ sleeveType: e.target.value as SleeveType })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="unsleeved">Unsleeved</option>
                    <option value="thin">Thin sleeves</option>
                    <option value="premium">Premium sleeves</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stack Quantity (for measurement)
                  </label>
                  <input
                    type="number"
                    value={localState.stackQuantity || ''}
                    onChange={(e) => update({ stackQuantity: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., 10"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Measured Stack Height (mm)
                  </label>
                  <input
                    type="number"
                    value={localState.stackHeight || ''}
                    onChange={(e) => update({ stackHeight: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., 3.5mm"
                  />
                </div>
              </div>
            </>
          )}

          {/* Special UI for Boards/Rulebooks (non-printed layer) */}
          {(localState.type === 'Boards' || localState.type === 'Rulebook') ? (
            <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xl">📦</span>
                <div>
                  <p className="text-sm font-semibold text-amber-900">Non-printed Layer</p>
                  <p className="text-xs text-amber-700">Sits on top of insert stack — no tray needed</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Footprint (from box)</label>
                  <p className="text-sm font-medium text-gray-700 bg-white px-3 py-2 rounded border border-amber-200">
                    {boxConfig.length}×{boxConfig.width}mm
                  </p>
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Thickness (mm)</label>
                  <input
                    type="number"
                    value={localState.height || ''}
                    onChange={(e) => update({ height: Number(e.target.value) || null })}
                    className="w-full px-3 py-2 border border-amber-300 rounded-md focus:ring-amber-500 focus:border-amber-500"
                    placeholder="e.g., 3"
                  />
                </div>
              </div>
            </div>
          ) : (
            /* Generic dimensions (for all other types) */
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dimensions (mm)
              </label>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Length</label>
                  <input
                    type="number"
                    value={localState.length || ''}
                    onChange={(e) => update({ length: Number(e.target.value) || null })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="L"
                  />
                </div>

                <div>
                  <label className="block text-xs text-gray-600 mb-1">Width</label>
                  <input
                    type="number"
                    value={localState.width || ''}
                    onChange={(e) => update({ width: Number(e.target.value) || null })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="W"
                  />
                </div>

                <div>
                  <label className="block text-xs text-gray-600 mb-1">Height</label>
                  <input
                    type="number"
                    value={localState.height || ''}
                    onChange={(e) => update({ height: Number(e.target.value) || null })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="H"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Prefill info */}
          {localState.prefillSource && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
              <strong>Auto-filled:</strong> {localState.prefillSource}
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={localState.notes || ''}
              onChange={(e) => update({ notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              rows={2}
              placeholder="Optional notes..."
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
            >
              Save Changes
            </button>
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={handleRemove}
              className="ml-auto px-4 py-2 bg-red-600 text-white font-medium rounded-md hover:bg-red-700"
            >
              Remove
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export function ComponentEditor() {
  const components = useDesignStore((state) => state.components);

  if (components.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Edit Components</h2>
      <p className="text-sm text-gray-600 mb-4">
        Review and edit component dimensions. Click to expand and modify details.
      </p>

      <div className="space-y-3">
        {components.map((component) => (
          <ComponentEditorItem key={component.id} component={component} />
        ))}
      </div>
    </div>
  );
}
