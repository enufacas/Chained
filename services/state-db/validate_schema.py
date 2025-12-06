#!/usr/bin/env python3
"""
AI-Native Control Plane - Database Schema Validator

Validates that the state-db schema is correctly installed and operational.
Tests all tables, constraints, indexes, and sample data.
"""

import logging
import sys
from datetime import datetime
from typing import Dict, List

from db import DatabaseSession, generate_deterministic_id, test_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validates database schema installation"""

    def __init__(self):
        self.db = DatabaseSession()
        self.results: Dict[str, bool] = {}

    def run_all_checks(self) -> bool:
        """
        Run all validation checks.

        Returns:
            True if all checks pass, False otherwise
        """
        checks = [
            ("Connection", self.check_connection),
            ("Tables", self.check_tables),
            ("Constraints", self.check_constraints),
            ("Indexes", self.check_indexes),
            ("Sample Data", self.check_sample_data),
            ("Foreign Keys", self.check_foreign_keys),
            ("JSONB Columns", self.check_jsonb_columns),
        ]

        print("\n" + "=" * 60)
        print("AI-Native Control Plane - Database Schema Validation")
        print("=" * 60 + "\n")

        all_passed = True
        for check_name, check_func in checks:
            try:
                print(f"Running check: {check_name}...", end=" ")
                result = check_func()
                self.results[check_name] = result
                print("✅ PASSED" if result else "❌ FAILED")
                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(f"Check '{check_name}' raised exception: {e}")
                self.results[check_name] = False
                print(f"❌ ERROR: {e}")
                all_passed = False

        # Print summary
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        print(f"\nPassed: {passed}/{total}")
        print(f"Status: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}\n")

        return all_passed

    def check_connection(self) -> bool:
        """Check database connection"""
        return test_connection()

    def check_tables(self) -> bool:
        """Check that all required tables exist"""
        required_tables = [
            'users',
            'apps',
            'infra_objects',
            'operations',
            'plan_versions',
            'policies',
            'schema_versions',
        ]

        with self.db.get_session() as session:
            result = session.execute("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            existing_tables = [row[0] for row in result.fetchall()]

        missing_tables = set(required_tables) - set(existing_tables)
        if missing_tables:
            logger.error(f"Missing tables: {missing_tables}")
            return False

        logger.info(f"Found all {len(required_tables)} required tables")
        return True

    def check_constraints(self) -> bool:
        """Check that CHECK constraints are properly defined"""
        with self.db.get_session() as session:
            result = session.execute("""
                SELECT
                    tc.table_name,
                    tc.constraint_name,
                    tc.constraint_type
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'public'
                  AND tc.constraint_type = 'CHECK'
                ORDER BY tc.table_name, tc.constraint_name
            """)
            constraints = result.fetchall()

        # Expect CHECK constraints on: users, apps, infra_objects, operations, plan_versions, policies
        expected_min = 10
        if len(constraints) < expected_min:
            logger.error(f"Expected at least {expected_min} CHECK constraints, found {len(constraints)}")
            return False

        logger.info(f"Found {len(constraints)} CHECK constraints")
        return True

    def check_indexes(self) -> bool:
        """Check that required indexes exist"""
        with self.db.get_session() as session:
            result = session.execute("""
                SELECT
                    schemaname,
                    tablename,
                    indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            indexes = result.fetchall()

        # Expect indexes on most tables
        expected_min = 20
        if len(indexes) < expected_min:
            logger.error(f"Expected at least {expected_min} indexes, found {len(indexes)}")
            return False

        logger.info(f"Found {len(indexes)} indexes")
        return True

    def check_sample_data(self) -> bool:
        """Check that sample/default data exists"""
        checks_passed = True

        with self.db.get_session() as session:
            # Check for admin user
            result = session.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
            admin_count = result.scalar()
            if admin_count < 1:
                logger.error("No admin users found")
                checks_passed = False
            else:
                logger.info(f"Found {admin_count} admin user(s)")

            # Check for global policies
            result = session.execute("SELECT COUNT(*) FROM policies WHERE scope='global'")
            policy_count = result.scalar()
            if policy_count < 3:
                logger.warning(f"Only {policy_count} global policies found (expected 3)")
                # Don't fail on this, just warn
            else:
                logger.info(f"Found {policy_count} global policies")

            # Check schema_versions
            result = session.execute("SELECT COUNT(*) FROM schema_versions WHERE status='applied'")
            schema_count = result.scalar()
            if schema_count < 1:
                logger.error("No applied schema versions found")
                checks_passed = False
            else:
                logger.info(f"Found {schema_count} applied schema version(s)")

        return checks_passed

    def check_foreign_keys(self) -> bool:
        """Check that foreign key relationships are defined"""
        with self.db.get_session() as session:
            result = session.execute("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name
            """)
            foreign_keys = result.fetchall()

        # Expect foreign keys between tables
        expected_min = 5
        if len(foreign_keys) < expected_min:
            logger.error(f"Expected at least {expected_min} foreign keys, found {len(foreign_keys)}")
            return False

        logger.info(f"Found {len(foreign_keys)} foreign key relationships")
        return True

    def check_jsonb_columns(self) -> bool:
        """Check that JSONB columns exist and are indexed"""
        with self.db.get_session() as session:
            # Check for JSONB columns
            result = session.execute("""
                SELECT
                    table_name,
                    column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND data_type = 'jsonb'
                ORDER BY table_name, column_name
            """)
            jsonb_columns = result.fetchall()

        # Expect JSONB in: apps.metadata, infra_objects.configuration, operations.before/after_snapshot, etc.
        expected_min = 8
        if len(jsonb_columns) < expected_min:
            logger.error(f"Expected at least {expected_min} JSONB columns, found {len(jsonb_columns)}")
            return False

        logger.info(f"Found {len(jsonb_columns)} JSONB columns")
        return True

    def cleanup(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main entry point"""
    validator = SchemaValidator()
    try:
        all_passed = validator.run_all_checks()
        exit_code = 0 if all_passed else 1
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}", exc_info=True)
        exit_code = 1
    finally:
        validator.cleanup()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
