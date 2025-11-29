import {
  CopilotRuntime,
  OpenAIAdapter,
  GoogleGenerativeAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

// Check for API keys - prefer Gemini over OpenAI
const geminiApiKey = process.env.GEMINI_API_KEY;
const openaiApiKey = process.env.OPENAI_API_KEY;

// Determine which adapter to use
const useGemini = !!geminiApiKey;
const useOpenAI = !useGemini && !!openaiApiKey;

if (!geminiApiKey && !openaiApiKey) {
  console.warn(
    "Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY environment variable is set. CopilotKit chat will not work."
  );
} else if (useGemini) {
  console.log("CopilotKit: Using Google Gemini API");
} else {
  console.log("CopilotKit: Using OpenAI API");
}

// Create the CopilotKit runtime
const copilotKit = new CopilotRuntime();

// Create the appropriate service adapter
const createServiceAdapter = () => {
  if (useGemini) {
    // GoogleGenerativeAIAdapter uses GOOGLE_API_KEY env var internally via @langchain/google-gauth
    // We need to set GOOGLE_API_KEY from GEMINI_API_KEY
    process.env.GOOGLE_API_KEY = geminiApiKey;
    return new GoogleGenerativeAIAdapter({
      model: "gemini-1.5-flash", // Use faster, cheaper model for chat
    });
  }
  
  // Fall back to OpenAI
  const openai = new OpenAI({
    apiKey: openaiApiKey || "missing-api-key",
  });
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return new OpenAIAdapter({ openai: openai as any });
};

export const POST = async (req: NextRequest) => {
  if (!geminiApiKey && !openaiApiKey) {
    return new Response(
      JSON.stringify({ 
        error: "No LLM API key configured",
        message: "Neither GEMINI_API_KEY nor OPENAI_API_KEY is set"
      }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime: copilotKit,
    serviceAdapter: createServiceAdapter(),
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};

// Export which LLM provider is being used (for status display)
export const GET = async () => {
  return new Response(
    JSON.stringify({
      provider: useGemini ? "gemini" : useOpenAI ? "openai" : "none",
      model: useGemini ? "gemini-1.5-flash" : "gpt-4",
      available: useGemini || useOpenAI,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};
