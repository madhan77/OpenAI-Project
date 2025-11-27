import { appointments, technicians } from './mock-data.js';

// --- Leaderboard Logic ---
const leaderboardContainer = document.getElementById('leaderboard-list');

function calculateLeaderboard(sourceAppts = appointments) {
  // Points: completed + active give scoring; badges scaled off completed
  const pointsPerCompleted = 100;
  const pointsPerActive = 40;
  const leaderboard = technicians.map((tech) => {
    const techAppts = sourceAppts.filter((appt) => appt.technician === tech.id);
    const completed = techAppts.filter((appt) => appt.status === 'Completed');
    const active = techAppts.filter((appt) => appt.status === 'On Site' || appt.status === 'En Route');
    const points = completed.length * pointsPerCompleted + active.length * pointsPerActive;
    const badges = Math.max(1, Math.floor(completed.length / 2));
    const progress = Math.min(100, Math.round(((completed.length % 2) / 2) * 100));
    return {
      id: tech.id,
      name: tech.name,
      region: tech.region,
      points,
      badges,
      progress
    };
  });
  // Sort by points descending
  leaderboard.sort((a, b) => b.points - a.points);
  return leaderboard.slice(0, 10);
}

function renderLeaderboard() {
  const leaderboard = calculateLeaderboard(state.filtered || appointments);
  leaderboardContainer.innerHTML = leaderboard
    .map(
      (user, idx) => `
        <div class="leaderboard-row">
          <span class="rank">${idx + 1}</span>
          <span class="name">${user.name} <span class="region">(${user.region})</span></span>
          <span class="points">${user.points} pts</span>
          <span class="badges" title="${user.badges} completed with feedback">🏅 × ${user.badges}</span>
        </div>
        <div class="leaderboard-progress">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:${user.progress}%;"></div>
          </div>
          <span class="progress-label">${user.progress}% toward next badge</span>
        </div>
      `
    )
    .join('');
}
// --- User Profile Logic ---
const profileBtn = document.getElementById('profile-btn');
const profileModal = document.getElementById('profile-modal');
const closeProfileModal = document.getElementById('close-profile-modal');
const profileForm = document.getElementById('profile-form');
const profileName = document.getElementById('profile-name');
const profileEmail = document.getElementById('profile-email');
const profileAvatar = document.getElementById('profile-avatar');
const avatarPreview = document.getElementById('avatar-preview');
const hasProfileUI =
  profileBtn &&
  profileModal &&
  closeProfileModal &&
  profileForm &&
  profileName &&
  profileEmail &&
  profileAvatar &&
  avatarPreview;

function loadProfile() {
  const data = JSON.parse(localStorage.getItem('userProfile')) || {
    name: 'Technician User',
    email: 'user@example.com',
    avatar: ''
  };
  profileName.value = data.name;
  profileEmail.value = data.email;
  profileAvatar.value = data.avatar;
  avatarPreview.src = data.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(data.name);
}

function saveProfile(e) {
  e.preventDefault();
  const data = {
    name: profileName.value,
    email: profileEmail.value,
    avatar: profileAvatar.value
  };
  localStorage.setItem('userProfile', JSON.stringify(data));
  avatarPreview.src = data.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(data.name);
  closeProfile();
}

function openProfile() {
  loadProfile();
  profileModal.style.display = 'flex';
}

function closeProfile() {
  profileModal.style.display = 'none';
}

if (hasProfileUI) {
  profileBtn.addEventListener('click', openProfile);
  closeProfileModal.addEventListener('click', closeProfile);
  profileForm.addEventListener('submit', saveProfile);
  profileAvatar.addEventListener('input', () => {
    avatarPreview.src = profileAvatar.value || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(profileName.value);
  });
  profileName.addEventListener('input', () => {
    if (!profileAvatar.value) {
      avatarPreview.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(profileName.value);
    }
  });
  window.addEventListener('click', (e) => {
    if (e.target === profileModal) closeProfile();
  });
} else {
  console.warn('Profile UI elements missing; skipping profile modal setup.');
}

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
const gamificationBar = document.getElementById('gamification-bar');
const slaIndicatorText = {
  ok: 'On track',
  risk: 'At risk',
  breach: 'Breached'
};

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
  renderGamificationBar();
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
    { label: 'Team Utilization', value: `${utilization || 0}%` },
    { label: 'SLA Breaches', value: state.filtered.filter((appt) => appt.slaBreached).length || 0 }
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

function renderGamificationBar() {
  if (!gamificationBar) return;
  const filteredCompleted = state.filtered.filter((appt) => appt.status === 'Completed').length;
  const filteredActive = state.filtered.filter((appt) => appt.status === 'On Site' || appt.status === 'En Route').length;
  const feedbackWins = state.filtered.filter((appt) => appt.customerHandoff?.survey === 'Completed').length;
  const xp = filteredCompleted * 120 + filteredActive * 40 + state.filtered.length * 10;
  const cards = [
    { label: 'Squad XP', value: `${xp} XP`, detail: `${filteredCompleted} completed · ${filteredActive} active`, icon: '🎯' },
    { label: 'Streak', value: `${Math.max(1, filteredCompleted)} days`, detail: 'Keep on-time arrivals to grow the streak', icon: '⚡' },
    { label: 'Customer Kudos', value: `${feedbackWins} badges`, detail: 'Feedback wins unlocked', icon: '🏆' }
  ];

  gamificationBar.innerHTML = cards
    .map(
      (card) => `
        <div class="meta-pill">
          <div class="pill-icon">${card.icon}</div>
          <div>
            <p class="pill-label">${card.label}</p>
            <p class="pill-value">${card.value}</p>
            <p class="pill-detail">${card.detail}</p>
          </div>
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
      const isActive = appt.id === state.selectedId;
      const cardClass = `card appointment-card ${isActive ? 'active' : ''}`;
      const completedTasks = appt.tasks.filter((task) => task.status === 'done').length;
      const progress = Math.round((completedTasks / appt.tasks.length) * 100);
      const slaChip = appt.slaBreached ? '<span class="chip warning">SLA breach</span>' : '';

      return `
        <article class="${cardClass}" data-id="${appt.id}">
          <div class="card-top">
            <div class="id-line">
              <p class="eyebrow">${appt.id}</p>
            </div>
            <div class="chip-stack">
              ${slaChip}
              <span class="${statusChipClass[appt.status] || 'chip'}">${appt.status}</span>
            </div>
          </div>
          <div class="card-body compact">
            <h3 class="card-title">${appt.title}</h3>
            <p class="muted small">${appt.customer} · ${appt.site}</p>
            <p class="muted smaller">${appt.routingEta || appt.eta} · ${tech?.name || 'Unassigned'}</p>
            <div class="meter small">
              <div class="meter-fill" style="width:${progress}%"></div>
            </div>
            <p class="microcopy">${progress}% tasks complete</p>
          </div>
        </article>
      `;
    })
    .join('');

  [...listContainer.querySelectorAll('[data-id]')].forEach((card) => {
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
  const compliancePass = appointment.complianceChecks?.filter((c) => c.status === 'pass').length || 0;
  const complianceTotal = appointment.complianceChecks?.length || 0;

  detailContainer.innerHTML = `
    <div class="detail-header">
      <div>
        <p class="eyebrow">${appointment.id}</p>
        <h3 class="detail-title">${appointment.title}</h3>
        <p class="muted">${appointment.customer} · ${appointment.site}</p>
      </div>
      <div class="detail-badges">
        <span class="${statusChipClass[appointment.status] || 'chip'}">${appointment.status}</span>
        <div class="pill">Progress ${progress}%</div>
        <div class="pill ${appointment.slaBreached ? 'pill-risk' : ''}">SLA ${appointment.slaBreached ? 'Breached' : 'On Track'}</div>
      </div>
    </div>

    <section class="detail-section">
      <div class="section-header">
        <h4>Assignment</h4>
      </div>
      <div class="assignment-grid">
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
          <p>${appointment.routingEta || appointment.eta}</p>
        </div>
        <div>
          <p class="microcopy">Contact</p>
          <p>${appointment.contact}</p>
        </div>
        <div>
          <p class="microcopy">SLA Status</p>
          <p>${appointment.slaBreached ? 'Breached' : 'On track'}</p>
        </div>
      </div>
    </section>

    <section class="detail-section">
      <div class="section-header">
        <h4>Checklist</h4>
        <span class="pill">+${completedTasks} / ${appointment.tasks.length} steps</span>
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
        <h4>Compliance Checks</h4>
        <span class="pill">${compliancePass}/${complianceTotal} passed</span>
      </div>
      <ul class="checks">
        ${(appointment.complianceChecks || [])
          .map(
            (check) => `
              <li class="check ${check.status}">
                <span class="check-dot"></span>
                <span>${check.label}</span>
              </li>
            `
          )
          .join('')}
      </ul>
    </section>

    <section class="detail-section">
      <div class="section-header">
        <h4>Parts Inventory</h4>
      </div>
      <div class="inventory">
        <div class="inventory-row inventory-head">
          <span>Item</span><span>On Hand</span><span>Reserved</span>
        </div>
        ${(appointment.partsInventory || [])
          .map(
            (item) => `
              <div class="inventory-row">
                <span>${item.item}</span>
                <span>${item.onHand}</span>
                <span>${item.reserved}</span>
              </div>
            `
          )
          .join('')}
      </div>
    </section>

    <section class="detail-section">
      <div class="section-header">
        <h4>Coordinator Notes</h4>
      </div>
      <ul class="notes">
        ${(appointment.coordinatorNotes || []).map((note) => `<li>${note}</li>`).join('')}
      </ul>
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
applyFilters();
renderLeaderboard();
renderGamificationBar();
