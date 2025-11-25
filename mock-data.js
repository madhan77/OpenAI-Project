const baseTechnicians = [
  {
    id: 't1',
    name: 'Avery Chen',
    role: 'Field Engineer',
    region: 'Bay Area',
    skills: ['HVAC', 'Controls', 'Safety'],
    phone: '+1 (415) 555-0184'
  },
  {
    id: 't2',
    name: 'Jordan Smith',
    role: 'Technician',
    region: 'South Bay',
    skills: ['Electrical', 'Networking'],
    phone: '+1 (408) 555-4421'
  },
  {
    id: 't3',
    name: 'Priya Patel',
    role: 'Consultant',
    region: 'Peninsula',
    skills: ['Audit', 'Compliance', 'Safety'],
    phone: '+1 (650) 555-7720'
  }
];

const baseAppointments = [
  {
    id: 'WO-1042',
    title: 'Quarterly HVAC tune-up',
    status: 'On Site',
    sla: '10:00-12:00',
    start: '2025-11-11T10:00:00',
    eta: '10:15',
    customer: 'Northwind Manufacturing',
    site: 'San Jose Plant 3',
    address: '3421 Meridian Ave, San Jose, CA',
    technician: 't1',
    contact: 'Maria Lopez · Facilities',
    tasks: [
      { label: 'Lockout-tagout and safety brief', status: 'done', required: true },
      { label: 'Inspect air filters and belts', status: 'done', required: true },
      { label: 'Calibrate thermostats and sensors', status: 'in-progress', required: true },
      { label: 'Capture photos of coil condition', status: 'pending', required: false },
      { label: 'Customer sign-off', status: 'pending', required: true }
    ],
    materials: [
      { item: 'MERV-13 filters', qty: 4 },
      { item: 'Drive belt A42', qty: 2 },
      { item: 'Cleaning solvent', qty: 1 }
    ],
    timeline: [
      { time: '09:35', label: 'Departed warehouse', type: 'info' },
      { time: '10:05', label: 'Arrived on site', type: 'success' },
      { time: '10:10', label: 'Safety checklist completed', type: 'success' },
      { time: '10:22', label: 'Found sensor drift on AHU-3', type: 'warning' }
    ],
    notes: [
      'Asset AHU-3 shows minor vibration—monitor next visit.',
      'Customer prefers work to pause during 12-1pm lunch window.'
    ],
    customerHandoff: {
      contact: 'Maria Lopez',
      signature: 'Pending',
      survey: 'Not sent'
    }
  },
  {
    id: 'WO-1043',
    title: 'Network cabinet cleanup',
    status: 'Scheduled',
    sla: '13:00-15:00',
    start: '2025-11-11T13:00:00',
    eta: '12:50',
    customer: 'Contoso Retail',
    site: 'Store #218',
    address: '1800 Junipero Serra Blvd, Daly City, CA',
    technician: 't2',
    contact: 'Andre Watts · Store Manager',
    tasks: [
      { label: 'Verify network diagram matches rack', status: 'pending', required: true },
      { label: 'Label patch panels and switches', status: 'pending', required: true },
      { label: 'Replace unmanaged switch with PoE', status: 'pending', required: true },
      { label: 'Run validation tests', status: 'pending', required: true },
      { label: 'Document changes and photos', status: 'pending', required: true }
    ],
    materials: [
      { item: 'Cat6 patch cables', qty: 12 },
      { item: '24-port PoE switch', qty: 1 }
    ],
    timeline: [
      { time: 'Now', label: 'Waiting to dispatch', type: 'info' }
    ],
    notes: ['Coordinate downtime with store lead at 1:15pm.'],
    customerHandoff: {
      contact: 'Andre Watts',
      signature: 'Not started',
      survey: 'Scheduled at completion'
    }
  },
  {
    id: 'WO-1044',
    title: 'Safety audit and compliance review',
    status: 'En Route',
    sla: '09:00-11:00',
    start: '2025-11-11T09:00:00',
    eta: '09:40',
    customer: 'Fabrikam Labs',
    site: 'R&D Campus',
    address: '4120 Page Mill Rd, Palo Alto, CA',
    technician: 't3',
    contact: 'Gwen Lee · EHS',
    tasks: [
      { label: 'Review SDS and site induction', status: 'done', required: true },
      { label: 'Validate PPE compliance', status: 'in-progress', required: true },
      { label: 'Sample incident drills', status: 'pending', required: false },
      { label: 'Sign digital audit report', status: 'pending', required: true }
    ],
    materials: [
      { item: 'Digital inspection checklist', qty: 1 }
    ],
    timeline: [
      { time: '08:55', label: 'Accepted by coordinator', type: 'info' },
      { time: '09:05', label: 'En route · light traffic', type: 'info' }
    ],
    notes: ['Site requires government ID at gate. Allow 10 minutes.'],
    customerHandoff: {
      contact: 'Gwen Lee',
      signature: 'Pending',
      survey: 'Queued'
    }
  },
  {
    id: 'WO-1045',
    title: 'Emergency power diagnostics',
    status: 'Completed',
    sla: 'Yesterday',
    start: '2025-11-10T16:00:00',
    eta: 'Completed',
    customer: 'Global Data Center',
    site: 'Santa Clara DC-2',
    address: '2555 Augustine Dr, Santa Clara, CA',
    technician: 't1',
    contact: 'Ethan Brooks · Ops',
    tasks: [
      { label: 'Run UPS self-test', status: 'done', required: true },
      { label: 'Inspect ATS logs', status: 'done', required: true },
      { label: 'Thermal scan of breakers', status: 'done', required: true },
      { label: 'Document remediation plan', status: 'done', required: true }
    ],
    materials: [
      { item: 'Thermal camera', qty: 1 },
      { item: 'UPS firmware 4.3', qty: 1 }
    ],
    timeline: [
      { time: '16:05', label: 'Arrived on site', type: 'success' },
      { time: '16:18', label: 'UPS self-test passed', type: 'success' },
      { time: '17:20', label: 'Thermal scan clear', type: 'success' },
      { time: '17:45', label: 'Customer sign-off captured', type: 'success' }
    ],
    notes: ['Recommend battery module swap within 30 days.'],
    customerHandoff: {
      contact: 'Ethan Brooks',
      signature: 'Captured',
      survey: 'Completed'
    }
  }
];

function expandTechnicians(count = 50) {
  const techs = [];
  const roles = ['Field Engineer', 'Technician', 'Consultant', 'Senior Tech', 'Coordinator'];
  const regions = ['Bay Area', 'South Bay', 'Peninsula', 'North Bay', 'Central Valley', 'Sacramento'];
  for (let i = 0; i < count; i++) {
    const template = baseTechnicians[i % baseTechnicians.length];
    techs.push({
      ...template,
      id: `t${i + 1}`,
      name: `${template.name.split(' ')[0]} ${String.fromCharCode(65 + (i % 26))}${i}`,
      region: regions[i % regions.length],
      role: roles[i % roles.length],
      phone: `+1 (555) 01${(i % 90 + 10).toString().padStart(2, '0')}-${(1000 + i).toString().slice(-4)}`
    });
  }
  return techs;
}

function expandAppointments(count = 2000, technicians) {
  const result = [];
  for (let i = 0; i < count; i++) {
    const template = baseAppointments[i % baseAppointments.length];
    const tech = technicians[i % technicians.length];
    const day = (i % 28) + 1;
    const id = `WO-${2000 + i}`;
    result.push({
      ...template,
      id,
      title: `${template.title} #${i + 1}`,
      technician: tech.id,
      status: ['On Site', 'En Route', 'Scheduled', 'Completed', 'Deferred'][i % 5],
      customer: `${template.customer} ${String.fromCharCode(65 + (i % 26))}`,
      site: `${template.site} Bay ${i % 7}`,
      start: `2025-11-${String(day).padStart(2, '0')}T10:00:00`,
      eta: template.eta,
      tasks: template.tasks.map((task, idx) => ({
        ...task,
        status: ['done', 'in-progress', 'pending'][((i + idx) % 3)]
      })),
      materials: template.materials,
      timeline: template.timeline,
      notes: template.notes,
      customerHandoff: template.customerHandoff
    });
  }
  return result;
}

export const technicians = expandTechnicians(60);
export const appointments = expandAppointments(2000, technicians);
