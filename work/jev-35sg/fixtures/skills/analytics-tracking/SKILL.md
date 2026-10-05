---
name: analytics-tracking
description: "When the user asks to 'set up analytics tracking', 'implement GA4', 'configure Google Tag Manager', 'create tracking plan', 'event tracking setup', 'conversion tracking', 'UTM parameter strategy', 'custom dimensions setup', 'ecommerce tracking', 'funnel tracking', 'user property tracking', 'debug analytics', 'validate tracking', 'privacy compliance tracking', 'consent management', 'cross-domain tracking', 'server-sid"
license: MIT
metadata:
  version: 1.0.0
  author: ZestStream.ai <josh@zeststream.ai>
  domains: [analytics, ga4, gtm, tracking, measurement, event-tracking, utm, privacy]
distribution: subscribers
---

# Analytics Tracking Implementation

Set up tracking that provides actionable insights for marketing and product decisions. Every tracked event must inform a decision -- if you cannot name the decision an event informs, do not track it.

## Core Principle

Track for decisions, not data. Start with the questions you need answered, work backwards to the events you need tracked. Quality over quantity: 20 well-defined events beat 200 noisy ones. Naming consistency is the foundation -- establish conventions before writing a single line of tracking code.

## When to Use

- Implementing GA4 and Google Tag Manager from scratch
- Creating a tracking plan for a new product or feature
- Auditing existing analytics for gaps and quality issues
- Setting up conversion tracking and funnels
- Designing UTM parameter strategy for campaigns
- Implementing privacy-compliant tracking (GDPR, CCPA)
- Debugging tracking issues and validating implementation
- Migrating from Universal Analytics to GA4

## Tracking Plan Framework

Build the tracking plan before writing any code. Structure:

| Column | Description | Example |
|--------|------------|---------|
| Event Name | snake_case, object_action format | signup_completed |
| Category | Grouping | conversion |
| Properties | Key-value pairs sent with event | method: google, plan: pro |
| Trigger | What fires the event | Click signup button on success page |
| Owner | Who maintains this | Marketing / Engineering |

## Event Naming Convention

Use **object_action** format in lowercase with underscores:

```
signup_completed       (not: SignupCompleted or complete_signup)
cta_clicked           (not: buttonClick or CTA_CLICK)
article_read          (not: readArticle)
checkout_started      (not: begin_checkout)
```

## Essential Events by Site Type

### SaaS Marketing Site
signup_started, signup_completed, demo_requested, pricing_viewed, cta_clicked, form_submitted, resource_downloaded, video_played, scroll_depth

### SaaS Product
onboarding_step_completed, feature_used, action_completed, trial_started, purchase_completed, subscription_changed, session_started

### E-commerce
product_viewed, product_added_to_cart, cart_viewed, checkout_started, purchase_completed, product_searched

Consult `references/event-catalog.md` for the complete event catalog with properties.

## GA4 and GTM Implementation

Consult `references/implementation-guide.md` for step-by-step GA4 setup, GTM container configuration, data layer specification, and server-side tracking patterns.

## UTM Parameter Strategy

| Parameter | Purpose | Convention |
|-----------|---------|-----------|
| utm_source | Traffic origin | Lowercase: google, facebook, newsletter |
| utm_medium | Marketing medium | cpc, email, social, referral |
| utm_campaign | Campaign name | product_launch_q1_2026 |
| utm_content | Differentiate versions | hero_cta, sidebar_link |
| utm_term | Paid search keywords | running+shoes |

Document all UTMs in a shared spreadsheet. Enforce lowercase and underscore conventions.

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Tracking everything "just in case" | Noise drowns signal, increases costs | Track only what informs decisions |
| Inconsistent naming (camelCase + snake_case) | Fragmented data, broken reports | Enforce one convention from day 1 |
| No tracking plan document | Tribal knowledge, drift over time | Write tracking plan before code |
| PII in event properties | Privacy violations, legal risk | Never send email, name, or IP as properties |
| Relying on pageviews only | Misses actual engagement | Track meaningful user actions |
| No validation after deployment | Silent failures, missing data | Validate with debugger after every change |
| Ignoring consent management | Legal exposure (GDPR, CCPA) | Implement consent before tracking |
| Client-side only tracking | Ad blockers remove 20-40% of data | Consider server-side for critical events |

## Implementation Checklist

- [ ] Created tracking plan document with all events, properties, and triggers
- [ ] Established naming convention and documented it
- [ ] Configured GA4 property with correct data stream settings
- [ ] Set up GTM container with data layer specification
- [ ] Implemented consent management for GDPR/CCPA
- [ ] Validated all events in GA4 DebugView and GTM Preview
- [ ] Created UTM convention document and shared with team
- [ ] Set up key conversions and custom dimensions in GA4

## Quick Calculations

Run the tracking plan generator for structured event documentation:
```bash
python3 ~/.claude/skills/analytics-tracking/scripts/tracking_planner.py \
  --config ~/.claude/skills/analytics-tracking/examples/tracking-config.yaml
```

## Key References

- **`references/sources.md`** -- Analytics research, GA4 documentation, tool references
- **`references/event-catalog.md`** -- Complete event catalog with properties by site type
- **`references/implementation-guide.md`** -- GA4 + GTM setup, data layer, server-side tracking

## Related Skills

- **ab-test-setup** -- For experiment tracking and measurement
- **seo-audit** -- For organic traffic analysis
- **page-cro** -- For conversion optimization (uses tracking data)
