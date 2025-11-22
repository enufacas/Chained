---
applyTo:
  - "docs/**/*.html"
  - "docs/**/*.js"
  - "docs/**/*.css"
  - "docs/**/*.md"
  - ".github/workflows/github-pages-review.yml"
  - ".github/workflows/*pages*.yml"
  - ".github/workflows/*docs*.yml"
---

# GitHub Pages Rendering and Testing Requirements

## MANDATORY RULE: Test GitHub Pages When Making Changes

When working with GitHub Pages files in the `docs/` directory or workflows that affect GitHub Pages, **you MUST render and test the pages** to ensure they work correctly before completing your task.

## Why This Matters

GitHub Pages is the public face of this project. Broken pages, rendering issues, or JavaScript errors directly impact users and stakeholders. Testing ensures:

1. **Visual Correctness**: Pages render as intended
2. **Functionality**: Interactive features work properly
3. **No Regressions**: Changes don't break existing functionality
4. **Professional Quality**: The site maintains a polished appearance
5. **User Experience**: Navigation, links, and interactions work smoothly

## When to Test

You MUST test GitHub Pages in these scenarios:

### Always Required
- ✅ Modifying HTML files in `docs/`
- ✅ Changing CSS styles in `docs/style.css` or other stylesheets
- ✅ Updating JavaScript in `docs/script.js`, `docs/ai-knowledge-graph.js`, or other JS files
- ✅ Adding new pages to the `docs/` directory
- ✅ Updating data files in `docs/data/` that pages consume
- ✅ Modifying workflows that generate or update GitHub Pages content

### Conditionally Required
- 🔄 Making changes that could affect page rendering (even indirectly)
- 🔄 Updating documentation that's displayed on GitHub Pages
- 🔄 Changing build or deployment processes for pages

## How to Test GitHub Pages

### Method 1: Local HTTP Server (Recommended for Quick Checks)

For simple HTML/CSS/JS changes:

```bash
# Start a local web server in the docs directory
cd docs
python3 -m http.server 8000

# Access pages at http://localhost:8000
```

**What to verify:**
- Page loads without errors
- Layout appears correct
- Styles are applied properly
- Images load successfully

### Method 2: Playwright Browser Automation (Recommended for Thorough Testing)

**You have access to the Playwright MCP Server** - use it for comprehensive testing:

```markdown
@playwright-browser_navigate to http://localhost:8000/index.html
@playwright-browser_snapshot to capture the page state
@playwright-browser_console_messages to check for errors
@playwright-browser_take_screenshot to document the visual state
```

**Playwright capabilities available to you:**
- `browser_navigate` - Navigate to pages
- `browser_snapshot` - Get accessibility snapshot
- `browser_take_screenshot` - Capture screenshots (REQUIRED for visual changes)
- `browser_console_messages` - Check for JavaScript errors
- `browser_click` - Test interactive elements
- `browser_evaluate` - Run JavaScript to test functionality
- `browser_network_requests` - Check for failed requests

### Method 3: Direct File Inspection (For Data Files)

For changes to JSON data files in `docs/data/`:

```bash
# Validate JSON syntax
cat docs/data/stats.json | jq .

# Check specific fields
jq '.last_updated' docs/data/stats.json

# Validate structure
jq 'type' docs/data/issues.json  # Should return "array"
```

## Required Testing Checklist

Before completing a GitHub Pages task, verify:

### Visual Verification ✅
- [ ] Page loads without errors
- [ ] Layout is correct and responsive
- [ ] Colors, fonts, and styling are applied correctly
- [ ] Images and icons display properly
- [ ] No visual glitches or layout breaks

### Functional Verification ✅
- [ ] Interactive elements work (buttons, links, dropdowns)
- [ ] JavaScript features function correctly
- [ ] Forms submit properly (if applicable)
- [ ] Navigation works between pages
- [ ] Data displays correctly from JSON files

### Technical Verification ✅
- [ ] No JavaScript console errors
- [ ] No browser console warnings (or document why they're acceptable)
- [ ] No 404 errors for resources
- [ ] No broken links or references
- [ ] Data files have valid JSON syntax

### Performance Verification ✅
- [ ] Page loads in reasonable time (< 3 seconds)
- [ ] No unnecessary network requests
- [ ] Images are optimized (reasonable file sizes)
- [ ] No blocking JavaScript issues

### Screenshot Documentation 📸

**CRITICAL**: When making visual changes to GitHub Pages:

1. **Take BEFORE screenshot** (if modifying existing page)
2. **Take AFTER screenshot** (showing your changes)
3. **Include screenshots in PR description**

Use Playwright's `browser_take_screenshot` tool:

```markdown
The tool will save screenshots automatically. Reference them in your PR.
```

## Testing Interactive Features

For pages with JavaScript interactivity:

### Knowledge Graph (`ai-knowledge-graph.html`)
```bash
# Test with Playwright
1. Navigate to the page
2. Click on graph nodes
3. Verify tooltip displays
4. Check console for errors
5. Test zoom and pan interactions
```

### Agent Dashboard (`agents.html`)
```bash
# Test with Playwright
1. Navigate to the page
2. Verify agent data loads
3. Click on agent cards
4. Test filtering if present
5. Check performance metrics display
```

### Timeline/Episodes (`episodes.html`, `tv.html`)
```bash
# Test with Playwright
1. Navigate to the page
2. Test timeline navigation
3. Verify episode content loads
4. Check video/media if present
5. Test any interactive filters
```

## Common Issues to Check For

### 1. Broken Links
```bash
# Find all links in HTML files
grep -r 'href=' docs/*.html

# Check for localhost or file:// links (should be relative)
grep -r 'href="http://localhost' docs/*.html
grep -r 'href="file://' docs/*.html
```

### 2. Missing Resources
```bash
# Check for references to non-existent files
# Look at browser network tab or console
```

### 3. JavaScript Errors
```javascript
// Common errors to watch for:
// - Undefined variables
// - Failed fetch requests
// - JSON parse errors
// - Event handler failures
```

### 4. CSS Issues
```css
/* Common issues:
 * - Overriding styles unintentionally
 * - Missing vendor prefixes
 * - Broken responsive design
 * - z-index conflicts
 */
```

### 5. Data Issues
```bash
# Verify JSON structure matches what JavaScript expects
jq 'keys' docs/data/stats.json
jq '.[0] | keys' docs/data/issues.json
```

## Workflow Testing

When modifying workflows that update GitHub Pages:

### 1. Test Data Generation
```bash
# Run the workflow step locally if possible
# Verify generated data has correct structure
jq . docs/data/stats.json
```

### 2. Verify Workflow Permissions
```yaml
# Ensure workflow has necessary permissions
permissions:
  contents: write  # To update docs/
  pages: write     # If deploying to pages
```

### 3. Check for Data Freshness
```bash
# Verify last_updated timestamp is current
jq '.last_updated' docs/data/stats.json
```

## Integration with GitHub Pages Review Workflow

Your changes should:
- ✅ Pass existing GitHub Pages health checks
- ✅ Not introduce new warnings
- ✅ Maintain data freshness standards
- ✅ Keep all required files present

The `github-pages-review.yml` workflow checks:
1. Presence of required HTML files
2. Presence of required data files
3. Data freshness (last_updated < 12 hours)
4. Site accessibility

## Examples of Proper Testing

### Example 1: CSS Style Change

```bash
# 1. Start local server
cd docs && python3 -m http.server 8000 &

# 2. Use Playwright to verify
browser_navigate url="http://localhost:8000/index.html"
browser_take_screenshot filename="before-style-change.png"

# 3. Make your CSS changes
# (edit files)

# 4. Refresh and verify
browser_navigate url="http://localhost:8000/index.html"
browser_take_screenshot filename="after-style-change.png"
browser_console_messages  # Check for errors

# 5. Compare screenshots and include in PR
```

### Example 2: JavaScript Feature Addition

```bash
# 1. Navigate to page
browser_navigate url="http://localhost:8000/ai-knowledge-graph.html"

# 2. Test the feature
browser_click element="graph node"
browser_snapshot  # Verify state after click

# 3. Check console
browser_console_messages  # Should have no errors

# 4. Document behavior
browser_take_screenshot filename="feature-working.png"
```

### Example 3: Data File Update

```bash
# 1. Validate JSON
jq . docs/data/stats.json

# 2. Start server and check page
cd docs && python3 -m http.server 8000 &
browser_navigate url="http://localhost:8000/index.html"

# 3. Verify data appears correctly
browser_evaluate function="() => { return document.querySelector('.stats').textContent; }"

# 4. Take screenshot showing correct data
browser_take_screenshot filename="stats-updated.png"
```

## Error Reporting

If you find issues during testing:

### In Your PR Description
```markdown
## Testing Performed

- [x] Local server testing
- [x] Playwright browser testing
- [x] Console error check
- [x] Screenshot verification

## Test Results

✅ All pages load successfully
✅ No JavaScript errors
✅ Interactive features work correctly

Screenshots:
- Before: [screenshot1.png]
- After: [screenshot2.png]
```

### In Console Errors
If you encounter errors:
1. **Document them** in the PR
2. **Explain why** they exist (if acceptable)
3. **Fix them** if they're new issues you introduced
4. **Report them** as separate issues if pre-existing and critical

## Non-Compliance Consequences

Failure to test GitHub Pages changes results in:
- ❌ Broken user experience
- ❌ Lost credibility for the project
- ❌ Potential rollback of your changes
- ❌ Additional work to fix issues post-deployment
- ❌ Lower agent performance scores

## Tools Available to You

### Playwright MCP Server (Microsoft)
Full browser automation capabilities:
- Navigate pages
- Interact with elements
- Take screenshots
- Check console messages
- Test JavaScript functionality
- Verify accessibility

### GitHub MCP Server (Microsoft/GitHub)
Repository and web operations:
- Search code
- Get file contents
- Web search for documentation
- Repository management

### Standard Shell Tools
- `python3 -m http.server` - Local web server
- `jq` - JSON validation and parsing
- `grep` - Search in files
- `curl` - Test HTTP endpoints
- `wget` - Download resources

## Best Practices

### 1. Test Early and Often
Don't wait until the end to test. Test as you make changes.

### 2. Use Playwright for Complex Pages
If the page has JavaScript or interactive features, use Playwright for thorough testing.

### 3. Take Screenshots
Visual documentation is invaluable. Always capture screenshots of visual changes.

### 4. Check Mobile Responsiveness
If making layout changes, verify responsive design:
```javascript
// Resize browser viewport
browser_resize(width=375, height=667)  // iPhone size
browser_take_screenshot(filename="mobile-view.png")
```

### 5. Verify Across Pages
If your change affects multiple pages, test all of them.

### 6. Clean Up Test Artifacts
Stop local servers, close browser instances, and clean up temporary files.

## Summary

**Testing GitHub Pages is not optional.** It's a critical part of your responsibility when working with the project's public documentation and website. Use the tools available to you, follow the checklist, and document your testing in the PR.

Remember: **@support-master**, **@create-guru**, **@coach-master**, and all other agents - when you improve or fix GitHub Pages, you MUST test them. No exceptions.

---

*🔍 Quality assurance for our public face - ensuring GitHub Pages works perfectly every time.*
