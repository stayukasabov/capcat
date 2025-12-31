# Utility Classes Reference

A comprehensive set of utility classes for rapid UI development using the design system's CSS variables.

## Text Alignment
- `.text-center` - Center align text
- `.text-left` - Left align text
- `.text-right` - Right align text

## Display
- `.flex` - Display flex
- `.flex-center` - Flex with centered content (justify-center + items-center)
- `.flex-column` - Flex column direction
- `.flex-row` - Flex row direction
- `.inline-flex` - Inline flex
- `.block` - Display block
- `.inline-block` - Display inline-block
- `.hidden` - Display none

## Spacing - Margin
Sizes: `0`, `xs`, `sm`, `md`, `lg`, `xl`, `auto`

Directions:
- `.m-{size}` - All sides
- `.mt-{size}` - Top
- `.mr-{size}` - Right
- `.mb-{size}` - Bottom
- `.ml-{size}` - Left
- `.mx-{size}` - Horizontal (left + right)
- `.my-{size}` - Vertical (top + bottom)
- `.mx-auto` - Auto horizontal centering
- `.my-auto` - Auto vertical centering

Examples:
- `mt-md` - margin-top: var(--space-md)
- `mx-auto` - margin-left: auto; margin-right: auto;
- `mb-lg` - margin-bottom: var(--space-lg)

## Spacing - Padding
Sizes: `0`, `xs`, `sm`, `md`, `lg`, `xl`

Directions (same as margin):
- `.p-{size}` - All sides
- `.pt-{size}` - Top
- `.pr-{size}` - Right
- `.pb-{size}` - Bottom
- `.pl-{size}` - Left
- `.px-{size}` - Horizontal
- `.py-{size}` - Vertical

Examples:
- `p-md` - padding: var(--space-md)
- `px-lg` - padding-left: var(--space-lg); padding-right: var(--space-lg)

## Width & Height
- `.w-full` - width: 100%
- `.w-auto` - width: auto
- `.h-full` - height: 100%
- `.h-auto` - height: auto

## Max Width
- `.max-w-xs` - max-width: 20rem
- `.max-w-sm` - max-width: 24rem
- `.max-w-md` - max-width: 28rem
- `.max-w-lg` - max-width: 32rem
- `.max-w-xl` - max-width: 36rem
- `.max-w-2xl` - max-width: 42rem
- `.max-w-3xl` - max-width: 48rem
- `.max-w-4xl` - max-width: 56rem
- `.max-w-full` - max-width: 100%

## Gap (Flexbox/Grid)
- `.gap-xs` - gap: var(--space-xs)
- `.gap-sm` - gap: var(--space-sm)
- `.gap-md` - gap: var(--space-md)
- `.gap-lg` - gap: var(--space-lg)
- `.gap-xl` - gap: var(--space-xl)

## Justify Content
- `.justify-start` - justify-content: flex-start
- `.justify-center` - justify-content: center
- `.justify-end` - justify-content: flex-end
- `.justify-between` - justify-content: space-between
- `.justify-around` - justify-content: space-around

## Align Items
- `.items-start` - align-items: flex-start
- `.items-center` - align-items: center
- `.items-end` - align-items: flex-end
- `.items-stretch` - align-items: stretch

## Position
- `.relative` - position: relative
- `.absolute` - position: absolute
- `.fixed` - position: fixed
- `.sticky` - position: sticky

## Overflow
- `.overflow-auto` - overflow: auto
- `.overflow-hidden` - overflow: hidden
- `.overflow-visible` - overflow: visible
- `.overflow-x-auto` - overflow-x: auto
- `.overflow-y-auto` - overflow-y: auto

## Border Radius
- `.rounded-none` - border-radius: 0
- `.rounded-sm` - border-radius: var(--radius-sm)
- `.rounded-md` - border-radius: var(--radius-md)
- `.rounded-lg` - border-radius: var(--radius-lg)
- `.rounded-full` - border-radius: 9999px (perfect circle)

## Font Weight
- `.font-light` - font-weight: var(--font-weight-light)
- `.font-normal` - font-weight: var(--font-weight-normal)
- `.font-medium` - font-weight: var(--font-weight-medium)
- `.font-semibold` - font-weight: var(--font-weight-semibold)
- `.font-bold` - font-weight: var(--font-weight-bold)

## Font Size
- `.text-xs` - font-size: var(--text-xsmall)
- `.text-sm` - font-size: var(--text-small)
- `.text-base` - font-size: var(--text-base)
- `.text-lg` - font-size: var(--text-large)
- `.text-xl` - font-size: var(--text-xlarge)
- `.text-2xl` - font-size: var(--text-xxlarge)

## Colors
- `.text-primary` - color: var(--accent-primary)
- `.text-muted` - color: var(--text-muted)
- `.bg-primary` - background-color: var(--accent-primary)
- `.bg-card` - background-color: var(--card-bg)

## Shadow
- `.shadow-sm` - box-shadow: var(--shadow-sm)
- `.shadow-md` - box-shadow: var(--shadow-md)
- `.shadow-lg` - box-shadow: var(--shadow-lg)
- `.shadow-none` - box-shadow: none

## Usage Examples

### Centered Card
```html
<div class="flex-center p-lg">
  <div class="bg-card rounded-lg shadow-md p-md max-w-md">
    <h2 class="text-center mb-md">Card Title</h2>
    <p class="text-muted">Card content</p>
  </div>
</div>
```

### Flex Row with Gap
```html
<div class="flex gap-md items-center">
  <button class="px-md py-sm rounded-md bg-primary">Button 1</button>
  <button class="px-md py-sm rounded-md bg-card">Button 2</button>
</div>
```

### Centered Text Section
```html
<section class="text-center py-xl">
  <h2 class="text-2xl mb-md">Section Title</h2>
  <p class="text-lg text-muted mx-auto max-w-2xl">
    Centered paragraph with max width
  </p>
</section>
```

## Design Principles

1. **Use design system variables** - All utilities reference CSS variables from design-system.css
2. **Mobile-first** - Utilities work on all screen sizes
3. **Composable** - Combine multiple utilities for complex layouts
4. **Semantic over utility** - Use component classes for complex, reusable patterns
5. **Maintainable** - Update design tokens in one place to affect all utilities
