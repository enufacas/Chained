"""
Session Store - Session management for ADK API Server
======================================================

Provides session management for the ADK API server, supporting
both in-memory storage (for development) and Firestore (for production).
"""

import json
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import logging

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Firestore, fallback to in-memory if not available
try:
    from google.cloud import firestore

    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    logger.info("google-cloud-firestore not available, using in-memory session store")


@dataclass
class Message:
    """A message in a session."""

    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """A session containing messages and state."""

    id: str
    user_id: str
    app_name: str
    messages: List[Message] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "app_name": self.app_name,
            "messages": [asdict(m) for m in self.messages],
            "state": self.state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary."""
        messages = [Message(**m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            app_name=data["app_name"],
            messages=messages,
            state=data.get("state", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
        )


class SessionStore(ABC):
    """Abstract base class for session storage."""

    @abstractmethod
    async def create_session(
        self, app_name: str, user_id: str, session_id: Optional[str] = None
    ) -> Session:
        """Create a new session."""
        pass

    @abstractmethod
    async def get_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> Optional[Session]:
        """Get a session by ID."""
        pass

    @abstractmethod
    async def list_sessions(self, app_name: str, user_id: str) -> List[Session]:
        """List all sessions for a user."""
        pass

    @abstractmethod
    async def update_session(self, session: Session) -> Session:
        """Update a session."""
        pass

    @abstractmethod
    async def delete_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> bool:
        """Delete a session."""
        pass

    @abstractmethod
    async def add_message(
        self, app_name: str, user_id: str, session_id: str, message: Message
    ) -> Session:
        """Add a message to a session."""
        pass


class InMemorySessionStore(SessionStore):
    """In-memory session store for development."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def _key(self, app_name: str, user_id: str, session_id: str) -> str:
        """Generate a unique key for a session."""
        return f"{app_name}:{user_id}:{session_id}"

    async def create_session(
        self, app_name: str, user_id: str, session_id: Optional[str] = None
    ) -> Session:
        """Create a new session."""
        if session_id is None:
            session_id = f"session-{uuid.uuid4().hex[:12]}"

        session = Session(
            id=session_id,
            user_id=user_id,
            app_name=app_name,
        )

        key = self._key(app_name, user_id, session_id)
        self._sessions[key] = session
        return session

    async def get_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> Optional[Session]:
        """Get a session by ID."""
        key = self._key(app_name, user_id, session_id)
        return self._sessions.get(key)

    async def list_sessions(self, app_name: str, user_id: str) -> List[Session]:
        """List all sessions for a user."""
        prefix = f"{app_name}:{user_id}:"
        return [s for k, s in self._sessions.items() if k.startswith(prefix)]

    async def update_session(self, session: Session) -> Session:
        """Update a session."""
        session.updated_at = datetime.utcnow().isoformat()
        key = self._key(session.app_name, session.user_id, session.id)
        self._sessions[key] = session
        return session

    async def delete_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> bool:
        """Delete a session."""
        key = self._key(app_name, user_id, session_id)
        if key in self._sessions:
            del self._sessions[key]
            return True
        return False

    async def add_message(
        self, app_name: str, user_id: str, session_id: str, message: Message
    ) -> Session:
        """Add a message to a session."""
        session = await self.get_session(app_name, user_id, session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        session.messages.append(message)
        return await self.update_session(session)


class FirestoreSessionStore(SessionStore):
    """Firestore session store for production."""

    def __init__(self, project_id: Optional[str] = None):
        if not FIRESTORE_AVAILABLE:
            raise ImportError(
                "google-cloud-firestore is required for FirestoreSessionStore"
            )
        self.db = firestore.AsyncClient(project=project_id)
        self.collection_name = "adk_sessions"

    def _doc_path(self, app_name: str, user_id: str, session_id: str) -> str:
        """Get the document path for a session."""
        return f"{self.collection_name}/{app_name}/{user_id}/{session_id}"

    def _collection_ref(self, app_name: str, user_id: str):
        """Get the collection reference for sessions."""
        return self.db.collection(self.collection_name).document(app_name).collection(
            user_id
        )

    async def create_session(
        self, app_name: str, user_id: str, session_id: Optional[str] = None
    ) -> Session:
        """Create a new session."""
        if session_id is None:
            session_id = f"session-{uuid.uuid4().hex[:12]}"

        session = Session(
            id=session_id,
            user_id=user_id,
            app_name=app_name,
        )

        doc_ref = self._collection_ref(app_name, user_id).document(session_id)
        await doc_ref.set(session.to_dict())
        return session

    async def get_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> Optional[Session]:
        """Get a session by ID."""
        doc_ref = self._collection_ref(app_name, user_id).document(session_id)
        doc = await doc_ref.get()
        if doc.exists:
            return Session.from_dict(doc.to_dict())
        return None

    async def list_sessions(self, app_name: str, user_id: str) -> List[Session]:
        """List all sessions for a user."""
        sessions = []
        collection_ref = self._collection_ref(app_name, user_id)
        async for doc in collection_ref.stream():
            sessions.append(Session.from_dict(doc.to_dict()))
        return sessions

    async def update_session(self, session: Session) -> Session:
        """Update a session."""
        session.updated_at = datetime.utcnow().isoformat()
        doc_ref = self._collection_ref(session.app_name, session.user_id).document(
            session.id
        )
        await doc_ref.set(session.to_dict())
        return session

    async def delete_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> bool:
        """Delete a session."""
        doc_ref = self._collection_ref(app_name, user_id).document(session_id)
        doc = await doc_ref.get()
        if doc.exists:
            await doc_ref.delete()
            return True
        return False

    async def add_message(
        self, app_name: str, user_id: str, session_id: str, message: Message
    ) -> Session:
        """Add a message to a session."""
        session = await self.get_session(app_name, user_id, session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        session.messages.append(message)
        return await self.update_session(session)


def get_session_store() -> SessionStore:
    """Get the appropriate session store based on environment."""
    use_firestore = os.getenv("USE_FIRESTORE", "false").lower() == "true"

    if use_firestore and FIRESTORE_AVAILABLE:
        project_id = os.getenv("GCP_PROJECT_ID")
        return FirestoreSessionStore(project_id=project_id)

    return InMemorySessionStore()
