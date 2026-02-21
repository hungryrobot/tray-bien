import { useDesignStore } from '../../../store/designStore';

interface AutoPackButtonProps {
  trayId: string;
}

export function AutoPackButton({ trayId }: AutoPackButtonProps) {
  const { autoPackTray } = useDesignStore();

  return (
    <button
      onClick={() => autoPackTray(trayId)}
      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium
        transition-colors duration-200"
      title="Auto-arrange compartments using shelf-packing algorithm"
    >
      🔄 Auto-Pack
    </button>
  );
}
