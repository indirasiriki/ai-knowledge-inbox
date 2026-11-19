// Centralized API fetch wrapper: translates non-2xx HTTP responses into catchable Errors
async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      accept: 'application/json',
      ...(options.body ? { 'content-type': 'application/json' } : {}),
      ...options.headers,
    },
  });

  // 204 No Content (e.g. DELETE) has no response body
  if (response.status === 204) return null;

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return payload;
}

// Check backend server readiness and API key status
export function fetchHealth() {
  return request('/api/health');
}

// Retrieve list of saved notes and URLs
export function fetchItems() {
  return request('/api/items');
}

// Ingest a new note or URL
export function createItem(body) {
  return request('/api/items', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

// Delete a saved item and its chunks by ID
export function removeItem(id) {
  return request(`/api/items/${encodeURIComponent(id)}`, { method: 'DELETE' });
}

// Query the knowledge base with a natural language question
export function askQuestion(question) {
  return request('/api/questions', {
    method: 'POST',
    body: JSON.stringify({ question }),
  });
}
