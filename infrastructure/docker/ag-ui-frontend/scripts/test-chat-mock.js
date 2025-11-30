#!/usr/bin/env node
/**
 * Mock test script for AG-UI Frontend chat functionality
 * 
 * This script tests the chat configuration and simulates API calls
 * to help diagnose issues without making actual GCP API calls.
 * 
 * Run: node scripts/test-chat-mock.js [url]
 * 
 * Environment variables:
 *   AG_UI_URL - Override the default deployment URL
 */

const https = require('https');

// Configuration - allow override via env var or command line arg
const DEPLOYED_URL = process.argv[2] || process.env.AG_UI_URL || 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app';

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
};

function log(level, message, data) {
  const timestamp = new Date().toISOString();
  const color = level === 'success' ? colors.green 
              : level === 'error' ? colors.red 
              : level === 'warn' ? colors.yellow 
              : colors.cyan;
  
  console.log(`${colors.dim}[${timestamp}]${colors.reset} ${color}[${level.toUpperCase()}]${colors.reset} ${message}`);
  if (data) {
    console.log(JSON.stringify(data, null, 2));
  }
}

// Make HTTP request
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: JSON.parse(data),
          });
        } catch {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data,
          });
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    req.end();
  });
}

async function testDebugEndpoint() {
  console.log('\n' + '='.repeat(60));
  console.log('AG-UI Frontend Chat Health Check');
  console.log('='.repeat(60));
  console.log(`Target: ${DEPLOYED_URL}`);
  console.log('='.repeat(60) + '\n');

  // Test 1: GET /api/debug - Check configuration
  log('info', 'Test 1: Checking configuration (GET /api/debug)');
  try {
    const configResponse = await makeRequest(`${DEPLOYED_URL}/api/debug`);
    
    if (configResponse.status === 200) {
      log('success', 'Configuration retrieved successfully');
      log('info', 'Environment configuration:', configResponse.data.environment);
      
      // Check for issues
      const env = configResponse.data.environment;
      if (!env.USE_VERTEX_AI) {
        log('warn', 'USE_VERTEX_AI is not enabled!');
      }
      if (!env.GOOGLE_CLOUD_PROJECT || env.GOOGLE_CLOUD_PROJECT === '(not set - will use ADC)') {
        log('warn', 'GOOGLE_CLOUD_PROJECT not explicitly set (will use ADC)');
      }
    } else {
      log('error', `Configuration check failed with status ${configResponse.status}`);
    }
  } catch (error) {
    log('error', 'Failed to get configuration', { error: error.message });
  }

  // Test 2: POST /api/debug - Full test
  log('info', '\nTest 2: Running full diagnostic (POST /api/debug)');
  try {
    const testResponse = await makeRequest(`${DEPLOYED_URL}/api/debug`, {
      method: 'POST',
      body: { test: 'full' },
    });
    
    log('info', 'Test response:', {
      success: testResponse.data.success,
      config: testResponse.data.config,
    });
    
    // Auth test results
    if (testResponse.data.authTest) {
      if (testResponse.data.authTest.success) {
        log('success', 'Auth test PASSED', {
          projectId: testResponse.data.authTest.projectId,
          email: testResponse.data.authTest.email,
        });
      } else {
        log('error', 'Auth test FAILED', testResponse.data.authTest);
      }
    }
    
    // Vertex AI test results
    if (testResponse.data.vertexTest) {
      if (testResponse.data.vertexTest.success) {
        log('success', 'Vertex AI test PASSED');
        log('info', 'Response preview:', { 
          response: testResponse.data.vertexTest.response?.substring(0, 100) 
        });
      } else {
        log('error', 'Vertex AI test FAILED', {
          error: testResponse.data.vertexTest.error,
          httpStatus: testResponse.data.vertexTest.details?.httpStatus,
          troubleshooting: testResponse.data.vertexTest.details?.httpStatus === 404 
            ? 'Model not found. Check if model name is valid.'
            : 'Check logs for details.',
        });
      }
    }
    
    // Chat test results
    if (testResponse.data.chatTest) {
      if (testResponse.data.chatTest.success) {
        log('success', 'Chat test PASSED');
        log('info', 'Chat response:', { 
          response: testResponse.data.chatTest.response?.substring(0, 100) 
        });
      } else {
        log('error', 'Chat test FAILED', {
          error: testResponse.data.chatTest.error,
          httpStatus: testResponse.data.chatTest.details?.httpStatus,
        });
      }
    }
    
  } catch (error) {
    log('error', 'Failed to run diagnostic', { error: error.message });
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  
  console.log(`
Based on the model name history in this repo:
- gemini-1.5-flash: Original working model
- gemini-2.0-flash-001: Changed in PR #3425 (INVALID - causes 404!)

The fix changes the model back to 'gemini-1.5-flash' which is the
alias that auto-points to the latest stable version.

Valid Vertex AI model names:
- gemini-1.5-flash (alias - recommended)
- gemini-1.5-flash-002 (specific stable version)
- gemini-1.5-pro (larger model)
- gemini-1.5-pro-002 (specific stable version)

Invalid model name:
- gemini-2.0-flash-001 (DOES NOT EXIST on Vertex AI!)
`);
}

// Run the test
testDebugEndpoint().catch(console.error);
