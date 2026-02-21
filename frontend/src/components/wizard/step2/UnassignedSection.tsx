import { useDesignStore } from '../../../store/designStore';

export function UnassignedSection() {
  const { trayStructure, moveComponentBetweenTrays } = useDesignStore();

  if (!trayStructure) return null;

  const { unassigned = [], trays } = trayStructure;

  if (!unassigned.length) return null;

  const trayNames = trays.map(t => t.name);
  const moveOptions = trayNames;

  return (
    <div className="mt-6 p-4 bg-orange-50 border border-orange-300 rounded-lg">
      <h3 className="font-semibold text-orange-900 mb-3">
        ⚠️ Unassigned components ({unassigned.length}) — assign these to a tray before continuing
      </h3>

      <div className="space-y-2">
        {unassigned.map((comp) => (
          <div key={comp.id} className="grid grid-cols-12 gap-2 items-center">
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
                onChange={(e) => moveComponentBetweenTrays(comp.id, 'unassigned', e.target.value)}
                className="w-full text-xs px-2 py-1 border border-orange-300 rounded"
              >
                <option value="">Move to...</option>
                {moveOptions.map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
