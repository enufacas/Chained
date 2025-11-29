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
export const geminiApiKey = process.env.GEMINI_API_KEY;
export const openaiApiKey = process.env.OPENAI_API_KEY;
export const useGemini = !!geminiApiKey;
export const useOpenAI = !useGemini && !!openaiApiKey;

// Log warning if no API keys configured
if (!geminiApiKey && !openaiApiKey) {
  console.warn(
    "Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY environment variable is set. CopilotKit chat will not work."
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
  if (useGemini && geminiApiKey) {
    // GoogleGenerativeAIAdapter uses GOOGLE_API_KEY env var internally via @langchain/google-gauth
    // We set it here from our GEMINI_API_KEY for compatibility
    // Note: This is a documented pattern for the Google adapter
    process.env.GOOGLE_API_KEY = geminiApiKey;
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
