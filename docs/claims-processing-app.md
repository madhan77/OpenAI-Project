# Claims Processing Application Architecture

## Overview
The claims processing application promotes the PRD commitments into an executable, end-to-end platform suitable for formal product review. It orchestrates intake, validation, adjudication, payment instruction, notification, and analytics tracking using modular components that mirror payer operations.

## Architecture
- **Workflow Orchestrator (`ClaimsProcessingApp`)** – Coordinates claim lifecycle transitions, invoking validators, rule engines, notifications, analytics, and payment generation while persisting rich timelines.
- **Domain Models** – `Claim`, `ClaimLine`, `MemberProfile`, `ProviderProfile`, and related types in `claims_app.models` capture the data required for policy enforcement and downstream communication.
- **Repositories** – `InMemoryClaimRepository` persists claim payloads and timeline events for deterministic testing; interfaces permit swapping to persistent stores.
- **Validation Layer** – Eligibility, attachment, coding, and duplicate validators enforce policy gates ahead of adjudication, returning structured issue codes for transparency.
- **Rule Engine** – Composite rule engine applies high-dollar, prior-auth, network, and fraud heuristics, returning explicit reason codes and manual-review directives.
- **Manual Review Queue** – Dedicated queue surfaces exception claims with priority hints for analyst workbench integrations.
- **Payments Module** – Generates Explanation of Benefits artifacts and payment instructions through an injectable gateway abstraction.
- **Notification Orchestrator** – Dispatches provider/member communications across email, SMS, and portal channels while capturing analytics.
- **Analytics Collector** – Aggregates metrics such as intake volume, pending information, manual review rates, auto-adjudication counts, and notification fan-out.
- **Reviewer Portal** – Static web experience backed by Firebase Authentication that surfaces mock claim queues, details, and performance summaries for stakeholders.

## Key Workflows
1. **Submit Claim** – Intake saves the claim, records baseline analytics, and immediately transitions to validation.
2. **Validate** – Validators contribute issue codes; if any arise, the claim is marked `PENDING_INFORMATION`, notifications are issued, and metrics tagged with root causes.
3. **Rules Evaluation** – Passing validation triggers rule evaluation. Manual-review directives enqueue the claim and return a `NEEDS_MANUAL_REVIEW` decision with annotated reasons.
4. **Auto-Adjudication** – Successful claims produce payment instructions, EOB summaries, analytics updates, and multi-channel notifications, culminating in a `NOTIFIED` status.
5. **Post-Processing** – All paths maintain an immutable event timeline for auditability, supporting downstream reviewer portals and compliance reporting.

## Reviewer Portal Experience
The portal focuses on rapid sign-off for formal review:
- Firebase Authentication protects access. Administrators provide production credentials through `portal/firebase-config.json` (or a local JavaScript override) and provision reviewer accounts via Firebase console.
- Authenticated reviewers explore mock claim queues that mirror adjudication states (approved, denied, pending information, manual review).
- Summary tiles surface portfolio KPIs (counts and dollar aggregates), while the queue and detail panels provide drill-down context and timeline notes.
- The portal intentionally relies on static mock data, enabling demonstrations without exposing PHI or requiring backend connectivity.

## Extensibility
- Validators and rules are constructed via protocols, enabling runtime composition of payer-specific policies.
- Repository, notification, and payment abstractions allow integration with enterprise systems without refactoring the orchestrator.
- Metrics collector can be replaced with observability platforms (e.g., Prometheus, Datadog) by implementing the same interface.
- The portal can be wired to live APIs by swapping the mock data module for REST/GraphQL clients once services are available.

## Review Readiness Highlights
- Implements the PRD’s core automation, manual review workflow, transparency, and analytics expectations.
- Ships with pytest coverage spanning auto-approval, manual review routing, document pend, and duplicate detection scenarios.
- Documentation and configuration defaults provide a clear runway for integration, making the application suitable for formal stakeholder review.
