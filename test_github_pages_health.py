#!/usr/bin/env python3
"""
Comprehensive test suite for GitHub Pages health validation.
Tests file existence, data file content, HTML structure, and AI conversations.
"""

import json
import sys
from pathlib import Path
from html.parser import HTMLParser


class HTMLStructureParser(HTMLParser):
    """Simple HTML parser to check for basic structure."""
    def __init__(self):
        super().__init__()
        self.has_html = False
        self.has_head = False
        self.has_body = False
        self.placeholders = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'html':
            self.has_html = True
        elif tag == 'head':
            self.has_head = True
        elif tag == 'body':
            self.has_body = True
    
    def handle_data(self, data):
        # Check for obvious placeholders
        data_lower = data.strip().lower()
        if data_lower in ['loading...', 'todo', 'coming soon']:
            self.placeholders.append(data.strip())


def test_html_files_exist():
    """Test that all expected HTML files exist."""
    html_files = [
        'docs/index.html',
        'docs/ai-knowledge-graph.html',
        'docs/ai-friends.html',
        'docs/agents.html'
    ]
    
    missing = []
    for html_file in html_files:
        if not Path(html_file).exists():
            missing.append(html_file)
    
    if missing:
        print(f"❌ Missing HTML files: {', '.join(missing)}")
        return False
    
    print("✅ All expected HTML files exist")
    return True


def test_css_js_files_exist():
    """Test that all expected CSS and JS files exist."""
    files = [
        'docs/style.css',
        'docs/script.js',
        'docs/ai-knowledge-graph.js'
    ]
    
    missing = []
    for file_path in files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing CSS/JS files: {', '.join(missing)}")
        return False
    
    print("✅ All expected CSS/JS files exist")
    return True


def test_data_files_exist():
    """Test that all expected data files exist in docs/data/ directory."""
    data_files = [
        'docs/data/stats.json',
        'docs/data/issues.json',
        'docs/data/pulls.json',
        'docs/data/workflows.json',
        'docs/data/automation-log.json'
    ]
    
    missing = []
    for data_file in data_files:
        if not Path(data_file).exists():
            missing.append(data_file)
    
    if missing:
        print(f"❌ Missing data files: {', '.join(missing)}")
        return False
    
    print("✅ All expected data files exist")
    return True


def test_markdown_docs_exist():
    """Test that expected markdown documentation files exist."""
    docs = [
        'docs/CONTRIBUTING.md',
        'docs/AI_GOALS.md',
        'docs/WORKFLOWS.md',
        'docs/MONITORING.md',
        'docs/tutorials/README.md',
        'docs/ai-conversations/README.md'
    ]
    
    missing = []
    for doc in docs:
        if not Path(doc).exists():
            missing.append(doc)
    
    if missing:
        print(f"❌ Missing documentation files: {', '.join(missing)}")
        return False
    
    print("✅ All expected markdown documentation files exist")
    return True


def test_stats_json_content():
    """Test that stats.json is not empty and has required fields."""
    stats_path = Path('docs/data/stats.json')
    
    if not stats_path.exists():
        print("❌ stats.json does not exist")
        return False
    
    try:
        with open(stats_path, 'r') as f:
            stats = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ stats.json is not valid JSON: {e}")
        return False
    
    if not stats or stats == {}:
        print("❌ stats.json is empty")
        return False
    
    required_fields = [
        'total_issues',
        'open_issues',
        'closed_issues',
        'total_prs',
        'merged_prs',
        'ai_generated',
        'copilot_assigned',
        'completed',
        'in_progress',
        'completion_rate',
        'merge_rate',
        'last_updated'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in stats:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ stats.json missing required fields: {', '.join(missing_fields)}")
        return False
    
    print("✅ stats.json has valid content and all required fields")
    return True


def test_issues_json_not_empty():
    """Test that issues.json is not empty."""
    issues_path = Path('docs/data/issues.json')
    
    if not issues_path.exists():
        print("❌ issues.json does not exist")
        return False
    
    try:
        with open(issues_path, 'r') as f:
            issues = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ issues.json is not valid JSON: {e}")
        return False
    
    if not issues or issues == []:
        print("❌ issues.json is empty (contains only [])")
        return False
    
    print("✅ issues.json is not empty")
    return True


def test_pulls_json_not_empty():
    """Test that pulls.json is not empty."""
    pulls_path = Path('docs/data/pulls.json')
    
    if not pulls_path.exists():
        print("❌ pulls.json does not exist")
        return False
    
    try:
        with open(pulls_path, 'r') as f:
            pulls = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ pulls.json is not valid JSON: {e}")
        return False
    
    if not pulls or pulls == []:
        print("❌ pulls.json is empty")
        return False
    
    print("✅ pulls.json is not empty")
    return True


def test_workflows_json_not_empty():
    """Test that workflows.json is not empty."""
    workflows_path = Path('docs/data/workflows.json')
    
    if not workflows_path.exists():
        print("❌ workflows.json does not exist")
        return False
    
    try:
        with open(workflows_path, 'r') as f:
            workflows = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ workflows.json is not valid JSON: {e}")
        return False
    
    if not workflows or workflows == []:
        print("❌ workflows.json is empty")
        return False
    
    print("✅ workflows.json is not empty")
    return True


def test_automation_log_json_not_empty():
    """Test that automation-log.json is not empty."""
    log_path = Path('docs/data/automation-log.json')
    
    if not log_path.exists():
        print("❌ automation-log.json does not exist")
        return False
    
    try:
        with open(log_path, 'r') as f:
            log = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ automation-log.json is not valid JSON: {e}")
        return False
    
    if not log or log == []:
        print("❌ automation-log.json is empty")
        return False
    
    print("✅ automation-log.json is not empty")
    return True


def test_json_files_valid():
    """Test that all JSON files are valid JSON format."""
    json_files = [
        'docs/data/stats.json',
        'docs/data/issues.json',
        'docs/data/pulls.json',
        'docs/data/workflows.json',
        'docs/data/automation-log.json'
    ]
    
    invalid = []
    for json_file in json_files:
        if Path(json_file).exists():
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid.append(f"{json_file}: {e}")
    
    if invalid:
        print(f"❌ Invalid JSON files: {'; '.join(invalid)}")
        return False
    
    print("✅ All JSON files have valid format")
    return True


def test_html_structure():
    """Test that HTML files have proper structure (html, head, body tags)."""
    html_files = [
        'docs/index.html',
        'docs/ai-knowledge-graph.html',
        'docs/ai-friends.html',
        'docs/agents.html'
    ]
    
    issues = []
    for html_file in html_files:
        if Path(html_file).exists():
            try:
                with open(html_file, 'r') as f:
                    content = f.read()
                
                parser = HTMLStructureParser()
                parser.feed(content)
                
                if not parser.has_html:
                    issues.append(f"{html_file}: missing <html> tag")
                if not parser.has_head:
                    issues.append(f"{html_file}: missing <head> tag")
                if not parser.has_body:
                    issues.append(f"{html_file}: missing <body> tag")
                    
            except Exception as e:
                issues.append(f"{html_file}: error parsing - {e}")
    
    if issues:
        print(f"❌ HTML structure issues: {'; '.join(issues)}")
        return False
    
    print("✅ All HTML files have proper structure")
    return True


def test_html_no_placeholders():
    """Test that HTML files don't have obvious placeholder text."""
    html_files = [
        'docs/index.html',
        'docs/ai-knowledge-graph.html',
        'docs/ai-friends.html',
        'docs/agents.html'
    ]
    
    placeholders_found = []
    for html_file in html_files:
        if Path(html_file).exists():
            try:
                with open(html_file, 'r') as f:
                    content = f.read().lower()
                
                # Check for common placeholder patterns
                # Note: "Loading..." might be intentional for dynamic content
                # so we only flag obvious TODOs
                if 'todo' in content and 'todo:' in content:
                    placeholders_found.append(f"{html_file}: contains TODO")
                    
            except Exception as e:
                pass  # Already handled in structure test
    
    if placeholders_found:
        print(f"❌ HTML placeholder issues: {'; '.join(placeholders_found)}")
        return False
    
    print("✅ HTML files don't have obvious placeholders")
    return True


def test_internal_links():
    """Test that HTML files don't have broken internal links to missing files."""
    html_files = [
        'docs/index.html',
        'docs/ai-knowledge-graph.html',
        'docs/ai-friends.html',
        'docs/agents.html'
    ]
    
    broken_links = []
    for html_file in html_files:
        if Path(html_file).exists():
            try:
                with open(html_file, 'r') as f:
                    content = f.read()
                
                # Simple check for common linked files
                common_files = [
                    'style.css',
                    'script.js',
                    'ai-knowledge-graph.js',
                    'index.html',
                    'agents.html',
                    'ai-knowledge-graph.html',
                    'ai-friends.html'
                ]
                
                for linked_file in common_files:
                    if linked_file in content:
                        # Check if the file exists
                        linked_path = Path('docs') / linked_file
                        if not linked_path.exists():
                            broken_links.append(f"{html_file} links to missing {linked_file}")
                            
            except Exception as e:
                pass  # Already handled in structure test
    
    if broken_links:
        print(f"❌ Broken internal links: {'; '.join(broken_links)}")
        return False
    
    print("✅ No broken internal links found")
    return True


def test_ai_conversations_index_exists():
    """Test that ai-conversations/index.json exists and is valid."""
    index_path = Path('docs/ai-conversations/index.json')
    
    if not index_path.exists():
        print("❌ ai-conversations/index.json does not exist")
        return False
    
    try:
        with open(index_path, 'r') as f:
            index = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ai-conversations/index.json is not valid JSON: {e}")
        return False
    
    if 'conversations' not in index:
        print("❌ ai-conversations/index.json missing 'conversations' field")
        return False
    
    print("✅ ai-conversations/index.json exists and is valid")
    return True


def test_conversation_files_exist():
    """Test that referenced conversation files in index actually exist."""
    index_path = Path('docs/ai-conversations/index.json')
    
    if not index_path.exists():
        print("❌ Cannot test conversation files - index.json missing")
        return False
    
    try:
        with open(index_path, 'r') as f:
            index = json.load(f)
    except json.JSONDecodeError:
        print("❌ Cannot test conversation files - index.json invalid")
        return False
    
    if 'conversations' not in index:
        print("❌ Cannot test conversation files - no conversations field")
        return False
    
    missing = []
    for conv in index['conversations']:
        if 'file' in conv:
            conv_path = Path('docs') / conv['file']
            if not conv_path.exists():
                missing.append(conv['file'])
    
    if missing:
        print(f"❌ Missing conversation files: {', '.join(missing)}")
        return False
    
    print("✅ All referenced conversation files exist")
    return True


def test_conversation_files_structure():
    """Test that conversation files have required structure."""
    index_path = Path('docs/ai-conversations/index.json')
    
    if not index_path.exists():
        print("❌ Cannot test conversation structure - index.json missing")
        return False
    
    try:
        with open(index_path, 'r') as f:
            index = json.load(f)
    except json.JSONDecodeError:
        print("❌ Cannot test conversation structure - index.json invalid")
        return False
    
    if 'conversations' not in index:
        print("❌ Cannot test conversation structure - no conversations field")
        return False
    
    required_fields = ['timestamp', 'date', 'model', 'question', 'response']
    invalid = []
    
    for conv in index['conversations']:
        if 'file' in conv:
            conv_path = Path('docs') / conv['file']
            if conv_path.exists():
                try:
                    with open(conv_path, 'r') as f:
                        conv_data = json.load(f)
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in conv_data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        invalid.append(f"{conv['file']} missing: {', '.join(missing_fields)}")
                        
                except json.JSONDecodeError as e:
                    invalid.append(f"{conv['file']}: invalid JSON")
                except Exception as e:
                    invalid.append(f"{conv['file']}: error reading - {e}")
    
    if invalid:
        print(f"❌ Conversation structure issues: {'; '.join(invalid)}")
        return False
    
    print("✅ All conversation files have required structure")
    return True


def main():
    """Run all tests."""
    print("🧪 Testing GitHub Pages Health\n")
    
    tests = [
        # File Existence Tests
        ("HTML Files Exist", test_html_files_exist),
        ("CSS/JS Files Exist", test_css_js_files_exist),
        ("Data Files Exist", test_data_files_exist),
        ("Markdown Documentation Exists", test_markdown_docs_exist),
        
        # Data File Content Tests
        ("stats.json Content", test_stats_json_content),
        ("issues.json Not Empty", test_issues_json_not_empty),
        ("pulls.json Not Empty", test_pulls_json_not_empty),
        ("workflows.json Not Empty", test_workflows_json_not_empty),
        ("automation-log.json Not Empty", test_automation_log_json_not_empty),
        ("JSON Files Valid", test_json_files_valid),
        
        # HTML Content Tests
        ("HTML Structure", test_html_structure),
        ("HTML No Placeholders", test_html_no_placeholders),
        ("Internal Links", test_internal_links),
        
        # AI Conversations Tests
        ("AI Conversations Index", test_ai_conversations_index_exists),
        ("Conversation Files Exist", test_conversation_files_exist),
        ("Conversation File Structure", test_conversation_files_structure)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing: {name}")
        print("-" * 50)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    print("\nDetailed Results:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("\nKnown Issue:")
        print("  - issues.json is empty (contains only []) - this causes incorrect")
        print("    statistics on the website (0 Ideas Generated)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
