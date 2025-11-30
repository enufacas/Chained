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

// Logging helper with timestamps
function log(message: string, data?: object) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[${timestamp}] [VertexAIAdapter] ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`[${timestamp}] [VertexAIAdapter] ${message}`);
  }
}

export interface VertexAIAdapterOptions {
  /** Model name (default: gemini-2.0-flash) */
  model?: string;
  /** GCP region (default: us-central1) */
  location?: string;
  /** API version (default: v1) - v1beta returns 404 for newer models */
  apiVersion?: string;
}

/**
 * CopilotKit adapter for Google Vertex AI using Application Default Credentials.
 * 
 * This adapter is designed for Cloud Run deployments where the service account
 * has the Vertex AI User role.
 */
export class VertexAIAdapter extends LangChainAdapter {
  private config: {
    modelName: string;
    location: string;
    apiVersion: string;
  };

  constructor(options?: VertexAIAdapterOptions) {
    const modelName = options?.model ?? "gemini-2.0-flash";
    const location = options?.location ?? process.env.GOOGLE_CLOUD_REGION ?? "us-central1";
    const apiVersion = options?.apiVersion ?? "v1"; // Changed from v1beta - v1beta returns 404 for newer models

    log("Initializing VertexAIAdapter", {
      modelName,
      location,
      apiVersion,
      envGoogleCloudRegion: process.env.GOOGLE_CLOUD_REGION,
      envGoogleApiKey: process.env.GOOGLE_API_KEY ? "SET (will be cleared)" : "NOT SET",
    });

    super({
      chainFn: async ({ messages, tools, threadId }) => {
        log("chainFn called", {
          messageCount: messages.length,
          toolCount: tools?.length ?? 0,
          threadId,
        });

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

        log("Filtered messages", {
          originalCount: messages.length,
          filteredCount: filteredMessages.length,
        });

        // Create ChatGoogle with Vertex AI configuration
        log("Creating ChatGoogle instance", {
          modelName,
          apiVersion,
          platformType: "gcp",
          location,
        });

        try {
          const model = new ChatGoogle({
            modelName,
            apiVersion,
            platformType: "gcp",  // Use Vertex AI (GCP) instead of Google AI Studio
            location,             // GCP region for Vertex AI
          }).bindTools(tools);

          log("ChatGoogle created successfully, starting stream...");

          const stream = model.stream(filteredMessages, {
            metadata: {
              conversation_id: threadId,
            },
          });

          log("Stream initiated successfully");
          return stream;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          const errorStack = error instanceof Error ? error.stack : undefined;
          
          log("ERROR in ChatGoogle", {
            error: errorMessage,
            stack: errorStack,
            // Get error type name safely
            errorType: error instanceof Error ? error.constructor.name : typeof error,
          });
          
          throw error;
        }
      },
    });

    this.config = { modelName, location, apiVersion };
    log("VertexAIAdapter initialized successfully");
  }

  /** Get the current configuration for debugging */
  getConfig() {
    return this.config;
  }
}
