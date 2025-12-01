/**
 * Storage utilities tests
 * 
 * Tests for session and artifact persistence in localStorage
 */

// Mock localStorage for Node environment
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

// Mock window and localStorage globally before importing storage
Object.defineProperty(global, 'window', {
  value: {
    localStorage: localStorageMock,
  },
  writable: true,
});

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Mock crypto.randomUUID for Node < 19
if (typeof crypto === 'undefined' || !crypto.randomUUID) {
  Object.defineProperty(global, 'crypto', {
    value: {
      randomUUID: () => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
          const r = (Math.random() * 16) | 0;
          const v = c === 'x' ? r : (r & 0x3) | 0x8;
          return v.toString(16);
        });
      },
    },
    writable: true,
  });
}

import {
  saveSession,
  getStoredSessions,
  saveArtifact,
  getStoredArtifacts,
  clearAllStorage,
} from '@/lib/storage';

describe('Storage utilities', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  describe('Session persistence', () => {
    it('should save and retrieve a basic session', () => {
      const session = saveSession({
        id: 'test-session-1',
        type: 'team',
        name: 'Test Session',
        topic: 'Test Topic',
        status: 'completed',
        artifacts: [],
        metadata: {
          recipeId: 'test-recipe',
          currentTurn: 2,
          totalTurns: 2,
        },
      });

      expect(session.id).toBe('test-session-1');
      expect(session.createdAt).toBeDefined();

      const sessions = getStoredSessions();
      expect(sessions).toHaveLength(1);
      expect(sessions[0].id).toBe('test-session-1');
      expect(sessions[0].name).toBe('Test Session');
    });

    it('should persist turnResults with A2A protocol objects', () => {
      const turnResults = [
        {
          stepIndex: 0,
          agentId: 'test-agent',
          agentName: 'Test Agent',
          status: 'completed' as const,
          startedAt: '2025-12-01T00:00:00Z',
          completedAt: '2025-12-01T00:00:30Z',
          durationMs: 30000,
          taskId: 'task-123',
          contextId: 'context-456',
          message: 'Task completed successfully',
          turnNumber: 1,
          artifacts: [
            { name: 'result.json', type: 'application/json', data: '{"key":"value"}' }
          ],
          agentCard: { name: 'Test Agent', capabilities: ['research'] },
          task: { id: 'task-123', status: 'completed' },
          userMessage: { role: 'user', parts: [{ text: 'Do research' }] },
          agentMessage: { role: 'agent', parts: [{ text: 'Research complete' }] },
        },
      ];

      const session = saveSession({
        id: 'session-with-turns',
        type: 'team',
        name: 'Session With Turns',
        topic: 'Test with turnResults',
        status: 'completed',
        completedAt: '2025-12-01T00:01:00Z',
        artifacts: [],
        metadata: {
          recipeId: 'test-recipe',
          currentTurn: 1,
          totalTurns: 1,
          turnResults,
          config: {
            maxTurnsPerAgent: 2,
            executionMode: 'sequential' as const,
          },
          finalResult: { success: true },
        },
      });

      const sessions = getStoredSessions();
      expect(sessions).toHaveLength(1);
      
      const retrievedSession = sessions[0];
      expect(retrievedSession.metadata?.turnResults).toBeDefined();
      
      const retrievedTurns = retrievedSession.metadata?.turnResults as typeof turnResults;
      expect(retrievedTurns).toHaveLength(1);
      expect(retrievedTurns[0].agentId).toBe('test-agent');
      expect(retrievedTurns[0].taskId).toBe('task-123');
      expect(retrievedTurns[0].turnNumber).toBe(1);
      
      // Verify A2A protocol objects are preserved
      expect(retrievedTurns[0].agentCard).toEqual({ name: 'Test Agent', capabilities: ['research'] });
      expect(retrievedTurns[0].task).toEqual({ id: 'task-123', status: 'completed' });
      expect(retrievedTurns[0].userMessage).toBeDefined();
      expect(retrievedTurns[0].agentMessage).toBeDefined();
    });

    it('should persist config and finalResult', () => {
      const session = saveSession({
        id: 'session-with-config',
        type: 'team',
        name: 'Session With Config',
        topic: 'Test config persistence',
        status: 'completed',
        artifacts: [],
        metadata: {
          recipeId: 'test-recipe',
          currentTurn: 4,
          totalTurns: 4,
          turnResults: [],
          config: {
            maxTurnsPerAgent: 2,
            executionMode: 'parallel' as const,
          },
          finalResult: {
            success: true,
            duration: 120000,
            artifactsGenerated: 5,
          },
        },
      });

      const sessions = getStoredSessions();
      const retrieved = sessions[0];
      
      expect(retrieved.metadata?.config).toEqual({
        maxTurnsPerAgent: 2,
        executionMode: 'parallel',
      });
      
      expect(retrieved.metadata?.finalResult).toEqual({
        success: true,
        duration: 120000,
        artifactsGenerated: 5,
      });
    });

    it('should update existing session', () => {
      // Save initial session
      saveSession({
        id: 'update-test',
        type: 'team',
        name: 'Initial',
        topic: 'Test',
        status: 'running',
        artifacts: [],
        metadata: {
          recipeId: 'test',
          currentTurn: 0,
          totalTurns: 2,
          turnResults: [],
        },
      });

      // Update with completed status and turnResults
      saveSession({
        id: 'update-test',
        type: 'team',
        name: 'Updated',
        topic: 'Test Updated',
        status: 'completed',
        completedAt: '2025-12-01T00:02:00Z',
        artifacts: [],
        metadata: {
          recipeId: 'test',
          currentTurn: 2,
          totalTurns: 2,
          turnResults: [
            {
              stepIndex: 0,
              agentId: 'agent1',
              agentName: 'Agent 1',
              status: 'completed' as const,
              startedAt: '2025-12-01T00:00:00Z',
              artifacts: [],
            },
          ],
        },
      });

      const sessions = getStoredSessions();
      expect(sessions).toHaveLength(1); // Should still be 1 (updated, not duplicate)
      expect(sessions[0].name).toBe('Updated');
      expect(sessions[0].status).toBe('completed');
      expect(sessions[0].metadata?.currentTurn).toBe(2);
      expect(sessions[0].metadata?.turnResults).toHaveLength(1);
    });
  });

  describe('Artifact persistence', () => {
    it('should save and retrieve artifacts', () => {
      const artifact = saveArtifact({
        name: 'test-artifact.json',
        type: 'application/json',
        data: '{"test": true}',
        preview: 'Test artifact',
        source: 'team',
        sourceId: 'session-123',
        sourceName: 'Test Session',
        agentName: 'test-agent',
        phase: 'Turn 1',
      });

      expect(artifact.id).toBeDefined();
      expect(artifact.createdAt).toBeDefined();

      const artifacts = getStoredArtifacts();
      expect(artifacts).toHaveLength(1);
      expect(artifacts[0].name).toBe('test-artifact.json');
    });
  });

  describe('Storage cleanup', () => {
    it('should clear all storage', () => {
      // Add some data
      saveSession({
        id: 'test',
        type: 'team',
        name: 'Test',
        topic: 'Test',
        status: 'completed',
        artifacts: [],
        metadata: {},
      });
      
      saveArtifact({
        name: 'test.json',
        type: 'application/json',
        data: '{}',
        source: 'team',
        sourceId: 'test',
        sourceName: 'Test',
      });

      expect(getStoredSessions()).toHaveLength(1);
      expect(getStoredArtifacts()).toHaveLength(1);

      clearAllStorage();

      expect(getStoredSessions()).toHaveLength(0);
      expect(getStoredArtifacts()).toHaveLength(0);
    });
  });
});
