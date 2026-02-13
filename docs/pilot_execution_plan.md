# Pilot Execution Plan (Based on Founder Decisions)

## 1) Pilot Account and Scope

- Pilot customer type: small business owner operating both bubble tea and small restaurant concepts.
- Expected footprint: up to ~10 stores under one owner account.
- Implication: support cross-store summary with store-level drill-down.

## 2) MVP Product Behavior

### Experience
- Primary: Web chat
- Secondary: SMS as notification + re-entry into web chat context

### Answer style
Every "status" response should include:
1. short business status,
2. top 3 action items,
3. confidence per action.

### Automation boundary
- MVP is recommendation-only.
- No autonomous execution.

## 3) Data Plan

### Current constraint
- No real pilot POS exports available today.

### Immediate workaround
- Use sample POS datasets for schema and logic hardening.
- Build import mapping that tolerates common POS field name variations.

### Transition plan
- Once pilot exports arrive:
  1. map columns,
  2. validate data quality,
  3. run side-by-side checks vs owner intuition,
  4. tune recommendation rules.

## 4) Success Measurement (Owner-Centric)

Primary success metric: **Money saved**.

Track weekly/monthly:
- estimated savings from accepted recommendations,
- realized before/after deltas where data allows,
- recommendation acceptance rate.

Avoid over-emphasizing dashboard KPIs in owner communication.

## 5) Multi-Store Account Model

- Tenant/account = owner business entity.
- One owner can have multiple stores.
- Bot name is configured once per owner account and reused across stores/channels.
- All access and retrieval remain tenant-scoped.

## 6) 2-Week Build Plan

### Week 1
1. Finalize CSV import templates + validation checks.
2. Add account/store metadata model for multi-store owner.
3. Implement status response format contract (status + actions + confidence).
4. Add SMS message formatter for brief notifications.

### Week 2
1. Add savings estimation method per recommendation type.
2. Add recommendation acceptance tracking.
3. Build store-level drill-down prompts in chat.
4. Prepare pilot onboarding checklist and data handoff template.

## 7) Risks and Mitigations

1. **Mixed concept data differences (bubble tea vs restaurant)**
   - Mitigation: concept-aware thresholds and per-store baselines.
2. **Limited early data quality**
   - Mitigation: strict validation and clear data freshness warnings.
3. **Owner trust in estimated savings**
   - Mitigation: show simple formula + confidence + before/after comparisons.
