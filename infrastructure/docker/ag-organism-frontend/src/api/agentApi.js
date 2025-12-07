// AG-UI Backend API URL configuration
const getApiBaseUrl = () => {
  // Use injected env var if available, otherwise fallback
  if (window.ENV?.AG_UI_FRONTEND_URL) {
    return `${window.ENV.AG_UI_FRONTEND_URL}/api`;
  }
  
  // Fallback based on environment
  if (import.meta.env.DEV || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:3000/api';
  }
  
  return 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api';
};

export const API_BASE_URL = getApiBaseUrl();

export async function loadAgents() {
  const response = await fetch(`${API_BASE_URL}/registry`);
  if (!response.ok) {
    throw new Error(`Failed to load agents: ${response.statusText}`);
  }
  const data = await response.json();
  return data.agents || [];
}

export async function executePipeline(topic, agents) {
  const response = await fetch(`${API_BASE_URL}/pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, agents }),
  });
  
  if (!response.ok) {
    throw new Error(`Pipeline failed: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.pipeline;
}

export async function getPipelineStatus(pipelineId) {
  const response = await fetch(`${API_BASE_URL}/pipeline?id=${pipelineId}`);
  if (!response.ok) {
    throw new Error(`Failed to get pipeline status: ${response.statusText}`);
  }
  const data = await response.json();
  return data.pipeline;
}

export async function logError(error, type, context = {}) {
  const errorData = {
    type: type || 'generic',
    timestamp: new Date().toISOString(),
    error: {
      name: error.name || 'Error',
      message: error.message || String(error),
      stack: error.stack || ''
    },
    url: window.location.href,
    userAgent: navigator.userAgent,
    context: context
  };
  
  console.error(`[${errorData.timestamp}] [Frontend Error] [${errorData.type}]`, errorData);
  
  try {
    await fetch('/api/log-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorData)
    });
  } catch (err) {
    console.warn('[Frontend Error] Failed to send error to backend:', err);
  }
}
