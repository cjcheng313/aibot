# High-Level Architecture (Guardrails for MVP Development)

This document is the **source of truth** for system boundaries and design decisions.
Use it to avoid architecture drift while coding features.

## 1) System Goal

Build an AI-first store assistant where owners:
1. import/store operational data,
2. ask questions in chat,
3. receive grounded insights and action items,
4. drill down with table/diagram/details on demand.

## 2) Architecture Principles (Do Not Break)

1. **Bot-first UX**: chat is the primary interaction surface.
2. **SQL is source-of-truth** for exact business metrics.
3. **No cross-tenant data sharing** anywhere in pipeline.
4. **AI answers must be grounded** in retrieved tenant data.
5. **Human-in-the-loop for execution** (no silent auto-actions in MVP).

## 3) High-Level Components

```text
[POS CSV/API] [Labor] [Inventory]
        \         |         /
         \        |        /
          --> [Ingestion + Validation] --> [SQL Core Tables]
                                         --> [Daily KPI Views]

[Store Notes / Incidents / Chat Logs] --> [Document Store]
                                             |
                                             v
                                      [Embedding Pipeline]
                                             |
                                             v
                                        [Vector Index]

[Owner Chat UI]
      |
      v
[Chat Orchestrator/API] --> reads SQL exact metrics
      |                 --> retrieves semantic context from Vector Index
      |                 --> optional raw context from Document Store
      v
[LLM + Prompt Layer]
      |
      v
[Grounded Response + Actions + (optional) table/diagram]
```

## 4) Data Ownership and Isolation

- Tenant ID is mandatory in every request path.
- SQL queries must be tenant-filtered.
- Document records are tenant-partitioned.
- Vector retrieval is namespace-scoped per tenant.
- No prompt may include another tenant’s data.

## 5) Logical Data Model Responsibilities

- **SQL**: orders, items, inventory snapshots, labor shifts, daily financials.
- **Document storage**: conversation history, notes, incidents, feedback artifacts.
- **Vector DB**: embedded notes/policies/incidents for semantic retrieval.

## 6) Request Lifecycle (Chat Query)

1. Authenticate user + resolve tenant/store scope.
2. Parse intent (`status`, `labor`, `waste`, `top item`, `table`, `diagram`).
3. Pull exact numbers from SQL.
4. Retrieve related context from vector/doc stores (tenant-scoped).
5. Assemble grounded prompt with cited facts.
6. Generate response with action suggestion.
7. Return concise answer + optional drill-down output.
8. Log interaction for analytics/quality review.

## 7) Non-Functional Guardrails

- Reliability target: daily brief success >= 99%
- Performance target: chat p50 <= 3s, p95 <= 8s (common intents)
- Security: encryption in transit/at rest, audit logs, RBAC
- Traceability: retain response inputs (sanitized) for QA and incident investigation

## 8) Coding Guardrails

Before merging features, confirm:
- [ ] Does this keep chat as primary UX?
- [ ] Are metrics sourced from SQL (not guessed by model)?
- [ ] Is tenant isolation enforced end-to-end?
- [ ] Are outputs explainable with concrete values?
- [ ] If action execution exists, is explicit approval required?

## 9) Change Management

If implementation requires breaking any principle above:
1. Update this document first,
2. explain tradeoff in PR description,
3. include migration/safety plan.

This keeps architecture decisions explicit and prevents accidental regressions.
