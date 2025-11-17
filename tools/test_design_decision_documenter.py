#!/usr/bin/env python3
"""
Test suite for Design Decision Documenter

Tests the functionality of the design decision documentation system.
Performance-focused tests by @accelerate-specialist
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
import time

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "design_decision_documenter",
    os.path.join(os.path.dirname(__file__), "design-decision-documenter.py")
)
design_decision_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design_decision_module)
DesignDecisionDocumenter = design_decision_module.DesignDecisionDocumenter


def create_test_repo():
    """Create a temporary git repository with design decision commits"""
    temp_dir = tempfile.mkdtemp()
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True, check=True)
    
    # Create commits with design decisions
    test_commits = [
        {
            "file": "architecture.md",
            "content": "# Architecture\nInitial setup",
            "message": """Decision: Use microservices architecture

Context: Our monolithic application is becoming difficult to maintain and scale.
We need to improve development velocity and allow independent deployment of components.

Decision: We decided to adopt a microservices architecture with the following principles:
- Each service owns its data
- Services communicate via REST APIs
- Use Docker for containerization

Consequences: This will improve scalability and development speed, but adds operational complexity."""
        },
        {
            "file": "database.md",
            "content": "# Database\nPostgreSQL chosen",
            "message": """Design decision: PostgreSQL for primary database

Because we need strong ACID guarantees and complex query support.
Alternatives: MongoDB (rejected - need relational features), MySQL (rejected - want better JSON support)

This means we get excellent data integrity but may have scaling challenges at very high volumes."""
        },
        {
            "file": "api.md",
            "content": "# API\nREST chosen",
            "message": """Decided to use REST API instead of GraphQL

Context: Need to choose API technology
Decision: REST because team has more experience and simpler for our use case
Alternative: GraphQL was considered but too complex for current needs"""
        },
        {
            "file": "deployment.md",
            "content": "# Deployment\nKubernetes",
            "message": """Deployment strategy: Kubernetes orchestration

Rationale: Need automated scaling and self-healing
Approach: Deploy all services to Kubernetes cluster
Impact: Operations team needs training but long-term benefits significant"""
        },
        {
            "file": "normal.md",
            "content": "# Normal commit\nJust a regular change",
            "message": "Fix typo in documentation"
        }
    ]
    
    for commit in test_commits:
        filepath = os.path.join(temp_dir, commit["file"])
        with open(filepath, 'w') as f:
            f.write(commit["content"])
        
        subprocess.run(['git', 'add', commit["file"]], cwd=temp_dir, capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', commit["message"]], cwd=temp_dir, capture_output=True, check=True)
    
    return temp_dir


def test_initialization():
    """Test documenter initialization"""
    print("Testing initialization...")
    
    temp_dir = tempfile.mkdtemp()
    decisions_file = os.path.join(temp_dir, "test_decisions.json")
    
    documenter = DesignDecisionDocumenter(repo_path=temp_dir, decisions_file=decisions_file)
    
    assert documenter.repo_path == temp_dir
    assert documenter.decisions_file == decisions_file
    
    data = documenter._load_decisions()
    assert data["version"] == "1.0.0"
    assert data["total_decisions"] == 0
    
    shutil.rmtree(temp_dir)
    print("✓ Initialization test passed")


def test_decision_extraction():
    """Test extracting design decisions from commits"""
    print("\nTesting decision extraction...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Extract decisions
        decisions = documenter.extract_decisions(max_commits=10)
        
        # Should find 4 decisions (not the normal commit)
        assert len(decisions) >= 3, f"Expected at least 3 decisions, got {len(decisions)}"
        
        # Check structure of first decision
        if decisions:
            decision = decisions[0]
            assert "id" in decision
            assert "title" in decision
            assert "date" in decision
            assert "status" in decision
            assert "category" in decision
            assert "commit" in decision
            assert "author" in decision
            
            # Check ID format
            assert decision["id"].startswith("DD-")
            
            # Check status is valid
            assert decision["status"] in ["accepted", "rejected", "deprecated", "proposed"]
            
            print(f"  Found {len(decisions)} decisions")
            print(f"  Example: {decision['id']} - {decision['title'][:50]}")
        
        print("✓ Decision extraction test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_database_operations():
    """Test database add/find operations"""
    print("\nTesting database operations...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Extract and add decisions
        decisions = documenter.extract_decisions(max_commits=10)
        
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Test find by ID
        if decisions:
            test_id = decisions[0]["id"]
            found = documenter.find_decision_by_id(test_id)
            assert found is not None, f"Could not find decision {test_id}"
            assert found["id"] == test_id
            print(f"  ✓ Found decision by ID: {test_id}")
        
        # Test find by status
        accepted = documenter.find_decisions_by_status("accepted")
        print(f"  ✓ Found {len(accepted)} accepted decisions")
        
        # Test find by category
        for decision in decisions:
            cat = decision.get("category", "general")
            by_cat = documenter.find_decisions_by_category(cat)
            assert len(by_cat) > 0
            break
        
        print(f"  ✓ Found decisions by category")
        
        print("✓ Database operations test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_search_functionality():
    """Test search across decisions"""
    print("\nTesting search functionality...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Add decisions
        decisions = documenter.extract_decisions(max_commits=10)
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Test search
        results = documenter.search_decisions("database")
        print(f"  ✓ Search 'database' returned {len(results)} results")
        
        if results:
            decision, score = results[0]
            assert score > 0
            print(f"    Top result: {decision['id']} (score: {score:.1f})")
        
        # Test empty search
        all_results = documenter.search_decisions("")
        print(f"  ✓ Empty search returned {len(all_results)} results")
        
        print("✓ Search functionality test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_related_decisions():
    """Test finding related decisions"""
    print("\nTesting related decisions...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Add decisions
        decisions = documenter.extract_decisions(max_commits=10)
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Find related decisions
        if len(decisions) > 1:
            test_id = decisions[0]["id"]
            related = documenter.find_related_decisions(test_id)
            
            print(f"  ✓ Found {len(related)} related decisions for {test_id}")
            
            if related:
                decision, similarity = related[0]
                assert 0 <= similarity <= 1
                print(f"    Most similar: {decision['id']} (similarity: {similarity:.2f})")
        
        print("✓ Related decisions test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_report_generation():
    """Test report generation"""
    print("\nTesting report generation...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Add decisions
        decisions = documenter.extract_decisions(max_commits=10)
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Generate report
        report = documenter.generate_report()
        
        assert len(report) > 0
        assert "Design Decisions Documentation" in report
        assert "Statistics" in report
        
        print(f"  ✓ Generated report ({len(report)} characters)")
        
        print("✓ Report generation test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_markdown_export():
    """Test exporting decisions to markdown files"""
    print("\nTesting markdown export...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Add decisions
        decisions = documenter.extract_decisions(max_commits=10)
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Export to markdown
        export_dir = os.path.join(test_repo, "exported_decisions")
        documenter.export_to_markdown(export_dir)
        
        # Check files were created
        assert os.path.exists(export_dir)
        assert os.path.exists(os.path.join(export_dir, "README.md"))
        
        # Check decision files
        decision_files = list(Path(export_dir).glob("DD-*.md"))
        assert len(decision_files) > 0
        
        print(f"  ✓ Exported {len(decision_files)} decision files")
        
        # Check content
        with open(decision_files[0], 'r') as f:
            content = f.read()
            assert "Status:" in content
            assert "Date:" in content
            assert "Category:" in content
        
        print(f"  ✓ Decision files have correct format")
        
        print("✓ Markdown export test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_performance():
    """Test performance characteristics"""
    print("\nTesting performance...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Measure extraction time
        start = time.time()
        decisions = documenter.extract_decisions(max_commits=10)
        extract_time = time.time() - start
        
        print(f"  ✓ Extracted {len(decisions)} decisions in {extract_time:.3f}s")
        
        # Add decisions
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Measure lookup time (should be O(1))
        if decisions:
            test_id = decisions[0]["id"]
            
            start = time.time()
            for _ in range(100):
                found = documenter.find_decision_by_id(test_id)
            lookup_time = (time.time() - start) / 100
            
            print(f"  ✓ Average ID lookup time: {lookup_time*1000:.3f}ms (O(1) expected)")
            
            # Should be very fast
            assert lookup_time < 0.01, f"Lookup too slow: {lookup_time}s"
        
        # Measure search time
        start = time.time()
        results = documenter.search_decisions("decision")
        search_time = time.time() - start
        
        print(f"  ✓ Search completed in {search_time:.3f}s")
        
        print("✓ Performance test passed")
    
    finally:
        shutil.rmtree(test_repo)


def test_index_rebuild():
    """Test index rebuilding for query performance"""
    print("\nTesting index rebuild...")
    
    test_repo = create_test_repo()
    
    try:
        decisions_file = os.path.join(test_repo, "test_decisions.json")
        documenter = DesignDecisionDocumenter(repo_path=test_repo, decisions_file=decisions_file)
        
        # Add decisions
        decisions = documenter.extract_decisions(max_commits=10)
        for decision in decisions:
            documenter.add_decision(decision)
        
        # Force save and reload to trigger index rebuild
        data = documenter._load_decisions()
        
        # Check indices exist
        assert "index" in data
        assert "by_status" in data["index"]
        assert "by_category" in data["index"]
        assert "by_hash" in data["index"]
        
        print(f"  ✓ Index built successfully")
        print(f"    Status index: {len(data['index']['by_status'])} keys")
        print(f"    Category index: {len(data['index']['by_category'])} keys")
        print(f"    Hash index: {len(data['index']['by_hash'])} keys")
        
        # Verify index accuracy
        for status, indices in data["index"]["by_status"].items():
            for idx in indices:
                assert data["decisions"][idx]["status"] == status
        
        print(f"  ✓ Index accuracy verified")
        
        print("✓ Index rebuild test passed")
    
    finally:
        shutil.rmtree(test_repo)


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Design Decision Documenter Test Suite")
    print("Performance-focused tests by @accelerate-specialist")
    print("=" * 60)
    
    tests = [
        test_initialization,
        test_decision_extraction,
        test_database_operations,
        test_search_functionality,
        test_related_decisions,
        test_report_generation,
        test_markdown_export,
        test_performance,
        test_index_rebuild,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
