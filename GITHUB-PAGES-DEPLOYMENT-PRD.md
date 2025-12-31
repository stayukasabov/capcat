# GitHub Pages Deployment - Product Requirements Document

**Project:** Capcat Documentation Website
**Document Type:** PRD - Deployment Strategy
**Version:** 1.0
**Date:** December 19, 2025
**Status:** Ready for Implementation

---

## Executive Summary

Deploy the Capcat documentation website to GitHub Pages for public access. The website is static HTML/CSS/JS and requires minimal preparation before deployment.

**Deployment URL:** `https://yourusername.github.io/capcat/`
**Timeline:** 1-2 hours for initial deployment
**Prerequisites:** GitHub repository, static website files

---

## 1. Repository Structure Options

### Option A: Dedicated Docs Repository (Recommended)
```
capcat-docs/
├── index.html
├── css/
├── js/
├── fonts/
├── icons/
├── docs/
└── README.md
```
**GitHub Pages URL:** `https://yourusername.github.io/capcat-docs/`

### Option B: Main Repository with `/docs` folder
```
capcat/
├── Application/          # Your Python app
├── docs/                 # GitHub Pages source
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── ...
└── README.md
```
**GitHub Pages URL:** `https://yourusername.github.io/capcat/`

### Option C: Main Repository with `/website` folder
Keep your current structure, configure GitHub Pages to serve from `/website`:
```
capcat/
├── Application/
├── website/              # GitHub Pages source
│   ├── index.html
│   ├── css/
│   └── ...
└── README.md
```

---

## 2. File Preparation Checklist

### ✓ What Works As-Is
Your site is **already GitHub Pages ready**:
- ✓ Static HTML files
- ✓ CSS files
- ✓ JavaScript files
- ✓ Font files
- ✓ Icons/images
- ✓ No server-side code

### ⚠ What Needs Adjustment

**A. Fix Absolute Paths**
Currently your links might use:
```html
<link rel="stylesheet" href="../css/design-system.css">
<link rel="stylesheet" href="../css/main.css">
```

For GitHub Pages with custom path, might need:
```html
<link rel="stylesheet" href="/capcat-docs/css/design-system.css">
```

**B. Verify All Asset Paths**
Check these files for path references:
- `index.html`
- All files in `docs/`
- `css/main.css` (font paths, background images)
- `js/` files (if they load resources)

**C. Create `.nojekyll` File**
GitHub Pages uses Jekyll by default. Create empty `.nojekyll` file in root to disable:
```bash
touch website/.nojekyll
```

This prevents Jekyll from ignoring folders starting with `_` and files in `css/`.

---

## 3. Step-by-Step Deployment

### Step 1: Choose Repository Structure
**Recommendation:** Use your existing `capcat` repo with `/website` folder

### Step 2: Prepare Website Folder
```bash
cd "/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application/website"

# Create .nojekyll file
touch .nojekyll

# Create CNAME file if using custom domain (optional)
# echo "docs.capcat.com" > CNAME
```

### Step 3: Update Paths (if needed)
Run this script to check if you need base path updates:

```python
# check_paths.py
import re
from pathlib import Path

def check_html_paths(directory):
    issues = []
    for html_file in Path(directory).rglob('*.html'):
        with open(html_file, 'r') as f:
            content = f.read()
            # Check for absolute local paths
            if re.search(r'href="/(?!http)', content):
                issues.append(f"{html_file}: Has absolute local paths")
    return issues

issues = check_html_paths('.')
for issue in issues:
    print(issue)
```

### Step 4: Git Setup
```bash
# Navigate to your main capcat repository
cd "/path/to/your/capcat/repo"

# Add website files
git add website/

# Commit
git commit -m "Add documentation website for GitHub Pages"

# Push to GitHub
git push origin main
```

### Step 5: Configure GitHub Pages
1. Go to your GitHub repository
2. Click **Settings** → **Pages**
3. Under **Source**:
   - Branch: `main`
   - Folder: `/website` (or `/docs` if you renamed)
4. Click **Save**
5. Wait 1-2 minutes for deployment

**Your site will be live at:**
`https://yourusername.github.io/repository-name/`

---

## 4. Path Configuration Strategy

### If Repository URL is `https://yourusername.github.io/capcat/`

You need to update paths to include `/capcat/` base:

**Option A: Manual Find & Replace**
```bash
# In website/ directory
find . -name "*.html" -exec sed -i '' 's|href="/css/|href="/capcat/css/|g' {} \;
find . -name "*.html" -exec sed -i '' 's|src="/js/|src="/capcat/js/|g' {} \;
```

**Option B: Use Relative Paths (Recommended)**
Keep your current relative paths - they work perfectly:
```html
<!-- Current - works on GitHub Pages -->
<link rel="stylesheet" href="../css/design-system.css">
<link rel="stylesheet" href="../css/main.css">
```

**Option C: Use Jekyll/Build Process**
Configure base URL as variable (more complex, probably unnecessary).

---

## 5. Testing Before Deployment

### Local Testing
Simulate GitHub Pages environment:
```bash
# Install simple HTTP server
python3 -m http.server 8000

# Or use Node.js
npx http-server website -p 8000

# Open browser to:
http://localhost:8000
```

Navigate through all pages to verify:
- ✓ All CSS loads
- ✓ All fonts render
- ✓ All links work
- ✓ All images/icons display
- ✓ JavaScript works
- ✓ Navigation works

---

## 6. Post-Deployment Checklist

After GitHub Pages goes live:

**✓ Verify URLs:**
- Homepage loads: `https://yourusername.github.io/capcat/`
- Documentation loads: `https://yourusername.github.io/capcat/docs/quick-start.html`
- CSS loads properly (check browser DevTools)
- Fonts load properly

**✓ Check Console:**
- Open browser DevTools → Console
- Look for 404 errors (missing resources)
- Fix any broken paths

**✓ Test Navigation:**
- Click all menu links
- Test breadcrumb navigation
- Test footer links
- Test internal documentation links

**✓ Mobile Testing:**
- Responsive layout works
- Mobile menu functions
- Touch targets work

---

## 7. Recommended Final Structure

```
capcat/                                    # Main repository
├── Application/                           # Python app
│   ├── capcat.py
│   ├── core/
│   └── sources/
├── website/                               # GitHub Pages source
│   ├── .nojekyll                         # ← ADD THIS
│   ├── index.html
│   ├── css/
│   │   ├── design-system.css
│   │   └── main.css
│   ├── js/
│   ├── fonts/
│   ├── icons/
│   └── docs/
│       ├── quick-start.html
│       ├── architecture.html
│       └── ...
├── README.md                              # Project readme
└── docs/                                  # Markdown documentation (optional)
    └── ...
```

**GitHub Pages Settings:**
- Source: `main` branch
- Folder: `/website`
- Custom domain: Optional

---

## 8. Optional Enhancements

### A. Custom Domain
If you own `capcat.com`:
1. Add `CNAME` file to `website/`:
   ```
   docs.capcat.com
   ```
2. Configure DNS:
   ```
   docs.capcat.com → CNAME → yourusername.github.io
   ```

### B. 404 Page
Create `website/404.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found - Capcat</title>
    <link rel="stylesheet" href="/capcat/css/design-system.css">
    <link rel="stylesheet" href="/capcat/css/main.css">
</head>
<body>
    <div class="container text-center py-xl">
        <h1>404 - Page Not Found</h1>
        <p><a href="/capcat/">Return to homepage</a></p>
    </div>
</body>
</html>
```

### C. robots.txt & sitemap.xml
```bash
# website/robots.txt
User-agent: *
Allow: /
Sitemap: https://yourusername.github.io/capcat/sitemap.xml

# Generate sitemap (manual or use tool)
```

---

## 9. Common Issues & Solutions

### Issue: CSS Not Loading
**Problem:** Paths broken
**Solution:** Check browser DevTools → Network tab, fix paths in HTML

### Issue: Fonts Not Loading
**Problem:** Font paths in `design-system.css` broken
**Solution:** Verify `url("../fonts/...")` paths are correct

### Issue: 404 on Nested Pages
**Problem:** Jekyll processing files
**Solution:** Ensure `.nojekyll` exists in root

### Issue: Site Not Updating
**Problem:** GitHub Pages cache
**Solution:** Wait 5-10 minutes, hard refresh browser (Cmd+Shift+R)

---

## 10. Deployment Automation (Optional)

### GitHub Actions Workflow
Create `.github/workflows/deploy-pages.yml`:
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'website/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./website
```

---

## 11. Quick Start Command Summary

```bash
# 1. Add .nojekyll
cd website
touch .nojekyll

# 2. Test locally
python3 -m http.server 8000
# Open http://localhost:8000

# 3. Commit and push
cd ../
git add website/
git commit -m "Add documentation site for GitHub Pages"
git push origin main

# 4. Configure on GitHub.com
# Settings → Pages → Source: main, Folder: /website

# 5. Visit your site
# https://yourusername.github.io/capcat/
```

---

## 12. Success Criteria

Deployment is successful when:
- ✓ Site loads at GitHub Pages URL
- ✓ All pages accessible via navigation
- ✓ All CSS styling renders correctly
- ✓ All fonts load properly
- ✓ All images/icons display
- ✓ Mobile responsive layout works
- ✓ JavaScript functionality works
- ✓ No 404 errors in browser console
- ✓ All internal links work
- ✓ Breadcrumb navigation works

---

## 13. Rollback Plan

If deployment fails:
1. Disable GitHub Pages in repository settings
2. Fix issues locally
3. Test with local server
4. Re-enable GitHub Pages
5. Verify deployment

---

## 14. Maintenance Plan

### Regular Updates
- Update content by editing HTML files
- Commit and push changes to `main` branch
- GitHub Pages auto-deploys within 1-2 minutes

### Monitoring
- Check GitHub Pages deployment status in repository
- Monitor browser console for errors
- Test site after each update

### Documentation Updates
- Keep this PRD updated with any configuration changes
- Document custom domain setup if implemented
- Note any path adjustments made

---

## 15. Resources

**GitHub Pages Documentation:**
- https://docs.github.com/en/pages

**Testing Tools:**
- Local server: `python3 -m http.server`
- Browser DevTools: Network tab, Console tab
- Mobile testing: Chrome DevTools responsive mode

**Support:**
- GitHub Pages status: https://www.githubstatus.com/
- Community: https://github.community/

---

## Conclusion

**Your website is already 99% ready for GitHub Pages.** Just add `.nojekyll`, verify paths, and deploy. The static HTML/CSS structure is perfect for GitHub Pages hosting.

**Next Steps:**
1. Create `.nojekyll` file
2. Test locally
3. Push to GitHub
4. Configure GitHub Pages settings
5. Verify deployment

**Estimated Time:** 1-2 hours for initial deployment

---

**Document Owner:** Technical Lead
**Last Updated:** December 19, 2025
**Review Date:** Quarterly or after major updates
