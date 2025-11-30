/**
 * Shared utilities for CopilotKit configuration
 * Enhanced with better logging and error handling
 * 
 * Authentication modes:
 * 1. Vertex AI (Cloud Run) - Uses Application Default Credentials (ADC) from service account
 *    - Set USE_VERTEX_AI=true or GOOGLE_GENAI_USE_VERTEXAI=true
 *    - No API key needed - uses service account OAuth2 tokens automatically
 * 2. Google AI Studio - Uses GEMINI_API_KEY (starts with AIza...)
 * 3. OpenAI - Uses OPENAI_API_KEY as fallback
 */

import {
  GoogleGenerativeAIAdapter,
  OpenAIAdapter,
  ExperimentalEmptyAdapter,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { VertexAIAdapter } from "./adapters/vertex-ai-adapter";

// Logging helper
function logConfig(message: string, data?: object) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[${timestamp}] [CopilotKit Config] ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`[${timestamp}] [CopilotKit Config] ${message}`);
  }
}

// Check for Vertex AI mode (uses Application Default Credentials on Cloud Run)
// This is the preferred mode when running on GCP with a service account
const useVertexAI = process.env.USE_VERTEX_AI === 'true' || 
                    process.env.GOOGLE_GENAI_USE_VERTEXAI === 'true';

// Check for API keys
// GEMINI_API_KEY is for Google AI Studio (starts with AIza...)
// GOOGLE_API_KEY is read from env but managed dynamically based on auth mode
export const geminiApiKey = process.env.GEMINI_API_KEY;
export const openaiApiKey = process.env.OPENAI_API_KEY;

// Track if GOOGLE_API_KEY was originally set (for logging)
const originalGoogleApiKey = process.env.GOOGLE_API_KEY;

// Determine which provider to use
// Priority: Vertex AI (ADC) > Google AI Studio (GEMINI_API_KEY) > OpenAI
export const useGemini = useVertexAI || !!geminiApiKey;
export const useOpenAI = !useGemini && !!openaiApiKey;

// Log configuration on module load
logConfig("Initializing CopilotKit configuration", {
  useVertexAI,
  hasGeminiApiKey: !!geminiApiKey,
  hasOriginalGoogleApiKey: !!originalGoogleApiKey,
  hasOpenAIApiKey: !!openaiApiKey,
  useGemini,
  useOpenAI,
  nodeEnv: process.env.NODE_ENV,
});

// Log warning if no authentication configured
if (!useVertexAI && !geminiApiKey && !openaiApiKey) {
  logConfig("WARNING: No LLM authentication configured. Set USE_VERTEX_AI=true (for Cloud Run), GEMINI_API_KEY, or OPENAI_API_KEY.");
} else if (useVertexAI) {
  logConfig("Using Vertex AI with Application Default Credentials (ADC)");
} else if (geminiApiKey) {
  logConfig("Using Google AI Studio API key");
} else {
  logConfig("Using OpenAI API");
}

/**
 * Creates the appropriate service adapter based on available authentication.
 * Priority: Vertex AI (ADC) > Google AI Studio (GEMINI_API_KEY) > OpenAI
 * Falls back to ExperimentalEmptyAdapter if no authentication is configured.
 * 
 * Note: We must modify process.env because GoogleGenerativeAIAdapter internally
 * uses @langchain/google-gauth which reads GOOGLE_API_KEY from the environment.
 * There's no way to pass auth config directly to the adapter constructor.
 * 
 * UPDATE: For Vertex AI, we now use our custom VertexAIAdapter which properly
 * configures platformType and location for ADC authentication.
 */
export const createServiceAdapter = () => {
  logConfig("Creating service adapter...");
  
  if (useGemini) {
    // For Vertex AI: Use our custom adapter that properly configures platformType and location
    if (useVertexAI) {
      logConfig("Creating VertexAIAdapter for Cloud Run/GCP", { 
        location: process.env.GOOGLE_CLOUD_REGION || "us-central1" 
      });
      
      // Clear GOOGLE_API_KEY so ADC uses service account credentials
      // Note: This has global effect but is intentional - we want ADC to be the only auth source
      // when running in Vertex AI mode. The original value was saved for logging purposes.
      if (process.env.GOOGLE_API_KEY) {
        delete process.env.GOOGLE_API_KEY;
        logConfig("Cleared GOOGLE_API_KEY to enable ADC for Vertex AI (was set, now removed)");
      }
      
      try {
        const adapter = new VertexAIAdapter({
          model: "gemini-1.5-flash", // Use faster, cheaper model for chat
          location: process.env.GOOGLE_CLOUD_REGION || "us-central1",
        });
        logConfig("VertexAIAdapter created successfully");
        return adapter;
      } catch (error) {
        logConfig("ERROR creating VertexAIAdapter", {
          error: error instanceof Error ? error.message : String(error),
        });
        throw error;
      }
    }
    
    // For Google AI Studio: Use the standard GoogleGenerativeAIAdapter
    logConfig("Creating GoogleGenerativeAIAdapter for Google AI Studio", { hasGeminiApiKey: !!geminiApiKey });
    
    // Set GOOGLE_API_KEY from GEMINI_API_KEY for Google AI Studio
    if (geminiApiKey) {
      process.env.GOOGLE_API_KEY = geminiApiKey;
      logConfig("Set GOOGLE_API_KEY from GEMINI_API_KEY for Google AI Studio");
    }
    
    try {
      const adapter = new GoogleGenerativeAIAdapter({
        model: "gemini-1.5-flash", // Use faster, cheaper model for chat
      });
      logConfig("GoogleGenerativeAIAdapter created successfully");
      return adapter;
    } catch (error) {
      logConfig("ERROR creating GoogleGenerativeAIAdapter", {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }
  
  if (openaiApiKey) {
    logConfig("Creating OpenAIAdapter");
    
    try {
      const openai = new OpenAI({
        apiKey: openaiApiKey,
      });
      // Type assertion needed due to version mismatch between @copilotkit/runtime and openai package
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const adapter = new OpenAIAdapter({ openai: openai as any });
      logConfig("OpenAIAdapter created successfully");
      return adapter;
    } catch (error) {
      logConfig("ERROR creating OpenAIAdapter", {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }
  
  logConfig("WARNING: Falling back to ExperimentalEmptyAdapter (no API key configured)");
  // Fall back to empty adapter - will only work with agent-based routes
  return new ExperimentalEmptyAdapter();
};

/**
 * Returns the active LLM provider info for status display
 */
export const getLLMProviderInfo = () => {
  const info = {
    provider: useVertexAI ? "vertex-ai" : useGemini ? "gemini" : useOpenAI ? "openai" : "none",
    model: useGemini ? "gemini-1.5-flash" : useOpenAI ? "gpt-4" : null,
    available: useGemini || useOpenAI,
    authMode: useVertexAI ? "adc" : geminiApiKey ? "api-key" : openaiApiKey ? "api-key" : "none",
  };
  
  logConfig("getLLMProviderInfo called", info);
  
  return info;
};
