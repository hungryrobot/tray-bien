/**
 * Main App component for Tray Bien v3 - Phase 2.
 * 4-step wizard for designing board game inserts.
 */

import { useState } from 'react';
import { WizardShell } from './components/wizard/WizardShell';
import { Settings } from './components/Settings';
import { useDesignStore } from './store/designStore';

function App() {
  const [showSettings, setShowSettings] = useState(false);
  const { resetWizard, designName } = useDesignStore();

  const handleNewDesign = () => {
    if (confirm('Start a new design? This will clear your current work.')) {
      resetWizard();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-3xl font-bold text-gray-900">
                🎲 Tray Bien <span className="text-blue-600">v3</span>
              </h1>
              {designName && (
                <span className="text-sm text-gray-500">
                  • {designName}
                </span>
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleNewDesign}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700
                  transition-colors duration-200 text-sm font-medium"
              >
                ➕ New Design
              </button>
              <button
                onClick={() => setShowSettings(true)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300
                  transition-colors duration-200 text-sm font-medium"
                title="Settings"
              >
                ⚙️ Settings
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Wizard */}
      <WizardShell onOpenSettings={() => setShowSettings(true)} />

      {/* Settings Modal */}
      {showSettings && <Settings onClose={() => setShowSettings(false)} />}

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-500">
          <p>
            Tray Bien v3 • Built with React, TypeScript, Tailwind CSS, and FastAPI
          </p>
          <p className="mt-1">
            Phase 2: 4-Step Wizard with Component Management
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
