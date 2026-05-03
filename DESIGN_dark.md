---
name: Luminous Knowledge Dark
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1b1b1d'
  surface-container: '#1f1f21'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e4e2e4'
  on-surface-variant: '#c0c6d6'
  inverse-surface: '#e4e2e4'
  inverse-on-surface: '#303032'
  outline: '#8b91a0'
  outline-variant: '#414754'
  surface-tint: '#aac7ff'
  primary: '#aac7ff'
  on-primary: '#003064'
  primary-container: '#3e90ff'
  on-primary-container: '#002957'
  inverse-primary: '#005db8'
  secondary: '#c2c1ff'
  on-secondary: '#1800a7'
  secondary-container: '#3630bf'
  on-secondary-container: '#b1b1ff'
  tertiary: '#ffb691'
  on-tertiary: '#552000'
  tertiary-container: '#eb6a12'
  on-tertiary-container: '#4a1b00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#aac7ff'
  on-primary-fixed: '#001b3e'
  on-primary-fixed-variant: '#00468d'
  secondary-fixed: '#e2dfff'
  secondary-fixed-dim: '#c2c1ff'
  on-secondary-fixed: '#0c006b'
  on-secondary-fixed-variant: '#332dbc'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb691'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#793100'
  background: '#131315'
  on-background: '#e4e2e4'
  surface-variant: '#353437'
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
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: '0'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin: 32px
---

## Brand & Style

The design system is centered on the concept of "Illuminated Intellect." It is designed for researchers, academics, and power users who spend extended periods in deep focus. The aesthetic is a fusion of **Corporate Modern** and **Glassmorphism**, heavily inspired by premium desktop operating systems. 

The personality is authoritative yet quiet, providing a high-end digital environment that recedes into the background to let content shine. By utilizing deep, monochromatic foundations paired with translucent architectural elements, the design system creates a sense of physical space and hierarchy without visual clutter. The emotional response is one of calm, professional focus and sophisticated reliability.

## Colors

The color palette is anchored in deep charcoal and near-black tones to reduce eye strain. The primary background uses a pure, matte charcoal (#121212), while elevated surfaces and containers transition to a slightly warmer near-black (#1C1C1E). 

The primary accent is a vibrant, high-legibility "Apple Blue" (#0A84FF), used sparingly for interactive states and primary actions. Secondary accents are reserved for data visualization or subtle categorization. Semantic colors (success, warning, error) are desaturated to maintain the premium feel while ensuring accessible contrast against the dark backdrop.

## Typography

This design system utilizes **Inter** for all typographic needs to ensure maximum clarity and a systematic, utilitarian feel. The hierarchy is established through significant weight shifts rather than excessive size changes. 

High-level headings use tight letter spacing and bold weights to feel grounded. Body text is optimized for long-form reading with a generous 1.6x line height and a subtle off-white color (#E5E5E7) to prevent the "vibrating" effect of pure white text on black backgrounds. Labels and metadata use a slightly brighter grey (#A1A1A6) with increased tracking for instant scannability.

## Layout & Spacing

The design system employs a **Fluid Grid** model with a strict 8px base unit. Content is organized within a 12-column system that adapts to screen width while maintaining consistent 24px gutters. 

White space (or "dark space") is used aggressively to separate logical sections, avoiding the need for heavy dividers. Sidebars and navigation panels are fixed at specific widths (e.g., 280px) to provide a stable frame for the fluid main content area. Padding within cards and containers should scale with the element's importance, typically starting at 24px (md) for primary content blocks.

## Elevation & Depth

Depth is communicated through **Glassmorphism** and subtle tonal shifts rather than traditional shadows. 

1.  **The Canvas (Level 0):** The base background (#121212).
2.  **The Frame (Level 1):** Sidebars and headers use a semi-transparent blur (`backdrop-filter: blur(20px)`) with a low-opacity border (white at 10%) to define edges.
3.  **The Content (Level 2):** Main cards and modals use the #1C1C1E surface color.
4.  **Floating Elements (Level 3):** Popovers and tooltips use a slightly lighter grey with a very soft, large-radius black shadow (`box-shadow: 0 10px 30px rgba(0,0,0,0.5)`) to simulate physical lift.

Borders are always thin (1px) and use low-contrast alpha-transparent whites to create "inner glows" on interactive elements.

## Shapes

The shape language is consistently **Rounded**, adhering to an 8px (0.5rem) standard for all primary UI components like buttons, input fields, and small cards. 

Larger structural elements, such as main content containers or modals, utilize `rounded-lg` (16px/1rem) to soften the overall appearance of the interface. This rounding helps the dark interface feel more approachable and less clinical. Interactive states should never change the border radius, maintaining a stable visual rhythm during hover and active transitions.

## Components

*   **Buttons:** Primary buttons use a solid Apple Blue fill with white text. Secondary buttons use a ghost style with a 1px border of #3A3A3C and no fill.
*   **Chips:** Compact, pill-shaped indicators with a subtle #2C2C2E background and #A1A1A6 text.
*   **Input Fields:** Darker than the surface background (#0F0F0F) with a 1px border that illuminates to Apple Blue upon focus. 
*   **Sidebars:** High-blur glassmorphic panels with a narrow 1px right-border divider. Navigation items use a "squircle" highlight on hover.
*   **Cards:** Non-bordered; depth is defined solely by the #1C1C1E fill against the #121212 background. 
*   **Progress Indicators:** Thin, 4px tall bars using a desaturated blue track and a bright Apple Blue glow for the active progress.
*   **Research Nodes:** Custom components for this design system—feature-rich cards with an icon header, summary text, and a footer for "source" tags, using the secondary typography scale.