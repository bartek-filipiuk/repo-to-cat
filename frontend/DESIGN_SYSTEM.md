# Repo-to-Cat Design System

**Version:** 1.0
**Last Updated:** 2025-10-14
**Framework:** Astro 5.14.4 + Tailwind CSS 3.4.17

---

## Overview

The Repo-to-Cat frontend uses an **Oxide-inspired design system** featuring a dark theme with vibrant green accents. The design emphasizes clarity, smooth interactions, and professional presentation of AI-generated cat images.

---

## Color Palette

### Primary Colors

```css
--oxide-dark:       #0a0a0a    /* Main background */
--oxide-green:      #00ffa3    /* Primary accent, CTAs */
--oxide-green-dim:  #00cc82    /* Hover states */
```

### Neutral Colors

```css
--oxide-gray:        #1a1a1a   /* Cards, inputs */
--oxide-gray-light:  #2a2a2a   /* Borders */
--oxide-darker:      #050505   /* Image placeholders */
```

### Text Colors

```css
--oxide-text:        #e0e0e0   /* Primary text */
--oxide-text-dim:    #a0a0a0   /* Secondary text */
--oxide-text-darker: #707070   /* Tertiary text */
```

### Semantic Colors

```css
/* Code Quality Badges */
--quality-high:  #00ffa3 (>= 8.0)   /* Green */
--quality-mid:   #facc15 (6.0-7.9)  /* Yellow */
--quality-low:   #ef4444 (< 6.0)    /* Red */
```

---

## Typography

### Font Stack

```css
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
             "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

### Type Scale

| Element       | Size   | Weight    | Usage                              |
|---------------|--------|-----------|-------------------------------------|
| H1            | 2.25rem| Bold (700)| Page titles                        |
| H2            | 1.5rem | Semibold  | Section headings                   |
| H3            | 1.125rem| Semibold | Card titles, subsections           |
| Body          | 1rem   | Regular   | Main content                       |
| Small         | 0.875rem| Regular  | Metadata, dates                    |
| Tiny          | 0.75rem| Regular   | Badges, labels                     |

---

## Components

### Buttons

#### Primary Button
```html
<button class="btn-primary">Generate</button>
```

**Styles:**
- Background: Oxide Green (#00ffa3)
- Text: Oxide Dark (#0a0a0a)
- Hover: Scales to 105%, dims to #00cc82
- Active: Scales to 95%
- Transition: 200ms ease-out

#### Secondary Button
```html
<button class="btn-secondary">Cancel</button>
```

**Styles:**
- Background: Oxide Gray (#1a1a1a)
- Border: 1px Oxide Green (#00ffa3)
- Text: Oxide Text (#e0e0e0)
- Hover: Green background, dark text
- Transition: 200ms ease-out

---

### Cards

#### Standard Card
```html
<div class="card">
  <!-- Content -->
</div>
```

**Styles:**
- Background: Oxide Gray (#1a1a1a)
- Border: 1px transparent → Oxide Green on hover
- Padding: 1.5rem (24px)
- Border radius: 0.5rem (8px)
- Shadow: Subtle green glow on hover
- Transition: 300ms ease-out

#### Interactive Card
```html
<a href="/link" class="card-interactive">
  <!-- Content -->
</a>
```

**Styles:**
- Extends `.card`
- Cursor: pointer
- Hover: Scales to 102%
- Active: Scales to 98%
- Transition: 300ms ease-out

---

### Inputs

```html
<input type="text" class="input" placeholder="Enter text" />
```

**Styles:**
- Background: Oxide Gray (#1a1a1a)
- Border: 1px Oxide Gray Light (#2a2a2a)
- Text: Oxide Text (#e0e0e0)
- Focus: Green border + subtle ring
- Transition: 200ms ease-out

---

### Links

#### Standard Link
```html
<a href="#" class="link">Documentation</a>
```

**Styles:**
- Color: Oxide Green (#00ffa3)
- Hover: Dims to #00cc82, underline appears
- Transition: 150ms ease-out

#### Subtle Link
```html
<a href="#" class="link-subtle">Back to Dashboard</a>
```

**Styles:**
- Color: Oxide Text Dim (#a0a0a0)
- Hover: Changes to Oxide Green (#00ffa3)
- No underline
- Transition: 150ms ease-out

---

## Responsive Design

### Breakpoints

```css
sm:  640px   /* Mobile landscape */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
```

### Grid System

**Dashboard Generation Grid:**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- Cards -->
</div>
```

| Viewport  | Columns | Gap  |
|-----------|---------|------|
| Mobile    | 1       | 24px |
| Tablet    | 2       | 24px |
| Desktop   | 3       | 24px |

---

## Layout Patterns

### Page Container
```html
<div class="container mx-auto px-4 py-8 max-w-7xl">
  <!-- Content -->
</div>
```

### Section Spacing
- Between sections: `mb-8` (32px)
- Within sections: `mb-6` (24px)
- Between elements: `mb-4` (16px)

---

## Animations & Transitions

### Timing Functions

```css
ease-out:       Smooth deceleration (buttons, links)
ease-in-out:    Balanced (modals, overlays)
linear:         Constant speed (loaders)
```

### Duration Standards

| Duration | Usage                              |
|----------|------------------------------------|
| 150ms    | Quick interactions (links, badges) |
| 200ms    | Standard interactions (buttons)    |
| 300ms    | Complex interactions (cards)       |
| 500ms    | Dramatic effects (image zoom)      |

### Common Transitions

**Button Hover:**
```css
transition: all 200ms ease-out;
transform: scale(1.05);
```

**Card Hover:**
```css
transition: all 300ms ease-out;
transform: scale(1.02);
border-color: #00ffa3;
box-shadow: 0 10px 15px rgba(0, 255, 163, 0.1);
```

**Image Zoom (on card hover):**
```css
transition: transform 500ms ease-out;
transform: scale(1.10);
```

---

## Icons

**Source:** Heroicons (SVG)
**Style:** Outline
**Size:** 24×24px (default), 16×16px (inline)

**Usage:**
```html
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
</svg>
```

---

## Accessibility

### Focus States

All interactive elements have visible focus indicators:
```css
focus:outline-none
focus:ring-2
focus:ring-oxide-green/20
focus:border-oxide-green
```

### Color Contrast

- Text on Dark Background: 14.4:1 (AAA)
- Green on Dark Background: 8.2:1 (AAA)
- Dim Text on Dark: 5.1:1 (AA)

### Keyboard Navigation

- All buttons and links are keyboard accessible
- Tab order follows visual layout
- Focus indicators clearly visible

---

## Best Practices

### Do ✓
- Use `card-interactive` for clickable cards
- Apply hover effects to interactive elements
- Use semantic HTML (buttons for actions, links for navigation)
- Include alt text for all images
- Test color combinations for sufficient contrast

### Don't ✗
- Don't mix `.card` and `.card-interactive` on same element
- Don't override Tailwind classes with inline styles
- Don't use green text on green backgrounds
- Don't create custom colors outside the palette
- Don't omit transitions on interactive elements

---

## Component Examples

### Generation Card

```astro
<a href={`/generation/${id}`} class="card-interactive group block">
  <div class="aspect-square mb-4 rounded overflow-hidden bg-oxide-darker">
    <img
      src={imagePath}
      alt="Cat for {repoName}"
      class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 ease-out"
    />
  </div>
  <h3 class="text-lg font-semibold text-oxide-text group-hover:text-oxide-green transition-colors">
    {repoName}
  </h3>
  <p class="text-sm text-oxide-text-dim">{owner}</p>
</a>
```

### Quality Badge

```astro
{score >= 8 && (
  <span class="text-xs px-2 py-1 rounded bg-oxide-green/20 text-oxide-green border border-oxide-green/30">
    Score: {score.toFixed(1)}
  </span>
)}
```

### Form Input

```astro
<input
  type="url"
  class="input w-full"
  placeholder="https://github.com/owner/repo"
  required
/>
```

---

## File Structure

```
frontend/
├── src/
│   ├── styles/
│   │   └── global.css          # Design system implementation
│   ├── components/
│   │   ├── Layout.astro        # Base layout with header/footer
│   │   ├── GenerationCard.astro # Card component
│   │   ├── GenerationList.astro # Grid layout
│   │   └── GenerateForm.astro   # Form with polling
│   └── pages/
│       ├── index.astro          # Dashboard
│       ├── login.astro          # Auth page
│       └── generation/[id].astro # Detail page
└── tailwind.config.mjs          # Color palette config
```

---

## Maintenance

### Adding New Colors

1. Define in `tailwind.config.mjs`:
   ```js
   colors: {
     'oxide-custom': '#hexcode',
   }
   ```

2. Document in this file
3. Ensure AA/AAA contrast ratios
4. Test across all components

### Adding New Components

1. Create component file in `src/components/`
2. Use existing utility classes when possible
3. Define new utility class in `global.css` if reusable
4. Document in this file with example
5. Test responsive behavior

---

## Resources

- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **Astro Docs:** https://docs.astro.build
- **Heroicons:** https://heroicons.com
- **WebAIM Contrast Checker:** https://webaim.org/resources/contrastchecker/

---

**Maintained by:** Repo-to-Cat Team
**Questions?** See `frontend/README.md` or project documentation
