# Architecture Evolution Page Troubleshooting Guide

**Document Created:** 2025-11-13  
**Troubleshoot Expert:** @troubleshoot-expert (Grace Hopper)  
**Status:** Active

## Overview

This document provides troubleshooting guidance for the Architecture Evolution visualization page (`architecture-evolution.html`). The page displays metrics and visualizations of the Chained codebase architecture over time.

## Quick Diagnosis

If the Architecture Evolution page is not working:

1. **Visit the Debug Page:** https://enufacas.github.io/Chained/architecture-evolution-debug.html
2. **Check Browser Console:** Press F12 and look for errors
3. **Verify Libraries Load:** Look for D3.js and Mermaid loading messages
4. **Test Data Files:** Use the debug page to test data file accessibility

## Common Issues and Solutions

### Issue 1: Page Shows "Loading..." Indefinitely

**Symptoms:**
- Page displays "Loading architecture data..." and never progresses
- No error message appears

**Likely Causes:**
1. CDN libraries (D3.js or Mermaid) blocked by ad blocker
2. Corporate firewall blocking external scripts
3. JavaScript disabled in browser
4. Network connectivity issues

**Solutions:**
1. **Disable ad blocker** for the GitHub Pages domain
2. **Check browser console** (F12) for specific error messages
3. **Enable JavaScript** in browser settings
4. **Try a different browser** or incognito mode
5. **Run the debug page** at `/architecture-evolution-debug.html`

### Issue 2: "Failed to Load Libraries" Error

**Symptoms:**
- Error message about D3.js or Mermaid failing to load
- Mentions ad blocker or firewall

**Likely Causes:**
- Ad blocker blocking CDN resources
- Corporate firewall blocking cdnjs.cloudflare.com or unpkg.com
- Browser security settings preventing external scripts

**Solutions:**
1. **Whitelist CDN domains:**
   - cdnjs.cloudflare.com
   - unpkg.com
   - cdn.jsdelivr.net

2. **Disable ad blocker** for GitHub Pages

3. **Check browser extensions** that might block scripts

4. **Contact IT department** if on corporate network

### Issue 3: "Failed to Load Architecture Data" Error

**Symptoms:**
- Libraries load successfully
- Error mentions data files not found or network error

**Likely Causes:**
1. Data files don't exist (architecture tracker not run)
2. GitHub Pages not deployed correctly
3. Files not included in Pages deployment
4. Path issues (wrong base URL)

**Solutions:**
1. **Verify data files exist:**
   ```bash
   ls docs/data/architecture/evolution.json
   ls docs/data/architecture/latest.json
   ```

2. **Run architecture tracker:**
   ```bash
   python tools/architecture-tracker.py
   git add docs/data/architecture/
   git commit -m "Update architecture data"
   git push
   ```

3. **Check GitHub Pages settings:**
   - Repository → Settings → Pages
   - Should be deployed from `main` branch, `/docs` folder
   - Wait 2-5 minutes after pushing for changes to deploy

4. **Verify .nojekyll file exists:**
   ```bash
   touch docs/.nojekyll
   git add docs/.nojekyll
   git commit -m "Add .nojekyll for GitHub Pages"
   git push
   ```

### Issue 4: Blank or Partially Rendered Page

**Symptoms:**
- Page loads but visualizations don't appear
- Some sections visible, others blank

**Likely Causes:**
1. Invalid or corrupted data in JSON files
2. JavaScript errors during rendering
3. Browser compatibility issues
4. CSS not loading properly

**Solutions:**
1. **Validate JSON data:**
   ```bash
   python -m json.tool docs/data/architecture/evolution.json > /dev/null
   python -m json.tool docs/data/architecture/latest.json > /dev/null
   ```

2. **Check browser console** for JavaScript errors

3. **Test in different browsers:**
   - Chrome/Edge (recommended)
   - Firefox
   - Safari

4. **Clear browser cache:**
   - Ctrl+Shift+Delete (Chrome/Firefox)
   - Hard refresh: Ctrl+F5 or Cmd+Shift+R

## Debug Tools

### Debug Page (`architecture-evolution-debug.html`)

The debug page provides comprehensive diagnostics:

- **Library Loading Tests:** Checks if D3.js and Mermaid load
- **Data File Tests:** Verifies data files are accessible
- **Browser Information:** Shows browser and environment details
- **Network Tests:** Tests CDN connectivity
- **Console Logs:** Displays all JavaScript console output

**Access:** https://enufacas.github.io/Chained/architecture-evolution-debug.html

### Browser Developer Tools

Press **F12** to open developer tools:

1. **Console Tab:** Shows JavaScript errors and logs
2. **Network Tab:** Shows which files failed to load
3. **Elements Tab:** Inspect page structure

### Useful Console Commands

Open browser console (F12) and try:

```javascript
// Check if libraries loaded
console.log('D3 version:', typeof d3 !== 'undefined' ? d3.version : 'NOT LOADED');
console.log('Mermaid loaded:', typeof mermaid !== 'undefined');

// Test data file fetch
fetch('data/architecture/evolution.json')
  .then(r => r.json())
  .then(data => console.log('Evolution data:', data))
  .catch(err => console.error('Error:', err));
```

## Page Requirements

### External Dependencies

The page requires these external libraries:

1. **D3.js v7.8.5**
   - Primary CDN: cdnjs.cloudflare.com
   - Fallback CDN: unpkg.com
   - Purpose: Data visualization and charting

2. **Mermaid v10.6.1**
   - Primary CDN: cdnjs.cloudflare.com
   - Fallback CDN: unpkg.com
   - Purpose: Architecture diagram rendering

### Data Files

Required data files:

1. **docs/data/architecture/evolution.json**
   - Contains historical snapshots of architecture metrics
   - Updated by `tools/architecture-tracker.py`
   - Structure: `{ "snapshots": [...] }`

2. **docs/data/architecture/latest.json**
   - Contains most recent architecture snapshot
   - Updated by `tools/architecture-tracker.py`
   - Structure: `{ "timestamp": "...", "metrics": {...}, "components": {...} }`

### Browser Support

Supported browsers:

- ✅ Chrome 90+ (recommended)
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+
- ⚠️ Older browsers may have issues with modern JavaScript

## Maintenance

### Regular Tasks

1. **Run Architecture Tracker Weekly:**
   ```bash
   python tools/architecture-tracker.py
   ```

2. **Verify Data Files Updated:**
   ```bash
   git log -1 --oneline docs/data/architecture/
   ```

3. **Test Page After Updates:**
   - Visit the debug page
   - Check all visualizations render
   - Verify data is current

### Monitoring

The page includes console logging to track:
- Library loading status
- Data fetch operations
- Rendering progress
- Any errors encountered

Monitor logs in browser console (F12) when debugging.

## Technical Details

### Loading Sequence

1. Browser loads HTML and CSS
2. D3.js script loads from CDN (with fallback)
3. Mermaid script loads from CDN (with fallback)
4. Page checks if libraries loaded successfully
5. Mermaid is initialized with dark theme
6. Data files fetched via AJAX
7. Data validated and parsed
8. Visualizations rendered:
   - Current metrics cards
   - Timeline chart (D3.js)
   - Component distribution chart (D3.js)
   - Architecture diagram (Mermaid)

### Error Handling

The page includes multiple error handling layers:

1. **CDN Fallback:** If primary CDN fails, tries fallback CDN
2. **Library Check:** Verifies libraries loaded before proceeding
3. **Data Fetch:** Catches and reports data loading errors
4. **Render Errors:** Logs errors during visualization rendering

### Performance

- Initial load time: 2-5 seconds (depends on CDN speed)
- Data files: ~50-100 KB total
- Renders 10-15 snapshots typically
- Timeline chart: Responsive, handles 50+ data points

## Getting Help

If issues persist after trying these solutions:

1. **Create an Issue:**
   - Include browser and OS details
   - Include console error messages
   - Include screenshots if helpful
   - Tag with `documentation` and `bug` labels

2. **Run Diagnostic:**
   - Visit debug page
   - Copy all diagnostic output
   - Include in issue report

3. **Check Workflow Logs:**
   - GitHub Actions may show deployment errors
   - Check "pages-build-deployment" workflow

## Related Documentation

- **Architecture Tracker:** `tools/architecture-tracker.py`
- **GitHub Pages Health:** `docs/GITHUB_PAGES_HEALTH_CHECK.md`
- **System Monitor:** `.github/workflows/system-monitor.yml`

## Changelog

### 2025-11-13 - Enhanced Error Handling
- Added detailed error messages for library loading failures
- Added debug page (`architecture-evolution-debug.html`)
- Improved console logging throughout loading process
- Added link to debug page in error messages
- Added version footer with load timestamp

### Previous Versions
- Initial implementation with basic error handling
- CDN loading with fallback support
- Three-tab visualization interface

---

**Maintained by:** @troubleshoot-expert  
**Last Updated:** 2025-11-13  
**Version:** 1.1
