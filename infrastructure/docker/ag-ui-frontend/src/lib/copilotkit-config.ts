/**
 * Shared utilities for CopilotKit configuration
 * Enhanced with better logging and error handling
 */

import {
  GoogleGenerativeAIAdapter,
  OpenAIAdapter,
  ExperimentalEmptyAdapter,
} from "@copilotkit/runtime";
import OpenAI from "openai";

// Logging helper
function logConfig(message: string, data?: object) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[${timestamp}] [CopilotKit Config] ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`[${timestamp}] [CopilotKit Config] ${message}`);
  }
}

// Check for API keys
// GOOGLE_API_KEY is the standard env var used by the Google adapter
// GEMINI_API_KEY is an alias for backward compatibility
export const googleApiKey = process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY;
export const openaiApiKey = process.env.OPENAI_API_KEY;
export const useGemini = !!googleApiKey;
export const useOpenAI = !useGemini && !!openaiApiKey;

// Log configuration on module load
logConfig("Initializing CopilotKit configuration", {
  hasGoogleApiKey: !!googleApiKey,
  hasGeminiApiKey: !!process.env.GEMINI_API_KEY,
  hasOpenAIApiKey: !!openaiApiKey,
  useGemini,
  useOpenAI,
  nodeEnv: process.env.NODE_ENV,
});

// Log warning if no API keys configured
if (!googleApiKey && !openaiApiKey) {
  logConfig("WARNING: No LLM API key configured (GOOGLE_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY). CopilotKit chat will not work.");
} else if (useGemini) {
  logConfig("Using Google Gemini API");
} else {
  logConfig("Using OpenAI API");
}

/**
 * Creates the appropriate service adapter based on available API keys.
 * Prefers Gemini over OpenAI when both are available.
 * Falls back to ExperimentalEmptyAdapter if no API keys are configured.
 */
export const createServiceAdapter = () => {
  logConfig("Creating service adapter...");
  
  if (useGemini && googleApiKey) {
    logConfig("Creating GoogleGenerativeAIAdapter");
    
    // GoogleGenerativeAIAdapter uses GOOGLE_API_KEY env var internally via @langchain/google-gauth
    // Ensure GOOGLE_API_KEY is set from whichever source provided the key
    process.env.GOOGLE_API_KEY = googleApiKey;
    
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
    provider: useGemini ? "gemini" : useOpenAI ? "openai" : "none",
    model: useGemini ? "gemini-1.5-flash" : useOpenAI ? "gpt-4" : null,
    available: useGemini || useOpenAI,
  };
  
  logConfig("getLLMProviderInfo called", info);
  
  return info;
};
