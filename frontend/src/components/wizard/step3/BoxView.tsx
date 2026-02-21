import { Stage, Layer, Rect } from 'react-konva';
import { useDesignStore } from '../../../store/designStore';
import { CanvasGrid } from './CanvasGrid';
import { TrayRect } from './TrayRect';

export function BoxView() {
  const { boxConfig, layouts, trayStructure } = useDesignStore();

  // Scale: fit box into ~800px wide canvas
  const canvasWidth = 800;
  const boxWidthMm = boxConfig.width;
  const boxLengthMm = boxConfig.length;
  const scale = canvasWidth / Math.max(boxWidthMm, boxLengthMm);
  const canvasHeight = (boxLengthMm / boxWidthMm) * canvasWidth;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Box View</h2>
        <p className="text-sm text-gray-600">
          Box dimensions: {boxConfig.width}×{boxConfig.length}×{boxConfig.height}mm
        </p>
      </div>

      <div className="border border-gray-300 rounded inline-block bg-white">
        <Stage width={canvasWidth} height={canvasHeight}>
          <Layer>
            {/* Box outline */}
            <Rect
              x={0}
              y={0}
              width={boxWidthMm * scale}
              height={boxLengthMm * scale}
              stroke="#374151"
              strokeWidth={3}
              fill="#FAFAFA"
              listening={false}
            />

            {/* Grid lines (20mm intervals - larger for box view) */}
            <CanvasGrid
              width={boxWidthMm}
              height={boxLengthMm}
              scale={scale}
              interval={20}
            />

            {/* Tray rectangles */}
            {layouts.map(layout => {
              const tray = trayStructure?.trays.find(t => t.tray_id === layout.trayId);
              return (
                <TrayRect
                  key={layout.trayId}
                  layout={layout}
                  tray={tray}
                  scale={scale}
                  boxWidth={boxWidthMm}
                  boxLength={boxLengthMm}
                />
              );
            })}
          </Layer>
        </Stage>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        💡 Tip: Drag trays to reposition. Double-click a tray to edit its compartments.
      </div>
    </div>
  );
}
