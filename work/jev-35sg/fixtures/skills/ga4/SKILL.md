---
name: ga4
description: >-
  Configure GA4 + GTM for Next.js SaaS: funnel tracking, scroll depth, CTA clicks,
  conversions, feature usage. Use when setting up analytics, tracking conversions,
  or implementing A/B tests.
---

# GA4 + GTM for Next.js SaaS

> **Stack**: Next.js 16 App Router + @next/third-parties + Supabase Auth + GA4 + GTM (all free)

## Table of Contents
- [Quick Start](#quick-start) | [Why GTM + GA4](#why-gtm-with-ga4) | [Workflow](#workflow)
- [Funnel Events](#funnel-events) | [dataLayer Push](#datalayer-push-pattern) | [GTM Tags](#gtm-tag-configurations)
- [Sign-up Conversion](#sign-up-conversion-tracking) | [Feature Usage](#in-app-feature-usage)
- [A/B Testing](#ab-testing-no-google-optimize) | [Validation](#validation) | [References](#references)

---

## Quick Start

```tsx
// app/layout.tsx
import { GoogleTagManager } from '@next/third-parties/google'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <GoogleTagManager gtmId="GTM-XXXXXXX" />
      </body>
    </html>
  )
}
```

Then in GTM: Create a **Google Tag** (it replaced the old "GA4 Configuration" tag) with Tag ID `G-XXXXXXXXXX`, trigger "All Pages".

## Why GTM with GA4

GTM is a **centralized hub** for all tracking. Benefits:

| Without GTM | With GTM |
|-------------|----------|
| Hardcoded analytics calls | Configure in web interface |
| Redeploy to change tracking | Update without code deploys |
| Testing in production | Preview mode before publish |
| Scattered event code | Unified dataLayer pattern |

GTM "listens" to dataLayer and routes events to GA4. Your Next.js code stays clean.

## Workflow

- [ ] 1. Create GTM container → note `GTM-XXXXXXX`
- [ ] 2. Add `<GoogleTagManager>` to root layout
- [ ] 3. Create Google Tag in GTM (Tag ID `G-...` + All Pages trigger)
- [ ] 4. Publish GTM, verify in GA4 Realtime
- [ ] 5. Add funnel events (scroll, CTA, sign_up, feature_use)
- [ ] 6. Register custom parameters in GA4 Admin > Custom Definitions
- [ ] 7. Mark `sign_up` as a key event (GA4's current name for conversions) in GA4 Admin > Data display > Events
- [ ] 8. Configure User-ID for cross-session tracking (optional)
- [ ] 9. Build funnel exploration in GA4 Explore

## Funnel Events

| Step | Event | Parameters | How |
|------|-------|------------|-----|
| 1. Landing | `page_view` | (automatic) | Google Tag |
| 2. Scroll | `scroll_depth` | `scroll_percent` | GTM Scroll trigger (25/50/75/90%) |
| 3. Section View | `section_view` | `section_name` | GTM Element Visibility trigger |
| 4. CTA Click | `cta_click` | `cta_text`, `cta_position` | GTM Click trigger or dataLayer |
| 5. Sign-up | `sign_up` | `method`, `user_id` | dataLayer on Supabase auth |
| 6. Feature Use | `feature_use` | `feature_name` | dataLayer on action |

**Note**: GA4 Enhanced Measurement auto-tracks scroll at 90% only. Use GTM for granular 25/50/75/90%.

## dataLayer Push Pattern

```tsx
// Declare type for TypeScript
declare global {
  interface Window { dataLayer: Record<string, any>[]; }
}

// Generic push helper
function trackEvent(event: string, params: Record<string, any>) {
  window.dataLayer?.push({ event, ...params });
}

// Examples
trackEvent('cta_click', { cta_text: 'Get Started', cta_position: 'hero' });
trackEvent('feature_use', { feature_name: 'export_report' });
```

## GTM Tag Configurations

### Scroll Depth (25/50/75/90%)

1. **Variables** > Built-in: Enable `Scroll Depth Threshold`, `Scroll Depth Units`, `Scroll Direction`
2. **Trigger** > Scroll Depth: Vertical, Percentages: `25,50,75,90`
3. **Tag** > GA4 Event: `scroll_depth`, param `scroll_percent` = `{{Scroll Depth Threshold}}`

### Section Visibility

Track which landing page sections users actually see (not just scroll past):

```tsx
// Add to section elements
<section className="ga-section-tracking" data-section-name="features">
  {/* content */}
</section>
```

1. **Variable** > Auto-Event Variable: Element Attribute `data-section-name`
2. **Trigger** > Element Visibility: CSS `.ga-section-tracking`, 50% visible, once per element
3. **Tag** > GA4 Event: `section_view`, param `section_name` = `{{AEV - section-name}}`

### CTA Click (Two Methods)

**Method A: No-Code (GTM only)**
```html
<button class="cta-signup" data-cta_text="Sign Up" data-cta_position="hero">
  Create Account
</button>
```
- Variable > Auto-Event Variable: Element Attribute `data-cta_text` (reads the clicked element; a DOM Element variable would always read the first `.cta-signup` on the page)
- Trigger > Click - All Elements: `Click Classes` contains `cta-signup`

**Method B: dataLayer (more reliable for dynamic content)**
```tsx
<button onClick={() => trackEvent('cta_click', { cta_text: 'Sign Up', cta_position: 'hero' })}>
  Create Account
</button>
```
- Trigger > Custom Event: `cta_click`

## Sign-up Conversion Tracking

Since you use **Supabase + Google OAuth**, fire `sign_up` after auth confirms:

```tsx
// In your auth provider or layout
useEffect(() => {
  const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
    if (event === 'SIGNED_IN' && session?.user) {
      window.dataLayer?.push({
        event: 'sign_up',          // GA4 recommended event name
        method: 'google',          // Auth method
        user_id: session.user.id   // For User-ID tracking
      });
    }
  });
  return () => subscription.unsubscribe();
}, []);
```

**Alternative**: Trigger on redirect page (e.g., `/dashboard` or `/auth/callback`) if that's where new users land.

**Critical**: Mark `sign_up` as a key event in GA4 Admin > Data display > Events ("Mark as key event"). GA4 renamed its "conversions" to "key events" in 2024; "conversions" now means Google Ads conversions.

## In-App Feature Usage

Track what paid users do after sign-up:

```tsx
// Strategy: Single event + feature_name parameter (scales better than separate events)
function useFeature(featureName: string) {
  trackEvent('feature_use', {
    feature_name: featureName,
    feature_category: 'reports' // optional grouping
  });
}

// Usage
useFeature('generate_report');
useFeature('export_csv');
useFeature('invite_team_member');
```

**Why single event?** Web streams have no cap on distinct event names (app streams cap at 500), but every parameter you want in reports needs a custom dimension, and those are capped (50 event-scoped per standard property). One `feature_use` event with a `feature_name` dimension scales indefinitely and keeps reports readable.

## A/B Testing (No Google Optimize)

**Google Optimize sunset Sept 2023.** DIY approach with cookies:

```tsx
// proxy.ts - Assign variant server-side (prevents flicker)
// Next.js 16 renamed middleware.ts / middleware() to proxy.ts / proxy()
import { NextResponse } from 'next/server'

export function proxy(request) {
  let variant = null
  if (!request.cookies.get('exp_hero_cta')) {
    variant = Math.random() < 0.5 ? 'A' : 'B'
    // Put it on the request too: cookies() in Next 15+ (and 14.2.8+) sees proxy-set
    // cookies, but Route Handlers, the Pages Router and Next <=14.2.7 only read the request
    request.cookies.set('exp_hero_cta', variant)
  }
  const response = NextResponse.next({ request: { headers: request.headers } })
  if (variant) response.cookies.set('exp_hero_cta', variant, { maxAge: 60 * 60 * 24 * 30 })
  return response
}
```

```tsx
// Server Component: read the variant (cookies() is async since Next.js 15)
const variant = (await cookies()).get('exp_hero_cta')?.value || 'A'

// Client: pass `variant` down as a prop and include it in all relevant events
trackEvent('cta_click', {
  cta_text: variant === 'A' ? 'Start Trial' : 'Get Started',
  experiment_variant: variant
});
```

**Analyze**: GA4 Explore > Create segments for `experiment_variant = A` vs `B`, compare conversion rates.

## Validation

| Step | Tool | What to Check |
|------|------|---------------|
| 1 | GTM Preview | Tags fire at correct moments, parameters populated |
| 2 | GA4 DebugView | Events arrive with all params, correct names |
| 3 | GA4 Realtime | Live traffic appears within 30s |
| 4 | GA4 Reports | Data in standard reports (24-48h delay) |

**Critical checks**:
- `sign_up` fires exactly once per conversion
- Scroll events fire at correct thresholds
- CTA clicks register with correct `cta_text`/`cta_position`

## References

| Topic | Reference |
|-------|-----------|
| Event schemas & naming | [EVENTS.md](references/EVENTS.md) |
| Complete GTM configs | [GTM-TAGS.md](references/GTM-TAGS.md) |
| Funnel analysis in GA4 | [FUNNEL-ANALYSIS.md](references/FUNNEL-ANALYSIS.md) |
| DIY A/B testing | [AB-TESTING.md](references/AB-TESTING.md) |
| Troubleshooting | [DEBUGGING.md](references/DEBUGGING.md) |

## Key Gotchas

- **Cookie consent**: GTM tags won't fire until consent given (GDPR)
- **Custom params**: Register in GA4 Admin > Custom Definitions before they appear in reports
- **Recommended events**: Use GA4's exact names (`sign_up`, `login`, `purchase`) for default reports
- **User-ID**: Requires setting `user_id` in the Google Tag's configuration settings for cross-session tracking
- **Event limits**: No cap on distinct event names for web streams (500 for app streams); 25 params per event, 50 event-scoped custom dimensions - consolidate with parameters
- **Data delay**: Real reports take 24-48h; use Realtime/DebugView for testing
