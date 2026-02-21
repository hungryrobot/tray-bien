/**
 * API client for Tray Bien backend.
 */

import axios from 'axios';
import type { ExtractionResult, ApiResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 minutes for AI extraction
});

/**
 * Extract components from a PDF rulebook.
 *
 * @param file - PDF file to upload
 * @param provider - AI provider ('gemini', 'claude', 'openai', 'ollama')
 * @param apiKey - Optional API key (if not provided, uses backend settings)
 * @returns Extracted component data
 */
export async function extractComponents(
  file: File,
  provider: string,
  apiKey?: string
): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('provider', provider);
  if (apiKey) {
    formData.append('api_key', apiKey);
  }

  const response = await api.post<ApiResponse<ExtractionResult>>(
    '/extract',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Extraction failed');
  }

  return response.data.data;
}
