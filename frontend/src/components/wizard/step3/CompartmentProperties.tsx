import { useDesignStore } from '../../../store/designStore';

export function CompartmentProperties() {
  const { selectedCompartmentId, layouts, selectedTrayId, updateCompartment } = useDesignStore();

  if (!selectedCompartmentId || !selectedTrayId) {
    return (
      <div className="bg-white rounded-lg shadow p-4 text-gray-500 text-sm">
        <p className="text-center">Click a compartment to view and edit its properties.</p>
      </div>
    );
  }

  const layout = layouts.find(l => l.trayId === selectedTrayId);
  const compartment = layout?.compartments.find(c => c.id === selectedCompartmentId);

  if (!compartment) return null;

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <h3 className="font-semibold text-gray-900">{compartment.name}</h3>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-500 mb-1">X (mm)</label>
          <input
            type="number"
            value={compartment.x}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { x: Number(e.target.value) })}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Y (mm)</label>
          <input
            type="number"
            value={compartment.y}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { y: Number(e.target.value) })}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Width (mm)</label>
          <input
            type="number"
            value={compartment.width}
            min={compartment.minWidth}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, {
              width: Math.max(compartment.minWidth, Number(e.target.value))
            })}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Length (mm)</label>
          <input
            type="number"
            value={compartment.length}
            min={compartment.minLength}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, {
              length: Math.max(compartment.minLength, Number(e.target.value))
            })}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div className="col-span-2">
          <label className="block text-xs text-gray-500 mb-1">Depth (mm)</label>
          <input
            type="number"
            value={compartment.depth}
            onChange={e => updateCompartment(selectedTrayId, compartment.id, { depth: Number(e.target.value) })}
            className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
      </div>

      <div className="text-xs text-gray-500 space-y-1 pt-2 border-t border-gray-200">
        <p>Min size: {compartment.minWidth}×{compartment.minLength}mm</p>
        <p>Volume: {((compartment.width * compartment.length * compartment.depth) / 1000).toFixed(1)} cm³</p>
      </div>

      <div className="pt-2 border-t border-gray-200 flex items-center gap-2">
        <div className="w-4 h-4 rounded" style={{ backgroundColor: compartment.color }} />
        <span className="text-sm text-gray-600">Component type color</span>
      </div>
    </div>
  );
}
