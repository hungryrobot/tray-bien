/**
 * Main App component for Tray Bien v3.
 */

import { useState } from 'react';
import { PDFUploader } from './components/PDFUploader';
import { ComponentDisplay } from './components/ComponentDisplay';
import { Settings } from './components/Settings';
import { extractComponents } from './api/client';
import type { ExtractionResult } from './types';

function App() {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const getApiKey = (provider: string): string | undefined => {
    try {
      const saved = localStorage.getItem('tray-bien-api-keys');
      if (saved) {
        const keys = JSON.parse(saved);
        return keys[provider];
      }
    } catch (e) {
      console.error('Failed to load API key:', e);
    }
    return undefined;
  };

  const hasApiKey = (provider: string): boolean => {
    const key = getApiKey(provider);
    return !!key && key.trim().length > 0;
  };

  const handleUpload = async (file: File, provider: string) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log(`Uploading ${file.name} to ${provider}...`);

      // Get API key from localStorage
      const apiKey = getApiKey(provider);
      console.log(`API key loaded from localStorage: ${!!apiKey}`);

      const data = await extractComponents(file, provider, apiKey);
      console.log('Extraction successful:', data);
      setResult(data);
    } catch (err) {
      console.error('Extraction error:', err);
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-4 mb-2">
            <h1 className="text-5xl font-bold text-gray-900">
              🎲 Tray Bien <span className="text-blue-600">v3</span>
            </h1>
            <button
              onClick={() => setShowSettings(true)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300
                transition-colors duration-200 text-sm font-medium"
              title="Settings"
            >
              ⚙️ Settings
            </button>
          </div>
          <p className="text-xl text-gray-600 italic">
            AI-Powered Component Extraction
          </p>
          <p className="text-sm text-gray-500 mt-2">
            React + FastAPI • Phase 1 MVP
          </p>
        </div>

        {/* Upload Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Extract Components from PDF
          </h2>
          <PDFUploader
            onUpload={handleUpload}
            onOpenSettings={() => setShowSettings(true)}
            loading={loading}
            hasApiKey={hasApiKey}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Extraction Failed</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <ComponentDisplay result={result} />
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>
            Tray Bien v3 • Built with React, TypeScript, Tailwind CSS, and FastAPI
          </p>
          <p className="mt-1">
            Phase 1: PDF Upload & Component Extraction
          </p>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && <Settings onClose={() => setShowSettings(false)} />}
    </div>
  );
}

export default App;
