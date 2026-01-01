# Capcat Website

Modern, responsive website for the Capcat article archiving tool.

## Design System

### Color Palette

Inspired by the UX Writing Skill design with warm, readable colors:

- **Cream Background:** `#FAF8EE` - Soft, paper-like reading surface
- **Ink Text:** `#1a1614` - High contrast, readable dark text
- **Ink Light:** `#4a4540` - Secondary text color
- **Accent Orange:** `#EA5E34` - Capcat brand color for CTAs and highlights

### Typography

- **Font Family:** IBM Plex Serif for headings and body text
- **Golden Ratio Scale:** 1.618 progression for harmonious hierarchy
- **Base Size:** 18px (1.125rem) for optimal readability
- **Line Height:** 1.6 for body text, 1.2 for headings

### Spacing System

Multiples of 8px for consistent rhythm:
- **xs:** 8px (0.5rem)
- **sm:** 16px (1rem)
- **md:** 24px (1.5rem)
- **lg:** 32px (2rem)
- **xl:** 48px (3rem)
- **xxl:** 64px (4rem)
- **xxxl:** 96px (6rem)

## File Structure

```
website/
├── index.html              # Homepage
├── css/
│   ├── design-system.css   # Design tokens and variables
│   └── main.css            # Component styles
├── js/
│   └── main.js             # Interactive behaviors
├── fonts/
│   └── IBMPlex/            # IBM Plex Serif font files
├── images/
│   └── ...                 # Website assets
└── README.md               # This file
```

## Features

### Homepage Sections

1. **Hero Section**
   - Main value proposition
   - CTA buttons
   - Interactive code demo

2. **Problem Section**
   - Information overload challenges
   - Research-backed statistics
   - User pain points

3. **Features Section**
   - Dual-mode architecture
   - CLI and TUI comparison
   - Key capabilities

4. **How It Works**
   - 5-step workflow visualization
   - Progressive disclosure

5. **Dual Mode Benefits**
   - Side-by-side comparison
   - Use case scenarios
   - Learning progression path

6. **Tutorials Section**
   - CLI commands
   - Interactive menu guides
   - Advanced topics
   - Learning paths for different user types

7. **Sources & Capabilities**
   - 17+ pre-configured sources
   - Categories: Tech, News, Science, AI
   - Custom RSS source addition guide

8. **Get Started**
   - Installation steps
   - Quick start commands
   - GitHub CTA

### Responsive Design

- **Desktop:** 1200px+ optimal width, horizontal navigation
- **Tablet:** 768px - 1023px, 2-column grids, full-screen menu
- **Mobile:** < 768px, single-column layout, full-screen overlay menu
- **Small Mobile:** < 480px, optimized touch targets, compressed spacing

#### Mobile Menu Features
- Full-screen overlay with cream background
- Smooth fade-in/fade-out animations (0.4s)
- Staggered menu item animations
- Animated hamburger icon (transforms to X)
- Body scroll lock when menu is open
- Close on: link click, overlay click, or Escape key
- 44px minimum touch targets for accessibility

### Interactive Features

- **Smooth scrolling** for anchor links with offset
- **Intersection Observer** animations for scroll-triggered reveals
- **Code snippet copy** buttons with success feedback
- **Full-screen mobile menu** with fade overlay
- **Animated hamburger** icon (3-line to X transformation)
- **Scroll-aware header** with shadow on scroll
- **Body scroll lock** prevents background scrolling when menu open
- **Keyboard navigation** (Escape to close menu)
- **Touch-optimized** 44px minimum hit areas

## Typography Scale

Based on golden ratio (1.618):

| Level | Desktop | Mobile | Usage |
|-------|---------|--------|-------|
| h1 | 2.618rem (42px) | 1.618rem (26px) | Page titles |
| h2 | 1.618rem (26px) | 1.25rem (20px) | Section headers |
| h3 | 1.25rem (20px) | 1.125rem (18px) | Subsections |
| body | 1.125rem (18px) | 1rem (16px) | Main text |
| small | 0.875rem (14px) | 0.875rem (14px) | Captions |

## Component Library

### Cards

- **Problem Card:** Pain point highlighting
- **Feature Card:** Product capabilities
- **Tutorial Card:** Learning resource links
- **Path Card:** Guided learning sequences
- **Source Category:** Available RSS sources by topic

### Buttons

- **Primary:** Orange background, white text
- **Secondary:** Transparent with border
- **Large variant:** Increased padding for CTAs

### Code Blocks

- Cream tinted background
- Monaco/SF Mono font stack
- Copy-to-clipboard functionality
- Syntax highlighting ready

### Navigation

- Sticky header with backdrop blur
- Desktop horizontal menu
- Mobile slide-down menu
- Smooth scroll to sections

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern mobile browsers

## Performance

- CSS custom properties for theming
- Minimal JavaScript (~5KB)
- Web font optimization with font-display: swap
- Lazy-loaded animations via Intersection Observer
- No external dependencies
- Hardware-accelerated transitions
- Viewport height fix for mobile browsers
- Optimized touch targets for mobile (44x44px minimum)

## Accessibility

- Semantic HTML5 structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Color contrast WCAG AA compliant
- Focus indicators for all interactive elements
- Responsive text sizing

## External Links

- **Case Study:** Links to Substack blog post in main navigation (update URL before launch)
- **GitHub:** Repository link
- **Designer Portfolio:** https://stayux.com

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Search functionality
- [ ] Interactive source selector
- [ ] User testimonials section
- [ ] Video tutorials embed
- [ ] Download analytics
- [ ] Newsletter signup
- [ ] Syntax highlighting for code blocks

## Development

### Local Testing

1. Open `index.html` in a modern browser
2. Use a local server for best experience:
   ```bash
   python -m http.server 8000
   # Navigate to http://localhost:8000
   ```

### Font Files

SourceSerif4 font files should be placed in `fonts/

### Customization

All design tokens are defined in `css/design-system.css`:
- Colors: `:root` CSS custom properties
- Spacing: `--space-*` variables
- Typography: `--text-*` and `--font-*` variables
- Layout widths: `--measure-*` variables

## Credits

- **Design & Development:** Stayu Kasabov
- **Typography:** IBM Plex Serif by IBM
- **Inspiration:** Source Serif 4 design palette
- **Architecture:** Based on Capcat case study

## License

See main Capcat repository for licensing information.
