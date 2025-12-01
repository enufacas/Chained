/**
 * Storage utilities for persisting AG-UI data
 *
 * Provides localStorage-based persistence for:
 * - Artifacts from team/recipe/pipeline runs
 * - Session history
 * - User preferences
 */

// Storage keys
const STORAGE_KEYS = {
  ARTIFACTS: "ag-ui-artifacts",
  SESSIONS: "ag-ui-sessions",
  PIPELINES: "ag-ui-pipelines",
  PREFERENCES: "ag-ui-preferences",
} as const;

// Types
export interface StoredArtifact {
  id: string;
  name: string;
  type: string;
  data: string;
  preview?: string;
  source: "pipeline" | "team" | "recipe" | "chat";
  sourceId: string;
  sourceName: string;
  createdAt: string;
  agentName?: string;
  phase?: string;
}

export interface StoredSession {
  id: string;
  type: "pipeline" | "team" | "recipe";
  name: string;
  topic: string;
  status: string;
  createdAt: string;
  completedAt?: string;
  artifacts: string[]; // artifact IDs
  metadata?: Record<string, unknown>;
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
 * Save an artifact to storage
 */
export function saveArtifact(artifact: Omit<StoredArtifact, "id" | "createdAt">): StoredArtifact {
  const stored: StoredArtifact = {
    ...artifact,
    id: `artifact-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
    createdAt: new Date().toISOString(),
  };

  if (!isStorageAvailable()) return stored;

  try {
    const artifacts = getStoredArtifacts();
    artifacts.unshift(stored);

    // Keep only the most recent artifacts
    const trimmed = artifacts.slice(0, MAX_ARTIFACTS);
    localStorage.setItem(STORAGE_KEYS.ARTIFACTS, JSON.stringify(trimmed));
  } catch (error) {
    console.warn("Failed to save artifact to storage:", error);
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
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(trimmed));
  } catch (error) {
    console.warn("Failed to save session to storage:", error);
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
    localStorage.removeItem(STORAGE_KEYS.PIPELINES);
  } catch (error) {
    console.warn("Failed to clear storage:", error);
  }
}
