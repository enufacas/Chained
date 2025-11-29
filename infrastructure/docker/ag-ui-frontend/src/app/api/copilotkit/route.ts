import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

// Check for OpenAI API key
const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) {
  console.warn(
    "Warning: OPENAI_API_KEY environment variable is not set. CopilotKit chat will not work."
  );
}

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: apiKey || "missing-api-key",
});

// Create the CopilotKit runtime
const copilotKit = new CopilotRuntime();

export const POST = async (req: NextRequest) => {
  if (!apiKey) {
    return new Response(
      JSON.stringify({ error: "OpenAI API key not configured" }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime: copilotKit,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    serviceAdapter: new OpenAIAdapter({ openai: openai as any }),
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
