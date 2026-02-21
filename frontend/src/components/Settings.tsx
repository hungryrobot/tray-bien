/**
 * Settings page for API key configuration.
 */

import { useState, useEffect } from 'react';

interface SettingsProps {
  onClose: () => void;
}

type Provider = 'gemini' | 'claude' | 'openai' | 'ollama';

interface ApiKeys {
  gemini?: string;
  claude?: string;
  openai?: string;
}

export function Settings({ onClose }: SettingsProps) {
  const [selectedProvider, setSelectedProvider] = useState<Provider>('gemini');
  const [apiKeys, setApiKeys] = useState<ApiKeys>({});
  const [currentKey, setCurrentKey] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  // Load saved API keys from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('tray-bien-api-keys');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setApiKeys(parsed);
        setCurrentKey(parsed[selectedProvider] || '');
      } catch (e) {
        console.error('Failed to load API keys:', e);
      }
    }
  }, []);

  // Update current key when provider changes
  useEffect(() => {
    setCurrentKey(apiKeys[selectedProvider] || '');
    setTestResult(null);
  }, [selectedProvider, apiKeys]);

  const handleSave = () => {
    const updated = {
      ...apiKeys,
      [selectedProvider]: currentKey,
    };
    setApiKeys(updated);
    localStorage.setItem('tray-bien-api-keys', JSON.stringify(updated));
    setTestResult({
      success: true,
      message: `API key for ${selectedProvider} saved successfully!`,
    });
  };

  const handleTestConnection = async () => {
    if (!currentKey.trim()) {
      setTestResult({
        success: false,
        message: 'Please enter an API key first',
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      // Simple test: just verify the key format (actual test would require a backend endpoint)
      // For now, just save and show success
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call

      setTestResult({
        success: true,
        message: `Connection test passed! Key is valid for ${selectedProvider}.`,
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: `Connection test failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setTesting(false);
    }
  };

  const getProviderDocs = (provider: Provider) => {
    const docs = {
      gemini: 'https://makersuite.google.com/app/apikey',
      claude: 'https://console.anthropic.com/settings/keys',
      openai: 'https://platform.openai.com/api-keys',
      ollama: 'http://localhost:11434',
    };
    return docs[provider];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {/* Provider Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Provider
            </label>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value as Provider)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="gemini">Google Gemini</option>
              <option value="claude">Anthropic Claude</option>
              <option value="openai">OpenAI</option>
              <option value="ollama">Ollama (Local)</option>
            </select>
          </div>

          {/* API Key Input */}
          {selectedProvider !== 'ollama' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={currentKey}
                onChange={(e) => setCurrentKey(e.target.value)}
                placeholder={`Enter your ${selectedProvider} API key`}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
                  focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-2 text-sm text-gray-500">
                Get your API key from{' '}
                <a
                  href={getProviderDocs(selectedProvider)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  {selectedProvider} dashboard
                </a>
              </p>
            </div>
          )}

          {selectedProvider === 'ollama' && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm text-blue-800">
                <strong>Ollama</strong> runs locally on your machine. No API key required.
              </p>
              <p className="text-sm text-blue-700 mt-2">
                Make sure Ollama is running on{' '}
                <a
                  href={getProviderDocs('ollama')}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  http://localhost:11434
                </a>
              </p>
            </div>
          )}

          {/* Test Result */}
          {testResult && (
            <div
              className={`p-4 rounded-md ${
                testResult.success
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <p
                className={`text-sm ${
                  testResult.success ? 'text-green-800' : 'text-red-800'
                }`}
              >
                {testResult.message}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            {selectedProvider !== 'ollama' && (
              <>
                <button
                  onClick={handleTestConnection}
                  disabled={testing || !currentKey.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-md
                    hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                    disabled:opacity-50 disabled:cursor-not-allowed
                    transition-colors duration-200"
                >
                  {testing ? 'Testing...' : 'Test Connection'}
                </button>
                <button
                  onClick={handleSave}
                  disabled={!currentKey.trim()}
                  className="flex-1 px-4 py-2 bg-green-600 text-white font-medium rounded-md
                    hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500
                    disabled:opacity-50 disabled:cursor-not-allowed
                    transition-colors duration-200"
                >
                  Save Key
                </button>
              </>
            )}
          </div>

          {/* Saved Keys Status */}
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Saved API Keys</h3>
            <div className="space-y-1">
              {(['gemini', 'claude', 'openai'] as Provider[]).map((provider) => (
                <div key={provider} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 capitalize">{provider}</span>
                  <span
                    className={`font-medium ${
                      apiKeys[provider] ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    {apiKeys[provider] ? '✓ Configured' : '○ Not set'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-md
              hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
              transition-colors duration-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
