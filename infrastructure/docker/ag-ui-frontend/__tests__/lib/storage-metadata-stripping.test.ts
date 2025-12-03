/**
 * @jest-environment jsdom
 * 
 * Test for metadata stripping behavior
 * 
 * Ensures that stripLargeMetadata preserves essential display fields
 */

import { saveSession, getStoredSessions, clearAllStorage } from "@/lib/storage";

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

describe("Metadata stripping behavior", () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  afterEach(() => {
    clearAllStorage();
  });

  it("should preserve essential metadata fields for workflow sessions", () => {
    // Create a session with workflow metadata
    saveSession({
      id: "workflow-session",
      type: "workflow",
      name: "Pipeline",
      topic: "Test",
      status: "completed",
      artifacts: ["art-1"],
      metadata: {
        totalDurationMs: 5000,
        agentStepsCount: 3,
        blogUrl: "https://example.com/blog.html",
        // These should be stripped
        finalResult: { huge: "data", that: "should", be: "removed" },
      },
    });

    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    
    const metadata = sessions[0].metadata;
    expect(metadata).toBeDefined();
    
    // Essential fields should be preserved
    expect(metadata?.totalDurationMs).toBe(5000);
    expect(metadata?.agentStepsCount).toBe(3);
    expect(metadata?.blogUrl).toBe("https://example.com/blog.html");
    
    // Large fields should be removed (but only after 3 sessions)
    // Since this is the first/only session, it should have full metadata
    expect(metadata?.finalResult).toBeDefined();
  });

  it("should preserve essential metadata for team/recipe sessions", () => {
    saveSession({
      id: "team-session",
      type: "team",
      name: "Team Session",
      topic: "Research",
      status: "running",
      artifacts: [],
      metadata: {
        currentTurn: 3,
        totalTurns: 10,
        recipeId: "recipe-123",
        turnResults: [
          { turn: 1, result: "data" },
          { turn: 2, result: "more data" },
          { turn: 3, result: "even more data" },
        ],
      },
    });

    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    
    const metadata = sessions[0].metadata;
    expect(metadata).toBeDefined();
    
    // Essential fields should be preserved
    expect(metadata?.currentTurn).toBe(3);
    expect(metadata?.totalTurns).toBe(10);
    expect(metadata?.recipeId).toBe("recipe-123");
    
    // turnResults should be present for recent sessions (first 3)
    expect(metadata?.turnResults).toBeDefined();
  });

  it("should strip large metadata from older sessions (4+)", () => {
    // Create 4 sessions to trigger stripping for the 4th one
    for (let i = 1; i <= 4; i++) {
      saveSession({
        id: `session-${i}`,
        type: "workflow",
        name: `Session ${i}`,
        topic: `Topic ${i}`,
        status: "completed",
        artifacts: [],
        metadata: {
          totalDurationMs: i * 1000,
          agentStepsCount: i,
          blogUrl: `https://example.com/blog-${i}.html`,
          finalResult: { large: "data", should: "be stripped" },
          turnResults: [{ huge: "array" }],
        },
      });
    }

    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(4);
    
    // First 3 sessions should have full metadata
    for (let i = 0; i < 3; i++) {
      const metadata = sessions[i].metadata;
      expect(metadata?.finalResult).toBeDefined();
    }
    
    // 4th session (oldest) should have stripped metadata
    const oldestMetadata = sessions[3].metadata;
    expect(oldestMetadata?.totalDurationMs).toBeDefined(); // Essential field preserved
    expect(oldestMetadata?.agentStepsCount).toBeDefined(); // Essential field preserved
    expect(oldestMetadata?.blogUrl).toBeDefined(); // Essential field preserved
    expect(oldestMetadata?.finalResult).toBeUndefined(); // Large field stripped
  });

  it("should handle sessions with missing metadata gracefully", () => {
    saveSession({
      id: "no-metadata-session",
      type: "workflow",
      name: "No Metadata",
      topic: "Test",
      status: "completed",
      artifacts: [],
      // No metadata field
    });

    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    expect(sessions[0].metadata).toBeUndefined();
  });

  it("should handle empty metadata object", () => {
    saveSession({
      id: "empty-metadata-session",
      type: "workflow",
      name: "Empty Metadata",
      topic: "Test",
      status: "completed",
      artifacts: [],
      metadata: {},
    });

    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    expect(sessions[0].metadata).toBeDefined();
    expect(Object.keys(sessions[0].metadata || {})).toHaveLength(0);
  });
});
