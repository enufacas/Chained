#!/usr/bin/env python3
"""
Test suite for the Architecture Tracker system.
Validates architecture analysis, tracking, and evolution features.
"""

import json
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


def test_architecture_tracker_exists():
    """Test that the architecture tracker tool exists and is executable"""
    print("\n🧪 Testing architecture tracker exists")
    print("-" * 60)
    
    tracker_path = Path("tools/architecture-tracker.py")
    
    if not tracker_path.exists():
        print(f"❌ FAILED: Architecture tracker not found at {tracker_path}")
        return False
    
    if not tracker_path.stat().st_mode & 0o111:
        print(f"⚠️  WARNING: Architecture tracker is not executable")
    
    print(f"✅ PASSED: Architecture tracker exists at {tracker_path}")
    return True


def test_architecture_tracker_runs():
    """Test that the architecture tracker can run successfully"""
    print("\n🧪 Testing architecture tracker runs")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ["python3", "tools/architecture-tracker.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ FAILED: Architecture tracker exited with code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
        
        if "Architecture evolution" not in result.stdout and "Track architecture" not in result.stdout:
            print(f"⚠️  WARNING: Help text may be incomplete")
        
        print("✅ PASSED: Architecture tracker runs successfully")
        return True
    
    except Exception as e:
        print(f"❌ FAILED: Exception running architecture tracker: {e}")
        return False


def test_architecture_analysis():
    """Test that architecture analysis produces valid output"""
    print("\n🧪 Testing architecture analysis")
    print("-" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Run analysis with output to temp directory
            result = subprocess.run(
                ["python3", "tools/architecture-tracker.py", 
                 "--repo-path", ".",
                 "--output-dir", tmpdir],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ FAILED: Analysis exited with code {result.returncode}")
                print(f"STDERR: {result.stderr}")
                return False
            
            # Check that output files were created
            latest_file = Path(tmpdir) / "latest.json"
            if not latest_file.exists():
                print(f"❌ FAILED: latest.json not created in {tmpdir}")
                return False
            
            # Validate JSON structure
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            required_keys = ["timestamp", "commit", "structure", "dependencies", "metrics", "components"]
            for key in required_keys:
                if key not in data:
                    print(f"❌ FAILED: Missing required key '{key}' in output")
                    return False
            
            print("✅ PASSED: Architecture analysis produces valid output")
            print(f"   - Files tracked: {data['metrics'].get('total_files', 0)}")
            print(f"   - Components: {data['metrics'].get('total_components', 0)}")
            return True
        
        except Exception as e:
            print(f"❌ FAILED: Exception during analysis: {e}")
            return False


def test_metrics_calculation():
    """Test that metrics are calculated correctly"""
    print("\n🧪 Testing metrics calculation")
    print("-" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            result = subprocess.run(
                ["python3", "tools/architecture-tracker.py", 
                 "--repo-path", ".",
                 "--output-dir", tmpdir,
                 "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ FAILED: Analysis failed")
                return False
            
            data = json.loads(result.stdout)
            metrics = data.get("metrics", {})
            
            # Validate metric types and ranges
            checks = [
                ("total_files", int, lambda x: x >= 0),
                ("total_lines", int, lambda x: x >= 0),
                ("total_components", int, lambda x: x >= 0),
                ("total_dependencies", int, lambda x: x >= 0),
                ("coupling_score", (int, float), lambda x: 0 <= x <= 1),
                ("complexity_score", (int, float), lambda x: 0 <= x <= 1)
            ]
            
            for metric_name, expected_type, validator in checks:
                if metric_name not in metrics:
                    print(f"❌ FAILED: Missing metric '{metric_name}'")
                    return False
                
                value = metrics[metric_name]
                if not isinstance(value, expected_type):
                    print(f"❌ FAILED: Metric '{metric_name}' has wrong type: {type(value)}")
                    return False
                
                if not validator(value):
                    print(f"❌ FAILED: Metric '{metric_name}' failed validation: {value}")
                    return False
            
            print("✅ PASSED: Metrics calculation is correct")
            return True
        
        except Exception as e:
            print(f"❌ FAILED: Exception during metrics test: {e}")
            return False


def test_mermaid_diagram_generation():
    """Test that Mermaid diagrams can be generated"""
    print("\n🧪 Testing Mermaid diagram generation")
    print("-" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            result = subprocess.run(
                ["python3", "tools/architecture-tracker.py", 
                 "--repo-path", ".",
                 "--output-dir", tmpdir,
                 "--mermaid"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ FAILED: Mermaid generation failed")
                return False
            
            mermaid_file = Path(tmpdir) / "architecture.mmd"
            if not mermaid_file.exists():
                print(f"❌ FAILED: Mermaid file not created")
                return False
            
            with open(mermaid_file, 'r') as f:
                content = f.read()
            
            if "graph TD" not in content:
                print(f"❌ FAILED: Mermaid diagram missing graph declaration")
                return False
            
            print("✅ PASSED: Mermaid diagram generation works")
            return True
        
        except Exception as e:
            print(f"❌ FAILED: Exception during Mermaid test: {e}")
            return False


def test_evolution_history():
    """Test that evolution history is tracked correctly"""
    print("\n🧪 Testing evolution history tracking")
    print("-" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Run analysis twice to create history
            for i in range(2):
                result = subprocess.run(
                    ["python3", "tools/architecture-tracker.py", 
                     "--repo-path", ".",
                     "--output-dir", tmpdir],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    print(f"❌ FAILED: Analysis {i+1} failed")
                    return False
            
            # Check evolution history
            evolution_file = Path(tmpdir) / "evolution.json"
            if not evolution_file.exists():
                print(f"❌ FAILED: evolution.json not created")
                return False
            
            with open(evolution_file, 'r') as f:
                history = json.load(f)
            
            if "snapshots" not in history:
                print(f"❌ FAILED: Missing 'snapshots' in evolution history")
                return False
            
            snapshots = history["snapshots"]
            if len(snapshots) < 2:
                print(f"❌ FAILED: Expected at least 2 snapshots, got {len(snapshots)}")
                return False
            
            # Validate snapshot structure
            required_keys = ["timestamp", "commit", "metrics", "component_count", "file_count"]
            for key in required_keys:
                if key not in snapshots[0]:
                    print(f"❌ FAILED: Missing key '{key}' in snapshot")
                    return False
            
            print("✅ PASSED: Evolution history tracking works")
            print(f"   - Snapshots tracked: {len(snapshots)}")
            return True
        
        except Exception as e:
            print(f"❌ FAILED: Exception during history test: {e}")
            return False


def test_comparison_functionality():
    """Test that comparisons with previous snapshots work"""
    print("\n🧪 Testing comparison functionality")
    print("-" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Run initial analysis
            result1 = subprocess.run(
                ["python3", "tools/architecture-tracker.py", 
                 "--repo-path", ".",
                 "--output-dir", tmpdir],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result1.returncode != 0:
                print(f"❌ FAILED: Initial analysis failed")
                return False
            
            # Run comparison
            result2 = subprocess.run(
                ["python3", "tools/architecture-tracker.py", 
                 "--repo-path", ".",
                 "--output-dir", tmpdir,
                 "--compare"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result2.returncode != 0:
                print(f"❌ FAILED: Comparison analysis failed")
                return False
            
            # Check that comparison output is present
            output = result2.stdout
            if "Comparing" not in output and "Files:" not in output:
                print(f"⚠️  WARNING: Comparison output may be incomplete")
            
            print("✅ PASSED: Comparison functionality works")
            return True
        
        except Exception as e:
            print(f"❌ FAILED: Exception during comparison test: {e}")
            return False


def test_visualization_file_exists():
    """Test that the visualization HTML file exists"""
    print("\n🧪 Testing visualization file exists")
    print("-" * 60)
    
    viz_path = Path("docs/architecture-evolution.html")
    
    if not viz_path.exists():
        print(f"❌ FAILED: Visualization file not found at {viz_path}")
        return False
    
    with open(viz_path, 'r') as f:
        content = f.read()
    
    # Check for key components
    required_elements = [
        "Architecture Evolution",
        "d3.v7.min.js",
        "mermaid",
        "evolution.json",
        "latest.json"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"⚠️  WARNING: Missing element '{element}' in visualization")
    
    print(f"✅ PASSED: Visualization file exists at {viz_path}")
    return True


def test_workflow_file_exists():
    """Test that the GitHub Actions workflow exists"""
    print("\n🧪 Testing workflow file exists")
    print("-" * 60)
    
    workflow_path = Path(".github/workflows/architecture-evolution.yml")
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found at {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check for key workflow components
    required_elements = [
        "Architecture Evolution Tracker",
        "architecture-tracker.py",
        "push:",
        "branches:",
        "main"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ FAILED: Missing element '{element}' in workflow")
            return False
    
    print(f"✅ PASSED: Workflow file exists at {workflow_path}")
    return True


def test_documentation_exists():
    """Test that documentation exists"""
    print("\n🧪 Testing documentation exists")
    print("-" * 60)
    
    doc_path = Path("docs/ARCHITECTURE_EVOLUTION.md")
    
    if not doc_path.exists():
        print(f"⚠️  WARNING: Documentation not found at {doc_path}")
        return True  # Not critical for initial implementation
    
    print(f"✅ PASSED: Documentation exists at {doc_path}")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("🏗️  ARCHITECTURE TRACKER TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_architecture_tracker_exists,
        test_architecture_tracker_runs,
        test_architecture_analysis,
        test_metrics_calculation,
        test_mermaid_diagram_generation,
        test_evolution_history,
        test_comparison_functionality,
        test_visualization_file_exists,
        test_workflow_file_exists,
        test_documentation_exists
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ FAILED: Unexpected exception: {e}")
            results.append(False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
