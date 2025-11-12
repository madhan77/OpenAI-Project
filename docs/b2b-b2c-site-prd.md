# Product Requirements Document: Unified B2B/B2C Site Setup

## 1. Overview
- **Product name:** Unified Commerce Portal (UCP)
- **Document owner:** Product team
- **Last updated:** 2024-05-23
- **Status:** Draft

## 2. Background & Opportunity
Many enterprise customers require bulk purchasing, invoicing, and account management features, while consumers prioritize fast browsing, personalization, and frictionless checkout. Maintaining separate sites slows feature velocity and creates inconsistent brand experiences. A unified platform with B2B/B2C capability enables:
- Single codebase and design system.
- Shared product/catalog services with role-based experiences.
- Cross-sell potential (e.g., consumer buys subscription, business orders equipment).

## 3. Goals & Success Metrics
| Goal | KPI | Target |
| --- | --- | --- |
| Launch unified site supporting both account types | % of B2B/B2C traffic on new site | 100% after 3-month rollout |
| Improve conversion | Checkout completion rate | +8% B2C, +5% B2B |
| Reduce operational overhead | Time to configure new customer type | -30% |
| Increase NPS | B2B +10pts, B2C +6pts | Post-launch surveys |

## 4. Non-Goals
- Building an ERP or CRM replacement.
- Supporting marketplaces or third-party sellers beyond existing catalog.
- Internationalization beyond English/US currency for MVP.

## 5. Assumptions
- Identity provider supports SSO, MFA, and customer-managed users.
- Product catalog, pricing, and inventory data live in existing microservices with GraphQL access.
- Payments processor already supports saved cards, ACH, and purchase orders.

## 6. Personas & Use Cases
### B2B Procurement Lead
- Needs custom pricing, bulk upload, PO checkout, approval flows, scheduled deliveries.
### B2B Finance Admin
- Needs invoices, payment status, usage reports, ability to manage budgets and credit lines.
### B2C Shopper
- Wants personalized recommendations, quick checkout, order tracking, loyalty rewards.

## 7. End-to-End Customer Journeys
### 7.1 B2B Journey
1. **Onboarding:** Sales or self-serve creates company account, assigns procurement lead. Lead receives SSO invite.
2. **Account Setup:** Lead defines departments, spending limits, shipping addresses, tax exemptions.
3. **Catalog Access:** Lead browses B2B catalog view showing tiered pricing and inventory by warehouse.
4. **Cart Building:** Uploads CSV or uses quick order form to add SKUs; system validates contract pricing and min quantities.
5. **Approvals:** Checkout triggers approval workflow; approvers receive notification, review order, and approve/reject.
6. **Checkout:** Approved order uses PO or ACH. Confirmation with downloadable PDF invoice.
7. **Fulfillment:** Logistics updates status via API; procurement lead tracks order milestones.
8. **Billing & Reporting:** Finance admin downloads invoices, schedules recurring reports, reconciles payments.

### 7.2 B2C Journey
1. **Discovery:** Customer lands on marketing page, uses search/filters, sees personalized recommendations.
2. **Evaluation:** Product detail page shows reviews, availability, financing offers.
3. **Cart & Checkout:** Express checkout (Apple Pay/Google Pay), saved addresses, loyalty points.
4. **Fulfillment:** Real-time shipment tracking, SMS/email notifications.
5. **Post-purchase:** Easy returns/exchanges, subscription management, referrals.

## 8. Functional Requirements
### 8.1 Account & Identity
- Unified login page detects account type based on email domain or manual selection.
- Role-based dashboards: company admin, buyer, finance, consumer.
- MFA enforcement for B2B roles, optional for B2C.

### 8.2 Catalog & Pricing
- Shared catalog service with feature flags for content blocks.
- B2B pricing derived from contracts and displayed net of tax; B2C shows MSRP and promos.
- Inventory per fulfillment center; B2B can reserve inventory for scheduled delivery.

### 8.3 Cart & Checkout
- Support mixed carts but enforce B2B-only items restricted to business accounts.
- Payment methods: cards, wallets, ACH, purchase order, net terms.
- Approval workflows configurable by spend threshold.

### 8.4 Account Management
- B2B admins manage users, roles, budgets, saved templates.
- B2C users manage addresses, payment methods, loyalty, subscriptions.
- Shared order history with filters by channel, status, fulfillment center.

### 8.5 Content & Marketing
- CMS surfaces targeted content modules per persona.
- Email/SMS triggers integrated with CRM (welcome, reorder reminders, abandoned cart).

### 8.6 Analytics & Reporting
- Real-time dashboards for conversion, average order value, approval cycle time.
- Exportable reports (CSV, API) for B2B finance teams.

## 9. Non-Functional Requirements
- **Performance:** <2s median page load; <4s 95th percentile API response for catalog.
- **Availability:** 99.9% uptime for transactional services.
- **Security:** SOC2, PCI DSS compliance; data encryption at rest/in transit.
- **Scalability:** Handle 5x traffic spikes during campaigns.

## 10. System Architecture & Integrations
- **Front-end:** React + SSR for SEO. Feature toggles for persona-specific modules.
- **Back-end:** GraphQL gateway (BFF) aggregating catalog, pricing, identity, orders.
- **Services:**
  - Identity (Okta/Azure AD) for SSO + MFA.
  - Catalog & inventory microservices.
  - Pricing engine with contract rules.
  - Order service orchestrating approvals and fulfillment.
  - Payment gateway (Stripe/Adyen) for cards + ACH, ERP for PO invoicing.
- **Data:** Event streaming to analytics warehouse (Snowflake/BigQuery) and CDP.

## 11. End-to-End Process Flow
1. **Account creation:**
   - Lead signs up or sales rep provisions via admin tool.
   - Identity service creates tenant, issues invite, stores metadata in customer master.
2. **Configuration:**
   - Admin configures payment terms, budgets, shipping locations.
   - Catalog service applies relevant price lists and availability rules.
3. **Shopping:**
   - Front-end queries GraphQL for catalog. Feature flags determine layout.
   - Users add items; cart service validates rules and promotions.
4. **Approval/Checkout:**
   - Workflow engine routes approvals (B2B) or immediate checkout (B2C).
   - Payments processed; order record created.
5. **Fulfillment:**
   - Order service sends fulfillment request to WMS. Status updates via webhooks.
6. **Post-order:**
   - Notifications triggered; invoices stored; analytics events emitted.
7. **Support:**
   - Customer service portal surfaces unified order data for agents.

## 12. Dependencies
- Identity provider enhancements for role metadata.
- Pricing engine support for tiered + contract pricing.
- Workflow service for approvals.
- CMS personalization features.

## 13. Risks & Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Feature creep delaying launch | Medium | Enforce MVP scope, staged rollout |
| Data inconsistency between B2B/B2C catalogs | High | Automated sync jobs, monitoring |
| Complex approvals degrade performance | Medium | Cache rules, asynchronous notifications |
| Change management for existing customers | High | Beta program, training materials |

## 14. Rollout Plan
1. **Alpha (internal):** Test login, catalog, checkout flows with employee accounts.
2. **Private Beta:** 5 pilot B2B customers + 5% of consumer traffic; monitor metrics.
3. **Public Beta:** 25% traffic, enable analytics dashboards.
4. **GA:** 100% traffic, decommission legacy sites.
5. **Post-GA:** Iterate on localization, marketplace features.

## 15. Analytics & Monitoring
- Funnel analytics (landing → PDP → cart → checkout) segmented by persona.
- Approval cycle time, PO adoption, avg order value.
- SLA dashboards for identity, pricing, checkout APIs.
- Incident response playbooks integrating PagerDuty/Slack.

## 16. Open Questions
1. Do we need guest checkout for B2B trials?
2. Should we support split shipments for B2B orders at launch?
3. Is headless CMS available for dynamic landing pages?
