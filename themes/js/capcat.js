// Capcat Theme Toggle and UI Functionality
// External JavaScript for HTML generation

function toggleTheme() {
    const htmlElement = document.documentElement;

    // Determine current theme from data-theme attribute
    const currentTheme = htmlElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    // Apply new theme
    applyTheme(newTheme);

    // Save user preference to localStorage (overrides system preference)
    localStorage.setItem("capcat-theme", newTheme);

    // Update URL hash for file:// protocol persistence
    updateThemeHash(newTheme);

    // Re-inject theme into all links
    if (window.injectThemeIntoLinks) {
        window.injectThemeIntoLinks(newTheme);
    }

    // Dispatch custom event for better cross-window communication
    window.dispatchEvent(new CustomEvent("capcat-theme-change", {
        detail: { theme: newTheme }
    }));
}

function applyTheme(theme) {
    const button = document.querySelector(".theme-toggle");
    const themeIcon = document.querySelector(".theme-icon");
    const htmlElement = document.documentElement;
    const body = document.body;

    // Add theme changing class for smooth animation
    body.classList.add('theme-changing');

    // Set data-theme attribute on HTML element - this is all we need now
    htmlElement.setAttribute('data-theme', theme);

    // Update button icon and accessibility attributes
    if (themeIcon && button) {
        if (theme === "dark") {
            // Dark theme active, icon shows what clicking will do (switch to light)
            themeIcon.style.transform = "scaleX(1)";
            button.setAttribute("aria-pressed", "false");
            button.setAttribute("title", "Switch to light theme");
        } else {
            // Light theme active, icon shows what clicking will do (switch to dark)
            themeIcon.style.transform = "scaleX(-1)";
            button.setAttribute("aria-pressed", "true");
            button.setAttribute("title", "Switch to dark theme");
        }
    }

    // Remove theme changing class after animation completes
    setTimeout(() => {
        body.classList.remove('theme-changing');
    }, 125);
}

// Update URL hash with theme for file:// protocol persistence
function updateThemeHash(theme) {
    const currentHash = window.location.hash;

    // Update or add theme to hash
    let newHash;
    if (currentHash.indexOf('theme=') !== -1) {
        // Replace existing theme value
        newHash = currentHash.replace(/theme=(light|dark)/, 'theme=' + theme);
    } else if (currentHash && currentHash !== '#') {
        // Append theme to existing hash
        newHash = currentHash + '&theme=' + theme;
    } else {
        // Create new hash
        newHash = '#theme=' + theme;
    }

    // Update hash without triggering scroll or page reload
    if (window.history && window.history.replaceState) {
        window.history.replaceState(null, null, newHash);
    } else {
        window.location.hash = newHash;
    }
}


// Copy to clipboard functionality
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        button.textContent = "Copied!";
        button.classList.add("copied");
        setTimeout(function() {
            button.textContent = "Copy";
            button.classList.remove("copied");
        }, 2000);
    }).catch(function(err) {
        console.error('Failed to copy:', err);
        button.textContent = "Error";
        setTimeout(function() {
            button.textContent = "Copy";
        }, 2000);
    });
}

// Theme preference cascade function (matches HTML inline script)
function getThemePreference() {
    // 1. Check localStorage first (user's explicit choice)
    const savedTheme = localStorage.getItem('capcat-theme');
    if (savedTheme) {
        return savedTheme;
    }

    // 2. Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }

    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        return 'light';
    }

    // 3. Default fallback
    return 'dark';
}

document.addEventListener("DOMContentLoaded", function() {
    // Add page transition fade-in effect
    document.body.classList.add('page-transition');

    // Use the initial theme that was computed in the HTML head script
    const initialTheme = window.capcat_initial_theme || getThemePreference();

    // Ensure the theme is properly applied (in case the inline script didn't run)
    applyTheme(initialTheme);

    // Scroll progress bar functionality
    const progressBar = document.querySelector('.progress');
    if (progressBar) {
        function updateProgressBar() {
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight;
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollPercent = Math.min(100, (scrollTop / (documentHeight - windowHeight)) * 100);
            progressBar.style.width = scrollPercent + '%';
        }

        // Update on scroll
        window.addEventListener('scroll', updateProgressBar, { passive: true });
        // Update on resize
        window.addEventListener('resize', updateProgressBar, { passive: true });
        // Initial update
        updateProgressBar();
    }

    // Trigger page fade-in after DOM is ready
    setTimeout(() => {
        document.body.classList.add('fade-in');
    }, 135);

    // Listen for system preference changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            // Only apply system preference if user hasn't explicitly set a preference
            if (!localStorage.getItem('capcat-theme')) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    // Listen for theme changes from other pages (global theme toggle)
    window.addEventListener("storage", function(e) {
        if (e.key === "capcat-theme" && e.newValue) {
            applyTheme(e.newValue);
        }
    });

    // Also listen for custom theme change events (for same-page updates)
    window.addEventListener("capcat-theme-change", function(e) {
        if (e.detail && e.detail.theme) {
            applyTheme(e.detail.theme);
        }
    });
    
    // Add copy buttons to all code blocks
    const codeBlocks = document.querySelectorAll("pre code");
    codeBlocks.forEach(function(block) {
        const pre = block.parentElement;

        // Create copy button
        const button = document.createElement("button");
        button.className = "copy-button";
        button.textContent = "Copy";
        button.setAttribute("aria-label", "Copy code to clipboard");

        // Position button
        pre.style.position = "relative";
        pre.appendChild(button);

        // Copy functionality
        button.addEventListener("click", async function() {
            const code = block.textContent;

            try {
                await navigator.clipboard.writeText(code);
                button.textContent = "Copied!";
                button.classList.add("copied");

                setTimeout(function() {
                    button.textContent = "Copy";
                    button.classList.remove("copied");
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
                button.textContent = "Error";

                setTimeout(function() {
                    button.textContent = "Copy";
                }, 2000);
            }
        });
    });
    
    // Make all links in article content and comments open in new window
    const contentLinks = document.querySelectorAll("main a, .comment-content a");
    contentLinks.forEach(function(link) {
        // Skip internal navigation links (those starting with #, relative paths, or specific internal elements)
        const href = link.getAttribute("href");
        if (href && !href.startsWith("#") && !href.includes("article.html") && !href.includes("comments.html") && !href.includes("news.html") && !href.includes("index.html")) {
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        }
    });

    // Add navigation fade effects for internal links
    const internalLinks = document.querySelectorAll("a[href*='article.html'], a[href*='comments.html'], a[href*='news.html'], a[href*='index.html'], .navigation-container a");
    internalLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Only apply fade effect for internal navigation
            const href = link.getAttribute("href");
            if (href && (href.includes(".html") || href.startsWith("./"))) {
                document.body.classList.remove('fade-in');
                document.body.style.opacity = '0.85';

                // Allow navigation to proceed after brief fade
                setTimeout(() => {
                    // Navigation will happen naturally after this timeout
                }, 100);
            }
        });
    });

    // Back to top button
    const backToTopButton = document.getElementById("backToTopBtn");

    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.opacity = "1";
                backToTopButton.style.visibility = "visible";
            } else {
                backToTopButton.style.opacity = "0";
                backToTopButton.style.visibility = "hidden";
            }
        }, { passive: true });
    }
});

function scrollToTop() {
    window.scrollTo({top: 0, behavior: 'smooth'});
}
