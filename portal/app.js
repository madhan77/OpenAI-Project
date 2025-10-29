import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

import { mockClaims } from "./mock-data.js";

const firebaseConfig = window.FIREBASE_CONFIG;
if (!firebaseConfig) {
  console.error("Missing Firebase configuration. Provide firebase-config.js.");
}

const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);

const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const userInfo = document.getElementById("user-info");
const userEmail = document.getElementById("user-email");
const signOutButton = document.getElementById("sign-out");

const dashboard = document.getElementById("dashboard");
const authGate = document.getElementById("auth-gate");
const claimsTable = document.getElementById("claims-table");
const claimDetails = document.getElementById("claim-details");
const summaryGrid = document.getElementById("summary-grid");
const statusFilter = document.getElementById("status-filter");
const searchInput = document.getElementById("search-input");

let selectedClaimId = null;

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD"
  }).format(amount);
}

function formatDate(value) {
  return new Date(value).toLocaleString();
}

function renderSummary(claims) {
  const counts = claims.reduce(
    (acc, claim) => {
      acc.total += 1;
      acc[claim.status] = (acc[claim.status] || 0) + 1;
      acc.billed += claim.financials.billed;
      acc.paid += claim.financials.paid;
      acc.patientResponsibility += claim.financials.patientResponsibility;
      return acc;
    },
    {
      total: 0,
      APPROVED: 0,
      DENIED: 0,
      PENDING_INFO: 0,
      MANUAL_REVIEW: 0,
      billed: 0,
      paid: 0,
      patientResponsibility: 0
    }
  );

  summaryGrid.innerHTML = "";
  const summaryItems = [
    { label: "Total Claims", value: counts.total },
    { label: "Approved", value: counts.APPROVED },
    { label: "Denied", value: counts.DENIED },
    { label: "Pending Info", value: counts.PENDING_INFO },
    { label: "Manual Review", value: counts.MANUAL_REVIEW },
    { label: "Billed", value: formatCurrency(counts.billed) },
    { label: "Paid", value: formatCurrency(counts.paid) },
    {
      label: "Member Responsibility",
      value: formatCurrency(counts.patientResponsibility)
    }
  ];

  summaryItems.forEach((item) => {
    const summaryCard = document.createElement("div");
    summaryCard.className = "summary-card";
    summaryCard.innerHTML = `
      <span class="summary-label">${item.label}</span>
      <span class="summary-value">${item.value}</span>
    `;
    summaryGrid.appendChild(summaryCard);
  });
}

function renderClaims(claims) {
  claimsTable.innerHTML = "";
  claims.forEach((claim) => {
    const row = document.createElement("tr");
    row.dataset.claimId = claim.id;
    row.className = selectedClaimId === claim.id ? "selected" : "";
    row.innerHTML = `
      <td>${claim.id}</td>
      <td>${claim.member.name}</td>
      <td>${claim.provider.name}</td>
      <td><span class="badge status-${claim.status.toLowerCase()}">${
        claim.status.replace("_", " ")
      }</span></td>
      <td>${formatDate(claim.lastUpdatedAt)}</td>
    `;
    row.addEventListener("click", () => {
      selectedClaimId = claim.id;
      renderClaims(claims);
      renderClaimDetails(claim);
    });
    claimsTable.appendChild(row);
  });
}

function renderClaimDetails(claim) {
  if (!claim) {
    claimDetails.innerHTML = "<p>Select a claim to review details.</p>";
    return;
  }

  const notesList = claim.notes
    .map(
      (note) => `
        <li>
          <p class="note-body">${note.body}</p>
          <span class="note-meta">${note.author} · ${formatDate(note.at)}</span>
        </li>
      `
    )
    .join("");

  claimDetails.innerHTML = `
    <div class="detail-grid">
      <div>
        <h3>Member</h3>
        <p><strong>${claim.member.name}</strong></p>
        <p>ID: ${claim.member.id}</p>
        <p>Plan: ${claim.member.plan}</p>
      </div>
      <div>
        <h3>Provider</h3>
        <p><strong>${claim.provider.name}</strong></p>
        <p>NPI: ${claim.provider.npi}</p>
      </div>
      <div>
        <h3>Financials</h3>
        <p>Billed: ${formatCurrency(claim.financials.billed)}</p>
        <p>Allowed: ${formatCurrency(claim.financials.allowed)}</p>
        <p>Paid: ${formatCurrency(claim.financials.paid)}</p>
        <p>Member Responsibility: ${formatCurrency(
          claim.financials.patientResponsibility
        )}</p>
      </div>
    </div>
    <div class="notes">
      <h3>Notes</h3>
      <ul>${notesList}</ul>
    </div>
  `;
}

function filterClaims() {
  const statusValue = statusFilter.value;
  const query = searchInput.value.trim().toLowerCase();

  const filtered = mockClaims.filter((claim) => {
    const matchesStatus = statusValue === "all" || claim.status === statusValue;
    const matchesQuery =
      !query ||
      claim.id.toLowerCase().includes(query) ||
      claim.member.name.toLowerCase().includes(query);
    return matchesStatus && matchesQuery;
  });

  renderSummary(filtered);
  renderClaims(filtered);

  const nextSelected = filtered.find((claim) => claim.id === selectedClaimId);
  renderClaimDetails(nextSelected || filtered[0]);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = emailInput.value.trim();
  const password = passwordInput.value;
  try {
    await signInWithEmailAndPassword(auth, email, password);
    loginForm.reset();
  } catch (error) {
    alert(error.message);
  }
});

signOutButton.addEventListener("click", () => {
  signOut(auth).catch((error) => alert(error.message));
});

statusFilter.addEventListener("change", filterClaims);
searchInput.addEventListener("input", filterClaims);

onAuthStateChanged(auth, (user) => {
  if (user) {
    userEmail.textContent = user.email;
    loginForm.classList.add("hidden");
    userInfo.classList.remove("hidden");
    dashboard.classList.remove("hidden");
    authGate.classList.add("hidden");
    selectedClaimId = mockClaims[0]?.id ?? null;
    filterClaims();
  } else {
    loginForm.classList.remove("hidden");
    userInfo.classList.add("hidden");
    dashboard.classList.add("hidden");
    authGate.classList.remove("hidden");
    claimsTable.innerHTML = "";
    claimDetails.innerHTML = "";
    summaryGrid.innerHTML = "";
  }
});

renderClaimDetails(null);
