#!/usr/bin/env python3
"""
Tests for Commit Verification Tool

Tests the verify_commit.sh script functionality and commit verification logic.
"""

import unittest
import subprocess
import os
import tempfile


class TestCommitVerification(unittest.TestCase):
    """Test commit verification functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        cls.script_path = os.path.join(cls.repo_root, 'tools', 'verify_commit.sh')
        
        # Ensure script is executable
        os.chmod(cls.script_path, 0o755)
        
        # Get a known valid commit from main branch
        result = subprocess.run(
            ['git', 'log', 'main', '--format=%H', '-1'],
            cwd=cls.repo_root,
            capture_output=True,
            text=True
        )
        cls.valid_commit = result.stdout.strip()
    
    def test_script_exists(self):
        """Test that the verification script exists"""
        self.assertTrue(
            os.path.exists(self.script_path),
            "verify_commit.sh script should exist"
        )
    
    def test_script_is_executable(self):
        """Test that the script is executable"""
        self.assertTrue(
            os.access(self.script_path, os.X_OK),
            "verify_commit.sh should be executable"
        )
    
    def test_verify_nonexistent_commit(self):
        """Test verification of a non-existent commit"""
        # This is the commit from the issue
        nonexistent_commit = "201c2090c02b819fa5f40b3fb36b2af906903407"
        
        result = subprocess.run(
            [self.script_path, nonexistent_commit],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        # Script should exit with non-zero status for non-existent commit
        self.assertNotEqual(result.returncode, 0, "Should fail for non-existent commit")
        self.assertIn("COMMIT NOT FOUND", result.stdout)
        self.assertIn(nonexistent_commit, result.stdout)
    
    def test_verify_existing_commit(self):
        """Test verification of an existing commit"""
        result = subprocess.run(
            [self.script_path, self.valid_commit],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        # Script should succeed for existing commit
        self.assertEqual(result.returncode, 0, "Should succeed for existing commit")
        self.assertIn("COMMIT FOUND", result.stdout)
        self.assertIn("COMMIT IS IN MAIN BRANCH", result.stdout)
    
    def test_verify_without_argument(self):
        """Test that script requires commit SHA argument"""
        result = subprocess.run(
            [self.script_path],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        # Script should fail without argument
        self.assertNotEqual(result.returncode, 0, "Should fail without argument")
        self.assertIn("Usage:", result.stdout)
    
    def test_git_command_commit_verification(self):
        """Test direct git commands for commit verification"""
        # Test that the problematic commit doesn't exist
        result = subprocess.run(
            ['git', 'cat-file', '-e', '201c2090c02b819fa5f40b3fb36b2af906903407'],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0, 
                          "Git should report commit doesn't exist")
    
    def test_known_commit_in_main(self):
        """Test that a known commit is in main branch"""
        result = subprocess.run(
            ['git', 'merge-base', '--is-ancestor', self.valid_commit, 'main'],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        "Known commit should be ancestor of main")
    
    def test_commit_search_negative(self):
        """Test that searching for non-existent commit returns nothing"""
        result = subprocess.run(
            ['git', 'log', '--all', '--format=%H'],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        # Check that the problematic commit is not in the output
        commits = result.stdout.strip().split('\n')
        self.assertNotIn('201c2090c02b819fa5f40b3fb36b2af906903407', commits,
                        "Problematic commit should not be in repository")
    
    def test_verification_document_exists(self):
        """Test that verification document was created"""
        doc_path = os.path.join(self.repo_root, 'COMMIT_VERIFICATION_201c209.md')
        self.assertTrue(
            os.path.exists(doc_path),
            "Verification document should exist"
        )
        
        # Verify document contains expected content
        with open(doc_path, 'r') as f:
            content = f.read()
            self.assertIn('201c2090c02b819fa5f40b3fb36b2af906903407', content)
            self.assertIn('COMMIT NOT FOUND', content)


class TestCommitVerificationReport(unittest.TestCase):
    """Test the verification report document"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        cls.report_path = os.path.join(cls.repo_root, 'COMMIT_VERIFICATION_201c209.md')
    
    def test_report_exists(self):
        """Test that the report file exists"""
        self.assertTrue(
            os.path.exists(self.report_path),
            "Verification report should exist"
        )
    
    def test_report_has_commit_sha(self):
        """Test that report contains the commit SHA"""
        with open(self.report_path, 'r') as f:
            content = f.read()
            self.assertIn('201c2090c02b819fa5f40b3fb36b2af906903407', content)
    
    def test_report_has_verification_result(self):
        """Test that report contains clear verification result"""
        with open(self.report_path, 'r') as f:
            content = f.read()
            # Should indicate commit not found
            self.assertIn('NOT FOUND', content)
            self.assertIn('does not exist', content)
    
    def test_report_has_methodology(self):
        """Test that report documents methodology"""
        with open(self.report_path, 'r') as f:
            content = f.read()
            self.assertIn('Methodology', content)
            self.assertIn('git', content.lower())
    
    def test_report_has_commands(self):
        """Test that report includes commands executed"""
        with open(self.report_path, 'r') as f:
            content = f.read()
            self.assertIn('Commands Executed', content)
            self.assertIn('git log', content)


if __name__ == '__main__':
    unittest.main()
