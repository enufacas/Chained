const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Parse JSON bodies for API endpoints
app.use(express.json());

// Environment variables with defaults
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || 'https://chained-adk-api-server-sguacxy5gq-uc.a.run.app';
const AG_UI_FRONTEND_URL = process.env.AG_UI_FRONTEND_URL || 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app';

// Load the HTML template
const htmlTemplate = fs.readFileSync(path.join(__dirname, 'public', 'ag-organism.html'), 'utf8');

// Inject environment variables into HTML
function injectEnvVars(html) {
  // Simple string replacement for the env injection placeholder
  const envScript = `<script>
        // Environment variables injected by server
        window.ENV = {
          ADK_API_URL: '${ADK_API_URL}',
          AG_UI_FRONTEND_URL: '${AG_UI_FRONTEND_URL}'
        };
      </script>`;
  
  return html.replace('<!-- ENV_INJECTED -->', envScript);
}

// Serve static files
app.use('/assets', express.static(path.join(__dirname, 'public', 'assets')));

// Serve Three.js from node_modules
app.use('/vendor/three', express.static(path.join(__dirname, 'node_modules', 'three')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'ag-organism-frontend' });
});

// Error logging endpoint - receives frontend errors and logs them to GCP
app.post('/api/log-error', (req, res) => {
  const errorData = req.body;
  
  // Log with structured format for GCP Cloud Logging
  console.error('[FRONTEND_ERROR]', JSON.stringify({
    severity: 'ERROR',
    type: errorData.type,
    timestamp: errorData.timestamp,
    error: errorData.error,
    url: errorData.url,
    userAgent: errorData.userAgent,
    context: errorData.context,
    service: 'ag-organism-frontend'
  }));
  
  res.status(200).json({ status: 'logged' });
});

// Main route - serve the HTML with injected environment variables
app.get('/', (req, res) => {
  const injectedHtml = injectEnvVars(htmlTemplate);
  res.setHeader('Content-Type', 'text/html');
  res.send(injectedHtml);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`AG-Organism Frontend running on port ${PORT}`);
  console.log(`ADK_API_URL: ${ADK_API_URL}`);
  console.log(`AG_UI_FRONTEND_URL: ${AG_UI_FRONTEND_URL}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  
  // Log startup information for debugging
  console.log('[STARTUP]', JSON.stringify({
    severity: 'INFO',
    service: 'ag-organism-frontend',
    port: PORT,
    nodeVersion: process.version,
    config: {
      adkApiUrl: ADK_API_URL,
      agUiFrontendUrl: AG_UI_FRONTEND_URL
    }
  }));
});
