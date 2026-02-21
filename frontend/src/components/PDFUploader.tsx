/**
 * PDF upload component with provider selection.
 */

import { useState, useEffect } from 'react';

interface Props {
  onUpload: (file: File, provider: string) => void;
  onOpenSettings: () => void;
  loading: boolean;
  hasApiKey: (provider: string) => boolean;
}

export function PDFUploader({ onUpload, onOpenSettings, loading, hasApiKey }: Props) {
  const [file, setFile] = useState<File | null>(null);

  // Load last selected provider from localStorage
  const getInitialProvider = () => {
    const saved = localStorage.getItem('tray-bien-last-provider');
    return saved || 'gemini';
  };

  const [provider, setProvider] = useState(getInitialProvider);

  // Save provider selection to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('tray-bien-last-provider', provider);
  }, [provider]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      onUpload(file, provider);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setFile(selectedFile || null);
  };

  const providerHasKey = hasApiKey(provider);
  const canSubmit = file && (provider === 'ollama' || providerHasKey);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Rulebook PDF
        </label>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100
            disabled:opacity-50"
          disabled={loading}
        />
        {file && (
          <p className="mt-2 text-sm text-gray-600">
            Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          AI Provider
        </label>
        <select
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
            focus:outline-none focus:ring-blue-500 focus:border-blue-500
            disabled:opacity-50 disabled:bg-gray-100"
          disabled={loading}
        >
          <option value="gemini">Google Gemini</option>
          <option value="claude">Anthropic Claude</option>
          <option value="openai">OpenAI</option>
          <option value="ollama">Ollama (Local)</option>
        </select>

        {/* API Key Status */}
        <div className="mt-2">
          {provider === 'ollama' ? (
            <p className="text-sm text-gray-600">
              ℹ️ No API key required for local Ollama
            </p>
          ) : providerHasKey ? (
            <p className="text-sm text-green-600">
              ✓ API key configured for {provider}
            </p>
          ) : (
            <div className="flex items-center gap-2">
              <p className="text-sm text-orange-600">
                ⚠️ No API key configured
              </p>
              <button
                type="button"
                onClick={onOpenSettings}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                Configure in Settings
              </button>
            </div>
          )}
        </div>
      </div>

      <button
        type="submit"
        disabled={!canSubmit || loading}
        className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-md
          hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors duration-200"
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Extracting Components...
          </span>
        ) : (
          'Extract Components'
        )}
      </button>

      {!canSubmit && file && provider !== 'ollama' && !providerHasKey && (
        <p className="text-sm text-orange-600 text-center">
          Please configure your {provider} API key in Settings first
        </p>
      )}
    </form>
  );
}
