/**
 * Storage Cleanup Utilities
 * 
 * Provides utilities for cleaning up localStorage when quota is exceeded.
 * These functions can be called manually or automatically.
 */

import { getStoredArtifacts, getStoredSessions, clearAllStorage } from './storage';

const STORAGE_KEYS = {
  ARTIFACTS: "ag-ui-artifacts",
  SESSIONS: "ag-ui-sessions",
  PREFERENCES: "ag-ui-preferences",
} as const;

/**
 * Get storage usage statistics
 */
export function getStorageUsage(): {
  used: number;
  usedMB: string;
  total: number;
  totalMB: string;
  percentage: number;
  isNearLimit: boolean;
} {
  let used = 0;
  
  try {
    // Estimate used storage
    for (const key of Object.values(STORAGE_KEYS)) {
      const value = localStorage.getItem(key);
      if (value) {
        used += new Blob([value]).size;
      }
    }
  } catch {
    used = 0;
  }
  
  // localStorage typically has 5-10MB limit, we'll use 5MB as conservative estimate
  const total = 5 * 1024 * 1024; // 5MB
  const percentage = (used / total) * 100;
  const isNearLimit = percentage > 70; // Consider "near limit" at 70%
  
  return {
    used,
    usedMB: (used / (1024 * 1024)).toFixed(2),
    total,
    totalMB: (total / (1024 * 1024)).toFixed(2),
    percentage: Math.round(percentage),
    isNearLimit,
  };
}

/**
 * Clear old artifacts (keeps only recent N)
 */
export function clearOldArtifacts(keepCount: number = 20): number {
  try {
    const artifacts = getStoredArtifacts();
    const kept = artifacts.slice(0, keepCount);
    localStorage.setItem(STORAGE_KEYS.ARTIFACTS, JSON.stringify(kept));
    return artifacts.length - kept.length;
  } catch {
    return 0;
  }
}

/**
 * Clear old sessions (keeps only recent N)
 */
export function clearOldSessions(keepCount: number = 5): number {
  try {
    const sessions = getStoredSessions();
    const kept = sessions.slice(0, keepCount);
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(kept));
    return sessions.length - kept.length;
  } catch {
    return 0;
  }
}

/**
 * Perform aggressive cleanup to free maximum space
 * Returns amount of space freed in bytes
 */
export function performAggressiveCleanup(): {
  artifactsRemoved: number;
  sessionsRemoved: number;
  spaceFreedMB: string;
  success: boolean;
} {
  const beforeUsage = getStorageUsage();
  
  try {
    // Keep only 10 most recent artifacts
    const artifactsRemoved = clearOldArtifacts(10);
    
    // Keep only 3 most recent sessions
    const sessionsRemoved = clearOldSessions(3);
    
    const afterUsage = getStorageUsage();
    const spaceFreed = beforeUsage.used - afterUsage.used;
    
    return {
      artifactsRemoved,
      sessionsRemoved,
      spaceFreedMB: (spaceFreed / (1024 * 1024)).toFixed(2),
      success: true,
    };
  } catch (error) {
    console.error("Aggressive cleanup failed:", error);
    return {
      artifactsRemoved: 0,
      sessionsRemoved: 0,
      spaceFreedMB: "0",
      success: false,
    };
  }
}

/**
 * Clear all storage (nuclear option)
 */
export function clearAllData(): void {
  clearAllStorage();
  console.log("✅ All storage cleared");
}

/**
 * Check if cleanup is recommended
 */
export function isCleanupRecommended(): {
  recommended: boolean;
  reason: string;
  usagePercentage: number;
} {
  const usage = getStorageUsage();
  
  if (usage.percentage > 80) {
    return {
      recommended: true,
      reason: `Storage is ${usage.percentage}% full. Cleanup strongly recommended.`,
      usagePercentage: usage.percentage,
    };
  }
  
  if (usage.percentage > 60) {
    return {
      recommended: true,
      reason: `Storage is ${usage.percentage}% full. Cleanup recommended to prevent quota errors.`,
      usagePercentage: usage.percentage,
    };
  }
  
  return {
    recommended: false,
    reason: `Storage usage is healthy at ${usage.percentage}%.`,
    usagePercentage: usage.percentage,
  };
}

/**
 * Auto cleanup if approaching limit
 * Returns true if cleanup was performed
 */
export function autoCleanupIfNeeded(): boolean {
  const check = isCleanupRecommended();
  
  if (check.recommended && check.usagePercentage > 70) {
    console.log(`🧹 Auto-cleanup triggered: ${check.reason}`);
    performAggressiveCleanup();
    return true;
  }
  
  return false;
}
