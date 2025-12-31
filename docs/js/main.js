// Capcat Website JavaScript

document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  initMobileMenu();

  // Smooth scrolling for anchor links
  initSmoothScroll();

  // Intersection Observer for animations
  initScrollAnimations();

  // Copy code snippets
  initCodeCopy();
});

/**
 * Mobile Menu Toggle with Full-Screen Overlay
 */
function initMobileMenu() {
  const toggle = document.querySelector(".mobile-menu-toggle");
  const navLinks = document.querySelector(".nav-links");
  const body = document.body;

  if (!toggle || !navLinks) return;

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = navLinks.classList.contains("active");

    if (isOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  function openMenu() {
    navLinks.classList.add("active");
    toggle.classList.add("active");
    toggle.setAttribute("aria-expanded", "true");
    body.classList.add("menu-open");
  }

  function closeMenu() {
    navLinks.classList.remove("active");
    toggle.classList.remove("active");
    toggle.setAttribute("aria-expanded", "false");
    body.classList.remove("menu-open");
  }

  // Close menu when clicking on the overlay (but not on links)
  navLinks.addEventListener("click", (e) => {
    // If clicking on the background (not a link)
    if (e.target === navLinks) {
      closeMenu();
    }
  });

  // Close menu when any link is clicked
  const links = navLinks.querySelectorAll("a");
  links.forEach((link) => {
    link.addEventListener("click", () => {
      closeMenu();
    });
  });

  // Close menu on escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && navLinks.classList.contains("active")) {
      closeMenu();
    }
  });
}

/**
 * Smooth Scrolling for Anchor Links
 */
function initSmoothScroll() {
  const links = document.querySelectorAll('a[href^="#"]');

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      const href = link.getAttribute("href");

      // Skip empty anchors
      if (href === "#") return;

      const target = document.querySelector(href);

      if (target) {
        e.preventDefault();

        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition =
          elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth",
        });

        // Update URL without jumping
        history.pushState(null, null, href);
      }
    });
  });
}

/**
 * Scroll Animations with Intersection Observer
 */
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-in");
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe elements
  const animatedElements = document.querySelectorAll(
    ".problem-card, .feature-card, .workflow-step, .tutorial-card, .path-card, .source-category, .install-step"
  );

  animatedElements.forEach((el) => {
    el.classList.add("animate-target");
    observer.observe(el);
  });

  // Add CSS for animations
  addAnimationStyles();
}

/**
 * Add Animation Styles Dynamically
 */
function addAnimationStyles() {
  const style = document.createElement("style");
  style.textContent = `
    .animate-target {
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .animate-in {
      opacity: 1;
      transform: translateY(0);
    }
  `;
  document.head.appendChild(style);
}

/**
 * Copy Code Snippets
 */
function initCodeCopy() {
  const codeBlocks = document.querySelectorAll("pre code");

  codeBlocks.forEach((block) => {
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
    button.addEventListener("click", async () => {
      const code = block.textContent;

      try {
        await navigator.clipboard.writeText(code);
        button.textContent = "Copied!";
        button.classList.add("copied");

        setTimeout(() => {
          button.textContent = "Copy";
          button.classList.remove("copied");
        }, 2000);
      } catch (err) {
        console.error("Failed to copy:", err);
        button.textContent = "Error";

        setTimeout(() => {
          button.textContent = "Copy";
        }, 2000);
      }
    });
  });

  // Add copy button styles
  addCopyButtonStyles();
}

/**
 * Add Copy Button Styles
 */
function addCopyButtonStyles() {
  const style = document.createElement("style");
  style.textContent = `
    .copy-button {
      position: absolute;
      top: 8px;
      right: 8px;
      padding: 4px 12px;
      font-size: 0.75rem;
      font-family: var(--font-family-sans-serif);
      background-color: rgba(255, 83, 31, 0.9);
      color: #ffffff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      opacity: 0;
      transition: opacity 0.2s ease, background-color 0.2s ease;
      z-index: 10;
    }

    pre:hover .copy-button {
      opacity: 1;
    }

    .copy-button:hover {
      background-color: rgba(234, 94, 52, 1);
    }

    .copy-button.copied {
      background-color: #22c55e;
    }

    .copy-button:focus {
      outline: 2px solid var(--accent-primary);
      outline-offset: 2px;
    }
  `;
  document.head.appendChild(style);
}

/**
 * Header scroll behavior
 */
window.addEventListener(
  "scroll",
  () => {
    const header = document.querySelector(".site-header");
    if (!header) return;

    const hero = document.querySelector(".hero");

    // Add shadow when scrolled
    if (window.scrollY > 50) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }

    // Invert header when past hero section (only on pages with hero)
    if (hero) {
      const heroBottom = hero.offsetTop + hero.offsetHeight;
      if (window.scrollY > heroBottom - 100) {
        header.classList.add("inverted");
      } else {
        header.classList.remove("inverted");
      }
    } else {
      // On docs pages without hero, invert header after scrolling a bit
      if (window.scrollY > 200) {
        header.classList.add("inverted");
      } else {
        header.classList.remove("inverted");
      }
    }
  },
  { passive: true }
);

// Add header scroll styles
const headerStyle = document.createElement("style");
headerStyle.textContent = `
  .site-header.scrolled {
    box-shadow: 0 2px 8px rgba(26, 22, 20, 0.15);
  }

  .site-header.inverted.scrolled {
    box-shadow: 0 2px 8px rgba(26, 22, 20, 0.18);
  }
`;
document.head.appendChild(headerStyle);

/**
 * Viewport height fix for mobile browsers
 */
function setVH() {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty("--vh", `${vh}px`);
}

// Set on load and resize
setVH();
window.addEventListener("resize", setVH);
window.addEventListener("orientationchange", setVH);

/**
 * Back to Top Button
 */
function initBackToTop() {
  const backToTopButton = document.getElementById("backToTopBtn");

  if (backToTopButton) {
    window.addEventListener(
      "scroll",
      function () {
        if (window.pageYOffset > 300) {
          backToTopButton.style.opacity = "1";
          backToTopButton.style.visibility = "visible";
        } else {
          backToTopButton.style.opacity = "0";
          backToTopButton.style.visibility = "hidden";
        }
      },
      { passive: true }
    );

    backToTopButton.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }
}

/*Capcat-cat-elastic-hover*/

class HoverButton {
  constructor(el) {
    this.el = el;
    this.hover = false;
    this.calculatePosition();
    this.attachEventsListener();
  }

  attachEventsListener() {
    window.addEventListener('mousemove', e => this.onMouseMove(e));
    window.addEventListener('resize', e => this.calculatePosition(e));

    // Use passive listener and requestAnimationFrame for scroll performance
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          this.calculatePosition();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  calculatePosition() {
    if (typeof gsap === 'undefined') {
      console.error('GSAP library not loaded');
      return;
    }
    gsap.set(this.el, {
      x: 0,
      y: 0,
      scale: 1
    });
    const box = this.el.getBoundingClientRect();
    this.x = box.left + (box.width * 0.5);
    this.y = box.top + (box.height * 0.5);
    this.width = box.width;
    this.height = box.height;
  }

  onMouseMove(e) {
    let hover = false;
    let hoverArea = (this.hover ? 0.35 : 0.25);
    let x = e.clientX - this.x;
    let y = e.clientY - this.y;
    let distance = Math.sqrt( x*x + y*y );
    if (distance < (this.width * hoverArea)) {
      hover = true;
      if (!this.hover) {
        this.hover = true;
        this.onHover(e.clientX, e.clientY);
      } else {
        // Update position without blur when already hovering
        this.onHoverUpdate(e.clientX, e.clientY);
      }
    }

    if(!hover && this.hover) {
      this.onLeave();
      this.hover = false;
    }
  }

  onHover(x, y) {
    if (typeof gsap === 'undefined') return;

    const deltaX = (x - this.x) * 0.4;
    const deltaY = (y - this.y) * 0.4;

    gsap.to(this.el, {
      x: deltaX,
      y: deltaY,
      scale: 1.15,
      ease: 'power2.out',
      duration: 0.4
    });

    this.el.style.zIndex = 10;
  }

  onHoverUpdate(x, y) {
    if (typeof gsap === 'undefined') return;

    const deltaX = (x - this.x) * 0.4;
    const deltaY = (y - this.y) * 0.4;

    gsap.to(this.el, {
      x: deltaX,
      y: deltaY,
      scale: 1.15,
      duration: 0.15,
      ease: 'power2.out',
      overwrite: true
    });
  }

  onLeave() {
    if (typeof gsap === 'undefined') return;

    gsap.to(this.el, {
      x: 0,
      y: 0,
      scale: 1,
      ease: 'elastic.out(1.2, 0.4)',
      duration: 0.7
    });

    this.el.style.zIndex = 1;
  }
}

// Initialize elastic hover with retry mechanism
function initElasticHover() {
  // Only run on pages with svg-wrapper (index page)
  const svgWrapper = document.querySelector('.svg-wrapper');
  if (!svgWrapper) {
    return; // No svg-wrapper, skip initialization silently
  }

  let attempts = 0;
  const maxAttempts = 20;

  function tryInit() {
    attempts++;

    if (typeof gsap === 'undefined') {
      if (attempts < maxAttempts) {
        requestAnimationFrame(tryInit);
      } else {
        console.error('GSAP library failed to load after maximum attempts');
      }
      return;
    }

    const box = svgWrapper.getBoundingClientRect();
    if (box.width === 0 || box.height === 0) {
      if (attempts < maxAttempts) {
        requestAnimationFrame(tryInit);
      } else {
        console.error('SVG wrapper has no dimensions after maximum attempts');
      }
      return;
    }

    // Initialize the hover effect
    new HoverButton(svgWrapper);
  }

  // Start trying immediately
  requestAnimationFrame(tryInit);
}

// Single initialization point for all DOM-dependent code
window.addEventListener("load", () => {
  // Initialize back to top button
  initBackToTop();

  // Initialize elastic hover effect with retry mechanism
  initElasticHover();

  // Prevent context menu on cat card
  const capcatCard = document.getElementById('capcatCard');
  if (capcatCard) {
    capcatCard.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      return false;
    });
  }
});
