/**
 * Custom Vertex AI Adapter for CopilotKit
 * 
 * This adapter properly configures ChatGoogle for Vertex AI (GCP) by setting:
 * - platformType: "gcp" (required for Vertex AI instead of Google AI Studio)
 * - location: GCP region (required for Vertex AI endpoints)
 * 
 * The built-in GoogleGenerativeAIAdapter doesn't support these options,
 * which causes authentication failures when using Application Default Credentials.
 */

import { LangChainAdapter } from "@copilotkit/runtime";
import { ChatGoogle } from "@langchain/google-gauth";
import { AIMessage } from "@langchain/core/messages";

export interface VertexAIAdapterOptions {
  /** Model name (default: gemini-1.5-flash) */
  model?: string;
  /** GCP region (default: us-central1) */
  location?: string;
  /** API version (default: v1beta) */
  apiVersion?: string;
}

/**
 * CopilotKit adapter for Google Vertex AI using Application Default Credentials.
 * 
 * This adapter is designed for Cloud Run deployments where the service account
 * has the Vertex AI User role.
 */
export class VertexAIAdapter extends LangChainAdapter {
  constructor(options?: VertexAIAdapterOptions) {
    const modelName = options?.model ?? "gemini-1.5-flash";
    const location = options?.location ?? process.env.GOOGLE_CLOUD_REGION ?? "us-central1";
    const apiVersion = options?.apiVersion ?? "v1beta";

    super({
      chainFn: async ({ messages, tools, threadId }) => {
        // Filter out empty AI messages (same as GoogleGenerativeAIAdapter)
        const filteredMessages = messages.filter((message) => {
          if (!(message instanceof AIMessage)) {
            return true;
          }
          return (
            (message.content && String(message.content).trim().length > 0) ||
            (message.tool_calls && message.tool_calls.length > 0)
          );
        });

        // Create ChatGoogle with Vertex AI configuration
        // Key difference from GoogleGenerativeAIAdapter:
        // - platformType: "gcp" ensures we use Vertex AI instead of Google AI Studio
        // - location: specifies the GCP region for the Vertex AI endpoint
        const model = new ChatGoogle({
          modelName,
          apiVersion,
          platformType: "gcp",  // Use Vertex AI (GCP) instead of Google AI Studio
          location,             // GCP region for Vertex AI
        }).bindTools(tools);

        return model.stream(filteredMessages, {
          metadata: {
            conversation_id: threadId,
          },
        });
      },
    });
  }
}
