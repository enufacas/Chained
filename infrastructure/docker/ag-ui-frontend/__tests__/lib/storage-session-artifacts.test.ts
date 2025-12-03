/**
 * @jest-environment jsdom
 * 
 * Integration test for session and artifact display
 * 
 * Tests the complete flow:
 * 1. Save artifacts from a pipeline
 * 2. Save session with artifact IDs
 * 3. Verify artifacts can be retrieved
 * 4. Verify session displays artifact count correctly
 */

import {
  saveArtifact,
  saveSession,
  getStoredArtifacts,
  getStoredSessions,
  getArtifactById,
  clearAllStorage,
} from "@/lib/storage";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock IndexedDB
Object.defineProperty(window, 'indexedDB', {
  value: undefined,
});

describe("Session and artifact integration", () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  afterEach(() => {
    clearAllStorage();
  });

  it("should save artifacts and session with correct references", () => {
    const pipelineId = "test-pipeline-1";
    const pipelineTopic = "Test AI Topic";

    // Simulate pipeline creating artifacts
    const artifact1 = saveArtifact({
      name: "research-data.json",
      type: "application/json",
      data: JSON.stringify({ topic: "AI", keywords: ["machine learning", "neural networks"] }),
      preview: "Research data for AI topic",
      source: "workflow",
      sourceId: pipelineId,
      sourceName: pipelineTopic,
      agentName: "Academic Research Agent",
      phase: "research",
    });

    const artifact2 = saveArtifact({
      name: "trends-data.json",
      type: "application/json",
      data: JSON.stringify({ trending: ["AI trends", "ML applications"] }),
      preview: "Trends analysis",
      source: "workflow",
      sourceId: pipelineId,
      sourceName: pipelineTopic,
      agentName: "Google Trends Agent",
      phase: "trends",
    });

    const artifact3 = saveArtifact({
      name: "blog-post.html",
      type: "text/html",
      data: "<html><body><h1>Blog about AI</h1><p>Content here...</p></body></html>",
      preview: "Blog about AI",
      source: "workflow",
      sourceId: pipelineId,
      sourceName: pipelineTopic,
      agentName: "Blog Writer Agent",
      phase: "writing",
    });

    // Save session with artifact references
    const session = saveSession({
      id: pipelineId,
      type: "workflow",
      name: "A2A Pipeline",
      topic: pipelineTopic,
      status: "completed",
      completedAt: new Date().toISOString(),
      artifacts: [artifact1.id, artifact2.id, artifact3.id],
      metadata: {
        totalDurationMs: 5000,
        agentStepsCount: 3,
        blogUrl: "https://example.com/blog.html",
      },
      a2aContextId: pipelineId,
      taskIds: ["task-1", "task-2", "task-3"],
    });

    // Verify artifacts are saved
    const savedArtifacts = getStoredArtifacts();
    expect(savedArtifacts).toHaveLength(3);

    // Verify we can retrieve artifacts by ID
    const retrieved1 = getArtifactById(artifact1.id);
    expect(retrieved1).toBeDefined();
    expect(retrieved1?.name).toBe("research-data.json");
    expect(retrieved1?.agentName).toBe("Academic Research Agent");

    const retrieved2 = getArtifactById(artifact2.id);
    expect(retrieved2).toBeDefined();
    expect(retrieved2?.name).toBe("trends-data.json");

    const retrieved3 = getArtifactById(artifact3.id);
    expect(retrieved3).toBeDefined();
    expect(retrieved3?.name).toBe("blog-post.html");

    // Verify session is saved with correct references
    const savedSessions = getStoredSessions();
    expect(savedSessions).toHaveLength(1);
    expect(savedSessions[0].artifacts).toHaveLength(3);
    expect(savedSessions[0].artifacts).toContain(artifact1.id);
    expect(savedSessions[0].artifacts).toContain(artifact2.id);
    expect(savedSessions[0].artifacts).toContain(artifact3.id);

    // Verify metadata is preserved
    expect(savedSessions[0].metadata).toBeDefined();
    expect(savedSessions[0].metadata?.totalDurationMs).toBe(5000);
    expect(savedSessions[0].metadata?.agentStepsCount).toBe(3);
    expect(savedSessions[0].metadata?.blogUrl).toBe("https://example.com/blog.html");

    // Verify A2A data is preserved
    expect(savedSessions[0].a2aContextId).toBe(pipelineId);
    expect(savedSessions[0].taskIds).toEqual(["task-1", "task-2", "task-3"]);
  });

  it("should handle retrieving artifacts for display on history page", () => {
    const pipelineId = "display-test-pipeline";
    const artifactIds: string[] = [];

    // Create multiple artifacts
    for (let i = 1; i <= 5; i++) {
      const artifact = saveArtifact({
        name: `artifact-${i}.json`,
        type: "application/json",
        data: JSON.stringify({ index: i, data: "content" }),
        preview: `Artifact ${i}`,
        source: "workflow",
        sourceId: pipelineId,
        sourceName: "Display Test",
        agentName: `Agent ${i}`,
        phase: "test",
      });
      artifactIds.push(artifact.id);
    }

    // Save session
    saveSession({
      id: pipelineId,
      type: "workflow",
      name: "Display Test Pipeline",
      topic: "Display Test",
      status: "completed",
      artifacts: artifactIds,
      metadata: {
        totalDurationMs: 10000,
        agentStepsCount: 5,
      },
    });

    // Simulate history page loading session
    const sessions = getStoredSessions();
    const session = sessions[0];

    // Simulate expanding session to show artifacts
    const sessionArtifacts = session.artifacts.map((id) => getArtifactById(id)).filter((a) => a !== undefined);

    expect(sessionArtifacts).toHaveLength(5);
    sessionArtifacts.forEach((artifact, index) => {
      expect(artifact?.name).toBe(`artifact-${index + 1}.json`);
      expect(artifact?.agentName).toBe(`Agent ${index + 1}`);
    });
  });

  it("should preserve metadata through session updates", async () => {
    const pipelineId = "metadata-test";
    
    // Create initial session with minimal metadata
    saveSession({
      id: pipelineId,
      type: "workflow",
      name: "Metadata Test",
      topic: "Testing",
      status: "running",
      artifacts: [],
      metadata: {
        agentStepsCount: 1,
      },
    });

    // Wait a bit
    await new Promise(resolve => setTimeout(resolve, 10));

    // Update with more metadata
    saveSession({
      id: pipelineId,
      type: "workflow",
      name: "Metadata Test",
      topic: "Testing",
      status: "completed",
      artifacts: ["art-1", "art-2"],
      metadata: {
        totalDurationMs: 5000,
        agentStepsCount: 3,
        blogUrl: "https://blog.example.com",
      },
    });

    // Verify metadata is updated
    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    expect(sessions[0].metadata?.totalDurationMs).toBe(5000);
    expect(sessions[0].metadata?.agentStepsCount).toBe(3);
    expect(sessions[0].metadata?.blogUrl).toBe("https://blog.example.com");
  });
});
