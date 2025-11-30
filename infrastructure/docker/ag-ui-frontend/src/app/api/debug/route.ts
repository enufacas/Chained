/**
 * Debug API endpoint for testing Gemini/Vertex AI connection via LangChain
 * 
 * This endpoint tests the connection to Gemini using the same libraries
 * that CopilotKit uses internally (LangChain's google-gauth).
 */

import { NextRequest } from "next/server";
import { ChatGoogle } from "@langchain/google-gauth";
import { HumanMessage } from "@langchain/core/messages";

// Logging helper
function logWithTimestamp(message: string, data?: object) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[${timestamp}] [Debug API] ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`[${timestamp}] [Debug API] ${message}`);
  }
}

export const GET = async (req: NextRequest) => {
  logWithTimestamp("GET request received - Debug endpoint");
  
  const useVertexAI = process.env.USE_VERTEX_AI === 'true' || 
                      process.env.GOOGLE_GENAI_USE_VERTEXAI === 'true';
  const projectId = process.env.GOOGLE_CLOUD_PROJECT;
  const geminiApiKey = process.env.GEMINI_API_KEY;
  
  // Environment info
  const envInfo = {
    USE_VERTEX_AI: useVertexAI,
    GOOGLE_CLOUD_PROJECT: projectId || 'not set',
    hasGeminiApiKey: !!geminiApiKey,
    nodeEnv: process.env.NODE_ENV,
    timestamp: new Date().toISOString(),
  };
  
  logWithTimestamp("Environment info", envInfo);
  
  return new Response(
    JSON.stringify({
      status: "debug",
      environment: envInfo,
      message: "Use POST with {\"message\": \"your message\"} to test Vertex AI chat",
    }, null, 2),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
};

export const POST = async (req: NextRequest) => {
  logWithTimestamp("POST request received - Debug chat test");
  
  let body;
  try {
    body = await req.json();
  } catch (e) {
    return new Response(
      JSON.stringify({ error: "Invalid JSON body" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
  
  const message = body.message || "Hello! Say 'Hi from Gemini!' in exactly those words.";
  
  const useVertexAI = process.env.USE_VERTEX_AI === 'true' || 
                      process.env.GOOGLE_GENAI_USE_VERTEXAI === 'true';
  const projectId = process.env.GOOGLE_CLOUD_PROJECT;
  
  if (!useVertexAI) {
    return new Response(
      JSON.stringify({
        error: "Vertex AI is not enabled",
        tip: "Set USE_VERTEX_AI=true and GOOGLE_CLOUD_PROJECT environment variables",
      }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }
  
  // Use same model configuration as the main CopilotKit adapter
  const modelName = process.env.GEMINI_MODEL || "gemini-1.5-flash";
  const apiVersion = process.env.GEMINI_API_VERSION || "v1beta";
  
  // Test using ChatGoogle (same as CopilotKit's GoogleGenerativeAIAdapter)
  try {
    logWithTimestamp("Testing Vertex AI chat...", { message, projectId, modelName, apiVersion });
    
    // Create the ChatGoogle model (same way CopilotKit does internally)
    const model = new ChatGoogle({
      modelName,
      apiVersion,
    });
    
    logWithTimestamp("ChatGoogle model created, invoking...");
    
    // Invoke the model
    const result = await model.invoke([new HumanMessage(message)]);
    
    const responseText = typeof result.content === 'string' 
      ? result.content 
      : JSON.stringify(result.content);
    
    logWithTimestamp("Vertex AI response received", { responsePreview: responseText.substring(0, 200) });
    
    return new Response(
      JSON.stringify({
        success: true,
        provider: "vertex-ai",
        projectId: projectId,
        model: modelName,
        apiVersion: apiVersion,
        input: message,
        response: responseText,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    logWithTimestamp("Vertex AI test FAILED", { error: errorMessage, stack: errorStack });
    
    return new Response(
      JSON.stringify({
        success: false,
        provider: "vertex-ai",
        error: errorMessage,
        stack: errorStack,
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};
