// frontend/js/api.js
// All HTTP calls to the FastAPI backend.

const BASE_URL = window.location.origin;

/**
 * Send a question to the RAG pipeline.
 * @param {string} query
 * @returns {Promise<{answer: string, key_points: string[], sources: {title:string, url:string}[], error: string|null, backend: string}>}
 */
export async function askQuestion(query) {
  const response = await fetch(`${BASE_URL}/api/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

/**
 * Clear all conversation memory.
 * @returns {Promise<void>}
 */
export async function clearMemory() {
  const response = await fetch(`${BASE_URL}/api/clear`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to clear memory');
}

/**
 * Get current conversation history.
 * @returns {Promise<{role: string, content: string}[]>}
 */
export async function getHistory() {
  const response = await fetch(`${BASE_URL}/api/history`);
  if (!response.ok) throw new Error('Failed to fetch history');
  return response.json();
}

/**
 * Get backend status / health.
 * @returns {Promise<{status: string, backend: string, memory: number}>}
 */
export async function getStatus() {
  const response = await fetch(`${BASE_URL}/api/status`);
  if (!response.ok) throw new Error('Failed to fetch status');
  return response.json();
}
