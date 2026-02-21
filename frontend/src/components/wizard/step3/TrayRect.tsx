import { useRef } from 'react';
import { Rect, Text, Group } from 'react-konva';
import Konva from 'konva';
import type { TrayLayout, Tray } from '../../../types';
import { useDesignStore } from '../../../store/designStore';

interface TrayRectProps {
  layout: TrayLayout;
  tray: Tray | undefined;
  scale: number;
  boxWidth: number;   // mm
  boxLength: number;  // mm
}

export function TrayRect({ layout, tray, scale, boxWidth, boxLength }: TrayRectProps) {
  const { updateTrayLayout, enterTrayView, selectedTrayId, setSelectedTrayId } = useDesignStore();
  const shapeRef = useRef<Konva.Rect>(null);

  const isSelected = selectedTrayId === layout.trayId;

  // Snap to grid (5mm for box level)
  const snapToGrid = (val: number) => Math.round(val / 5) * 5;

  const handleDragEnd = (e: Konva.KonvaEventObject<DragEvent>) => {
    const newX = snapToGrid(e.target.x() / scale);
    const newY = snapToGrid(e.target.y() / scale);

    // Clamp within box bounds
    const clampedX = Math.max(0, Math.min(newX, boxWidth - layout.boxWidth));
    const clampedY = Math.max(0, Math.min(newY, boxLength - layout.boxLength));

    updateTrayLayout(layout.trayId, { boxX: clampedX, boxY: clampedY });
  };

  const handleDoubleClick = () => {
    enterTrayView(layout.trayId);
  };

  return (
    <Group>
      <Rect
        ref={shapeRef}
        x={layout.boxX * scale}
        y={layout.boxY * scale}
        width={layout.boxWidth * scale}
        height={layout.boxLength * scale}
        fill="#E0F2FE"
        opacity={0.8}
        stroke={isSelected ? '#2563EB' : '#0369A1'}
        strokeWidth={isSelected ? 3 : 2}
        draggable
        onDragEnd={handleDragEnd}
        onClick={() => setSelectedTrayId(layout.trayId)}
        onTap={() => setSelectedTrayId(layout.trayId)}
        onDblClick={handleDoubleClick}
        onDblTap={handleDoubleClick}
      />

      {/* Tray name */}
      <Text
        x={layout.boxX * scale + 8}
        y={layout.boxY * scale + 8}
        text={tray?.name || layout.trayId}
        fontSize={14}
        fontStyle="bold"
        fill="#0369A1"
        listening={false}
      />

      {/* Component count + height */}
      <Text
        x={layout.boxX * scale + 8}
        y={layout.boxY * scale + 28}
        text={`${layout.compartments.length} compartments • ${tray?.estimated_height_mm || 0}mm tall`}
        fontSize={11}
        fill="#0C4A6E"
        listening={false}
      />

      {/* Dimensions */}
      <Text
        x={layout.boxX * scale + 8}
        y={layout.boxY * scale + (layout.boxLength * scale) - 24}
        text={`${Math.round(layout.boxWidth)}×${Math.round(layout.boxLength)}mm`}
        fontSize={10}
        fill="#64748B"
        listening={false}
      />
    </Group>
  );
}
