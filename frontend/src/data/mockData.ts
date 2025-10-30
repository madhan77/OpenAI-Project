export interface Task {
  id: string;
  title: string;
  owner: string;
  status: 'pending' | 'in_progress' | 'completed';
  dueDate?: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  summary: string;
  category: 'update' | 'milestone' | 'decision' | 'risk';
}

export interface Escalation {
  id: string;
  level: 'l1' | 'l2' | 'executive';
  status: 'open' | 'resolved';
  owner: string;
  openedAt: string;
  notes?: string;
}

export interface Issue {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium';
  status: 'open' | 'mitigated' | 'resolved';
  description: string;
  serviceImpact: string;
  openedAt: string;
  targetResolutionAt?: string;
  lastUpdatedAt: string;
  slaMinutes: number;
  tasks: Task[];
  timeline: TimelineEvent[];
  escalations: Escalation[];
}

export const mockIssues: Issue[] = [
  {
    id: 'INC-2404',
    title: 'Payment API latency spike',
    severity: 'critical',
    status: 'open',
    description: 'Regional payment API requests timing out for EMEA customers.',
    serviceImpact: 'Checkout failures for 32% of transactions in EMEA region.',
    openedAt: '2024-04-18T04:15:00Z',
    targetResolutionAt: '2024-04-18T10:15:00Z',
    lastUpdatedAt: '2024-04-18T07:55:00Z',
    slaMinutes: 360,
    tasks: [
      {
        id: 'TASK-1',
        title: 'Add synthetic monitoring to capture failure traces',
        owner: 'Alex Wong',
        status: 'in_progress'
      },
      {
        id: 'TASK-2',
        title: 'Coordinate with payment partner to validate upstream status',
        owner: 'Priya Patel',
        status: 'pending',
        dueDate: '2024-04-18T08:30:00Z'
      }
    ],
    timeline: [
      {
        id: 'TL-1',
        timestamp: '2024-04-18T04:15:00Z',
        summary: 'Automated alert triggered for latency breach in EMEA.',
        category: 'update'
      },
      {
        id: 'TL-2',
        timestamp: '2024-04-18T05:05:00Z',
        summary: 'Mitigation runbook executed to recycle stateless pods.',
        category: 'milestone'
      },
      {
        id: 'TL-3',
        timestamp: '2024-04-18T06:40:00Z',
        summary: 'Discovered elevated error rate from upstream PSP.',
        category: 'risk'
      }
    ],
    escalations: [
      {
        id: 'ESC-1',
        level: 'l2',
        status: 'open',
        owner: 'NOC Manager',
        openedAt: '2024-04-18T06:10:00Z',
        notes: 'Executive stakeholders notified; awaiting partner response.'
      }
    ]
  },
  {
    id: 'INC-2397',
    title: 'Customer service telephony outage',
    severity: 'high',
    status: 'mitigated',
    description: 'Contact center agents intermittently disconnected from telephony provider.',
    serviceImpact: 'Agents required to fall back to manual callback queue for 45 minutes.',
    openedAt: '2024-04-16T15:42:00Z',
    targetResolutionAt: '2024-04-16T18:30:00Z',
    lastUpdatedAt: '2024-04-16T19:10:00Z',
    slaMinutes: 240,
    tasks: [
      {
        id: 'TASK-3',
        title: 'Collect call detail records for impacted timeframe',
        owner: 'Jamie Rivera',
        status: 'completed'
      },
      {
        id: 'TASK-4',
        title: 'Draft customer-facing RCA outline',
        owner: 'Morgan Lee',
        status: 'in_progress'
      }
    ],
    timeline: [
      {
        id: 'TL-4',
        timestamp: '2024-04-16T15:42:00Z',
        summary: 'Carrier outage reported affecting 40% of inbound calls.',
        category: 'update'
      },
      {
        id: 'TL-5',
        timestamp: '2024-04-16T16:20:00Z',
        summary: 'Failover to backup carrier initiated for NA region.',
        category: 'milestone'
      },
      {
        id: 'TL-6',
        timestamp: '2024-04-16T17:05:00Z',
        summary: 'Carrier confirmed fiber cut; ETA for fix 18:30.',
        category: 'decision'
      }
    ],
    escalations: []
  }
];
