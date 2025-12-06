"""
AI-Native Control Plane - Database Connection Module

Provides SQLAlchemy database connection and session management for state-db.
Supports both local PostgreSQL and Google Cloud SQL.
"""

import hashlib
import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


class DatabaseConfig:
    """Database configuration from environment variables"""

    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:@localhost/ai_native_control_plane",
        )
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.echo_sql = os.getenv("DB_ECHO_SQL", "false").lower() == "true"
        self.connection_timeout = int(os.getenv("DB_CONNECTION_TIMEOUT", "10"))

    def is_cloud_sql(self) -> bool:
        """Check if using Google Cloud SQL (unix socket connection)"""
        return "/cloudsql/" in self.database_url

    def __repr__(self) -> str:
        # Mask password in URL for logging
        masked_url = self.database_url
        if ":" in masked_url and "@" in masked_url:
            parts = masked_url.split("@")
            if len(parts) == 2:
                before_at = parts[0]
                if ":" in before_at:
                    protocol, credentials = before_at.rsplit(":", 1)
                    masked_url = f"{protocol}:****@{parts[1]}"
        return f"DatabaseConfig(url={masked_url}, pool_size={self.pool_size})"


# =============================================================================
# Engine Creation
# =============================================================================


def create_db_engine(config: Optional[DatabaseConfig] = None) -> Engine:
    """
    Create SQLAlchemy engine with appropriate configuration.

    Args:
        config: DatabaseConfig instance (creates default if None)

    Returns:
        SQLAlchemy Engine instance

    Raises:
        SQLAlchemyError: If engine creation fails
    """
    if config is None:
        config = DatabaseConfig()

    logger.info(f"Creating database engine: {config}")

    # Engine arguments
    engine_args = {
        "url": config.database_url,
        "echo": config.echo_sql,
        "future": True,  # SQLAlchemy 2.0 style
    }

    # Connection pool configuration
    if config.is_cloud_sql():
        # Cloud SQL: Use NullPool for serverless (Cloud Run) or small pool
        logger.info("Using Cloud SQL unix socket connection")
        engine_args["poolclass"] = NullPool  # Serverless-friendly
    else:
        # Local/standard PostgreSQL: Use connection pooling
        logger.info("Using standard PostgreSQL connection pooling")
        engine_args["pool_size"] = config.pool_size
        engine_args["max_overflow"] = config.max_overflow
        engine_args["pool_timeout"] = config.pool_timeout
        engine_args["pool_recycle"] = config.pool_recycle
        engine_args["poolclass"] = QueuePool

    # Connection arguments
    connect_args = {
        "connect_timeout": config.connection_timeout,
        "options": "-c timezone=utc",  # Force UTC timezone
    }
    engine_args["connect_args"] = connect_args

    try:
        engine = create_engine(**engine_args)

        # Add connection event listeners for logging
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")

        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")

        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.scalar()
            logger.info(f"Database connection successful: {version}")

        return engine

    except SQLAlchemyError as e:
        logger.error(f"Failed to create database engine: {e}", exc_info=True)
        raise


# =============================================================================
# Session Management
# =============================================================================


class DatabaseSession:
    """Database session factory and context manager"""

    def __init__(self, engine: Optional[Engine] = None):
        """
        Initialize session factory.

        Args:
            engine: SQLAlchemy engine (creates new if None)
        """
        self.engine = engine or create_db_engine()
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Usage:
            db = DatabaseSession()
            with db.get_session() as session:
                result = session.execute("SELECT * FROM users")

        Yields:
            SQLAlchemy Session

        Raises:
            SQLAlchemyError: On database errors
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def close(self):
        """Close all connections and dispose engine"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed")


# =============================================================================
# Utility Functions
# =============================================================================


def generate_deterministic_id(entity_type: str, *components: str) -> str:
    """
    Generate deterministic SHA256-based ID.

    Args:
        entity_type: Entity type prefix (e.g., 'app', 'user', 'operation')
        *components: Components to hash together

    Returns:
        Deterministic ID string (format: 'entity_type:hash16')

    Example:
        >>> generate_deterministic_id('app', 'my-app', '2025-01-01T00:00:00Z')
        'app:a1b2c3d4e5f67890'
    """
    content = ":".join([entity_type] + list(components))
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"{entity_type}:{hash_value}"


def test_connection(database_url: Optional[str] = None) -> bool:
    """
    Test database connection.

    Args:
        database_url: Database URL (uses env var if None)

    Returns:
        True if connection successful, False otherwise
    """
    try:
        config = DatabaseConfig()
        if database_url:
            config.database_url = database_url

        engine = create_db_engine(config)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            test_val = result.scalar()
            assert test_val == 1

        engine.dispose()
        logger.info("Database connection test: PASSED")
        return True

    except Exception as e:
        logger.error(f"Database connection test: FAILED - {e}")
        return False


# =============================================================================
# Singleton Instance (Optional)
# =============================================================================

# Global database session instance (optional - use for simple cases)
_global_db: Optional[DatabaseSession] = None


def get_db() -> DatabaseSession:
    """
    Get or create global database session instance.

    Returns:
        DatabaseSession instance

    Note:
        This is a singleton pattern for simple use cases.
        For more control, create DatabaseSession instances directly.
    """
    global _global_db
    if _global_db is None:
        _global_db = DatabaseSession()
    return _global_db


def close_db():
    """Close global database session"""
    global _global_db
    if _global_db:
        _global_db.close()
        _global_db = None


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Test connection
    print("\n=== Testing Database Connection ===\n")
    success = test_connection()
    print(f"\nConnection test: {'✅ PASSED' if success else '❌ FAILED'}\n")

    if success:
        # Example: Query users table
        print("=== Querying Users Table ===\n")
        db = DatabaseSession()
        with db.get_session() as session:
            result = session.execute(
                "SELECT user_id, email, display_name, role FROM users LIMIT 5"
            )
            users = result.fetchall()
            for user in users:
                print(f"User: {user.email} ({user.role})")

        db.close()
        print("\n✅ Database operations completed successfully\n")
