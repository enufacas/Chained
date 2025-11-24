---
applyTo:
  - "docs/**/*.html"
  - "docs/**/*.css"
  - "docs/**/*.js"
  - "docs/data/**"
  - "docs/assets/**"
---

# GitHub Pages Tech Lead Instructions

## Overview

**@github-pages-tech-lead** is responsible for the GitHub Pages site quality, including HTML, CSS, JavaScript, and all web content in the `docs/` directory.

## When to Consult GitHub Pages Tech Lead

You should consult **@github-pages-tech-lead** when:
- Modifying HTML pages in docs/
- Updating CSS styles
- Changing JavaScript functionality
- Adding new web pages or assets
- Optimizing page performance
- Fixing rendering or display issues

## Key Responsibilities

**@github-pages-tech-lead** ensures:

1. **Rendering Quality**: All pages render correctly across browsers
2. **Performance**: Fast page loads and smooth interactions
3. **Accessibility**: WCAG compliance and keyboard navigation
4. **Maintainability**: Clean, well-structured web code
5. **User Experience**: Intuitive navigation and responsive design

## Review Focus Areas

When working with GitHub Pages content, **@github-pages-tech-lead** reviews:

### Visual Quality
- Pages render correctly in major browsers
- Responsive design works on mobile/tablet/desktop
- Colors and fonts meet accessibility standards
- Images display properly with appropriate alt text
- Layout doesn't break on different screen sizes

### JavaScript Functionality
- No console errors or warnings
- Interactive features work as expected
- Event handlers properly attached
- Async operations handle errors gracefully
- No memory leaks from event listeners

### Performance
- Page load time &lt; 3 seconds
- Images optimized for web (compressed, appropriate format)
- CSS and JavaScript minified for production
- Proper caching headers if applicable
- No blocking resources

### Accessibility
- Semantic HTML elements used
- ARIA labels where appropriate
- Keyboard navigation works
- Color contrast meets WCAG AA standards
- Screen reader compatible

## Common Anti-Patterns to Avoid

❌ **Don't:**
- Use inline styles instead of CSS files
- Leave JavaScript unminified in production
- Forget alt text on images
- Create fixed-width layouts that don't scale
- Ignore JavaScript console errors

✅ **Do:**
- Use external CSS files for styles
- Minify and optimize assets
- Always include descriptive alt text
- Design responsive, mobile-first layouts
- Fix all console errors and warnings

## Web Development Best Practices

### HTML Structure
```html
<!-- ✅ Good - semantic HTML -->
<article>
  <header>
    <h1>Title</h1>
  </header>
  <section>
    <p>Content</p>
  </section>
</article>

<!-- ❌ Bad - div soup -->
<div>
  <div>
    <div>Title</div>
  </div>
  <div>
    <div>Content</div>
  </div>
</div>
```

### CSS Organization
```css
/* ✅ Good - organized, reusable */
.button {
  padding: 10px 20px;
  border-radius: 4px;
}

.button-primary {
  background: blue;
  color: white;
}

/* ❌ Bad - repetitive, unorganized */
.btn1 {
  padding: 10px 20px;
  border-radius: 4px;
  background: blue;
  color: white;
}
```

### JavaScript Error Handling
```javascript
// ✅ Good - handles errors
async function loadData() {
  try {
    const response = await fetch('/data.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to load data:', error);
    return null;
  }
}

// ❌ Bad - no error handling
async function loadData() {
  const response = await fetch('/data.json');
  return await response.json();
}
```

### Responsive Design
```css
/* ✅ Good - mobile-first, progressive enhancement */
.container {
  width: 100%;
  padding: 1rem;
}

@media (min-width: 768px) {
  .container {
    max-width: 720px;
    margin: 0 auto;
  }
}

/* ❌ Bad - desktop-only, breaks on mobile */
.container {
  width: 1200px;
  margin: 0 auto;
}
```

## Testing Requirements

### Visual Testing Checklist
Before committing changes to web content:
1. ✅ Test in Chrome, Firefox, and Safari
2. ✅ Test on mobile viewport (375px width)
3. ✅ Test on tablet viewport (768px width)
4. ✅ Test on desktop viewport (1200px+ width)
5. ✅ Check browser console for errors
6. ✅ Verify all interactive features work

### Performance Testing Checklist
For significant changes:
1. ✅ Measure page load time
2. ✅ Check image file sizes
3. ✅ Verify JavaScript doesn't block rendering
4. ✅ Test on slow 3G network (throttling)
5. ✅ Monitor memory usage

### Accessibility Testing Checklist
1. ✅ Keyboard navigation works (Tab, Enter, Esc)
2. ✅ Color contrast meets WCAG AA (4.5:1 for text)
3. ✅ Screen reader announces content correctly
4. ✅ Form labels associated with inputs
5. ✅ Images have alt text

## Special Considerations

### Three.js and 3D Content
For pages with Three.js (organism.html, lifecycle-3d.html):
- Maintain 60fps target framerate
- Optimize draw calls and geometry
- Test on lower-end devices
- Handle WebGL errors gracefully
- Provide fallback for unsupported browsers

### Data-Driven Pages
For pages consuming JSON data:
- Validate JSON structure
- Handle missing or malformed data
- Provide loading states
- Show error messages for failed loads
- Cache data appropriately

## Getting Help

If you're unsure about:
- Browser compatibility for a feature
- Performance optimization techniques
- Accessibility best practices
- Responsive design patterns

Mention **@github-pages-tech-lead** in your PR or issue for guidance.

## Protected Status

**@github-pages-tech-lead** is a protected agent that cannot be eliminated through standard performance evaluation. This ensures consistent quality and maintenance for our public-facing web content.

---

*These instructions apply to all web content in `docs/` to ensure **@github-pages-tech-lead** maintains high standards for our GitHub Pages site.*
