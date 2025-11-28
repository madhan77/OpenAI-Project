import { personas } from "./mock-data.js";

const heroTitle = document.getElementById("hero-title");
const heroSubtitle = document.getElementById("hero-subtitle");
const heroActions = document.getElementById("hero-actions");
const personaEyebrow = document.getElementById("persona-eyebrow");
const summaryGrid = document.getElementById("summary-cards");
const journeySteps = document.getElementById("journey-steps");
const personaSwitcher = document.getElementById("persona-switcher");
const timestamp = document.getElementById("timestamp");

const primaryEyebrow = document.getElementById("primary-eyebrow");
const primaryTitle = document.getElementById("primary-title");
const primaryContent = document.getElementById("primary-content");
const primaryCta = document.getElementById("primary-cta");

const secondaryEyebrow = document.getElementById("secondary-eyebrow");
const secondaryTitle = document.getElementById("secondary-title");
const secondaryContent = document.getElementById("secondary-content");

const calloutsList = document.getElementById("callouts");
const roadmapList = document.getElementById("roadmap");

let currentPersona = "b2b";

function formatTimestamp(date) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  }).format(date);
}

timestamp.textContent = `Updated ${formatTimestamp(new Date())}`;

function setActivePersonaButton() {
  const buttons = personaSwitcher.querySelectorAll(".persona-button");
  buttons.forEach((button) => {
    button.classList.toggle("active", button.dataset.persona === currentPersona);
  });
}

function renderHero(data) {
  personaEyebrow.textContent = data.eyebrow;
  heroTitle.textContent = data.heroTitle;
  heroSubtitle.textContent = data.heroSubtitle;
  heroActions.innerHTML = "";
  data.actions.forEach((action) => {
    const button = document.createElement("button");
    button.textContent = action.label;
    if (action.type === "primary") {
      button.style.background = "var(--accent)";
      button.style.color = "#032437";
    }
    heroActions.appendChild(button);
  });
}

function renderSummary(metrics) {
  summaryGrid.innerHTML = "";
  metrics.forEach((metric) => {
    const card = document.createElement("div");
    card.className = "summary-card";
    card.innerHTML = `
      <h3>${metric.label}</h3>
      <span class="value">${metric.value}</span>
      <span class="trend ${metric.trend.startsWith("-") ? "negative" : "positive"}">
        ${metric.trend}
      </span>
    `;
    summaryGrid.appendChild(card);
  });
}

function renderJourney(steps) {
  journeySteps.innerHTML = "";
  steps.forEach((step, index) => {
    const container = document.createElement("div");
    container.className = "journey-step";
    container.innerHTML = `
      <div class="step-icon">${index + 1}</div>
      <div class="step-content">
        <div class="step-status">${step.status}</div>
        <h4>${step.title}</h4>
        <p>${step.description}</p>
      </div>
    `;
    journeySteps.appendChild(container);
  });
}

function renderPrimaryPanel(data) {
  primaryEyebrow.textContent = data.eyebrow;
  primaryTitle.textContent = data.title;
  primaryCta.textContent = data.cta;
  primaryContent.innerHTML = "";

  const table = document.createElement("table");
  table.className = "table";
  const headerRow = document.createElement("tr");
  const headers =
    currentPersona === "b2b"
      ? ["Request", "Dept / Customer", "Amount / Stage", "Owner"]
      : ["Order", "Customer", "Stage", "Value"];
  headers.forEach((header) => {
    const th = document.createElement("th");
    th.textContent = header;
    headerRow.appendChild(th);
  });
  table.appendChild(headerRow);

  data.rows.forEach((row) => {
    const tr = document.createElement("tr");
    if (currentPersona === "b2b") {
      tr.innerHTML = `
        <td>${row.id}</td>
        <td>${row.dept}</td>
        <td>${row.amount}</td>
        <td>${row.submitter}</td>
      `;
    } else {
      tr.innerHTML = `
        <td>${row.id}</td>
        <td>${row.customer}</td>
        <td>${row.stage}</td>
        <td>${row.value}</td>
      `;
    }
    table.appendChild(tr);
  });
  primaryContent.appendChild(table);
}

function renderSecondaryPanel(data) {
  secondaryEyebrow.textContent = data.eyebrow;
  secondaryTitle.textContent = data.title;
  secondaryContent.innerHTML = "";

  const container = document.createElement("div");
  container.className = currentPersona === "b2b" ? "invoice-cards" : "order-cards";

  data.cards.forEach((card) => {
    const cardEl = document.createElement("div");
    cardEl.className = currentPersona === "b2b" ? "invoice-card" : "order-card";
    cardEl.innerHTML = `
      <h4>${card.id}</h4>
      <p><strong>${card.company ?? card.customer ?? ""}</strong></p>
      <p>${card.due}</p>
      <p>${card.amount}</p>
      <span class="badge ${badgeTone(card.status)}">${card.status}</span>
    `;
    container.appendChild(cardEl);
  });

  secondaryContent.appendChild(container);
}

function badgeTone(status) {
  const normalized = status.toLowerCase();
  if (normalized.includes("ready") || normalized.includes("live") || normalized.includes("auto")) {
    return "success";
  }
  if (normalized.includes("goal") || normalized.includes("due") || normalized.includes("pilot")) {
    return "warning";
  }
  return "danger";
}

function renderCallouts(callouts) {
  calloutsList.innerHTML = "";
  callouts.forEach((callout) => {
    const li = document.createElement("li");
    li.className = `callout ${callout.tone ?? ""}`.trim();
    li.innerHTML = `
      <strong>${callout.title}</strong>
      <span>${callout.body}</span>
    `;
    calloutsList.appendChild(li);
  });
}

function renderRoadmap(items) {
  roadmapList.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    roadmapList.appendChild(li);
  });
}

function renderPersona(personaKey) {
  currentPersona = personaKey;
  setActivePersonaButton();

  const data = personas[personaKey];
  renderHero(data);
  renderSummary(data.summaryMetrics);
  renderJourney(data.journeySteps);
  renderPrimaryPanel(data.primaryPanel);
  renderSecondaryPanel(data.secondaryPanel);
  renderCallouts(data.callouts);
  renderRoadmap(data.roadmap);
}

personaSwitcher.addEventListener("click", (event) => {
  if (event.target.matches(".persona-button")) {
    renderPersona(event.target.dataset.persona);
  }
});

renderPersona(currentPersona);
