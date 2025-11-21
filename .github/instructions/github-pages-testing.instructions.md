---
applyTo:
  - "docs/**/*.html"
  - "docs/**/*.js"
  - "docs/**/*.css"
---

# GitHub Pages Testing - Quick Reference

## MANDATORY: Test GitHub Pages Changes

When modifying GitHub Pages content in `docs/`, **you MUST render and test pages** before completing your task.

### Quick Testing Steps
1. Start local server: `cd docs && python3 -m http.server 8000`
2. Open `http://localhost:8000/[your-page]` in browser
3. Check browser console for errors (F12)
4. Verify all interactive features work
5. Test on mobile viewport (resize browser)
6. Take screenshots for visual changes

### Testing Checklist
- [ ] Page loads without errors
- [ ] Layout is correct and responsive
- [ ] JavaScript features work
- [ ] No console errors or warnings
- [ ] Links and navigation work
- [ ] Images and icons display properly

### Playwright Testing
```javascript
browser_navigate url="http://localhost:8000/index.html"
browser_snapshot  // Get accessibility snapshot
browser_take_screenshot filename="page.png"
browser_console_messages  // Check for errors
```

### Data File Validation
```bash
# Validate JSON
cat docs/data/stats.json | jq .
```

**For detailed guidance**, see: [docs/guides/copilot-instructions/github-pages-testing-guide.md](../../../docs/guides/copilot-instructions/github-pages-testing-guide.md)
