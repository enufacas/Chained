/**
 * Shared utilities for CopilotKit configuration
 */

import {
  GoogleGenerativeAIAdapter,
  OpenAIAdapter,
  ExperimentalEmptyAdapter,
} from "@copilotkit/runtime";
import OpenAI from "openai";

// Check for API keys
// GOOGLE_API_KEY is the standard env var used by the Google adapter
// GEMINI_API_KEY is an alias for backward compatibility
export const googleApiKey = process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY;
export const openaiApiKey = process.env.OPENAI_API_KEY;
export const useGemini = !!googleApiKey;
export const useOpenAI = !useGemini && !!openaiApiKey;

// Log warning if no API keys configured
if (!googleApiKey && !openaiApiKey) {
  console.warn(
    "Warning: No LLM API key configured (GOOGLE_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY). CopilotKit chat will not work."
  );
} else if (useGemini) {
  console.log("CopilotKit: Using Google Gemini API");
} else {
  console.log("CopilotKit: Using OpenAI API");
}

/**
 * Creates the appropriate service adapter based on available API keys.
 * Prefers Gemini over OpenAI when both are available.
 * Falls back to ExperimentalEmptyAdapter if no API keys are configured.
 */
export const createServiceAdapter = () => {
  if (useGemini && googleApiKey) {
    // GoogleGenerativeAIAdapter uses GOOGLE_API_KEY env var internally via @langchain/google-gauth
    // Ensure GOOGLE_API_KEY is set from whichever source provided the key
    process.env.GOOGLE_API_KEY = googleApiKey;
    return new GoogleGenerativeAIAdapter({
      model: "gemini-1.5-flash", // Use faster, cheaper model for chat
    });
  }
  
  if (openaiApiKey) {
    const openai = new OpenAI({
      apiKey: openaiApiKey,
    });
    // Type assertion needed due to version mismatch between @copilotkit/runtime and openai package
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return new OpenAIAdapter({ openai: openai as any });
  }
  
  // Fall back to empty adapter - will only work with agent-based routes
  return new ExperimentalEmptyAdapter();
};

/**
 * Returns the active LLM provider info for status display
 */
export const getLLMProviderInfo = () => ({
  provider: useGemini ? "gemini" : useOpenAI ? "openai" : "none",
  model: useGemini ? "gemini-1.5-flash" : useOpenAI ? "gpt-4" : null,
  available: useGemini || useOpenAI,
});
