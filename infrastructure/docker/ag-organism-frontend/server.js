const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Environment variables with defaults
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || 'https://chained-adk-api-server-sguacxy5gq-uc.a.run.app';
const AG_UI_FRONTEND_URL = process.env.AG_UI_FRONTEND_URL || 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app';

// Load the HTML template
const htmlTemplate = fs.readFileSync(path.join(__dirname, 'public', 'ag-organism.html'), 'utf8');

// Inject environment variables into HTML
function injectEnvVars(html) {
  return html
    .replace(
      /const API_BASE_URL = window\.location\.hostname === 'localhost'.*?\n.*?:\s*'[^']+';/s,
      `const API_BASE_URL = '${AG_UI_FRONTEND_URL}/api';`
    )
    .replace(
      '<!-- ENV_INJECTED -->',
      `<script>
        // Environment variables injected by server
        window.ENV = {
          ADK_API_URL: '${ADK_API_URL}',
          AG_UI_FRONTEND_URL: '${AG_UI_FRONTEND_URL}'
        };
      </script>`
    );
}

// Serve static files
app.use('/assets', express.static(path.join(__dirname, 'public', 'assets')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'ag-organism-frontend' });
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
});
