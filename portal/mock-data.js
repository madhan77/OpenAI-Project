export const mockClaims = [
  {
    id: "CLM-10001",
    member: {
      id: "MBR-501",
      name: "Avery Johnson",
      plan: "PPO Gold"
    },
    provider: {
      name: "Sunrise Family Practice",
      npi: "1457382911"
    },
    status: "APPROVED",
    submittedAt: "2024-03-18T15:35:22Z",
    lastUpdatedAt: "2024-03-19T12:10:00Z",
    financials: {
      billed: 425.0,
      allowed: 370.0,
      paid: 296.0,
      patientResponsibility: 74.0
    },
    notes: [
      {
        author: "Auto-Adjudication",
        body: "Claim matched contracted rate; paid at 80% coinsurance.",
        at: "2024-03-19T12:10:00Z"
      }
    ]
  },
  {
    id: "CLM-10002",
    member: {
      id: "MBR-502",
      name: "Jordan Patel",
      plan: "HMO Core"
    },
    provider: {
      name: "Downtown Imaging Center",
      npi: "1892736150"
    },
    status: "PENDING_INFO",
    submittedAt: "2024-03-17T09:15:00Z",
    lastUpdatedAt: "2024-03-18T08:20:00Z",
    financials: {
      billed: 890.0,
      allowed: 712.0,
      paid: 0.0,
      patientResponsibility: 0.0
    },
    notes: [
      {
        author: "Manual Review",
        body: "Awaiting clinical documentation from provider.",
        at: "2024-03-18T08:20:00Z"
      }
    ]
  },
  {
    id: "CLM-10003",
    member: {
      id: "MBR-503",
      name: "Casey Lee",
      plan: "EPO Silver"
    },
    provider: {
      name: "Northside Specialty Clinic",
      npi: "1063984520"
    },
    status: "MANUAL_REVIEW",
    submittedAt: "2024-03-16T11:05:00Z",
    lastUpdatedAt: "2024-03-19T09:00:00Z",
    financials: {
      billed: 1240.0,
      allowed: 0.0,
      paid: 0.0,
      patientResponsibility: 0.0
    },
    notes: [
      {
        author: "SIU",
        body: "High-cost injection flagged for investigative review.",
        at: "2024-03-19T09:00:00Z"
      }
    ]
  },
  {
    id: "CLM-10004",
    member: {
      id: "MBR-504",
      name: "Taylor Morgan",
      plan: "POS Bronze"
    },
    provider: {
      name: "Metro Urgent Care",
      npi: "1736489205"
    },
    status: "DENIED",
    submittedAt: "2024-03-12T14:40:00Z",
    lastUpdatedAt: "2024-03-14T16:05:00Z",
    financials: {
      billed: 210.0,
      allowed: 0.0,
      paid: 0.0,
      patientResponsibility: 210.0
    },
    notes: [
      {
        author: "Auto-Adjudication",
        body: "Non-covered service per plan document.",
        at: "2024-03-14T16:05:00Z"
      }
    ]
  }
];
