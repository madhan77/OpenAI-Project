import { initializeApp, getApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

import { loadFirebaseConfig } from "./firebase-config.js";
import { mockClaims } from "./mock-data.js";

let firebaseAuth = null;
let selectedClaimId = null;
let listenersAttached = false;
let isDemoSession = false;
let googleProvider = null;

const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const userInfo = document.getElementById("user-info");
const userEmail = document.getElementById("user-email");
const signOutButton = document.getElementById("sign-out");
const demoLoginButton = document.getElementById("demo-login");
const googleLoginButton = document.getElementById("google-login");

const dashboard = document.getElementById("dashboard");
const authGate = document.getElementById("auth-gate");
const claimsTable = document.getElementById("claims-table");
const claimDetails = document.getElementById("claim-details");
const summaryGrid = document.getElementById("summary-grid");
const statusFilter = document.getElementById("status-filter");
const searchInput = document.getElementById("search-input");

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
  renderClaimDetails(nextSelected || filtered[0] || null);
}

function resetDashboard() {
  summaryGrid.innerHTML = "";
  claimsTable.innerHTML = "";
  claimDetails.innerHTML = "<p>Sign in to review claim details.</p>";
  selectedClaimId = null;
}

function enterDemoMode() {
  isDemoSession = true;
  firebaseAuth = null;
  userEmail.textContent = "demo.reviewer@openai.health (Demo)";
  loginForm.classList.add("hidden");
  userInfo.classList.remove("hidden");
  authGate.classList.add("hidden");
  dashboard.classList.remove("hidden");
  statusFilter.value = "all";
  searchInput.value = "";
  filterClaims();
}

function exitDemoMode() {
  isDemoSession = false;
  loginForm.classList.remove("hidden");
  userInfo.classList.add("hidden");
  authGate.classList.remove("hidden");
  dashboard.classList.add("hidden");
  resetDashboard();
}

function showConfigError(message) {
  authGate.innerHTML = `
    <div class="card">
      <h2>Configuration Required</h2>
      <p>${message}</p>
      <p>
        Provide Firebase credentials via <code>portal/firebase-config.json</code> or
        <code>portal/firebase-config.local.js</code> and reload the page.
      </p>
      <p>You can also select <strong>Use Demo Mode</strong> to explore the mock workflow without signing in.</p>
    </div>
  `;
  authGate.classList.remove("hidden");
  exitDemoMode();
}

function attachEventListeners() {
  if (listenersAttached) {
    return;
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!firebaseAuth) {
      alert("Firebase has not been initialised yet. Check configuration.");
      return;
    }

    try {
      await signInWithEmailAndPassword(firebaseAuth, email, password);
      loginForm.reset();
    } catch (error) {
      alert(error.message);
    }
  });

  signOutButton.addEventListener("click", () => {
    if (isDemoSession) {
      exitDemoMode();
      return;
    }

    if (!firebaseAuth) {
      exitDemoMode();
      return;
    }
    signOut(firebaseAuth).catch((error) => alert(error.message));
  });

  statusFilter.addEventListener("change", filterClaims);
  searchInput.addEventListener("input", filterClaims);

  if (demoLoginButton) {
    demoLoginButton.addEventListener("click", () => {
      enterDemoMode();
    });
  }

  if (googleLoginButton) {
    googleLoginButton.addEventListener("click", async () => {
      if (!firebaseAuth || !googleProvider) {
        alert("Firebase has not been initialised yet. Check configuration.");
        return;
      }

      try {
        await signInWithPopup(firebaseAuth, googleProvider);
      } catch (error) {
        if (error?.code === "auth/popup-closed-by-user") {
          return;
        }
        alert(error.message || "Unable to complete Google sign-in.");
      }
    });
  }

  listenersAttached = true;
}

function handleAuthState(user) {
  if (isDemoSession) {
    return;
  }

  if (user) {
    userEmail.textContent = user.email || user.uid;
    loginForm.classList.add("hidden");
    userInfo.classList.remove("hidden");
    authGate.classList.add("hidden");
    dashboard.classList.remove("hidden");
    selectedClaimId = null;
    statusFilter.value = "all";
    searchInput.value = "";
    filterClaims();
  } else {
    loginForm.classList.remove("hidden");
    userInfo.classList.add("hidden");
    authGate.classList.remove("hidden");
    dashboard.classList.add("hidden");
    resetDashboard();
  }
}

function initialisePortal(firebaseConfig) {
  let firebaseApp;
  try {
    firebaseApp = initializeApp(firebaseConfig);
  } catch (error) {
    if (error?.code === "app/duplicate-app") {
      firebaseApp = getApp();
    } else {
      console.error("Failed to initialise Firebase:", error);
      showConfigError("Unable to initialise Firebase. Check console logs for details.");
      return;
    }
  }

  firebaseAuth = getAuth(firebaseApp);
  googleProvider = new GoogleAuthProvider();
  googleProvider.setCustomParameters({ prompt: "select_account" });
  attachEventListeners();
  onAuthStateChanged(firebaseAuth, handleAuthState);
}

async function bootstrap() {
  try {
    const firebaseConfig = await loadFirebaseConfig();

    if (!firebaseConfig) {
      showConfigError(
        "Firebase configuration is missing. Update the portal configuration and try again."
      );
      return;
    }

    initialisePortal(firebaseConfig);
  } catch (error) {
    console.error("Error loading Firebase configuration:", error);
    showConfigError("Unable to load Firebase configuration. Check console logs for details.");
  }
}

attachEventListeners();
resetDashboard();
bootstrap();
