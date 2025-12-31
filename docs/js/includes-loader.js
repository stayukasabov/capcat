/**
 * Capcat Includes Loader
 * Loads header and footer from /includes/ folder
 */

(function() {
  // Calculate relative path to includes folder based on current location
  function getIncludesPath() {
    const path = window.location.pathname;
    const depth = (path.match(/\//g) || []).length - 2; // -2 for /docs/ base
    return '../'.repeat(Math.max(0, depth)) + 'includes/';
  }

  // Load include file and inject into placeholder
  async function loadInclude(file, placeholderId) {
    try {
      const includesPath = getIncludesPath();
      const response = await fetch(includesPath + file);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const html = await response.text();
      const placeholder = document.getElementById(placeholderId);
      if (placeholder) {
        placeholder.outerHTML = html;
      }
    } catch (error) {
      console.error(`Failed to load ${file}:`, error);
    }
  }

  // Load when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    loadInclude('header.html', 'header-placeholder');
    loadInclude('footer.html', 'footer-placeholder');
  }
})();
