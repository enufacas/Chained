/**
 * Debug API endpoint for testing Gemini/Vertex AI connection via LangChain
 * 
 * This endpoint tests the connection to Gemini using the same libraries
 * that CopilotKit uses internally (LangChain's google-gauth).
 * 
 * Endpoints:
 * - GET /api/debug - Show configuration and environment
 * - POST /api/debug - Test Vertex AI chat with detailed debugging
 * - POST /api/debug with {"test": "auth"} - Test just authentication
 */

import { NextRequest } from "next/server";
import { ChatGoogle } from "@langchain/google-gauth";
import { HumanMessage } from "@langchain/core/messages";
import { GoogleAuth } from "google-auth-library";

// Logging helper
function log(message: string, data?: object) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[${timestamp}] [Debug API] ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`[${timestamp}] [Debug API] ${message}`);
  }
}

// Extract detailed error info
function extractErrorDetails(error: unknown): Record<string, unknown> {
  const details: Record<string, unknown> = {};
  
  if (error instanceof Error) {
    details.name = error.name;
    details.message = error.message;
    details.stack = error.stack?.split('\n').slice(0, 10).join('\n');
  }
  
  if (error && typeof error === 'object') {
    const errorObj = error as Record<string, unknown>;
    
    // Common error properties
    ['cause', 'code', 'status', 'statusCode', 'errno', 'syscall'].forEach(key => {
      if (key in errorObj) details[key] = errorObj[key];
    });
    
    // HTTP response details
    if ('response' in errorObj) {
      const resp = errorObj.response as Record<string, unknown>;
      if (resp && typeof resp === 'object') {
        details.httpStatus = resp.status;
        details.httpStatusText = resp.statusText;
        if ('data' in resp) {
          const data = resp.data;
          if (typeof data === 'string') {
            details.responseData = data.substring(0, 1000);
          } else if (typeof data === 'object') {
            details.responseData = JSON.stringify(data).substring(0, 1000);
          }
        }
        if ('headers' in resp) {
          details.responseHeaders = resp.headers;
        }
      }
    }
    
    // Google API error details
    if ('errors' in errorObj) details.errors = errorObj.errors;
    if ('details' in errorObj) details.details = errorObj.details;
  }
  
  return details;
}

// Test Google Auth directly
async function testGoogleAuth(): Promise<{ success: boolean; projectId?: string; email?: string; error?: string; details?: Record<string, unknown> }> {
  try {
    log("Testing Google Auth directly...");
    
    const auth = new GoogleAuth({
      scopes: ['https://www.googleapis.com/auth/cloud-platform'],
    });
    
    const projectId = await auth.getProjectId();
    log("Got project ID from ADC", { projectId });
    
    const client = await auth.getClient();
    const credentials = await client.getAccessToken();
    
    // Get the service account email if available
    let email: string | undefined;
    if ('email' in client && typeof client.email === 'string') {
      email = client.email;
    }
    
    log("Auth test successful", { 
      projectId, 
      email,
      hasAccessToken: !!credentials.token,
      tokenExpiry: credentials.res?.data?.expiry_date,
    });
    
    return { 
      success: true, 
      projectId: projectId ?? undefined,
      email,
    };
  } catch (error) {
    log("Auth test FAILED", extractErrorDetails(error));
    return { 
      success: false, 
      error: error instanceof Error ? error.message : String(error),
      details: extractErrorDetails(error),
    };
  }
}

// Test Vertex AI endpoint directly
async function testVertexAI(location: string, projectId: string): Promise<{ success: boolean; response?: string; error?: string; details?: Record<string, unknown> }> {
  try {
    log("Testing Vertex AI directly...", { location, projectId });
    
    const modelName = "gemini-2.0-flash-001";
    const apiVersion = "v1beta";
    
    // Create ChatGoogle with explicit Vertex AI config
    const model = new ChatGoogle({
      modelName,
      apiVersion,
      platformType: "gcp",
      location,
    });
    
    log("ChatGoogle created, invoking with test message...");
    
    const result = await model.invoke([
      new HumanMessage("Say exactly: 'Vertex AI is working!'")
    ]);
    
    const responseText = typeof result.content === 'string' 
      ? result.content 
      : JSON.stringify(result.content);
    
    log("Vertex AI test successful", { responsePreview: responseText.substring(0, 200) });
    
    return { success: true, response: responseText };
  } catch (error) {
    log("Vertex AI test FAILED", extractErrorDetails(error));
    return { 
      success: false, 
      error: error instanceof Error ? error.message : String(error),
      details: extractErrorDetails(error),
    };
  }
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const GET = async (_req: NextRequest) => {
  log("GET request received - Debug endpoint");
  
  const useVertexAI = process.env.USE_VERTEX_AI === 'true' || 
                      process.env.GOOGLE_GENAI_USE_VERTEXAI === 'true';
  const projectId = process.env.GOOGLE_CLOUD_PROJECT;
  const location = process.env.GOOGLE_CLOUD_REGION || 'us-central1';
  const geminiApiKey = process.env.GEMINI_API_KEY;
  
  // Comprehensive environment info
  const envInfo = {
    // Vertex AI settings
    USE_VERTEX_AI: useVertexAI,
    GOOGLE_CLOUD_PROJECT: projectId || '(not set - will use ADC)',
    GOOGLE_CLOUD_REGION: location,
    
    // API Keys
    hasGeminiApiKey: !!geminiApiKey,
    geminiApiKeyPrefix: geminiApiKey ? geminiApiKey.substring(0, 8) + '...' : null,
    hasGoogleApiKey: !!process.env.GOOGLE_API_KEY,
    googleApiKeyPrefix: process.env.GOOGLE_API_KEY ? process.env.GOOGLE_API_KEY.substring(0, 8) + '...' : null,
    
    // Runtime info
    nodeEnv: process.env.NODE_ENV,
    nodeVersion: process.version,
    
    // GCP metadata (Cloud Run specific)
    K_SERVICE: process.env.K_SERVICE || '(not on Cloud Run)',
    K_REVISION: process.env.K_REVISION || '(not on Cloud Run)',
    
    timestamp: new Date().toISOString(),
  };
  
  log("Environment info", envInfo);
  
  return new Response(
    JSON.stringify({
      status: "debug",
      environment: envInfo,
      tests: {
        auth: "POST with {\"test\": \"auth\"} to test ADC authentication",
        vertex: "POST with {\"test\": \"vertex\"} to test Vertex AI",
        chat: "POST with {\"message\": \"your message\"} to test chat",
        full: "POST with {\"test\": \"full\"} to run all tests",
      },
    }, null, 2),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
};

export const POST = async (req: NextRequest) => {
  log("POST request received - Debug test");
  
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return new Response(
      JSON.stringify({ error: "Invalid JSON body" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  
  const testType = typeof body.test === 'string' ? body.test : 'chat';
  const message = typeof body.message === 'string' ? body.message : "Say exactly: 'Hello from Vertex AI!'";
  
  const useVertexAI = process.env.USE_VERTEX_AI === 'true' || 
                      process.env.GOOGLE_GENAI_USE_VERTEXAI === 'true';
  const projectId = process.env.GOOGLE_CLOUD_PROJECT || '';
  const location = process.env.GOOGLE_CLOUD_REGION || "us-central1";
  const modelName = process.env.GEMINI_MODEL || "gemini-2.0-flash-001";
  
  log("Test requested", { testType, useVertexAI, projectId, location, modelName });
  
  // Run tests based on type
  const results: Record<string, unknown> = {
    timestamp: new Date().toISOString(),
    config: { useVertexAI, projectId, location, modelName },
  };
  
  // Auth test
  if (testType === 'auth' || testType === 'full') {
    results.authTest = await testGoogleAuth();
  }
  
  // Vertex AI test
  if (testType === 'vertex' || testType === 'full') {
    if (!useVertexAI) {
      results.vertexTest = { 
        success: false, 
        error: "Vertex AI not enabled. Set USE_VERTEX_AI=true" 
      };
    } else {
      // Use project from auth test if available
      const testProjectId = projectId || (results.authTest as { projectId?: string })?.projectId || '';
      results.vertexTest = await testVertexAI(location, testProjectId);
    }
  }
  
  // Chat test (default)
  if (testType === 'chat' || testType === 'full') {
    if (!useVertexAI) {
      results.chatTest = { 
        success: false, 
        error: "Vertex AI not enabled. Set USE_VERTEX_AI=true" 
      };
    } else {
      try {
        log("Running chat test...", { message });
        
        const model = new ChatGoogle({
          modelName,
          apiVersion: "v1beta",
          platformType: "gcp",
          location,
        });
        
        const result = await model.invoke([new HumanMessage(message)]);
        
        const responseText = typeof result.content === 'string' 
          ? result.content 
          : JSON.stringify(result.content);
        
        results.chatTest = {
          success: true,
          input: message,
          response: responseText,
        };
      } catch (error) {
        results.chatTest = {
          success: false,
          input: message,
          error: error instanceof Error ? error.message : String(error),
          details: extractErrorDetails(error),
        };
      }
    }
  }
  
  // Determine overall success
  interface TestResult { success: boolean }
  const allTests = ['authTest', 'vertexTest', 'chatTest']
    .map(t => results[t] as TestResult | undefined)
    .filter((t): t is TestResult => t !== undefined && typeof t.success === 'boolean');
  
  const success = allTests.length > 0 && allTests.every(t => t.success);
  
  log("Tests completed", { success, testCount: allTests.length });
  
  return new Response(
    JSON.stringify({ success, ...results }, null, 2),
    { 
      status: success ? 200 : 500, 
      headers: { "Content-Type": "application/json" } 
    }
  );
};
