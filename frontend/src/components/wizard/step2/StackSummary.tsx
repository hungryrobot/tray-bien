import { useDesignStore } from '../../../store/designStore';

export function StackSummary() {
  const { trayStructure } = useDesignStore();

  if (!trayStructure) return null;

  const { trays, board_layer, stack_order, box_height_mm } = trayStructure;

  const boardThickness = board_layer.estimated_thickness_mm;

  // Calculate tray heights
  const trayById = Object.fromEntries(trays.map(t => [t.tray_id, t]));
  const trayHeights = Object.fromEntries(
    stack_order.map(id => [id, trayById[id]?.estimated_height_mm || 0])
  );

  const totalTrayHeight = Object.values(trayHeights).reduce((sum, h) => sum + h, 0);
  const totalUsed = totalTrayHeight + boardThickness;
  const remaining = box_height_mm - totalUsed;
  const pct = box_height_mm > 0 ? Math.round((totalUsed / box_height_mm) * 100) : 0;

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Stack Summary</h2>

      <div className="space-y-2 text-sm font-mono">
        <p className="font-bold">
          {totalUsed}mm used of {box_height_mm}mm ({pct}%)
        </p>

        {boardThickness > 0 && (
          <p className="text-gray-600">
            └─ Board & rulebook (top, not printed) — ~{boardThickness}mm
          </p>
        )}

        {/* Reversed stack order (bottom to top visually = top to bottom in UI) */}
        {[...stack_order].reverse().map(trayId => {
          const tray = trayById[trayId];
          if (!tray) return null;

          const h = trayHeights[trayId];
          let label = tray.name;
          if (tray.player_sets) label += ` ×${tray.player_sets}`;

          return (
            <p key={trayId} className="text-gray-600">
              └─ {label} — ~{h}mm
            </p>
          );
        })}

        {remaining < 0 && (
          <p className="text-red-600 font-semibold">
            OVER by {Math.abs(remaining)}mm — trays will not fit
          </p>
        )}
        {remaining >= 0 && remaining < 10 && (
          <p className="text-orange-600">
            {remaining}mm headroom (tight fit)
          </p>
        )}
        {remaining >= 10 && (
          <p className="text-green-600">
            {remaining}mm headroom
          </p>
        )}
      </div>

      {totalUsed > box_height_mm && (
        <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded text-sm text-red-800">
          <strong>Error:</strong> Estimated stack height (~{totalUsed}mm) exceeds box height
          ({box_height_mm}mm) by ~{totalUsed - box_height_mm}mm. Reduce tray count or use shallower compartments.
        </div>
      )}
    </div>
  );
}
