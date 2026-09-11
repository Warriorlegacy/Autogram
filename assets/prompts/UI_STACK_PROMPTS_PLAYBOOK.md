# ⚡ Signhify UI Stack & Prompt Engineering Playbook

> **The Modern React UI Engineering & Prompt Blueprint**
> Based on the curated `Signhify_assets/prompts/ui_stack` architecture.
> *"Polished UI ≠ More Libraries. Use the right tools. Keep the interface intentional."*

---

## 🧭 Executive Summary: The 4-Tier Foundation Stack

```
┌────────────────────────────────────────────────────────┐
│                   REACT + TAILWIND CSS                 │
├───────────────┬─────────────────┬──────────────────────┤
│ 01 COMPONENTS │ 02 MOTION       │ 03 ICONS             │
│   SHADCN/UI   │  FRAMER MOTION  │    LUCIDE            │
│ (Radix-based) │ (Micro-physics) │ (Ultra-crisp)        │
├───────────────┴─────────────────┴──────────────────────┤
│ 04 DATA & STATE: TANSTACK QUERY (API -> Cache -> UI)   │
└────────────────────────────────────────────────────────┘
```

### Specialized Production Powerhouses:
- 💬 **Chat & AI Copilots:** `assistant-ui` (`@assistant-ui/react`)
- 🏛️ **Landing Pages & Bento Layouts:** `tailark`
- ✨ **Kinetic Visuals & Hero Shaders:** `reactbits`
- 🎯 **Interactive Onboarding & Guided Tours:** `driver.js`

---

## 📑 Master Prompt Playbook: Step-by-Step

---

### #1. AI Chat Interface (Don't prompt: "build an AI chat interface")
> **Rule:** Replace generic chat prompts with production-grade `@assistant-ui/react` primitives.

#### 🎯 Master Prompt:
```markdown
Act as a Principal AI Frontend Architect. Build a modern, production-ready AI chat interface inspired by assistant-ui using React 19, Tailwind CSS v4, Lucide icons, and Framer Motion.

Requirements:
1. Header & Controls: Model selector dropdown (e.g. GPT-5.6 Luna, Claude 3.7 Sonnet, Gemini 3 Flash, DeepSeek V3.1), session token budget meter, and theme selector (Default, Blue, Violet, Emerald).
2. Prompt Suggestion Chips: Quick-action pills at the top ("Weather", "Code", "Write", "Analyze", "Brainstorm", "Strategy") with subtle hover glow.
3. Message Thread Architecture: User speech bubbles with timestamp, Assistant streaming bubble with smooth typewriter effect, markdown formatting, syntax highlighted code blocks with one-click copy and language tags.
4. Input Tray: Multi-line expanding textarea with keyboard shortcut (Enter to send, Shift+Enter for newline), attachment uploader button (+), voice audio transcription toggle (mic pulse wave animation), and send button with disabled/loading states.
5. Action Bar per Message: One-click Copy, Regenerate, Share, and Branch Thread options.
6. Clean Mobile Collapse: Bottom sheet controls on mobile, touch-friendly 44px tap targets.
```

---

### #2. High-Converting Landing Page (Don't prompt: "build my landing page")
> **Rule:** Replace standard bootstrap-style pages with `tailark`-style dark luxury bento architectures.

#### 🎯 Master Prompt:
```markdown
Act as an Elite Creative Developer (Awwwards-tier). Build a high-converting, dark-mode SaaS landing page using Tailark design principles, React 19, and Tailwind CSS v4.

Requirements:
1. Aesthetic Profile: OLED Deep Black (#050505) background, subtle ambient radial gradient orbs (emerald & indigo hues), vantablack cards with heavy backdrop-blur-2xl and white/10 hairline borders.
2. The Asymmetrical Bento Grid:
   - Bento Item 1 (col-span-8): Interactive agentic canvas preview with animated workflow nodes.
   - Bento Item 2 (col-span-4): Live telemetry metrics card with real-time counters and sparklines.
   - Bento Item 3 (col-span-4): Customer testimonial card with verified proof badges.
   - Bento Item 4 (col-span-8): Multi-account connectivity matrix with subtle glass hover states.
3. Typography & Rhythm: High contrast Grotesk typography, microscopic eyebrow tags (`rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em]`), and generous vertical section rhythm (`py-28` to `py-36`).
4. Island CTA Buttons: Fully rounded pill buttons (`rounded-full px-7 py-3.5`) featuring nested "button-in-button" trailing icon circles with magnetic hover physics.
```

---

### #3. Kinetic Visuals & Micro-Animations (Don't prompt: "make my app look awesome")
> **Rule:** Replace vague styling requests with modular `reactbits` animation primitives.

#### 🎯 Master Prompt:
```markdown
Act as a Senior Creative Technologist. Implement interactive, GPU-accelerated visual components using React Bits principles in React + Framer Motion:

1. Retro Dithered Wave Canvas (`DitherWaves`):
   - Canvas-based sine wave rendering with retro halftone/dithering filter effect.
   - Interactive mouse-reactive ripple disturbance.
2. Silk Touch Tactile Card (`SilkTouchCard`):
   - 3D perspective tilt reacting to mouse position (`rotateX`, `rotateY`).
   - Dynamic specular highlight sheen tracking cursor coordinates.
3. Gentle Aurora Glow (`AuroraGlow`):
   - Smooth, multi-stop floating gradient mesh behind hero sections with subtle oscillation.
4. Spotlight Card (`SpotlightCard`):
   - Card with radial gradient torch effect following cursor over dark glass background.
5. Kinetic Text Entrance (`TextDither`):
   - Staggered letter-by-letter fade, blur, and scale entrance simulating matrix/digital decay.
```

---

### #4. Design System Foundations (Don't prompt: "create a design system")
> **Rule:** Replace ad-hoc UI components with accessible, composable `shadcn/ui` tokens.

#### 🎯 Master Prompt:
```markdown
Act as a Design System Engineer. Implement a unified component foundation using Shadcn/UI primitives, Radix UI, Class Variance Authority (CVA), and Tailwind CSS v4.

Required Base Components:
1. Button: Variants (default, secondary, outline, ghost, destructive, link, glow), sizes (sm, md, lg, icon), loading spinner states, slot support via `@radix-ui/react-slot`.
2. Card Suite: Double-bezel hardware architecture (outer bezel shell + inner core container with inset specular highlight).
3. Input & Form: Floating label support, error feedback rings, input OTP slots, and keyboard accessible select dropdowns.
4. Dialog & Sheet: Fluid spring entrance with backdrop blur, accessible focus trapping, escape key dismiss, and portal rendering.
5. Feedback & Overlays: Accessible Tooltips, Context Menus, Hover Cards, Dropdown Menus, and Sonner toast notifications.
```

---

### #5. Product Onboarding Tour (Don't prompt: "build an onboarding tour")
> **Rule:** Replace complex custom tour modals with lightweight, zero-dependency `driver.js`.

#### 🎯 Master Prompt:
```markdown
Act as a Product Growth Engineer. Implement a guided onboarding product tour using `driver.js` and React hooks.

Requirements:
1. Integration: Wrap `driver.js` in a custom `useTour(tourId)` hook that manages `localStorage` completion flags, step indexing, and restart capabilities.
2. Luxury Theme Styling: Override default Driver.js popovers with dark glass theme (`bg-zinc-950/90`, `border-white/10`, `backdrop-blur-xl`, amber CTA buttons).
3. Step Architecture:
   - Step 1: Welcome & Mission Overview (centered popover).
   - Step 2: Highlight Search & Command Palette (`#nav-search`).
   - Step 3: Highlight Prompt Generator & Preset Chips (`#ai-input-tray`).
   - Step 4: Highlight Model Configuration & BYOK Security (`#byok-config-btn`).
   - Step 5: Highlight Export & Deployment Sandbox (`#export-deploy-btn`).
4. Keyboard & Accessibility: Enable Escape to exit, arrow keys for Prev/Next, and click-outside dismissal option.
```

---

### #6. Motion Choreography Framework (Framer Motion)
> **Rule:** Structure every animation across the 3-state progression: `01 Static -> 02 Shift -> 03 Transition`.

#### 🎯 Motion Specification Guide:
| State | Behavior | Implementation |
|---|---|---|
| **01 Static** | Neutral rest state, crisp typography, clean alignment. | `initial={{ opacity: 0, y: 16, filter: 'blur(4px)' }}` |
| **02 Shift** | Hover / Focus / Active micro-displacement. Simulates real mass. | `whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}` |
| **03 Transition** | Page enter/exit, modal expansion, layout morphs. | `transition={{ type: "spring", stiffness: 300, damping: 25 }}` |

#### Core Use Cases:
- **Page Transitions:** Staggered content reveal with `AnimatePresence`.
- **Hover States:** Nested icon translation (`translate-x-1 -translate-y-0.5`).
- **Modal Animations:** Scale-up from trigger coordinates with backdrop blur transition.
- **Layout Changes:** Fluid reordering using `layout` and `layoutId` props.

---

### #7. Iconography & Visual Actions (Lucide)
> **Rule:** Use clean, consistent, 1.5px to 2px stroke icons with systematic sizing.

#### Icon Standard Matrix:
- **Navigation (20px / size-5):** `LayoutGrid`, `FolderKanban`, `Sparkles`, `Terminal`, `Settings`, `Layers`.
- **Actions (16px / size-4):** `ArrowRight`, `ExternalLink`, `Copy`, `Check`, `Share2`, `Download`, `Plus`.
- **Status (14px / size-3.5):** `CheckCircle2`, `AlertTriangle`, `XCircle`, `Loader2`, `ShieldCheck`.
- **Physics Rule:** Icons inside buttons should always be nested inside a circular container and animate on parent `group-hover`.

---

### #8. Data Synchronization & Cache (TanStack Query)
> **Rule:** Keep UI responsive with the `API -> CACHE -> UI` lifecycle.

#### 🎯 Master Implementation Pattern:
```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// 1. Fetching with intelligent caching & stale-while-revalidate
export function useBlueprint(id: string) {
  return useQuery({
    queryKey: ["blueprint", id],
    queryFn: () => fetchBlueprintById(id),
    staleTime: 5 * 60 * 1000, // 5 min fresh cache
    gcTime: 30 * 60 * 1000,    // 30 min memory persistence
  });
}

// 2. Optimistic Mutation for zero-latency user actions
export function useUpdateBlueprint() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateBlueprintFn,
    onMutate: async (newPlan) => {
      await queryClient.cancelQueries({ queryKey: ["blueprint", newPlan.id] });
      const previous = queryClient.getQueryData(["blueprint", newPlan.id]);
      queryClient.setQueryData(["blueprint", newPlan.id], newPlan);
      return { previous };
    },
    onError: (err, newPlan, context) => {
      queryClient.setQueryData(["blueprint", newPlan.id], context?.previous);
    },
    onSettled: (data, error, variables) => {
      queryClient.invalidateQueries({ queryKey: ["blueprint", variables.id] });
    },
  });
}
```

---

## 🛠️ Stack Quick Reference & Dependency Setup

```bash
# Core 4-Tier Foundation
bun add @tanstack/react-query framer-motion lucide-react clsx tailwind-merge class-variance-authority @radix-ui/react-slot

# Guided Tours
bun add driver.js

# AI & Chat Primitives
# Assistant UI / Custom Assistant chat layer
```

---

## 💎 Design System Checklist for Signhify

- [x] **Double-Bezel Card Architecture:** Outer shell (`ring-1 ring-white/10 bg-white/[0.02] p-1.5 rounded-2xl`) + Inner core.
- [x] **No Generic AI Slop:** Banned plain gray borders, flat linear transitions, and unstyled modals.
- [x] **Micro-Interactions First:** Magnetic button hovers, animated spring physics, and subtle particle glows.
- [x] **Zero-Jank Performance:** CSS transform/opacity-only animations, strict backdrop-blur limits on scroll containers.
- [x] **Complete Mobile Fidelity:** Auto-collapse asymmetrical grids to `grid-cols-1` with 44px+ touch targets below 768px.
