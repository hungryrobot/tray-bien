import { useState } from 'react';
import type { Tray, Component, TrayType } from '../../../types';
import { useDesignStore } from '../../../store/designStore';

interface TrayCardProps {
  tray: Tray;
  trayIndex: number;
  allTrays: Tray[];
}

export function TrayCard({ tray, trayIndex, allTrays }: TrayCardProps) {
  const { updateTray, removeTray, moveComponentBetweenTrays, reorderTrays } = useDesignStore();
  const [isExpanded, setIsExpanded] = useState(true);

  const { tray_id, tray_type, name, components, player_sets, player_names, estimated_height_mm, needs_lid, lid_reason } = tray;

  const typeLabels: Record<TrayType, string> = {
    player: 'Player',
    shared: 'Shared',
    setup: 'Setup',
  };

  const typeLabel = typeLabels[tray_type];

  // Build header text
  let header = `${typeLabel} — ${name} (${components.length} items, ~${estimated_height_mm}mm)`;
  if (tray_type === 'player' && player_sets) {
    header = `${typeLabel} ×${player_sets} — ${name} (${components.length} items, ~${estimated_height_mm}mm)`;
  }

  const handleMoveTo = (comp: Component, targetName: string) => {
    if (targetName === '— stay here —') return;
    moveComponentBetweenTrays(comp.id, tray_id, targetName);
  };

  return (
    <div className="border border-gray-200 rounded-lg mb-4">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between"
      >
        <span className="font-semibold text-gray-900">{header}</span>
        <svg
          className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* Name + Type row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tray name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => updateTray(tray_id, { name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={tray_type}
                onChange={(e) => updateTray(tray_id, { tray_type: e.target.value as TrayType })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="player">Player</option>
                <option value="shared">Shared</option>
                <option value="setup">Setup</option>
              </select>
            </div>
          </div>

          {/* Player sets info */}
          {tray_type === 'player' && player_sets && (
            <p className="text-sm text-gray-600">
              Template tray — ×{player_sets} identical sets
              {player_names && ` (${player_names.join(', ')})`}
            </p>
          )}
          {tray_type === 'player' && !player_sets && (
            <p className="text-sm text-gray-600">Unique faction tray (asymmetric game)</p>
          )}

          {/* Lid toggle */}
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded border border-blue-200">
            <input
              type="checkbox"
              id={`lid_${tray_id}`}
              checked={needs_lid}
              onChange={(e) => updateTray(tray_id, { needs_lid: e.target.checked })}
              className="w-4 h-4"
            />
            <label htmlFor={`lid_${tray_id}`} className="text-sm font-medium text-gray-700">
              Include lid for this tray
            </label>
            {lid_reason && (
              <span className="text-xs text-blue-600 ml-auto">{lid_reason}</span>
            )}
          </div>

          {/* Component list */}
          {components.length > 0 ? (
            <div>
              <h4 className="font-semibold mb-2">Components ({components.length} items)</h4>

              {components.map((comp) => {
                const otherTrayNames = allTrays
                  .filter(t => t.tray_id !== tray_id)
                  .map(t => t.name);
                const moveOptions = ['— stay here —', ...otherTrayNames, 'Unassigned'];

                return (
                  <div key={comp.id} className="grid grid-cols-12 gap-2 items-center py-2 border-b border-gray-100">
                    <div className="col-span-5">
                      <code className="text-sm">{comp.name}</code>
                    </div>
                    <div className="col-span-3 text-sm text-gray-600">
                      {comp.type}
                    </div>
                    <div className="col-span-1 text-sm text-gray-600">
                      ×{comp.quantity}
                    </div>
                    <div className="col-span-3">
                      <select
                        value="— stay here —"
                        onChange={(e) => handleMoveTo(comp, e.target.value)}
                        className="w-full text-xs px-2 py-1 border border-gray-300 rounded"
                      >
                        {moveOptions.map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500">This tray is empty — move components here from other trays.</p>
          )}

          {/* Stack order controls + Remove */}
          <div className="flex gap-2">
            {trayIndex > 0 && (
              <button
                onClick={() => reorderTrays(trayIndex, trayIndex - 1)}
                className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
              >
                ↑ Up
              </button>
            )}
            {trayIndex < allTrays.length - 1 && (
              <button
                onClick={() => reorderTrays(trayIndex, trayIndex + 1)}
                className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
              >
                ↓ Down
              </button>
            )}
            <button
              onClick={() => removeTray(tray_id)}
              className="ml-auto px-3 py-1 text-sm bg-red-600 text-white hover:bg-red-700 rounded"
            >
              × Remove tray
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
