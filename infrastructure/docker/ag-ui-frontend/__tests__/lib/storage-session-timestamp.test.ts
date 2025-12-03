/**
 * @jest-environment jsdom
 * 
 * Test for session timestamp preservation bug fix
 * 
 * Tests that:
 * 1. New sessions get a createdAt timestamp
 * 2. Updated sessions preserve their original createdAt
 * 3. Multiple updates don't change the createdAt
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

// Mock IndexedDB to avoid errors
Object.defineProperty(window, 'indexedDB', {
  value: undefined,
});

describe("Session timestamp preservation", () => {
  beforeEach(() => {
    // Clear storage before each test
    localStorageMock.clear();
  });

  afterEach(() => {
    // Clean up after each test
    clearAllStorage();
  });

  it("should create a new session with createdAt timestamp", () => {
    const sessionData = {
      id: "test-session-1",
      type: "workflow" as const,
      name: "Test Pipeline",
      topic: "Test Topic",
      status: "completed",
      artifacts: ["artifact-1", "artifact-2"],
      metadata: {
        totalDurationMs: 5000,
        agentStepsCount: 3,
      },
    };

    const saved = saveSession(sessionData);

    // Should have a createdAt timestamp
    expect(saved.createdAt).toBeDefined();
    expect(typeof saved.createdAt).toBe("string");
    expect(saved.createdAt).toMatch(/^\d{4}-\d{2}-\d{2}T/); // ISO format

    // Should be retrievable from storage
    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    expect(sessions[0].id).toBe("test-session-1");
    expect(sessions[0].createdAt).toBe(saved.createdAt);
  });

  it("should preserve original createdAt when updating existing session", async () => {
    // Create initial session
    const sessionData = {
      id: "test-session-2",
      type: "workflow" as const,
      name: "Test Pipeline",
      topic: "Test Topic",
      status: "running",
      artifacts: ["artifact-1"],
      metadata: {
        totalDurationMs: 1000,
      },
    };

    const firstSave = saveSession(sessionData);
    const originalCreatedAt = firstSave.createdAt;

    // Wait a bit to ensure timestamp would be different
    await new Promise(resolve => setTimeout(resolve, 10));

    // Update the session with new data
    const updatedData = {
      id: "test-session-2",
      type: "workflow" as const,
      name: "Test Pipeline",
      topic: "Test Topic",
      status: "completed",
      artifacts: ["artifact-1", "artifact-2", "artifact-3"],
      metadata: {
        totalDurationMs: 5000,
        agentStepsCount: 3,
      },
    };

    const secondSave = saveSession(updatedData);

    // Should preserve the original createdAt
    expect(secondSave.createdAt).toBe(originalCreatedAt);

    // Verify in storage
    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    expect(sessions[0].createdAt).toBe(originalCreatedAt);
    expect(sessions[0].status).toBe("completed");
    expect(sessions[0].artifacts).toHaveLength(3);
  });

  it("should preserve createdAt through multiple updates", async () => {
    // Create initial session
    const sessionData = {
      id: "test-session-3",
      type: "team" as const,
      name: "Team Session",
      topic: "Multi-update Test",
      status: "pending",
      artifacts: [],
      metadata: {},
    };

    const firstSave = saveSession(sessionData);
    const originalCreatedAt = firstSave.createdAt;

    // Perform multiple updates
    for (let i = 1; i <= 5; i++) {
      await new Promise(resolve => setTimeout(resolve, 5));
      
      const updated = saveSession({
        ...sessionData,
        status: `iteration-${i}`,
        artifacts: Array(i).fill("artifact").map((a, idx) => `${a}-${idx}`),
      });

      // Each update should preserve the original createdAt
      expect(updated.createdAt).toBe(originalCreatedAt);
    }

    // Final verification
    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(1);
    expect(sessions[0].createdAt).toBe(originalCreatedAt);
    expect(sessions[0].status).toBe("iteration-5");
    expect(sessions[0].artifacts).toHaveLength(5);
  });

  it("should handle multiple different sessions correctly", () => {
    // Create multiple sessions
    const session1 = saveSession({
      id: "session-1",
      type: "workflow" as const,
      name: "Pipeline 1",
      topic: "Topic 1",
      status: "completed",
      artifacts: [],
    });

    const session2 = saveSession({
      id: "session-2",
      type: "team" as const,
      name: "Team 2",
      topic: "Topic 2",
      status: "running",
      artifacts: [],
    });

    const session3 = saveSession({
      id: "session-3",
      type: "recipe" as const,
      name: "Recipe 3",
      topic: "Topic 3",
      status: "pending",
      artifacts: [],
    });

    // Each should have its own createdAt
    expect(session1.createdAt).toBeDefined();
    expect(session2.createdAt).toBeDefined();
    expect(session3.createdAt).toBeDefined();

    // Update session 2
    const updatedSession2 = saveSession({
      id: "session-2",
      type: "team" as const,
      name: "Team 2",
      topic: "Topic 2",
      status: "completed",
      artifacts: ["art-1"],
    });

    // Should preserve session 2's original createdAt
    expect(updatedSession2.createdAt).toBe(session2.createdAt);

    // Verify all sessions in storage
    const sessions = getStoredSessions();
    expect(sessions).toHaveLength(3);
    
    const stored1 = sessions.find(s => s.id === "session-1");
    const stored2 = sessions.find(s => s.id === "session-2");
    const stored3 = sessions.find(s => s.id === "session-3");

    expect(stored1?.createdAt).toBe(session1.createdAt);
    expect(stored2?.createdAt).toBe(session2.createdAt);
    expect(stored3?.createdAt).toBe(session3.createdAt);
    expect(stored2?.status).toBe("completed");
  });
});
