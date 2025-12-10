/**
 * Server-Side Persistence Layer for AG-UI
 * 
 * Provides persistent storage for sessions and artifacts using Firestore.
 * Falls back to in-memory storage for development.
 * 
 * Key features:
 * - Firestore-backed persistence for production
 * - In-memory fallback for development
 * - Pagination support for historical runs
 * - Complete session data with all turnResults
 * - Session recovery on server restart
 * 
 * This solves the volatility issue where sessions are lost when:
 * - Cloud Run instances scale down
 * - Server restarts/redeploys
 * - Container instances are replaced
 */

import { Firestore } from "@google-cloud/firestore";

// =============================================================================
// Types
// =============================================================================

export interface PersistedArtifact {
  id: string;
  name: string;
  type: string;
  data: string;
  preview?: string;
  source: "workflow" | "team" | "recipe" | "chat";
  sourceId: string;
  sourceName: string;
  createdAt: string;
  agentName?: string;
  phase?: string;
  // A2A Protocol metadata
  a2aType?: string;
  taskId?: string;
  contextId?: string;
}

export interface PersistedSession {
  id: string;
  type: "workflow" | "team" | "recipe";
  name: string;
  topic: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  artifacts: string[]; // artifact IDs
  metadata?: Record<string, unknown>;
  // A2A Protocol metadata
  a2aContextId?: string;
  agentCards?: string[];
  taskIds?: string[];
}

interface PaginatedResult<T> {
  items: T[];
  total: number;
  hasMore: boolean;
  nextCursor?: string;
}

// =============================================================================
// Abstract Store Interface
// =============================================================================

export interface PersistenceStore {
  // Session operations
  saveSession(session: PersistedSession): Promise<PersistedSession>;
  getSession(id: string): Promise<PersistedSession | null>;
  listSessions(
    type?: "workflow" | "team" | "recipe",
    limit?: number,
    cursor?: string
  ): Promise<PaginatedResult<PersistedSession>>;
  deleteSession(id: string): Promise<boolean>;
  
  // Artifact operations
  saveArtifact(artifact: PersistedArtifact): Promise<PersistedArtifact>;
  getArtifact(id: string): Promise<PersistedArtifact | null>;
  listArtifacts(
    sourceId?: string,
    limit?: number,
    cursor?: string
  ): Promise<PaginatedResult<PersistedArtifact>>;
  deleteArtifact(id: string): Promise<boolean>;
}

// =============================================================================
// In-Memory Store (Development Fallback)
// =============================================================================

class InMemoryStore implements PersistenceStore {
  private sessions: Map<string, PersistedSession> = new Map();
  private artifacts: Map<string, PersistedArtifact> = new Map();

  async saveSession(session: PersistedSession): Promise<PersistedSession> {
    session.updatedAt = new Date().toISOString();
    this.sessions.set(session.id, session);
    return session;
  }

  async getSession(id: string): Promise<PersistedSession | null> {
    return this.sessions.get(id) || null;
  }

  async listSessions(
    type?: "workflow" | "team" | "recipe",
    limit: number = 20,
    cursor?: string
  ): Promise<PaginatedResult<PersistedSession>> {
    let sessions = Array.from(this.sessions.values());
    
    // Filter by type
    if (type) {
      sessions = sessions.filter((s) => s.type === type);
    }
    
    // Sort by createdAt descending
    sessions.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
    
    // Handle pagination (simple offset-based for in-memory)
    const offset = cursor ? parseInt(cursor, 10) : 0;
    const items = sessions.slice(offset, offset + limit);
    const hasMore = sessions.length > offset + limit;
    const nextCursor = hasMore ? String(offset + limit) : undefined;
    
    return {
      items,
      total: sessions.length,
      hasMore,
      nextCursor,
    };
  }

  async deleteSession(id: string): Promise<boolean> {
    return this.sessions.delete(id);
  }

  async saveArtifact(artifact: PersistedArtifact): Promise<PersistedArtifact> {
    this.artifacts.set(artifact.id, artifact);
    return artifact;
  }

  async getArtifact(id: string): Promise<PersistedArtifact | null> {
    return this.artifacts.get(id) || null;
  }

  async listArtifacts(
    sourceId?: string,
    limit: number = 50,
    cursor?: string
  ): Promise<PaginatedResult<PersistedArtifact>> {
    let artifacts = Array.from(this.artifacts.values());
    
    // Filter by sourceId
    if (sourceId) {
      artifacts = artifacts.filter((a) => a.sourceId === sourceId);
    }
    
    // Sort by createdAt descending
    artifacts.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
    
    // Handle pagination
    const offset = cursor ? parseInt(cursor, 10) : 0;
    const items = artifacts.slice(offset, offset + limit);
    const hasMore = artifacts.length > offset + limit;
    const nextCursor = hasMore ? String(offset + limit) : undefined;
    
    return {
      items,
      total: artifacts.length,
      hasMore,
      nextCursor,
    };
  }

  async deleteArtifact(id: string): Promise<boolean> {
    return this.artifacts.delete(id);
  }
}

// =============================================================================
// Firestore Store (Production)
// =============================================================================

class FirestoreStore implements PersistenceStore {
  private db: Firestore;
  private sessionsCollection = "ag_ui_sessions";
  private artifactsCollection = "ag_ui_artifacts";

  constructor(projectId?: string) {
    this.db = new Firestore({
      projectId: projectId || process.env.GCP_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT,
    });
  }

  async saveSession(session: PersistedSession): Promise<PersistedSession> {
    session.updatedAt = new Date().toISOString();
    const docRef = this.db.collection(this.sessionsCollection).doc(session.id);
    await docRef.set(session);
    return session;
  }

  async getSession(id: string): Promise<PersistedSession | null> {
    const docRef = this.db.collection(this.sessionsCollection).doc(id);
    const doc = await docRef.get();
    return doc.exists ? (doc.data() as PersistedSession) : null;
  }

  async listSessions(
    type?: "workflow" | "team" | "recipe",
    limit: number = 20,
    cursor?: string
  ): Promise<PaginatedResult<PersistedSession>> {
    let query = this.db
      .collection(this.sessionsCollection)
      .orderBy("createdAt", "desc")
      .limit(limit + 1); // +1 to check if there are more
    
    // Filter by type
    if (type) {
      query = query.where("type", "==", type);
    }
    
    // Handle cursor (pagination)
    if (cursor) {
      const cursorDoc = await this.db
        .collection(this.sessionsCollection)
        .doc(cursor)
        .get();
      if (cursorDoc.exists) {
        query = query.startAfter(cursorDoc);
      }
    }
    
    const snapshot = await query.get();
    const items = snapshot.docs.slice(0, limit).map((doc) => doc.data() as PersistedSession);
    const hasMore = snapshot.docs.length > limit;
    const nextCursor = hasMore ? snapshot.docs[limit - 1].id : undefined;
    
    // Get total count (for display)
    let totalQuery = this.db.collection(this.sessionsCollection);
    if (type) {
      totalQuery = totalQuery.where("type", "==", type) as any;
    }
    const countSnapshot = await totalQuery.count().get();
    const total = countSnapshot.data().count;
    
    return {
      items,
      total,
      hasMore,
      nextCursor,
    };
  }

  async deleteSession(id: string): Promise<boolean> {
    try {
      await this.db.collection(this.sessionsCollection).doc(id).delete();
      return true;
    } catch {
      return false;
    }
  }

  async saveArtifact(artifact: PersistedArtifact): Promise<PersistedArtifact> {
    const docRef = this.db.collection(this.artifactsCollection).doc(artifact.id);
    await docRef.set(artifact);
    return artifact;
  }

  async getArtifact(id: string): Promise<PersistedArtifact | null> {
    const docRef = this.db.collection(this.artifactsCollection).doc(id);
    const doc = await docRef.get();
    return doc.exists ? (doc.data() as PersistedArtifact) : null;
  }

  async listArtifacts(
    sourceId?: string,
    limit: number = 50,
    cursor?: string
  ): Promise<PaginatedResult<PersistedArtifact>> {
    let query = this.db
      .collection(this.artifactsCollection)
      .orderBy("createdAt", "desc")
      .limit(limit + 1);
    
    // Filter by sourceId
    if (sourceId) {
      query = query.where("sourceId", "==", sourceId);
    }
    
    // Handle cursor
    if (cursor) {
      const cursorDoc = await this.db
        .collection(this.artifactsCollection)
        .doc(cursor)
        .get();
      if (cursorDoc.exists) {
        query = query.startAfter(cursorDoc);
      }
    }
    
    const snapshot = await query.get();
    const items = snapshot.docs.slice(0, limit).map((doc) => doc.data() as PersistedArtifact);
    const hasMore = snapshot.docs.length > limit;
    const nextCursor = hasMore ? snapshot.docs[limit - 1].id : undefined;
    
    // Get total count
    let totalQuery = this.db.collection(this.artifactsCollection);
    if (sourceId) {
      totalQuery = totalQuery.where("sourceId", "==", sourceId) as any;
    }
    const countSnapshot = await totalQuery.count().get();
    const total = countSnapshot.data().count;
    
    return {
      items,
      total,
      hasMore,
      nextCursor,
    };
  }

  async deleteArtifact(id: string): Promise<boolean> {
    try {
      await this.db.collection(this.artifactsCollection).doc(id).delete();
      return true;
    } catch {
      return false;
    }
  }
}

// =============================================================================
// Factory Function
// =============================================================================

let _store: PersistenceStore | null = null;

export function getPersistenceStore(): PersistenceStore {
  if (_store) return _store;
  
  const useFirestore = process.env.USE_FIRESTORE !== "false"; // Default to true in production
  const isProduction = process.env.NODE_ENV === "production";
  
  // Use Firestore in production (unless explicitly disabled)
  if (isProduction && useFirestore) {
    try {
      console.log("[Persistence] Initializing Firestore store");
      _store = new FirestoreStore();
      return _store;
    } catch (error) {
      console.warn("[Persistence] Failed to initialize Firestore, falling back to in-memory:", error);
      _store = new InMemoryStore();
      return _store;
    }
  }
  
  // Use in-memory store in development
  console.log("[Persistence] Using in-memory store (development)");
  _store = new InMemoryStore();
  return _store;
}
