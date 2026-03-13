design-system.css is the centralized source of design tokens. The HTML generator uses DesignSystemCompiler
which:

1. Reads design-system.css
2. Extracts all CSS variables (--font-size-code, --space-md, etc.)
3. Resolves any var() references (e.g., --font-size-body: var(--text-base) → --font-size-body: 1rem)
4. Generates compiled CSS with fully resolved values

Compilation Flow:
design_system_compiler.get_compiled_design_system_css()
↓
compiled_design_system.css + base.css + theme.css
↓
Embedded into HTML <style> tag

The @import statements in base.css and theme.css are for development only (IDE support, local testing). During
HTML generation, the compiler explicitly reads and compiles design-system.css separately - the imports are
NOT processed.

This architecture ensures self-contained HTML files have all CSS values hardcoded without needing external
files for portability.

---

Source of Truth: design-system.css

/_ design-system.css - SINGLE SOURCE OF TRUTH _/
:root {
--font-size-code: 1.125rem;
--space-md: 1.5rem;
--border-color: #232323;
}

Development Files (use variables):

/_ base.css _/
code {
font-size: var(--font-size-code); /_ References design-system.css _/
padding: var(--space-md);
}

/_ theme.css _/
:root {
--border-color: #232323; /_ Can override for dark theme _/
}

Compilation Process:

1. Extract values from design-system.css
2. Replace all var() in base.css → font-size: 1.125rem;
3. Replace all var() in theme.css → --border-color: #232323; (already hardcoded)
4. Embed fully resolved CSS into HTML

Result: Change one value in design-system.css → All references update automatically when compiled.

---

Single Source of Truth:

To change parameters:

| What you want to change                   | Edit this file         |
| ----------------------------------------- | ---------------------- |
| Font sizes, spacing, widths, line heights | design-system.css ONLY |
| Colors, backgrounds, shadows, borders     | theme.css ONLY         |
| Layout/styling using those variables      | base.css               |

Example workflow:

- Want smaller code font? → Edit design-system.css:28 → --font-size-code: 0.9rem;
- Want different dark background? → Edit theme.css:9 → --bg-color: #151515;
- Want different padding on buttons? → Edit base.css selectors (uses existing spacing variables)

Rule: If you find yourself defining a variable in base.css, you're doing it wrong. Move it to
design-system.css or theme.css.
