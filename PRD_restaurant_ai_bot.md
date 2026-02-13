# PRD: AI-First Restaurant Owner Bot (Bot-First Daily Operator)

## 1) Product Overview

### Problem Statement
Restaurant owners are busy and do not want to open BI dashboards every morning. Current tools force owners to pull reports themselves, then figure out what matters and what to do.

### Product Vision (AI-First, Bot-First)
The **first screen is the bot**. The owner’s default workflow is:
1. Ask: **"What is my business status today?"**
2. Ask: **"What should I know?"**
3. Ask: **"What should I do first?"**

The bot proactively answers with a short status brief, top risks/opportunities, and prioritized actions with evidence.

### Product Principle
**No dashboard-first experience.** Dashboards are secondary support tools; the primary interface is conversational AI.

### Target Users
- Primary: single-store and multi-store restaurant owners/operators
- Secondary: general managers, area managers

## 2) Goals and Non-Goals

### Goals
1. Make the bot the owner’s first daily touchpoint.
2. Deliver one concise daily "status + actions" brief before opening hours.
3. Let owners ask follow-up questions naturally and get evidence-backed answers.
4. Reduce decision time and increase action quality.

### Non-Goals (Phase 1)
- Replacing POS/ERP systems
- Fully autonomous execution without human approval
- Building custom BI dashboards as a primary product surface

## 3) Core User Jobs To Be Done

1. **As an owner**, I want to ask one question and instantly know my current business status.
2. **As an owner**, I want top action items ranked by impact so I can act quickly.
3. **As an owner**, I want to ask "why" and "show me evidence" before deciding.
4. **As an owner**, I want chain-level and store-level exceptions explained clearly.

## 4) North-Star Experience (Bot-First)

### Daily Morning Flow
Owner opens app/chat and asks:
- "What is my status today?"

Bot responds in 20-40 seconds read time:
1. **Business Status:** Revenue, labor ratio, margin signal, traffic/check trends.
2. **What Changed:** Biggest positive/negative deltas vs baseline.
3. **Why It Happened (Likely):** 1-3 key drivers with confidence.
4. **What To Do Today:** Top 3 actions with expected impact + effort.

### Drill-Down Flow
Owner asks:
- "Why is labor high?"
- "Which store caused most of the drop?"
- "What should GM do today at Store B?"

Bot answers with facts, comparison window, and recommended next step.

## 5) MVP Scope

### Core Capabilities
1. **Data Connectors (read-only)**
   - POS (sales, tickets, discounts, items)
   - Labor/scheduling (hours, overtime, labor cost)
   - Optional COGS/inventory if available
2. **Status Engine**
   - Computes KPI health and detects notable changes
   - Builds "today status" summary and ranks priorities
3. **Action Engine**
   - Generates recommended actions with impact/confidence/effort
4. **Conversational Copilot**
   - Natural-language Q&A for metric, trend, cause, and action guidance
5. **Delivery Channels**
   - In-app chat/web chat first
   - Optional push/email/WhatsApp as entry points back to the bot

### Explicitly Out of Scope (MVP)
- Dashboard builder as core surface
- Automatic operational execution without confirmation
- Advanced long-horizon forecasting as primary value proposition

## 6) Functional Requirements

### FR1: Bot-First Entry
- Product home opens directly to the bot conversation.
- First suggested prompts include:
  - "What is my status today?"
  - "What should I know right now?"
  - "What should I do first?"

### FR2: Daily Status Brief
- Bot can generate daily status for yesterday + current context.
- Brief includes: KPI health, top deltas, top 3 action items.
- Brief clearly states data freshness and completeness.

### FR3: Action Item Format
Each action includes:
- recommendation,
- reason,
- expected impact (range or directional),
- confidence,
- effort (low/medium/high),
- owner/GM assignee suggestion.

### FR4: Conversational Explainability
- Bot supports "why", "show detail", "compare periods", and "by store/daypart" follow-ups.
- Responses include concrete numbers and source period references.
- If uncertain, bot must say what data is missing.

### FR5: Multi-Store Intelligence
- Chain-level overview + store outlier detection.
- Identifies which locations most influenced aggregate movement.

### FR6: Safety
- No fabricated values.
- Recommendations are guidance, not guaranteed outcomes.

### FR7: Configurable Bot Identity per Store/Account
- Each owner account can set a custom bot name (e.g., "Nomi", "Kai", "OpsMate").
- Bot name appears consistently in chat, notifications, and daily briefings.
- Name customization is scoped to that account/tenant and does not affect other customers.

## 7) Non-Functional Requirements

1. Reliability: daily brief success >= 99%
2. Performance: common chat queries p50 <= 3s, p95 <= 8s
3. Security: encryption in transit/at rest, RBAC, audit logs
4. Data isolation: strict tenant-level isolation; one owner can never access another owner’s data
5. Deployment options: support shared multi-tenant SaaS and isolated single-tenant deployment for enterprise/security-sensitive groups
6. Observability: monitor data freshness, connector health, response quality

## 8) UX Principles (AI-First)

1. **Conversation is the product:** bot is primary; reports are supporting evidence.
2. **Status first, details second:** summarize first, drill down on request.
3. **Action over analytics:** always end with clear next steps.
4. **Trust by transparency:** show data basis, confidence, and uncertainty.

## 9) Success Metrics (MVP)

### Adoption / Behavior Shift (most important)
- % owners who start day in bot >= 70%
- % sessions starting with "status" intent >= 60%
- Weekly active owner rate >= 50%

### Value Metrics
- Median reported decision-time reduction >= 30 min/day
- Action follow-through rate >= 35%
- Owner trust score >= 4.2/5

### Quality Metrics
- Numeric response error rate < 1%
- "Insufficient data" used correctly (measured via QA sampling)

## 10) Risks and Mitigations

1. **Owners still fallback to old BI habits**
   - Mitigation: make bot home default; daily nudges with direct question prompts.
2. **Low trust in recommendations**
   - Mitigation: evidence + confidence + clear assumptions in every critical answer.
3. **Data quality inconsistency**
   - Mitigation: freshness indicators, data quality scoring, safe fallback wording.
4. **Cross-tenant data exposure risk**
   - Mitigation: tenant-scoped access controls, per-tenant encryption keys (where required), and regular security testing.

## 11) Rollout Plan

### Phase 0 (2-4 weeks): Discovery
- Interview 15-20 owners on morning decision workflow.
- Validate "status" question patterns and action vocabulary.

### Phase 1 (8-12 weeks): MVP Pilot
- Launch bot-first interface with daily status + top actions + Q&A.
- Integrate 1-2 POS systems + one labor source.
- Pilot with 5-10 restaurant groups.

### Phase 2: Expansion
- Add COGS/inventory and role-based action routing (owner vs GM).
- Add closed-loop tracking: "did action improve KPI?"

## 12) Open Questions

1. Which bot surface should be primary at launch (WhatsApp vs in-app chat)?
2. Should the bot always answer first with summary, then ask if owner wants detail?
3. How should role-based actions be split between owner and GM?
4. What minimum integrations are required to provide trustworthy status?

## 13) Business Model and Go-To-Market Plan

### Positioning
- Primary positioning: **"Your AI Store Manager"**
- Supporting message: **"Run your store by talking to it."**
- Avoid dashboard-heavy positioning (e.g., "AI analytics tool") as primary message.

### Initial Customer Segment (Narrow ICP)
Start with one focused segment to increase win rate and speed:
- Bubble tea shops
- Small Asian restaurants
- Coffee shops
- Fast-casual groups with 2-20 locations

Why this segment first:
- High labor + waste sensitivity
- Owner-operator decision style (needs fast actions, not reports)
- Relatively standard operating patterns (good for repeatable AI playbooks)

### Pricing Hypothesis
- Subscription: **$99-$299 per location/month**
- Value promise: save **$1,000-$3,000/month** per location from labor, waste, and promotion optimization.
- Expansion motion: start with insights + recommendations, then upsell execution automation.

### Distribution / GTM Motion
1. Founder-led sales to local multi-store operators
2. Land with one store or one district manager
3. Expand account after showing measurable KPI improvements in 4-8 weeks
4. Build partner channels with POS consultants / regional restaurant tech integrators

## 14) MVP Delivery Plan (3-6 Months)

### Month 0-1: Data Foundations
- Connect to top systems first: Square, Toast, Shopify POS (or equivalent regional leaders)
- Normalize core metrics: sales, labor, check size, discounts, item mix
- Define "data readiness" and fallback logic for incomplete data days

### Month 1-3: Bot-First Daily Briefing
- Ship daily AI status briefing via in-app chat + WhatsApp/SMS entry points
- Must answer:
  - "What is my status today?"
  - "What should I know?"
  - "What should I do first?"
- Include top 3 actions with impact/confidence/effort

### Month 3-6: Action + Controlled Execution
- Add one-click "Approve" flows for low-risk actions:
  - prep quantity adjustments
  - suggested labor shift edits
  - simple promo/task recommendations
- Keep human-in-the-loop approval in MVP
- Track action outcome to show closed-loop value (before vs after KPI)

## 15) Expansion Roadmap (Company-Building Path)

### Phase 1: AI Insights
- Reliable status + anomaly detection + conversational explanation

### Phase 2: AI Recommendations
- Playbook-based suggestions for labor, waste, ordering, and promotions

### Phase 3: AI-Assisted Execution
- One-click approvals that write back into connected systems

### Phase 4: AI Operating System
- Unified business brain across ordering, staffing, pricing, finance, and supply chain

## 16) Strategic Scale Hypothesis

- If the business reaches **50,000 locations** at **$200/location/month**:
  - Monthly recurring revenue = **$10M**
  - Annual recurring revenue = **$120M**

This frames the long-term upside and supports building for multi-location repeatability early.

## 17) Founder/Team Advantage Statement

- Deep real-world restaurant operations experience is a competitive advantage.
- Product decisions should favor practical operator workflows over generic AI demos.
- The goal is trusted daily decisions, not "interesting analytics."

## 18) Bot Naming and Brand Direction

### Configurable Bot Name (Per Store / Per Owner Group)
- The bot name is **configurable** so each business can choose its own assistant identity.
- Default name on new accounts: **Nomi** (working default only).
- Examples: "Nomi", "Kai", "StorePilot", "Miso".

### Naming Rules
- Name is unique only within that customer account scope (no global uniqueness requirement).
- Name changes are allowed by account admin and versioned in settings history.
- Name is propagated to all channels (app chat, SMS/WhatsApp, email brief) for consistent branding.

### Brand/Legal Guardrails
- We provide recommendations for easy-to-brand names.
- Customers are responsible for final trademark checks for their chosen name in their market.

## 19) Data Privacy, Isolation, and Deployment Model

### Tenant Data Isolation (Required)
- Owner data is isolated by tenant/account boundary.
- No cross-owner data sharing in prompts, retrieval, analytics, or model context.
- Access control is enforced at API, database, cache, and analytics layers.

### Deployment Modes
1. **Shared multi-tenant SaaS** (default): logical tenant isolation.
2. **Isolated single-tenant deployment** (premium/enterprise): dedicated data plane and stricter network/security controls.

### Compliance and Trust Controls
- Customer-specific data retention/deletion policies.
- Audit logs for data access and admin actions.
- Security review checklist before enabling write-back automations.

## 20) Example Bot Interaction (Draft)

> **Owner:** What is my status today?
>
> **{{ConfiguredBotName}}:** Good morning, Jamie. Overall status: **stable with 2 risks**.
> - Revenue yesterday: **$12,480 (+6.2% WoW)**
> - Labor ratio: **34.8% (+3.1 pts, above target)**
> - Dinner average check: **-5.4% vs 4-week baseline**
>
> **What you should know:** labor and dinner check are driving margin pressure.
>
> **What to do first:**
> 1. Reduce late-shift overlap by 1 staff-hour (impact: $55-$80/day, confidence: high).
> 2. Push dinner upsell combo on tickets < $18 (impact: +2-4% check, confidence: medium).
> 3. Review salad prep plan at Store B (waste +19%, confidence: medium).
>
> Ask me: "Why is labor high?" or "Show Store B details."


## 21) Pilot Decisions (Locked for MVP)

Based on founder decisions, the following are locked for the first pilot cycle:

1. **Pilot customer profile**
   - Start with a friendly pilot account operating:
     - bubble tea shop(s)
     - small restaurant(s)
   - Treat these as one SMB multi-store operator profile (likely < 10 stores).

2. **Data availability strategy**
   - Current state: no live POS exports yet.
   - Immediate action: use sample POS-like datasets for prototyping and pipeline hardening.
   - Next step: replace sample data with real pilot exports as soon as available.

3. **Primary product channels**
   - Web chat is primary experience.
   - SMS is secondary alert/entry channel back to chat.

4. **Response format preference**
   - Use short status summary + prioritized action items + confidence labels.
   - Keep owner-facing output concise and decision-oriented.

5. **Execution policy (MVP)**
   - Recommendation-only mode.
   - No automatic write-back actions in pilot.

6. **Pilot success definition**
   - Focus on quantified money saved for owner (not abstract KPI dashboards).
   - Track estimated impact from accepted recommendations and realized before/after comparisons.

7. **Deployment model (MVP)**
   - Start with multi-tenant deployment first.

8. **Bot naming policy**
   - Each owner configures one bot name at account level.
   - The same owner-level bot identity applies across all stores under that owner account.

