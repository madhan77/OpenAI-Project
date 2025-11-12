export const personas = {
  b2b: {
    eyebrow: "Enterprise procurement",
    heroTitle: "Command center for multi-location B2B buyers",
    heroSubtitle:
      "Onboard departments, validate contract pricing, and move approvals from request to invoice without leaving one workspace.",
    actions: [
      { label: "Launch onboarding flow", type: "primary" },
      { label: "Share beta link", type: "secondary" }
    ],
    summaryMetrics: [
      { label: "Active companies", value: "126", trend: "+12% vs LY" },
      { label: "Avg approval SLA", value: "3.1 hrs", trend: "-18%" },
      { label: "ACH adoption", value: "64%", trend: "+9 pts" },
      { label: "Net terms outstanding", value: "$4.2M", trend: "Stable" }
    ],
    journeySteps: [
      {
        title: "Account provisioning",
        description: "All 126 companies synced via Okta SCIM provisioning.",
        status: "Completed"
      },
      {
        title: "Budget & policy setup",
        description: "Finance owners configuring departmental limits via admin API.",
        status: "In progress"
      },
      {
        title: "Catalog & pricing",
        description: "Contract price lists connected to GraphQL gateway; final QA this week.",
        status: "Blocked"
      },
      {
        title: "Approval workflows",
        description: "PO + ACH checkout testing with pilot customers.",
        status: "Next"
      },
      {
        title: "Fulfillment & reporting",
        description: "Snowflake exports connected for finance self-serve.",
        status: "Upcoming"
      }
    ],
    primaryPanel: {
      eyebrow: "Approvals",
      title: "Spending queue by department",
      cta: "View routing rules",
      rows: [
        {
          id: "PO-1482",
          dept: "Facilities",
          amount: "$38,200",
          submitter: "M. Lopez",
          status: "Awaiting finance"
        },
        {
          id: "PO-1483",
          dept: "Field Ops",
          amount: "$12,480",
          submitter: "S. Kline",
          status: "Auto-approved"
        },
        {
          id: "PO-1485",
          dept: "R&D",
          amount: "$84,960",
          submitter: "C. Adebayo",
          status: "Needs review"
        }
      ]
    },
    secondaryPanel: {
      eyebrow: "Billing",
      title: "Invoices ready for reconciliation",
      cards: [
        {
          id: "INV-9032",
          company: "Northwind Utilities",
          due: "Due in 5 days",
          amount: "$128,440",
          status: "Ready"
        },
        {
          id: "INV-9037",
          company: "Evergreen Logistics",
          due: "Due in 14 days",
          amount: "$56,320",
          status: "Scheduled"
        },
        {
          id: "INV-9039",
          company: "Apex Health",
          due: "Due in 21 days",
          amount: "$214,870",
          status: "Pending export"
        }
      ]
    },
    callouts: [
      {
        title: "Contract sync lag",
        body: "Pricing microservice reporting 7-minute lag. Enable cache warmers before full launch.",
        tone: "warning"
      },
      {
        title: "ACH limits",
        body: "Stripe daily ACH cap hit twice this week. Coordinate with payments team for uplift.",
        tone: "danger"
      },
      {
        title: "Approver onboarding",
        body: "Only 62% of finance approvers completed MFA enrollment. Send reminder campaign.",
        tone: "warning"
      }
    ],
    roadmap: [
      "Enable split-shipments for large equipment orders.",
      "Expose approval audit log via support console.",
      "Automate net-terms credit checks with ERP webhook.",
      "Pilot loyalty crossover offers with procurement admins."
    ]
  },
  b2c: {
    eyebrow: "Consumer storefront",
    heroTitle: "Personalized shopping & fulfillment insights",
    heroSubtitle:
      "Optimize discovery, conversion, and post-purchase care with data pulled from the shared GraphQL layer.",
    actions: [
      { label: "Preview landing page", type: "primary" },
      { label: "Launch experiment", type: "secondary" }
    ],
    summaryMetrics: [
      { label: "Traffic routed", value: "25%", trend: "+5 pts" },
      { label: "Checkout conversion", value: "3.4%", trend: "+0.6 pts" },
      { label: "Avg order value", value: "$162", trend: "+$12" },
      { label: "Return rate", value: "4.1%", trend: "-1.2 pts" }
    ],
    journeySteps: [
      {
        title: "Acquisition",
        description: "CMS hero, search, and recommendations wired to feature flags.",
        status: "Completed"
      },
      {
        title: "Evaluation",
        description: "PDP experiments running on 10% of traffic; review heatmaps tomorrow.",
        status: "In progress"
      },
      {
        title: "Checkout",
        description: "Digital wallets + loyalty redemption available in sandbox.",
        status: "Next"
      },
      {
        title: "Fulfillment",
        description: "Real-time shipment tracking integrated with carrier webhooks.",
        status: "Upcoming"
      },
      {
        title: "Retention",
        description: "Email/SMS journeys templated and ready for CRM triggers.",
        status: "Upcoming"
      }
    ],
    primaryPanel: {
      eyebrow: "Orders",
      title: "In-flight consumer orders",
      cta: "Open order ops",
      rows: [
        {
          id: "EC-7841",
          customer: "Alana Rhodes",
          stage: "Out for delivery",
          value: "$218"
        },
        {
          id: "EC-7842",
          customer: "Marcus Lee",
          stage: "Packed",
          value: "$94"
        },
        {
          id: "EC-7844",
          customer: "Yuna Patel",
          stage: "Preparing shipment",
          value: "$301"
        }
      ]
    },
    secondaryPanel: {
      eyebrow: "Engagement",
      title: "Loyalty & offers",
      cards: [
        {
          id: "LOY-118",
          company: "XP Platinum",
          due: "Boost expires in 3 days",
          amount: "8.4k members",
          status: "Multiplier live"
        },
        {
          id: "LOY-202",
          company: "Refer-a-friend",
          due: "Target 500 signups",
          amount: "320 achieved",
          status: "64% to goal"
        },
        {
          id: "LOY-209",
          company: "Same-day delivery",
          due: "Seattle + Denver",
          amount: "NPS 72",
          status: "Pilot"
        }
      ]
    },
    callouts: [
      {
        title: "Wallet adoption",
        body: "Apple Pay drives 34% of checkouts. Enable Google Pay on Android traffic before GA.",
        tone: "success"
      },
      {
        title: "Catalog latency",
        body: "95th percentile PDP load at 3.9s after personalization toggle. Investigate caching strategy.",
        tone: "warning"
      }
    ],
    roadmap: [
      "Launch guest checkout with cart recovery emails.",
      "Add store locator with real-time inventory.",
      "Feed shopper cohorts into CDP for personalization.",
      "Co-market subscription bundles inside consumer portal."
    ]
  }
};
