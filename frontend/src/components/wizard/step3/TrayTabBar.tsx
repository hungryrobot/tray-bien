import type { TrayLayout, Tray } from '../../../types';

interface TrayTabBarProps {
  layouts: TrayLayout[];
  trays: Tray[];
  selectedTrayId: string | null;
  onSelect: (trayId: string) => void;
}

export function TrayTabBar({ layouts, trays, selectedTrayId, onSelect }: TrayTabBarProps) {
  return (
    <div className="flex gap-2 border-b border-gray-200 pb-0">
      {layouts.map(layout => {
        const tray = trays.find(t => t.tray_id === layout.trayId);
        const isActive = layout.trayId === selectedTrayId;

        return (
          <button
            key={layout.trayId}
            onClick={() => onSelect(layout.trayId)}
            className={`px-4 py-2 rounded-t text-sm font-medium transition-colors duration-200 ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tray?.name || layout.trayId}
            <span className="ml-2 text-xs opacity-75">
              ({layout.compartments.length})
            </span>
          </button>
        );
      })}
    </div>
  );
}
