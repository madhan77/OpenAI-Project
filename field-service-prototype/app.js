import { appointments, technicians } from './mock-data.js';

const statusChipClass = {
  'Scheduled': 'chip info',
  'En Route': 'chip info',
  'On Site': 'chip success',
  'Completed': 'chip neutral',
  'Deferred': 'chip warning'
};

const statusOrder = ['On Site', 'En Route', 'Scheduled', 'Completed', 'Deferred'];

const state = {
  filtered: appointments,
  selectedId: appointments[0].id
};

const statusFilter = document.getElementById('status-filter');
const technicianFilter = document.getElementById('technician-filter');
const searchInput = document.getElementById('search-input');
const listContainer = document.getElementById('appointment-list');
const detailContainer = document.getElementById('detail');
const snapshotContainer = document.getElementById('snapshot-grid');

function initFilters() {
  technicians.forEach((tech) => {
    const option = document.createElement('option');
    option.value = tech.id;
    option.textContent = `${tech.name} · ${tech.region}`;
    technicianFilter.appendChild(option);
  });

  [statusFilter, technicianFilter].forEach((control) => {
    control.addEventListener('change', applyFilters);
  });
  searchInput.addEventListener('input', applyFilters);
}

function applyFilters() {
  const status = statusFilter.value;
  const technician = technicianFilter.value;
  const search = searchInput.value.trim().toLowerCase();

  state.filtered = appointments.filter((appt) => {
    const matchesStatus = status === 'all' || appt.status === status;
    const matchesTech = technician === 'all' || appt.technician === technician;
    const matchesSearch =
      !search ||
      appt.id.toLowerCase().includes(search) ||
      appt.customer.toLowerCase().includes(search) ||
      appt.site.toLowerCase().includes(search);
    return matchesStatus && matchesTech && matchesSearch;
  });

  if (!state.filtered.some((appt) => appt.id === state.selectedId)) {
    state.selectedId = state.filtered[0]?.id;
  }

  renderList();
  renderSnapshot();
  renderDetail();
}

function renderSnapshot() {
  const counts = state.filtered.reduce(
    (acc, appt) => {
      acc[appt.status] = (acc[appt.status] || 0) + 1;
      return acc;
    },
    {}
  );

  const utilization = Math.round((state.filtered.filter((appt) => appt.status !== 'Scheduled').length / state.filtered.length || 0) * 100);

  const cards = [
    { label: 'In Progress', value: (counts['On Site'] || 0) + (counts['En Route'] || 0) },
    { label: 'Scheduled Today', value: counts['Scheduled'] || 0 },
    { label: 'Completed', value: counts['Completed'] || 0 },
    { label: 'Team Utilization', value: `${utilization || 0}%` }
  ];

  snapshotContainer.innerHTML = cards
    .map(
      (card) => `
        <div class="stat-card">
          <p class="microcopy">${card.label}</p>
          <div class="stat-value">${card.value}</div>
        </div>
      `
    )
    .join('');
}

function renderList() {
  const sorted = [...state.filtered].sort((a, b) => statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status));

  listContainer.innerHTML = sorted
    .map((appt) => {
      const tech = technicians.find((t) => t.id === appt.technician);
      const active = appt.id === state.selectedId ? 'card active' : 'card';
      const completedTasks = appt.tasks.filter((task) => task.status === 'done').length;
      const progress = Math.round((completedTasks / appt.tasks.length) * 100);

      return `
        <article class="${active}" data-id="${appt.id}">
          <div class="card-top">
            <div>
              <p class="eyebrow">${appt.id}</p>
              <h3>${appt.title}</h3>
              <p class="microcopy">${appt.customer} · ${appt.site}</p>
            </div>
            <span class="${statusChipClass[appt.status] || 'chip'}">${appt.status}</span>
          </div>
          <div class="card-body">
            <div class="meta">
              <div>
                <p class="microcopy">Window</p>
                <p>${appt.sla}</p>
              </div>
              <div>
                <p class="microcopy">ETA</p>
                <p>${appt.eta}</p>
              </div>
              <div>
                <p class="microcopy">Technician</p>
                <p>${tech?.name || 'Unassigned'}</p>
              </div>
            </div>
            <div class="progress">
              <div class="progress-bar" style="width:${progress}%"></div>
            </div>
          </div>
        </article>
      `;
    })
    .join('');

  [...listContainer.querySelectorAll('.card')].forEach((card) => {
    card.addEventListener('click', () => {
      state.selectedId = card.dataset.id;
      renderList();
      renderDetail();
    });
  });
}

function renderDetail() {
  const appointment = state.filtered.find((appt) => appt.id === state.selectedId) || state.filtered[0];
  if (!appointment) {
    detailContainer.innerHTML = '<p class="microcopy">No appointments match the filters.</p>';
    return;
  }

  const tech = technicians.find((t) => t.id === appointment.technician);
  const completedTasks = appointment.tasks.filter((task) => task.status === 'done').length;
  const progress = Math.round((completedTasks / appointment.tasks.length) * 100);

  detailContainer.innerHTML = `
    <div class="detail-header">
      <div>
        <p class="eyebrow">${appointment.id}</p>
        <h3>${appointment.title}</h3>
        <p class="microcopy">${appointment.customer} · ${appointment.site}</p>
      </div>
      <div class="detail-meta">
        <span class="${statusChipClass[appointment.status] || 'chip'}">${appointment.status}</span>
        <div>
          <p class="microcopy">Technician</p>
          <p>${tech?.name} · ${tech?.role}</p>
          <p class="microcopy">${tech?.phone}</p>
        </div>
        <div>
          <p class="microcopy">Window</p>
          <p>${appointment.sla}</p>
        </div>
        <div>
          <p class="microcopy">ETA</p>
          <p>${appointment.eta}</p>
        </div>
      </div>
    </div>

    <section class="detail-section">
      <div class="section-header">
        <h4>Checklist</h4>
        <span class="pill">${progress}% complete</span>
      </div>
      <ul class="tasks">
        ${appointment.tasks
          .map(
            (task) => `
              <li class="task ${task.status}">
                <div class="task-main">
                  <span class="task-status">${iconForStatus(task.status)}</span>
                  <span>${task.label}${task.required ? ' · Required' : ''}</span>
                </div>
              </li>
            `
          )
          .join('')}
      </ul>
    </section>

    <section class="detail-section two-col">
      <div>
        <div class="section-header">
          <h4>Materials & Parts</h4>
        </div>
        <ul class="chips">
          ${appointment.materials.map((mat) => `<li class="chip neutral">${mat.qty} × ${mat.item}</li>`).join('')}
        </ul>
      </div>
      <div>
        <div class="section-header">
          <h4>Customer Handoff</h4>
        </div>
        <div class="handoff">
          <p><strong>Contact:</strong> ${appointment.customerHandoff.contact}</p>
          <p><strong>Signature:</strong> ${appointment.customerHandoff.signature}</p>
          <p><strong>Survey:</strong> ${appointment.customerHandoff.survey}</p>
        </div>
      </div>
    </section>

    <section class="detail-section">
      <div class="section-header">
        <h4>Timeline</h4>
      </div>
      <ul class="timeline">
        ${appointment.timeline
          .map(
            (entry) => `
              <li>
                <span class="time">${entry.time}</span>
                <span class="dot ${entry.type}"></span>
                <span>${entry.label}</span>
              </li>
            `
          )
          .join('')}
      </ul>
    </section>

    <section class="detail-section">
      <div class="section-header">
        <h4>Notes</h4>
      </div>
      <ul class="notes">
        ${appointment.notes.map((note) => `<li>${note}</li>`).join('')}
      </ul>
    </section>
  `;
}

function iconForStatus(status) {
  if (status === 'done') return '✔';
  if (status === 'in-progress') return '➜';
  return '○';
}

initFilters();
renderSnapshot();
renderList();
renderDetail();
