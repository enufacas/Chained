import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

// Parse JSON bodies for API endpoints
app.use(express.json());

// Environment variables with defaults
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || 'https://chained-adk-api-server-sguacxy5gq-uc.a.run.app';
const AG_UI_FRONTEND_URL = process.env.AG_UI_FRONTEND_URL || 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app';

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

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'dist')));

// Inject environment variables into index.html
app.get('/', (req, res) => {
  const indexPath = path.join(__dirname, 'dist', 'index.html');
  
  if (!fs.existsSync(indexPath)) {
    return res.status(500).send('Build not found. Please run npm run build first.');
  }

  let html = fs.readFileSync(indexPath, 'utf8');
  
  // Inject environment variables as a script tag before the closing head
  const envScript = `
    <script>
      window.ENV = {
        ADK_API_URL: '${ADK_API_URL}',
        AG_UI_FRONTEND_URL: '${AG_UI_FRONTEND_URL}'
      };
    </script>
  `;
  
  html = html.replace('</head>', `${envScript}</head>`);
  
  res.setHeader('Content-Type', 'text/html');
  res.send(html);
});

// Fallback to index.html for SPA routing
app.get('*', (req, res) => {
  const indexPath = path.join(__dirname, 'dist', 'index.html');
  
  if (fs.existsSync(indexPath)) {
    let html = fs.readFileSync(indexPath, 'utf8');
    
    const envScript = `
      <script>
        window.ENV = {
          ADK_API_URL: '${ADK_API_URL}',
          AG_UI_FRONTEND_URL: '${AG_UI_FRONTEND_URL}'
        };
      </script>
    `;
    
    html = html.replace('</head>', `${envScript}</head>`);
    res.setHeader('Content-Type', 'text/html');
    res.send(html);
  } else {
    res.status(404).send('Not found');
  }
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
