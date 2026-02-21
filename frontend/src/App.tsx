/**
 * Main App component for Tray Bien v3.
 */

import { useState } from 'react';
import { PDFUploader } from './components/PDFUploader';
import { ComponentDisplay } from './components/ComponentDisplay';
import { extractComponents } from './api/client';
import type { ExtractionResult } from './types';

function App() {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File, provider: string, apiKey?: string) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log(`Uploading ${file.name} to ${provider}...`);
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
          <h1 className="text-5xl font-bold text-gray-900 mb-2">
            🎲 Tray Bien <span className="text-blue-600">v3</span>
          </h1>
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
          <PDFUploader onUpload={handleUpload} loading={loading} />
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
    </div>
  );
}

export default App;
