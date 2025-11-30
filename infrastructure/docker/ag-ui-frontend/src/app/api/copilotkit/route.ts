/**
 * CopilotKit API Route with enhanced logging and error handling
 *
 * This route handles CopilotKit chat requests, supporting both Gemini and OpenAI.
 * It includes robust logging to help troubleshoot API key issues.
 */

import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";
import { 
  createServiceAdapter, 
  getLLMProviderInfo,
  geminiApiKey,
  openaiApiKey,
  useGemini,
} from "@/lib/copilotkit-config";

// Create the CopilotKit runtime
const copilotKit = new CopilotRuntime();

// Enhanced logging helper
function logWithTimestamp(message: string, data?: object) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[${timestamp}] [CopilotKit API] ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`[${timestamp}] [CopilotKit API] ${message}`);
  }
}

export const POST = async (req: NextRequest) => {
  logWithTimestamp("POST request received");
  
  // Log request details for debugging (sanitized - only log metadata, not content)
  try {
    const body = await req.clone().text();
    // Only log body length and structure type, not actual content which may contain user messages
    const isJson = body.startsWith('{') || body.startsWith('[');
    logWithTimestamp("Request body metadata", { 
      bodyLength: body.length, 
      isJson,
      contentType: req.headers.get('content-type'),
    });
  } catch {
    logWithTimestamp("Could not read request body for logging");
  }
  
  // Check if any authentication method is available
  const hasGeminiAuth = useGemini; // This includes Vertex AI ADC or GEMINI_API_KEY
  const hasOpenAIKey = !!openaiApiKey;
  
  logWithTimestamp("Authentication check", {
    hasGeminiAuth,
    hasOpenAIKey,
    geminiKeyLength: geminiApiKey ? geminiApiKey.length : 0,
    openaiKeyLength: openaiApiKey ? openaiApiKey.length : 0,
  });

  if (!hasGeminiAuth && !hasOpenAIKey) {
    logWithTimestamp("ERROR: No LLM authentication configured");
    return new Response(
      JSON.stringify({ 
        error: "No LLM authentication configured",
        message: "Set USE_VERTEX_AI=true (for Cloud Run), GEMINI_API_KEY, or OPENAI_API_KEY environment variable",
        debug: {
          timestamp: new Date().toISOString(),
          envVarsChecked: ["USE_VERTEX_AI", "GOOGLE_GENAI_USE_VERTEXAI", "GEMINI_API_KEY", "OPENAI_API_KEY"],
        }
      }),
      { 
        status: 503, 
        headers: { 
          "Content-Type": "application/json",
          "X-CopilotKit-Error": "missing-authentication",
        } 
      }
    );
  }

  try {
    logWithTimestamp("Creating service adapter...");
    const serviceAdapter = createServiceAdapter();
    logWithTimestamp("Service adapter created successfully");

    const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
      runtime: copilotKit,
      serviceAdapter,
      endpoint: "/api/copilotkit",
    });

    logWithTimestamp("Handling request...");
    const response = await handleRequest(req);
    logWithTimestamp("Request handled successfully", { 
      status: response.status,
      contentType: response.headers.get('content-type'),
    });
    
    // Log response metadata for debugging (don't log actual content to protect privacy)
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('text/event-stream')) {
      try {
        const clonedResponse = response.clone();
        const responseText = await clonedResponse.text();
        // Only log metadata, not actual content which may contain AI responses
        logWithTimestamp("Response body metadata", { 
          length: responseText.length,
          isJson: responseText.startsWith('{') || responseText.startsWith('['),
        });
      } catch {
        logWithTimestamp("Could not read response body for logging");
      }
    } else {
      logWithTimestamp("Response is streaming (text/event-stream)");
    }
    
    return response;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    logWithTimestamp("ERROR in request handling", {
      message: errorMessage,
      stack: errorStack,
    });

    return new Response(
      JSON.stringify({
        error: "Internal server error",
        message: errorMessage,
        debug: {
          timestamp: new Date().toISOString(),
          provider: hasGeminiAuth ? "gemini" : "openai",
        }
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
          "X-CopilotKit-Error": "internal-error",
        }
      }
    );
  }
};

// GET endpoint for status checking and debugging
export const GET = async () => {
  logWithTimestamp("GET request received (status check)");
  
  const info = getLLMProviderInfo();
  const isProduction = process.env.NODE_ENV === "production";
  
  // Add additional debug info (redact sensitive data in production)
  const debugInfo = {
    ...info,
    debug: {
      timestamp: new Date().toISOString(),
      hasGeminiApiKey: !!geminiApiKey,
      hasOpenAIApiKey: !!openaiApiKey,
      useVertexAI: info.authMode === "adc",
      // Only show key prefixes in development mode for security
      geminiKeyPrefix: !isProduction && geminiApiKey ? geminiApiKey.substring(0, 4) + "..." : (geminiApiKey ? "[redacted]" : null),
      openaiKeyPrefix: !isProduction && openaiApiKey ? openaiApiKey.substring(0, 4) + "..." : (openaiApiKey ? "[redacted]" : null),
      nodeEnv: process.env.NODE_ENV,
    }
  };

  logWithTimestamp("Returning status info", { provider: info.provider, available: info.available, authMode: info.authMode });
  
  return new Response(
    JSON.stringify(debugInfo),
    { 
      status: 200, 
      headers: { 
        "Content-Type": "application/json",
        "X-CopilotKit-Provider": info.provider,
        "X-CopilotKit-Available": String(info.available),
        "X-CopilotKit-AuthMode": info.authMode,
      } 
    }
  );
};
