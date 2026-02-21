import { Line } from 'react-konva';

interface CanvasGridProps {
  width: number;     // mm
  height: number;    // mm
  scale: number;     // pixels per mm
  interval?: number; // mm between grid lines
}

export function CanvasGrid({ width, height, scale, interval = 10 }: CanvasGridProps) {
  const lines = [];

  // Vertical lines
  for (let x = 0; x <= width; x += interval) {
    lines.push(
      <Line
        key={`v-${x}`}
        points={[x * scale, 0, x * scale, height * scale]}
        stroke="#E5E7EB"
        strokeWidth={0.5}
        dash={[2, 4]}
        listening={false}
      />
    );
  }

  // Horizontal lines
  for (let y = 0; y <= height; y += interval) {
    lines.push(
      <Line
        key={`h-${y}`}
        points={[0, y * scale, width * scale, y * scale]}
        stroke="#E5E7EB"
        strokeWidth={0.5}
        dash={[2, 4]}
        listening={false}
      />
    );
  }

  return <>{lines}</>;
}
