import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";
import { 
  createServiceAdapter, 
  getLLMProviderInfo,
  googleApiKey,
  openaiApiKey,
} from "@/lib/copilotkit-config";

// Create the CopilotKit runtime
const copilotKit = new CopilotRuntime();

export const POST = async (req: NextRequest) => {
  if (!googleApiKey && !openaiApiKey) {
    return new Response(
      JSON.stringify({ 
        error: "No LLM API key configured",
        message: "Set GOOGLE_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY"
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
    JSON.stringify(getLLMProviderInfo()),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};
