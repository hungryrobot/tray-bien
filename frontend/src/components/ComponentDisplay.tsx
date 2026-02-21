/**
 * Component display for extracted game components.
 */

import type { ExtractionResult } from '../types';

interface Props {
  result: ExtractionResult;
}

export function ComponentDisplay({ result }: Props) {
  const hasPlayerCount = result.player_count.min || result.player_count.max;

  return (
    <div className="space-y-6">
      {/* Game metadata header */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {result.game_name || 'Board Game Components'}
        </h2>
        {hasPlayerCount && (
          <p className="text-sm text-gray-700">
            <span className="font-medium">Players:</span>{' '}
            {result.player_count.min === result.player_count.max
              ? result.player_count.min
              : `${result.player_count.min || '?'}-${result.player_count.max || '?'}`}
          </p>
        )}
        {result.factions_or_colors.length > 0 && (
          <p className="text-sm text-gray-700 mt-1">
            <span className="font-medium">Factions/Colors:</span>{' '}
            {result.factions_or_colors.join(', ')}
          </p>
        )}
      </div>

      {/* Extraction notes */}
      {result.extraction_notes && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">{result.extraction_notes}</p>
            </div>
          </div>
        </div>
      )}

      {/* Component groups */}
      <div className="space-y-4">
        {result.component_groups.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center">
            <p className="text-gray-600">No components extracted</p>
          </div>
        ) : (
          result.component_groups.map((group, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Group header */}
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  {group.group_name}
                  <span className="ml-2 text-sm font-normal text-gray-500">
                    ({group.group_type}
                    {group.per_player && ', per player'}
                    {group.identical_sets && ', identical sets'})
                  </span>
                </h3>
                {group.notes && (
                  <p className="text-sm text-gray-600 mt-1">{group.notes}</p>
                )}
              </div>

              {/* Components table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Quantity
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Notes
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {group.components.map((comp) => (
                      <tr key={comp.extraction_index} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {comp.name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {comp.type}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {comp.quantity}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {comp.notes || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Metadata footer */}
      {result.metadata.tokens_used && (
        <div className="text-sm text-gray-500 text-right">
          Tokens used: {result.metadata.tokens_used.total_tokens.toLocaleString()} • Provider:{' '}
          {result.metadata.provider}
        </div>
      )}
    </div>
  );
}
