import { Stage, Layer, Rect } from 'react-konva';
import type { TrayLayout, Tray } from '../../../types';
import { useDesignStore } from '../../../store/designStore';
import { CanvasGrid } from './CanvasGrid';
import { CompartmentRect } from './CompartmentRect';

interface TrayCanvasProps {
  layout: TrayLayout | undefined;
  tray: Tray | undefined;
}

export function TrayCanvas({ layout, tray }: TrayCanvasProps) {
  const { boxConfig } = useDesignStore();

  if (!layout || !tray) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 border-2 border-dashed border-gray-300 rounded">
        <p className="text-gray-500">No tray selected</p>
      </div>
    );
  }

  // Scale: convert mm to pixels
  // Fit the tray into ~700px wide canvas
  const canvasWidth = 700;
  const trayWidthMm = boxConfig.width - layout.outerWallThickness * 2;
  const trayLengthMm = boxConfig.length - layout.outerWallThickness * 2;
  const scale = canvasWidth / Math.max(trayWidthMm, trayLengthMm);
  const canvasHeight = (trayLengthMm / trayWidthMm) * canvasWidth;

  return (
    <div className="border border-gray-300 rounded inline-block bg-white">
      <Stage width={canvasWidth} height={canvasHeight}>
        <Layer>
          {/* Tray outline */}
          <Rect
            x={0}
            y={0}
            width={trayWidthMm * scale}
            height={trayLengthMm * scale}
            stroke="#9CA3AF"
            strokeWidth={2}
            fill="#F9FAFB"
            listening={false}
          />

          {/* Grid lines (10mm intervals) */}
          <CanvasGrid
            width={trayWidthMm}
            height={trayLengthMm}
            scale={scale}
            interval={10}
          />

          {/* Compartments */}
          {layout.compartments.map(comp => (
            <CompartmentRect
              key={comp.id}
              compartment={comp}
              scale={scale}
              trayId={layout.trayId}
              trayWidth={trayWidthMm}
              trayLength={trayLengthMm}
            />
          ))}
        </Layer>
      </Stage>
    </div>
  );
}
