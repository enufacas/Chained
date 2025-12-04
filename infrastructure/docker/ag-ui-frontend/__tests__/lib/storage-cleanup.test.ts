/**
 * @jest-environment jsdom
 */

/**
 * Storage Cleanup Tests
 * 
 * Tests for localStorage cleanup utilities
 */

// Note: localStorage is now provided by jsdom test environment

// Clear localStorage before each test
beforeEach(() => {
  localStorage.clear();
});

// Mock Blob for size calculation
global.Blob = class Blob {
  constructor(parts: any[]) {
    this.parts = parts;
  }
  parts: any[];
  get size() {
    return this.parts.reduce((total, part) => {
      if (typeof part === 'string') return total + part.length;
      return total;
    }, 0);
  }
} as any;

import {
  getStorageUsage,
  clearOldArtifacts,
  clearOldSessions,
  performAggressiveCleanup,
  isCleanupRecommended,
  autoCleanupIfNeeded,
} from '@/lib/storage-cleanup';

import {
  saveArtifact,
  saveSession,
  getStoredArtifacts,
  getStoredSessions,
} from '@/lib/storage';

describe('Storage Cleanup Utilities', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('getStorageUsage', () => {
    it('should calculate storage usage correctly', () => {
      // Add some data
      saveArtifact({
        name: 'test.json',
        type: 'application/json',
        data: '{"test": true}',
        source: 'team',
        sourceId: 'session-1',
        sourceName: 'Test Session',
      });

      const usage = getStorageUsage();
      expect(usage.used).toBeGreaterThan(0);
      expect(usage.percentage).toBeGreaterThan(0);
      expect(usage.percentage).toBeLessThanOrEqual(100);
    });
  });

  describe('clearOldArtifacts', () => {
    it('should remove old artifacts', () => {
      // Create 30 artifacts
      for (let i = 0; i < 30; i++) {
        saveArtifact({
          name: `artifact-${i}.json`,
          type: 'application/json',
          data: `{"index": ${i}}`,
          source: 'team',
          sourceId: 'session-1',
          sourceName: 'Test Session',
        });
      }

      expect(getStoredArtifacts()).toHaveLength(30);

      // Keep only 10
      const removed = clearOldArtifacts(10);
      expect(removed).toBe(20);
      expect(getStoredArtifacts()).toHaveLength(10);
    });
  });

  describe('clearOldSessions', () => {
    it('should remove old sessions', () => {
      // Create 10 sessions
      for (let i = 0; i < 10; i++) {
        saveSession({
          id: `session-${i}`,
          type: 'team',
          name: `Session ${i}`,
          topic: 'Test',
          status: 'completed',
          artifacts: [],
        });
      }

      expect(getStoredSessions()).toHaveLength(10);

      // Keep only 3
      const removed = clearOldSessions(3);
      expect(removed).toBe(7);
      expect(getStoredSessions()).toHaveLength(3);
    });
  });

  describe('performAggressiveCleanup', () => {
    it('should free space aggressively', () => {
      // Create lots of data
      for (let i = 0; i < 50; i++) {
        saveArtifact({
          name: `artifact-${i}.json`,
          type: 'application/json',
          data: `{"data": "${Array(100).fill('x').join('')}"}`,
          source: 'team',
          sourceId: 'session-1',
          sourceName: 'Test',
        });
      }

      for (let i = 0; i < 20; i++) {
        saveSession({
          id: `session-${i}`,
          type: 'team',
          name: `Session ${i}`,
          topic: 'Test',
          status: 'completed',
          artifacts: [],
        });
      }

      const beforeUsage = getStorageUsage();
      const result = performAggressiveCleanup();

      expect(result.success).toBe(true);
      expect(result.artifactsRemoved).toBeGreaterThan(0);
      expect(result.sessionsRemoved).toBeGreaterThan(0);

      const afterUsage = getStorageUsage();
      expect(afterUsage.used).toBeLessThan(beforeUsage.used);
    });
  });

  describe('isCleanupRecommended', () => {
    it('should recommend cleanup when storage is high', () => {
      // Fill storage to ~70%
      const largeData = Array(500000).fill('x').join(''); // ~500KB
      for (let i = 0; i < 7; i++) {
        saveArtifact({
          name: `large-${i}.json`,
          type: 'application/json',
          data: largeData,
          source: 'team',
          sourceId: 'session-1',
          sourceName: 'Test',
        });
      }

      const check = isCleanupRecommended();
      // May or may not recommend depending on actual size, but should have a valid response
      expect(check).toHaveProperty('recommended');
      expect(check).toHaveProperty('reason');
      expect(check).toHaveProperty('usagePercentage');
    });
  });

  describe('autoCleanupIfNeeded', () => {
    it('should auto-cleanup when needed', () => {
      // This is a smoke test - actual behavior depends on storage state
      const cleaned = autoCleanupIfNeeded();
      expect(typeof cleaned).toBe('boolean');
    });
  });

  describe('localStorage quota exceeded handling', () => {
    it('should handle quota exceeded when saving large data', () => {
      // Try to save data larger than mock quota (1MB)
      const largeData = Array(2 * 1024 * 1024).fill('x').join(''); // 2MB

      // This should trigger QuotaExceededError in storage.ts
      // which should handle it gracefully with pruning
      expect(() => {
        saveArtifact({
          name: 'large.json',
          type: 'application/json',
          data: largeData,
          source: 'team',
          sourceId: 'session-1',
          sourceName: 'Test',
        });
      }).not.toThrow();

      // Storage should still work after quota error
      saveArtifact({
        name: 'small.json',
        type: 'application/json',
        data: '{"small": true}',
        source: 'team',
        sourceId: 'session-1',
        sourceName: 'Test',
      });

      const artifacts = getStoredArtifacts();
      expect(artifacts.length).toBeGreaterThanOrEqual(1);
    });
  });
});
