import { useDesignStore } from '../../../store/designStore';
import { estimateComponentHeight } from '../../../utils/trayEstimation';

export function BoardLayerCard() {
  const { trayStructure } = useDesignStore();

  if (!trayStructure) return null;

  const { components, estimated_thickness_mm } = trayStructure.board_layer;

  if (!components.length) return null;

  return (
    <div className="border border-gray-200 rounded-lg mb-4 bg-amber-50">
      <div className="px-4 py-3 bg-amber-100 border-b border-amber-200">
        <h3 className="font-semibold text-gray-900">
          Board & Rulebook Layer — On Top ({components.length} items, ~{estimated_thickness_mm}mm)
        </h3>
      </div>

      <div className="p-4">
        <p className="text-sm text-gray-600 mb-3">
          These items sit on top of the insert stack. They don't need printed tray compartments
          but contribute to the total stack height.
        </p>

        <div className="space-y-2">
          {components.map((comp) => {
            const est = estimateComponentHeight(comp);
            return (
              <div key={comp.id} className="grid grid-cols-12 gap-2 text-sm">
                <div className="col-span-6">
                  <code>{comp.name}</code>
                </div>
                <div className="col-span-3 text-gray-600">
                  {comp.type}
                </div>
                <div className="col-span-3 text-gray-600">
                  ×{comp.quantity} (~{est}mm)
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
