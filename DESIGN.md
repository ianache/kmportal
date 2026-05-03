---
name: Luminous Knowledge
colors:
  surface: '#f9f9ff'
  surface-dim: '#d8d9e5'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3fe'
  surface-container: '#ecedf9'
  surface-container-high: '#e6e8f3'
  surface-container-highest: '#e0e2ed'
  on-surface: '#181c23'
  on-surface-variant: '#414755'
  inverse-surface: '#2d3039'
  inverse-on-surface: '#eef0fc'
  outline: '#717786'
  outline-variant: '#c1c6d7'
  surface-tint: '#005bc1'
  primary: '#0058bc'
  on-primary: '#ffffff'
  primary-container: '#0070eb'
  on-primary-container: '#fefcff'
  inverse-primary: '#adc6ff'
  secondary: '#5e5e63'
  on-secondary: '#ffffff'
  secondary-container: '#e0dfe4'
  on-secondary-container: '#626267'
  tertiary: '#9e3d00'
  on-tertiary: '#ffffff'
  tertiary-container: '#c64f00'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#e3e2e7'
  secondary-fixed-dim: '#c7c6cb'
  on-secondary-fixed: '#1a1b1f'
  on-secondary-fixed-variant: '#46464b'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb595'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7c2e00'
  background: '#f9f9ff'
  on-background: '#181c23'
  surface-variant: '#e0e2ed'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.25'
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 17px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: -0.01em
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
    letterSpacing: 0em
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  max-width: 1200px
---

## Brand & Style

The design system is engineered for a premium knowledge management experience that prioritizes clarity, focus, and intellectual calm. It targets power users, researchers, and creative professionals who require a tool that feels invisible yet highly capable. 

The aesthetic is a fusion of **Minimalism** and **Glassmorphism**, heavily influenced by contemporary Apple web standards. It utilizes significant whitespace to reduce cognitive load and employs translucent layers to maintain spatial context. The emotional response is one of "focused sophistication"—a digital workspace that feels as high-end and intentional as a physical studio.

## Colors

The palette is intentionally restrained to allow user content to remain the focal point. 

- **Canvas & Surface:** The primary background uses a cool light gray (#F5F5F7), while interactive surfaces and content cards use pure white (#FFFFFF) to create a subtle natural lift.
- **Accents:** A single vibrant blue (#007AFF) is used sparingly for primary actions and active states. 
- **Typography:** High-contrast neutrals are used for hierarchy. #1D1D1F provides near-black intensity for headers, while #86868B is used for secondary metadata and icons.

## Typography

The typography system relies on **Inter**, a typeface designed for screen readability that mirrors the functional elegance of San Francisco. 

Hierarchy is established through weight and slight tracking adjustments rather than dramatic size shifts. Display sizes use tighter tracking and heavier weights to feel authoritative. Body text is set at 17px—a signature Apple sizing choice—to ensure effortless readability for long-form knowledge consumption.

## Layout & Spacing

This design system employs a **Fixed Grid** for content consumption and a **Fluid Layout** for the workspace editor. 

- **Grid:** A 12-column grid with 24px gutters ensures structural alignment across the platform. 
- **Rhythm:** Spacing follows an 8px linear scale. Large-scale sections are separated by 48px or 64px to create an "airy" feel that prevents the UI from feeling cluttered.
- **Margins:** Generous outer margins (40px on desktop) frame the content, signaling that the information within is valuable and curated.

## Elevation & Depth

Depth in this design system is achieved through **Glassmorphism** and soft, ambient shadows.

1.  **Backdrop Blurs:** Headers and sidebars use a `saturate(180%) blur(20px)` effect with a semi-transparent white background (`rgba(255, 255, 255, 0.7)`). This maintains a sense of place as the user scrolls.
2.  **Shadows:** Shadows are highly diffused and low-opacity. They should never look "muddy." Use a 0px offset for Y-axis on standard cards to create a subtle glow, or a 4px Y-offset for floating modals to indicate higher elevation.
3.  **Borders:** Use ultra-thin (1px) borders in a light gray (`#E5E5E7`) instead of heavy shadows to define boundaries between similar tonal layers.

## Shapes

The shape language is "Rounded" to convey a modern, approachable, yet professional tone. 

- **Standard Elements:** Buttons and input fields use a 10px corner radius.
- **Containers:** Content cards and larger sections utilize a 12px to 16px radius.
- **Interactive States:** Hover states on list items or navigation links should use a 6px-8px radius to softly highlight the selection without feeling sharp.

## Components

### Buttons
- **Primary:** Solid blue (#007AFF) with white text. High-gloss finish via subtle 10% white-to-transparent vertical gradient.
- **Secondary:** Light gray background with blue text. No border.

### Cards
- Pure white background with a 1px border (#E5E5E7) and a very soft 10px blur shadow. Padding should be generous (24px-32px).

### Input Fields
- Subtle gray background (#F2F2F7) that transitions to white with a blue glow/border on focus. 

### Glass Sidebars
- Full-height containers with `backdrop-filter: blur(30px)`. Navigation items should have a 100% width hover state with a 8px border-radius.

### Chips & Tags
- Pill-shaped with a light gray fill and #424245 text. No borders. Used for categorization and metadata.

### Additional Elements
- **Segmented Controls:** A sliding toggle style for switching views, utilizing a soft gray track and a white high-elevation "thumb" for the active state.
- **Breadcrumbs:** Minimalist text links separated by a chevron, set in `body-sm` to maintain focus on the page title.