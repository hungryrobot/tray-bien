import { useRef, useEffect } from 'react';
import { Rect, Text, Group, Transformer } from 'react-konva';
import Konva from 'konva';
import type { Compartment } from '../../../types';
import { useDesignStore } from '../../../store/designStore';

interface CompartmentRectProps {
  compartment: Compartment;
  scale: number;
  trayId: string;
  trayWidth: number;   // mm — inner usable width
  trayLength: number;  // mm — inner usable length
}

export function CompartmentRect({
  compartment,
  scale,
  trayId,
  trayWidth,
  trayLength,
}: CompartmentRectProps) {
  const { updateCompartment, selectedCompartmentId, setSelectedCompartmentId } = useDesignStore();
  const shapeRef = useRef<Konva.Rect>(null);
  const trRef = useRef<Konva.Transformer>(null);

  const isSelected = selectedCompartmentId === compartment.id;

  // Snap to 1mm grid
  const snapToGrid = (val: number) => Math.round(val);

  const handleDragEnd = (e: Konva.KonvaEventObject<DragEvent>) => {
    const newX = snapToGrid(e.target.x() / scale);
    const newY = snapToGrid(e.target.y() / scale);

    // Clamp within tray bounds
    const clampedX = Math.max(0, Math.min(newX, trayWidth - compartment.width));
    const clampedY = Math.max(0, Math.min(newY, trayLength - compartment.length));

    updateCompartment(trayId, compartment.id, { x: clampedX, y: clampedY });
  };

  const handleTransformEnd = () => {
    const node = shapeRef.current;
    if (!node) return;

    const scaleX = node.scaleX();
    const scaleY = node.scaleY();

    // Reset scale and apply to width/length
    node.scaleX(1);
    node.scaleY(1);

    const newWidth = snapToGrid(
      Math.max(compartment.minWidth, (node.width() * scaleX) / scale)
    );
    const newLength = snapToGrid(
      Math.max(compartment.minLength, (node.height() * scaleY) / scale)
    );

    updateCompartment(trayId, compartment.id, {
      x: snapToGrid(node.x() / scale),
      y: snapToGrid(node.y() / scale),
      width: newWidth,
      length: newLength,
    });
  };

  // Attach transformer when selected
  useEffect(() => {
    if (isSelected && trRef.current && shapeRef.current) {
      trRef.current.nodes([shapeRef.current]);
      trRef.current.getLayer()?.batchDraw();
    }
  }, [isSelected]);

  return (
    <>
      <Group>
        <Rect
          ref={shapeRef}
          x={compartment.x * scale}
          y={compartment.y * scale}
          width={compartment.width * scale}
          height={compartment.length * scale}
          fill={compartment.color}
          opacity={0.7}
          stroke={isSelected ? '#2563EB' : '#374151'}
          strokeWidth={isSelected ? 2 : 1}
          draggable
          onDragEnd={handleDragEnd}
          onClick={() => setSelectedCompartmentId(compartment.id)}
          onTap={() => setSelectedCompartmentId(compartment.id)}
        />

        {/* Component name label */}
        <Text
          x={compartment.x * scale + 4}
          y={compartment.y * scale + 4}
          text={compartment.name}
          fontSize={11}
          fill="#1F2937"
          width={(compartment.width * scale) - 8}
          wrap="word"
          listening={false}
        />

        {/* Dimensions label */}
        <Text
          x={compartment.x * scale + 4}
          y={compartment.y * scale + (compartment.length * scale) - 18}
          text={`${compartment.width}×${compartment.length}mm`}
          fontSize={9}
          fill="#6B7280"
          listening={false}
        />
      </Group>

      {/* Resize transformer (when selected) */}
      {isSelected && (
        <Transformer
          ref={trRef}
          boundBoxFunc={(oldBox, newBox) => {
            // Enforce minimum size
            if (
              newBox.width < compartment.minWidth * scale ||
              newBox.height < compartment.minLength * scale
            ) {
              return oldBox;
            }
            return newBox;
          }}
          onTransformEnd={handleTransformEnd}
          rotateEnabled={false}
          keepRatio={false}
        />
      )}
    </>
  );
}
