import { useState } from 'react';
import { useDesignStore } from '../../../store/designStore';
import { extractComponents } from '../../../api/client';

interface Props {
  onExtractionComplete: () => void;
  onOpenSettings: () => void;
}

type Provider = 'gemini' | 'claude' | 'openai' | 'ollama';

export function PDFExtraction({ onExtractionComplete, onOpenSettings }: Props) {
  const { setPdfExtractionResult, setBoxConfig } = useDesignStore();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get configured provider and API key from Settings
  const getConfiguredProvider = (): { provider: Provider; hasKey: boolean; apiKey?: string } => {
    const lastProvider = (localStorage.getItem('tray-bien-last-provider') || 'gemini') as Provider;

    // Get API keys from Settings format
    try {
      const apiKeysJson = localStorage.getItem('tray-bien-api-keys');
      if (apiKeysJson) {
        const apiKeys = JSON.parse(apiKeysJson);
        const apiKey = apiKeys[lastProvider];
        return {
          provider: lastProvider,
          hasKey: lastProvider === 'ollama' || !!apiKey,
          apiKey: apiKey || undefined,
        };
      }
    } catch (e) {
      console.error('Failed to load API keys:', e);
    }

    return {
      provider: lastProvider,
      hasKey: lastProvider === 'ollama',
      apiKey: undefined,
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const { provider, apiKey } = getConfiguredProvider();
      const result = await extractComponents(file, provider, apiKey);

      // Store extraction result
      setPdfExtractionResult(result);

      // Auto-populate box config if game name is available
      if (result.game_name) {
        setBoxConfig({ gameName: result.game_name });
      }

      // Trigger Quick Defaults modal
      onExtractionComplete();
    } catch (err: any) {
      setError(err.message || 'Failed to extract components');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setFile(selectedFile || null);
    setError(null);
  };

  const { provider, hasKey } = getConfiguredProvider();

  const providerLabels: Record<Provider, string> = {
    gemini: 'Google Gemini',
    claude: 'Anthropic Claude',
    openai: 'OpenAI',
    ollama: 'Ollama (Local)',
  };

  const canSubmit = file && hasKey;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Extract Components from PDF
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* File Upload */}
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

        {/* Provider Status (read-only) */}
        <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">AI Provider</p>
              <p className="text-lg font-semibold text-gray-900">{providerLabels[provider]}</p>
            </div>

            <button
              type="button"
              onClick={onOpenSettings}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Change in Settings
            </button>
          </div>

          {/* API Key Status */}
          <div className="mt-2">
            {provider === 'ollama' ? (
              <p className="text-sm text-gray-600">
                ℹ️ No API key required for local Ollama
              </p>
            ) : hasKey ? (
              <p className="text-sm text-green-600">
                ✓ API key configured
              </p>
            ) : (
              <div className="flex items-center gap-2">
                <p className="text-sm text-orange-600">
                  ⚠️ No API key configured for {provider}
                </p>
                <button
                  type="button"
                  onClick={onOpenSettings}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  Configure Now
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
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
            'Extract Components from PDF'
          )}
        </button>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-100 border border-red-300 rounded text-sm text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}

        {!hasKey && file && provider !== 'ollama' && (
          <p className="text-sm text-orange-600 text-center">
            Please configure your {provider} API key in Settings first
          </p>
        )}
      </form>
    </div>
  );
}
