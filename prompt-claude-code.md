# Prompt — Dark Portfolio Landing Page

Build a **single-page dark portfolio** using the stack below. Scaffold the project, install every dependency, write all source files, and run `npm run dev` to confirm it compiles without errors.

---

## Stack

```
React 18 + Vite + TypeScript + Tailwind CSS
GSAP (with ScrollTrigger)
Framer Motion
hls.js
react-router-dom
tailwindcss-animate
```

Initialize with:
```bash
npm create vite@latest portfolio -- --template react-ts
cd portfolio
npm install gsap framer-motion hls.js react-router-dom tailwindcss-animate
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## 1. Design System

### `index.css`

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@1&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg: 0 0% 4%;
  --surface: 0 0% 8%;
  --text: 0 0% 96%;
  --muted: 0 0% 53%;
  --stroke: 0 0% 12%;
  --accent: 0 0% 96%;
}

body {
  @apply bg-bg text-text-primary font-body;
}

.accent-gradient {
  background: linear-gradient(90deg, #89AACC 0%, #4E85BF 100%);
}

@keyframes scroll-down {
  0%   { transform: translateY(-100%); }
  100% { transform: translateY(200%); }
}
@keyframes role-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50%       { background-position: 100% 50%; }
}

.animate-scroll-down  { animation: scroll-down  1.5s ease-in-out infinite; }
.animate-role-fade-in { animation: role-fade-in 0.4s ease-out; }
.animate-gradient-shift { animation: gradient-shift 6s ease infinite; }
```

### `tailwind.config.ts`

```ts
import type { Config } from 'tailwindcss'
import animate from 'tailwindcss-animate'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        body:    ['Inter', 'sans-serif'],
        display: ['Instrument Serif', 'serif'],
      },
      colors: {
        bg:            'hsl(var(--bg))',
        surface:       'hsl(var(--surface))',
        'text-primary':'hsl(var(--text))',
        muted:         'hsl(var(--muted))',
        stroke:        'hsl(var(--stroke))',
      },
    },
  },
  plugins: [animate],
} satisfies Config
```

---

## 2. File Structure

```
src/
  components/
    LoadingScreen.tsx
    Navbar.tsx
    HeroSection.tsx
    WorksSection.tsx
    JournalSection.tsx
    ExplorationsSection.tsx
    StatsSection.tsx
    FooterSection.tsx
  App.tsx
  main.tsx
  index.css
```

---

## 3. Component Specs

### `LoadingScreen.tsx`

- Full-screen fixed overlay `z-[9999] bg-bg`.
- `requestAnimationFrame` counter: 0 → 100 over **2700 ms**.
- **Top-left**: `"Portfolio"` label — `text-xs text-muted uppercase tracking-[0.3em]`. Animate with Framer Motion: `y:-20→0, opacity:0→1`.
- **Center**: Framer Motion `AnimatePresence mode="wait"`. Cycle words `["Design","Create","Inspire"]` every 900 ms. Enter: `y:20→0, opacity:0→1`. Exit: `y:0→-20, opacity:1→0`. Style: `text-4xl md:text-6xl lg:text-7xl font-display italic text-text-primary/80`.
- **Bottom-right**: Counter `String(count).padStart(3,"0")` — `text-6xl md:text-8xl lg:text-9xl font-display text-text-primary tabular-nums`.
- **Bottom progress bar**: `h-[3px] bg-stroke/50`. Inner div `.accent-gradient`, `scaleX(count/100)`, `box-shadow: 0 0 8px rgba(137,170,204,0.35)`.
- At count === 100: wait 400 ms then call `onComplete()`.

---

### `Navbar.tsx`

Fixed pill navbar centered at top.

```
fixed top-0 left-0 right-0 z-50 flex justify-center pt-4 md:pt-6 px-4
```

Inner pill: `inline-flex items-center rounded-full backdrop-blur-md border border-white/10 bg-surface px-2 py-2`. Add `shadow-md shadow-black/10` when `scrollY > 100`.

Contents (left → right):
1. **Logo**: 9×9 circle, accent-gradient border, reverses direction on hover. Inner bg-bg circle with `"JA"` in `font-display italic text-[13px]`. `scale-110` on hover.
2. `w-px h-5 bg-stroke mx-1` divider (hidden mobile).
3. **Nav links** `["Home","Work","Resume"]`: `text-xs sm:text-sm rounded-full px-3 sm:px-4 py-1.5 sm:py-2`. Active → `text-text-primary bg-stroke/50`. Inactive → `text-muted hover:text-text-primary hover:bg-stroke/50`. Smooth scroll to matching section IDs.
4. Divider.
5. **"Say hi ↗"** button: same size. On hover show accent-gradient border ring (`absolute span inset: -2px`). Inner content inside `bg-surface rounded-full`.

---

### `HeroSection.tsx`

Full viewport (`min-h-screen relative overflow-hidden`).

**Background video** (HLS):
```ts
const HLS_SRC = 'https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8'
```
- If `Hls.isSupported()` → create instance, attach to `<video>` ref.
- Else if `video.canPlayType('application/vnd.apple.mpegurl')` → `video.src = HLS_SRC`.
- `<video autoPlay muted loop playsInline>` — `absolute top-1/2 left-1/2 min-w-full min-h-full object-cover -translate-x-1/2 -translate-y-1/2`.
- Dark overlay `absolute inset-0 bg-black/20`.
- Bottom fade `absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-bg to-transparent`.

**Hero content** (`relative z-10 flex flex-col items-center justify-center min-h-screen text-center px-6`):
- Eyebrow `.blur-in`: `text-xs text-muted uppercase tracking-[0.3em] mb-8` → `"COLLECTION '26"`.
- Name `.name-reveal`: `text-6xl md:text-8xl lg:text-9xl font-display italic leading-[0.9] tracking-tight text-text-primary mb-6` → `"Michael Smith"`.
- Role line `.blur-in`: `"A "` + cycling word (`key={roleIndex}` `animate-role-fade-in font-display italic`) + `" lives in Chicago."` — cycle `["Creative","Fullstack","Founder","Scholar"]` every 2 s.
- Description `.blur-in`: `text-sm md:text-base text-muted max-w-md mb-12`.
- CTA buttons `.blur-in` (`inline-flex gap-4`):
  - **"See Works"**: `bg-text-primary text-bg rounded-full text-sm px-7 py-3.5 hover:scale-105`. Hover → accent-gradient border ring.
  - **"Reach out..."**: `border-2 border-stroke bg-bg text-text-primary rounded-full text-sm px-7 py-3.5 hover:scale-105`. Hover → border-transparent + accent-gradient ring.

**GSAP entrance** (run after loading screen):
```ts
gsap.timeline({ ease: 'power3.out' })
  .fromTo('.name-reveal', { opacity:0, y:50 }, { opacity:1, y:0, duration:1.2, delay:0.1 })
  .fromTo('.blur-in',
    { opacity:0, filter:'blur(10px)', y:20 },
    { opacity:1, filter:'blur(0px)', y:0, duration:1, stagger:0.1 },
    0.3)
```

**Scroll indicator** (bottom-center, absolute):
`text-xs text-muted uppercase tracking-[0.2em] "SCROLL"` above `w-px h-10 bg-stroke` line with inner `.animate-scroll-down` highlight.

---

### `WorksSection.tsx`

`id="work"`, `bg-bg py-12 md:py-16`.
Inner: `max-w-[1200px] mx-auto px-6 md:px-10 lg:px-16`.

**Header** (Framer Motion `whileInView opacity:0→1, y:30→0, duration:1, once:true, margin:"-100px"`):
- Eyebrow: `w-8 h-px bg-stroke` line + `"Selected Work"` `text-xs text-muted uppercase tracking-[0.3em]`.
- Heading: `"Featured "` + `<em className="font-display italic">"projects"</em>`.
- Subtext + `"View all work →"` button (desktop, gradient hover ring).

**Bento grid** `grid grid-cols-1 md:grid-cols-12 gap-5 md:gap-6`:

| Title                | col-span |
|----------------------|----------|
| Automotive Motion    | 7        |
| Urban Architecture   | 5        |
| Human Perspective    | 5        |
| Brand Identity       | 7        |

Each card (`group relative bg-surface border border-stroke rounded-3xl overflow-hidden`):
- Background `<img>` with `object-cover group-hover:scale-105 transition-transform duration-700`.
- Halftone overlay: `background: radial-gradient(circle, #000 1px, transparent 1px) 0 0/4px 4px` `opacity-20 mix-blend-multiply`.
- Hover overlay: `absolute inset-0 bg-bg/70 opacity-0 group-hover:opacity-100 backdrop-blur-lg transition-opacity`.
- Hover label: centered pill with animated gradient border, white inner bg, `"View — "` + `<em>Title</em>`.

Use placeholder images from `https://picsum.photos/seed/{title}/800/600`.

---

### `JournalSection.tsx`

`bg-bg py-16 md:py-24`.

Same header pattern (`"Recent "` + `<em>"thoughts"</em>`).

4 journal entries as horizontal pills `rounded-[40px] sm:rounded-full`:
```
flex items-center gap-6 p-4 bg-surface/30 hover:bg-surface border border-stroke
transition-colors cursor-pointer
```
Each: thumbnail (64×64, rounded-2xl), title (`font-medium`), read time (`text-xs text-muted`), date (`text-xs text-muted ml-auto`).

Sample data:
```ts
[
  { title: 'The Art of Minimal UI', readTime: '4 min read', date: 'Mar 2026' },
  { title: 'Typography in Motion',  readTime: '6 min read', date: 'Feb 2026' },
  { title: 'Building With Intent',  readTime: '5 min read', date: 'Jan 2026' },
  { title: 'Color Theory Revisited',readTime: '3 min read', date: 'Dec 2025' },
]
```

---

### `ExplorationsSection.tsx`

`min-h-[300vh] relative`.

**Layer 1 — Pinned center** `(z-10)`: `h-screen` div pinned with:
```ts
ScrollTrigger.create({ trigger: sectionRef.current, pin: contentRef.current, pinSpacing: false, start:'top top', end:'bottom bottom' })
```
Content: eyebrow `"Explorations"`, heading `"Visual "` + `<em>"playground"</em>`, subtext, Dribbble button.

**Layer 2 — Parallax columns** `(z-20, absolute inset-0)`:
- `grid grid-cols-2 gap-12 md:gap-40 max-w-[1400px] mx-auto`.
- 6 images split left/right. Left column: `gsap.to(el, { y: -200, ease:'none', scrollTrigger:{ ... scrub:1 } })`. Right: `y: +150`.
- Each card: `aspect-square max-w-[320px] rounded-2xl overflow-hidden`. Click → lightbox modal (full-screen with close button).

---

### `StatsSection.tsx`

`bg-bg py-16 md:py-24`.

3-column grid `grid grid-cols-1 md:grid-cols-3 gap-8 text-center max-w-4xl mx-auto`:

| Stat | Label |
|------|-------|
| 20+  | Years Experience |
| 95+  | Projects Done |
| 200% | Satisfied Clients |

Each: large number in `font-display italic text-6xl`, label in `text-sm text-muted uppercase tracking-widest mt-2`. Animate number count-up with GSAP when in view.

---

### `FooterSection.tsx`

`bg-bg pt-16 md:pt-20 pb-8 md:pb-12 overflow-hidden relative`.

**Background video**: same HLS source, `transform: scaleY(-1)` (CSS `scale-y-[-1]`). Overlay `bg-black/60`.

**GSAP Marquee** (relative z-10):
```ts
gsap.to(marqueeRef.current, { xPercent: -50, duration: 40, ease: 'none', repeat: -1 })
```
Text: `"BUILDING THE FUTURE • "` × 10 in `text-4xl md:text-6xl font-display italic whitespace-nowrap`.

**CTA**: `mailto:hello@michaelsmith.com` button, gradient hover ring.

**Footer bar** (`flex justify-between items-center mt-12 border-t border-stroke pt-6`):
- Social links: `[Twitter, LinkedIn, Dribbble, GitHub]` — `text-muted hover:text-text-primary text-sm`.
- Right: green pulsing dot `w-2 h-2 rounded-full bg-green-400 animate-pulse` + `"Available for projects"` `text-xs text-muted`.

---

### `App.tsx`

```tsx
import { useState } from 'react'
import LoadingScreen   from './components/LoadingScreen'
import Navbar          from './components/Navbar'
import HeroSection     from './components/HeroSection'
import WorksSection    from './components/WorksSection'
import JournalSection  from './components/JournalSection'
import ExplorationsSection from './components/ExplorationsSection'
import StatsSection    from './components/StatsSection'
import FooterSection   from './components/FooterSection'

export default function App() {
  const [isLoading, setIsLoading] = useState(true)
  return (
    <>
      {isLoading && <LoadingScreen onComplete={() => setIsLoading(false)} />}
      {!isLoading && (
        <>
          <Navbar />
          <main>
            <HeroSection />
            <WorksSection />
            <JournalSection />
            <ExplorationsSection />
            <StatsSection />
            <FooterSection />
          </main>
        </>
      )}
    </>
  )
}
```

---

## 4. Extra Requirements

- **Smooth scroll**: `html { scroll-behavior: smooth }` + nav links use `document.querySelector(id)?.scrollIntoView({ behavior:'smooth' })`.
- **No light mode**: only dark theme, no toggle.
- **GSAP ScrollTrigger**: register plugin at top of each component that needs it: `gsap.registerPlugin(ScrollTrigger)`.
- **hls.js cleanup**: destroy HLS instance in `useEffect` cleanup to avoid memory leaks.
- **TypeScript**: strict mode, no `any`.
- **After writing all files**: run `npm run build` and fix any TypeScript or Tailwind errors before reporting done.
