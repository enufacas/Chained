/**
 * Storage utilities for persisting AG-UI data
 *
 * Provides localStorage-based persistence for:
 * - Artifacts from team/recipe/workflow runs
 * - Session history
 * - User preferences
 * - A2A protocol objects (agent cards, tasks, messages)
 */

import { logStorageError } from "./error-logging";

// Storage keys
const STORAGE_KEYS = {
  ARTIFACTS: "ag-ui-artifacts",
  SESSIONS: "ag-ui-sessions",
  PREFERENCES: "ag-ui-preferences",
} as const;

// A2A Protocol artifact types
// See: https://a2a-protocol.org/ for protocol specification
export type A2AArtifactType = 
  | "agent-card"       // A2A Agent Card - metadata about agent capabilities (agent.json)
  | "task"             // A2A Task - represents a unit of work with status and artifacts
  | "message"          // A2A Message - communication between user and agent
  | "artifact"         // Standard artifact - data/content produced by agents
  | "workflow-context"; // Workflow context - state shared across agents in a workflow

// Types
export interface StoredArtifact {
  id: string;
  name: string;
  type: string;
  data: string;
  preview?: string;
  source: "workflow" | "team" | "recipe" | "chat";  // Renamed from "pipeline" to "workflow"
  sourceId: string;
  sourceName: string;
  createdAt: string;
  agentName?: string;
  phase?: string;
  // A2A Protocol metadata
  a2aType?: A2AArtifactType;
  taskId?: string;
  contextId?: string;
}

export interface StoredSession {
  id: string;
  type: "workflow" | "team" | "recipe";  // Renamed from "pipeline" to "workflow"
  name: string;
  topic: string;
  status: string;
  createdAt: string;
  completedAt?: string;
  artifacts: string[]; // artifact IDs
  metadata?: Record<string, unknown>;
  // A2A Protocol metadata
  a2aContextId?: string;
  agentCards?: string[]; // IDs of stored agent cards
  taskIds?: string[]; // IDs of A2A tasks
}

export interface UserPreferences {
  artifactView: "grid" | "list";
  autoExpandSteps: boolean;
  showPreviewOnHover: boolean;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  artifactView: "grid",
  autoExpandSteps: false,
  showPreviewOnHover: true,
};

// Max items to keep in storage
const MAX_ARTIFACTS = 100;
const MAX_SESSIONS = 50;

// Storage size limits (in bytes)
const MAX_STORAGE_SIZE = 4 * 1024 * 1024; // 4MB (localStorage typically has 5-10MB limit)
const STORAGE_WARNING_THRESHOLD = 3 * 1024 * 1024; // 3MB - warn at 75%

/**
 * Get current storage size in bytes
 */
function getCurrentStorageSize(): number {
  if (!isStorageAvailable()) return 0;
  try {
    let total = 0;
    for (const key of Object.values(STORAGE_KEYS)) {
      const value = localStorage.getItem(key);
      if (value) {
        total += new Blob([value]).size;
      }
    }
    return total;
  } catch {
    return 0;
  }
}

/**
 * Check if we're approaching storage quota
 */
function isStorageNearLimit(): boolean {
  return getCurrentStorageSize() >= STORAGE_WARNING_THRESHOLD;
}

/**
 * Free up storage space by removing old items
 */
function pruneStorage(): void {
  if (!isStorageAvailable()) return;
  
  try {
    // Remove oldest artifacts first
    const artifacts = getStoredArtifacts();
    if (artifacts.length > MAX_ARTIFACTS / 2) {
      const kept = artifacts.slice(0, Math.floor(MAX_ARTIFACTS / 2));
      localStorage.setItem(STORAGE_KEYS.ARTIFACTS, JSON.stringify(kept));
      console.log(`🧹 Pruned ${artifacts.length - kept.length} old artifacts to free space`);
    }
    
    // Remove oldest sessions
    const sessions = getStoredSessions();
    if (sessions.length > MAX_SESSIONS / 2) {
      const kept = sessions.slice(0, Math.floor(MAX_SESSIONS / 2));
      localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(kept));
      console.log(`🧹 Pruned ${sessions.length - kept.length} old sessions to free space`);
    }
  } catch (error) {
    console.warn("Failed to prune storage:", error);
  }
}

/**
 * Check if localStorage is available
 */
function isStorageAvailable(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const test = "__storage_test__";
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get all stored artifacts
 */
export function getStoredArtifacts(): StoredArtifact[] {
  if (!isStorageAvailable()) return [];
  try {
    const data = localStorage.getItem(STORAGE_KEYS.ARTIFACTS);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

/**
 * Generate a unique ID using crypto.randomUUID when available
 */
function generateId(prefix: string): string {
  const randomPart = typeof crypto !== 'undefined' && crypto.randomUUID 
    ? crypto.randomUUID().substring(0, 12)
    : `${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
  return `${prefix}-${randomPart}`;
}

/**
 * Save an artifact to storage
 */
export function saveArtifact(artifact: Omit<StoredArtifact, "id" | "createdAt">): StoredArtifact {
  const stored: StoredArtifact = {
    ...artifact,
    id: generateId("artifact"),
    createdAt: new Date().toISOString(),
  };

  if (!isStorageAvailable()) return stored;

  try {
    // Check if we're approaching storage limit and prune if needed
    if (isStorageNearLimit()) {
      console.warn("⚠️ Storage approaching limit, pruning old data...");
      pruneStorage();
    }
    
    const artifacts = getStoredArtifacts();
    artifacts.unshift(stored);

    // Keep only the most recent artifacts
    const trimmed = artifacts.slice(0, MAX_ARTIFACTS);
    
    // Try to save, catch quota errors
    try {
      localStorage.setItem(STORAGE_KEYS.ARTIFACTS, JSON.stringify(trimmed));
    } catch (quotaError: any) {
      if (quotaError.name === "QuotaExceededError") {
        console.warn("💾 Storage quota exceeded, aggressive pruning...");
        // Try aggressive pruning
        pruneStorage();
        // Try saving with reduced list
        const reduced = artifacts.slice(0, Math.floor(MAX_ARTIFACTS / 4));
        localStorage.setItem(STORAGE_KEYS.ARTIFACTS, JSON.stringify(reduced));
        console.log(`✅ Saved after pruning to ${reduced.length} artifacts`);
      } else {
        throw quotaError;
      }
    }
  } catch (error) {
    console.warn("Failed to save artifact to storage:", error);
    logStorageError(error, "saveArtifact", STORAGE_KEYS.ARTIFACTS, {
      artifactName: artifact.name,
      artifactType: artifact.type,
      sourceId: artifact.sourceId,
    });
  }

  return stored;
}

/**
 * Save multiple artifacts at once
 */
export function saveArtifacts(
  artifacts: Array<{
    name: string;
    type: string;
    data: string;
    preview?: string;
  }>,
  source: StoredArtifact["source"],
  sourceId: string,
  sourceName: string,
  agentName?: string,
  phase?: string
): StoredArtifact[] {
  return artifacts.map((a) =>
    saveArtifact({
      ...a,
      source,
      sourceId,
      sourceName,
      agentName,
      phase,
    })
  );
}

/**
 * Get artifact by ID
 */
export function getArtifactById(id: string): StoredArtifact | undefined {
  const artifacts = getStoredArtifacts();
  return artifacts.find((a) => a.id === id);
}

/**
 * Get artifacts by source
 */
export function getArtifactsBySource(source: StoredArtifact["source"]): StoredArtifact[] {
  return getStoredArtifacts().filter((a) => a.source === source);
}

/**
 * Get artifacts by source ID
 */
export function getArtifactsBySourceId(sourceId: string): StoredArtifact[] {
  return getStoredArtifacts().filter((a) => a.sourceId === sourceId);
}

/**
 * Delete an artifact
 */
export function deleteArtifact(id: string): void {
  if (!isStorageAvailable()) return;
  try {
    const artifacts = getStoredArtifacts().filter((a) => a.id !== id);
    localStorage.setItem(STORAGE_KEYS.ARTIFACTS, JSON.stringify(artifacts));
  } catch (error) {
    console.warn("Failed to delete artifact:", error);
  }
}

/**
 * Clear all artifacts
 */
export function clearArtifacts(): void {
  if (!isStorageAvailable()) return;
  try {
    localStorage.removeItem(STORAGE_KEYS.ARTIFACTS);
  } catch (error) {
    console.warn("Failed to clear artifacts:", error);
  }
}

// ============================================================================
// A2A Protocol Artifact Helpers
// ============================================================================

/**
 * Save an A2A Agent Card as an artifact
 */
export function saveAgentCard(
  agentCard: object,
  agentName: string,
  source: StoredArtifact["source"],
  sourceId: string,
  sourceName: string
): StoredArtifact {
  return saveArtifact({
    name: `${agentName} Agent Card`,
    type: "application/json",
    data: JSON.stringify(agentCard, null, 2),
    preview: `A2A Agent Card for ${agentName}`,
    source,
    sourceId,
    sourceName,
    agentName,
    a2aType: "agent-card",
  });
}

/**
 * Save an A2A Task as an artifact
 */
export function saveA2ATask(
  task: object & { id?: string; contextId?: string },
  agentName: string,
  source: StoredArtifact["source"],
  sourceId: string,
  sourceName: string,
  phase?: string
): StoredArtifact {
  const taskId = task.id || `task-${Date.now()}`;
  return saveArtifact({
    name: `${agentName} Task`,
    type: "application/json",
    data: JSON.stringify(task, null, 2),
    preview: `A2A Task ${taskId}`,
    source,
    sourceId,
    sourceName,
    agentName,
    phase,
    a2aType: "task",
    taskId,
    contextId: task.contextId,
  });
}

/**
 * Save an A2A Message as an artifact
 */
export function saveA2AMessage(
  message: object & { role?: string },
  agentName: string,
  source: StoredArtifact["source"],
  sourceId: string,
  sourceName: string,
  taskId?: string
): StoredArtifact {
  const role = (message as { role?: string }).role || "agent";
  return saveArtifact({
    name: `${agentName} Message (${role})`,
    type: "application/json",
    data: JSON.stringify(message, null, 2),
    preview: `A2A ${role} message from ${agentName}`,
    source,
    sourceId,
    sourceName,
    agentName,
    a2aType: "message",
    taskId,
  });
}

/**
 * Get artifacts by A2A type
 */
export function getArtifactsByA2AType(a2aType: A2AArtifactType): StoredArtifact[] {
  return getStoredArtifacts().filter((a) => a.a2aType === a2aType);
}

/**
 * Get A2A artifacts for a specific task
 */
export function getArtifactsByTaskId(taskId: string): StoredArtifact[] {
  return getStoredArtifacts().filter((a) => a.taskId === taskId);
}

// ============================================================================
// Session Storage
// ============================================================================

/**
 * Get all stored sessions
 */
export function getStoredSessions(): StoredSession[] {
  if (!isStorageAvailable()) return [];
  try {
    const data = localStorage.getItem(STORAGE_KEYS.SESSIONS);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

/**
 * Save a session to storage
 */
export function saveSession(session: Omit<StoredSession, "createdAt">): StoredSession {
  const stored: StoredSession = {
    ...session,
    createdAt: new Date().toISOString(),
  };

  if (!isStorageAvailable()) return stored;

  try {
    // Check storage limit
    if (isStorageNearLimit()) {
      console.warn("⚠️ Storage approaching limit, pruning old data...");
      pruneStorage();
    }
    
    const sessions = getStoredSessions();
    // Update existing or add new
    const existingIndex = sessions.findIndex((s) => s.id === session.id);
    if (existingIndex >= 0) {
      sessions[existingIndex] = stored;
    } else {
      sessions.unshift(stored);
    }

    // Keep only the most recent sessions
    const trimmed = sessions.slice(0, MAX_SESSIONS);
    
    // Try to save, catch quota errors
    try {
      localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(trimmed));
    } catch (quotaError: any) {
      if (quotaError.name === "QuotaExceededError") {
        console.warn("💾 Session storage quota exceeded, aggressive pruning...");
        pruneStorage();
        // Try with reduced list
        const reduced = sessions.slice(0, Math.floor(MAX_SESSIONS / 4));
        localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(reduced));
        console.log(`✅ Saved after pruning to ${reduced.length} sessions`);
      } else {
        throw quotaError;
      }
    }
  } catch (error) {
    console.warn("Failed to save session to storage:", error);
    logStorageError(error, "saveSession", STORAGE_KEYS.SESSIONS, {
      sessionId: session.id,
      sessionType: session.type,
      artifactsCount: session.artifacts?.length || 0,
    });
  }

  return stored;
}

/**
 * Get session by ID
 */
export function getSessionById(id: string): StoredSession | undefined {
  return getStoredSessions().find((s) => s.id === id);
}

/**
 * Get sessions by type
 */
export function getSessionsByType(type: StoredSession["type"]): StoredSession[] {
  return getStoredSessions().filter((s) => s.type === type);
}

/**
 * Delete a session
 */
export function deleteSession(id: string): void {
  if (!isStorageAvailable()) return;
  try {
    const sessions = getStoredSessions().filter((s) => s.id !== id);
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessions));
  } catch (error) {
    console.warn("Failed to delete session:", error);
  }
}

/**
 * Clear all sessions
 */
export function clearSessions(): void {
  if (!isStorageAvailable()) return;
  try {
    localStorage.removeItem(STORAGE_KEYS.SESSIONS);
  } catch (error) {
    console.warn("Failed to clear sessions:", error);
  }
}

// ============================================================================
// User Preferences
// ============================================================================

/**
 * Get user preferences
 */
export function getPreferences(): UserPreferences {
  if (!isStorageAvailable()) return DEFAULT_PREFERENCES;
  try {
    const data = localStorage.getItem(STORAGE_KEYS.PREFERENCES);
    return data ? { ...DEFAULT_PREFERENCES, ...JSON.parse(data) } : DEFAULT_PREFERENCES;
  } catch {
    return DEFAULT_PREFERENCES;
  }
}

/**
 * Save user preferences
 */
export function savePreferences(prefs: Partial<UserPreferences>): void {
  if (!isStorageAvailable()) return;
  try {
    const current = getPreferences();
    const updated = { ...current, ...prefs };
    localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(updated));
  } catch (error) {
    console.warn("Failed to save preferences:", error);
  }
}

// ============================================================================
// Storage Statistics
// ============================================================================

/**
 * Get storage statistics
 */
export function getStorageStats(): {
  artifactsCount: number;
  sessionsCount: number;
  estimatedSize: string;
} {
  const artifacts = getStoredArtifacts();
  const sessions = getStoredSessions();

  // Estimate storage size
  let size = 0;
  if (isStorageAvailable()) {
    try {
      const artifactsStr = localStorage.getItem(STORAGE_KEYS.ARTIFACTS) || "";
      const sessionsStr = localStorage.getItem(STORAGE_KEYS.SESSIONS) || "";
      size = artifactsStr.length + sessionsStr.length;
    } catch {
      // Ignore
    }
  }

  const estimatedSize =
    size < 1024
      ? `${size} B`
      : size < 1024 * 1024
      ? `${(size / 1024).toFixed(1)} KB`
      : `${(size / (1024 * 1024)).toFixed(1)} MB`;

  return {
    artifactsCount: artifacts.length,
    sessionsCount: sessions.length,
    estimatedSize,
  };
}

/**
 * Clear all storage
 */
export function clearAllStorage(): void {
  if (!isStorageAvailable()) return;
  try {
    localStorage.removeItem(STORAGE_KEYS.ARTIFACTS);
    localStorage.removeItem(STORAGE_KEYS.SESSIONS);
  } catch (error) {
    console.warn("Failed to clear storage:", error);
  }
}
