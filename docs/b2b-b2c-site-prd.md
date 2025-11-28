# Product Requirements Document: Unified B2B & B2C Insurance Portal

## 1. Executive Summary
- **Goal:** Launch a single web experience that supports both business customers (brokers, corporate HR teams) and individual consumers shopping for insurance products.
- **Drivers:** Reduce operational costs by reusing shared services, increase conversion by personalizing journeys, and enable rapid experimentation for both segments.
- **Success Metrics:**
  - 20% increase in B2C quote completions within 6 months.
  - 30% reduction in manual broker onboarding time.
  - Net Promoter Score (NPS) of 50+ for both personas.
  - Shared platform uptime >99.9% with independent feature flags per segment.

## 2. Personas & Use Cases
### B2B Personas
1. **Broker Admin** – needs to onboard agencies, manage contracts, and access client policies.
2. **Corporate Benefits Manager** – configures plans for employees, reviews utilization, and approves renewals.

### B2C Personas
1. **Prospective Individual** – compares plans, completes quote, and purchases coverage.
2. **Existing Policyholder** – views policy documents, files claims, and updates payment methods.

### Cross-Cutting Use Cases
- Unified authentication with role-based access control (RBAC).
- Shared document repository and claims status tracking.
- Segmented dashboards displaying relevant KPIs.

## 3. Scope & Requirements
### Functional Requirements
1. **Landing & Segmentation**
   - Smart landing page auto-detects persona via referral tags or account profile.
   - Manual toggle between "For Business" and "For Individuals" views.
2. **Account Management**
   - SSO/SAML for B2B; email/password + social login for B2C.
   - Multi-factor authentication available to all.
3. **Product Catalog & Configuration**
   - Dynamic catalog filtered by persona.
   - B2B: Bulk plan builder with census upload; B2C: guided questionnaire.
4. **Quoting & Enrollment**
   - Shared rules engine; B2B supports multi-employee enrollment workflows.
   - Integrate payment gateways (ACH for B2B, credit card for B2C).
5. **Policy & Claims Management**
   - Dashboard with policy summaries, downloadable documents, and claim tracking.
6. **Support & Communications**
   - Embedded chat, knowledge base, and notification center segmented by persona.

### Non-Functional Requirements
- Accessibility AA compliance, responsive design.
- API-first microservice architecture; latency <400ms P95 for critical flows.
- Audit logging and SOC2 controls.

## 4. End-to-End Process
### 4.1 B2B Journey
1. **Acquisition & Onboarding**
   - Broker receives invite; completes SSO provisioning and agency profile.
   - Uploads compliance docs; automated verification via compliance service.
2. **Plan Configuration**
   - Imports employee census (CSV/API); runs plan simulations.
   - Selects carrier offerings; negotiates pricing via in-app workflow.
3. **Enrollment & Billing**
   - Sends enrollment links to employees; tracks completion status.
   - Configures employer-paid vs employee-paid contributions; sets up ACH billing schedule.
4. **Policy Management**
   - Accesses real-time utilization dashboards; exports reports.
   - Submits renewal adjustments; e-signatures captured.
5. **Support & Retention**
   - Dedicated account manager chat; SLA timer displayed.
   - Feedback loop into product team with NPS prompts.

### 4.2 B2C Journey
1. **Discovery & Consideration**
   - Persona detection tailors hero content; SEO landing pages.
   - Guided questionnaire collects demographics and coverage goals.
2. **Quote & Compare**
   - Real-time pricing from rules engine; highlight subsidies or discounts.
   - Comparison table with plan tiers, provider networks, and add-ons.
3. **Application & Payment**
   - Pre-fill data from government APIs (e.g., DMV) when consented.
   - Integrate credit card wallet and recurring payment setup.
4. **Policy Activation**
   - Instant policy documents via secure vault; digital ID cards.
   - Onboarding checklist (beneficiaries, PCP selection, autopay confirmation).
5. **Service & Retention**
   - Self-service claims submission with photo/document upload.
   - Proactive notifications for renewals and life events.

## 5. System Architecture Overview
- **Presentation Layer:** React portal with feature toggles (LaunchDarkly) controlling B2B/B2C components.
- **API Gateway:** GraphQL gateway orchestrating services (Identity, Catalog, Quoting, Billing, Claims).
- **Shared Services:**
  - Identity & Access with RBAC.
  - Document Management (S3 + CDN).
  - Notification service (email, SMS, push).
- **Data Layer:** Multi-tenant PostgreSQL for transactional data; Redshift for analytics.
- **Integrations:** CRM (Salesforce), payment processors, carrier APIs, government verification services.

## 6. Milestones & Timeline
1. **MVP (Quarter 1)**
   - Unified landing page, authentication flows, basic catalog, B2C quoting.
2. **Expansion (Quarter 2)**
   - B2B onboarding, census upload, ACH billing, shared dashboards.
3. **Optimization (Quarter 3)**
   - Advanced analytics, experimentation framework, automated renewals.

## 7. Risks & Mitigations
- **Complex RBAC causing delays:** adopt policy-as-code and reusable permission templates.
- **Data privacy concerns:** implement data masking and regional hosting.
- **Integration failures:** build sandbox simulators and contract tests.

## 8. Analytics & KPIs
- Funnel metrics per persona: visits → quotes → enrollments.
- Support metrics: average resolution time, SLA adherence.
- Financial metrics: premium volume, churn rate, broker retention.

## 9. Open Questions
1. Which carrier integrations are phase-one vs later?
2. Do we support multilingual content at launch?
3. How will we measure cross-sell/upsell across personas?

