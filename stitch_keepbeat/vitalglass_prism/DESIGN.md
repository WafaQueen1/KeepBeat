# Design System Specification: The Vital Pulse

## 1. Overview & Creative North Star
**Creative North Star: "The Living Chronometer"**

This design system transcends traditional medical dashboards by treating the human heart as a high-performance digital asset. We reject the sterile, "hospital-white" aesthetic in favor of **Organic Precision**. The interface must feel like a premium, tactile instrument—combining the weight of 3D Claymorphism with the ethereal lightness of Glassmorphism.

Our signature look is defined by the **"Bento-box" Modular Grid**. Instead of a continuous scroll, we use a choreographed arrangement of tiles that vary in depth and scale. We break the "template" look through:
*   **Intentional Asymmetry:** Using larger, 3D-heavy cards for primary vitals (Digital Twin) contrasted against smaller, frosted-glass utility modules.
*   **Atmospheric Depth:** Elements do not just sit on a page; they float within a 3D space, utilizing light-source-aware shadows and tonal layering.

---

## 2. Color Palette & Surface Philosophy
The color system is rooted in the "Soft Red Degradation," shifting the perception of heart health from "alarm red" to a sophisticated, life-affirming Crimson-to-Rose spectrum.

### The "No-Line" Rule
**Prohibit all 1px solid borders for sectioning.** Boundaries are defined strictly through background shifts. A card (`surface_container_lowest`) sits on a background (`surface`) to create a boundary through contrast, not lines.

### Surface Tiers & Glassmorphism
*   **Base Layer:** `surface` (#f8f9fa) – The canvas for the bento layout.
*   **The Frosted Glass Module:** Use `surface_container_low` at 60% opacity with a `20px` backdrop-blur. This is our signature for secondary data overlays.
*   **The Hero Module:** Use a gradient from `primary` (#b6171e) to `primary_container` (#da3433) with a subtle inner glow to create the 3D "clay" volume.
*   **The AI Insight Layer:** `tertiary_container` (#a54dcc) serves as the "Electric Purple" beacon for predictive battery and AI diagnostics.

---

## 3. Typography: Medical Authority
We utilize a tri-font system to balance editorial elegance with clinical legibility.

*   **Display & Headlines (Manrope):** High-end, geometric, and authoritative. Used for high-level vitals (e.g., BPM, Battery %).
*   **Primary Navigation & Titles (Plus Jakarta Sans):** Modern and approachable. Used for card headers and data labels.
*   **Utility & Labels (Inter):** Maximum legibility for small-scale medical data and timestamps.

**Hierarchy Strategy:**
*   **`display-lg`:** Reserved for the primary Digital Twin metric.
*   **`headline-md`:** Used for Bento-box module titles to ensure a clear "scan-path."
*   **`label-sm`:** Used for "Electric Purple" AI insights, always set in semi-bold for high-contrast accessibility.

---

## 4. Elevation, Depth & Claymorphism
We move away from flat Material Design into a world of **Tactile Volume.**

### The Layering Principle
Depth is achieved by "stacking" surface tokens. Place a `surface_container_lowest` tile on a `surface_container_low` section to create a soft, natural lift.

### 3.5D Claymorphism Shadows
To achieve the "Clay" look for primary heart-rate modules:
*   **Outer Shadow:** `0px 20px 40px rgba(186, 26, 32, 0.12)` (using a tinted `surface_tint` color).
*   **Inner Shadow (The Volume):** A 4px inner-top-left highlight (White at 30%) and a 4px inner-bottom-right shadow (Deep Red at 10%).

### The Ghost Border Fallback
If an element requires a container edge for accessibility, use a "Ghost Border": `outline_variant` at **15% opacity**. Never use 100% opaque lines.

---

## 5. Signature Components

### The Bento Card (Base)
*   **Corner Radius:** `xl` (1.5rem) for the outer container; `md` (0.75rem) for nested elements.
*   **Background:** `surface_container_lowest` (#ffffff).
*   **Constraint:** No dividers. Use `spacing-6` (2rem) to separate content blocks within the card.

### 3D Action Buttons
*   **Primary:** Gradient from `primary` to `primary_container`. High-gloss finish using a subtle top-down linear-gradient highlight.
*   **Interaction:** On hover, the element should "depress" (reduce Y-axis shadow and scale by 0.98) to mimic a physical soft-touch button.

### Health Indicator Chips
*   **Positive (Mint Sage):** Use `on_secondary_container` text on `secondary_container` background.
*   **AI Insight (Electric Purple):** Use `tertiary` for the icon and `tertiary_fixed` for the chip background.

### Input Fields
*   **Style:** Inset-style "well" using `surface_container_high`.
*   **Focus State:** A soft `2px` glow using `primary_fixed` rather than a hard stroke.

---

## 6. Do’s and Don'ts

### Do:
*   **Do** use `spacing-8` (2.75rem) between Bento modules to allow the 3D shadows room to breathe.
*   **Do** prioritize the "Electric Purple" (`tertiary`) for battery predictions to ensure they are visually distinct from health vitals.
*   **Do** use `backdrop-blur` on all navigation overlays to maintain the glassmorphism theme.

### Don't:
*   **Don't** use black shadows. Always tint shadows with the `on_surface` or `primary` color to maintain a high-end, editorial feel.
*   **Don't** use standard 1px dividers. If you need to separate data, use a tonal shift or a `surface_variant` background block.
*   **Don't** cram more than three primary metrics into a single Bento tile. Clarity is the ultimate luxury in medical design.

---

## 7. Spacing & Touch Targets
To satisfy the "Large Touch Target" principle, all interactive elements (buttons, chips, toggles) must have a minimum height of `spacing-10` (3.5rem). The Bento grid itself follows a strict `spacing-4` (1.4rem) gutter to ensure the layout remains cohesive yet airy.