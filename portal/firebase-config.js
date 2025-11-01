const CONFIG_JSON_PATH = "firebase-config.json";

const ENV_KEY_MAP = {
  VITE_FIREBASE_API_KEY: "apiKey",
  VITE_FIREBASE_AUTH_DOMAIN: "authDomain",
  VITE_FIREBASE_PROJECT_ID: "projectId",
  VITE_FIREBASE_APP_ID: "appId"
};

function normaliseEnvRecord(envRecord) {
  if (!envRecord || typeof envRecord !== "object") {
    return null;
  }

  const config = {};
  let hasValue = false;

  for (const [envKey, configKey] of Object.entries(ENV_KEY_MAP)) {
    const value = envRecord[envKey];
    if (typeof value === "string" && value.trim() !== "") {
      config[configKey] = value;
      hasValue = true;
    }
  }

  return hasValue ? config : null;
}

function readViteEnvironment() {
  try {
    if (typeof import.meta !== "undefined" && import.meta.env) {
      return normaliseEnvRecord(import.meta.env);
    }
  } catch (error) {
    console.warn("Unable to access import.meta.env for Firebase config:", error);
  }
  return null;
}

function readWindowEnvironment() {
  if (typeof window === "undefined") {
    return null;
  }

  if (window.FIREBASE_ENV && typeof window.FIREBASE_ENV === "object") {
    return normaliseEnvRecord(window.FIREBASE_ENV);
  }

  return null;
}

async function fetchConfigFromJson() {
  try {
    const response = await fetch(CONFIG_JSON_PATH, { cache: "no-store" });
    if (!response.ok) {
      if (response.status !== 404) {
        console.error(
          `Failed to load ${CONFIG_JSON_PATH}: ${response.status} ${response.statusText}`
        );
      }
      return null;
    }
    const config = await response.json();
    if (config && typeof config === "object") {
      return config;
    }
    console.error(
      `Unexpected content in ${CONFIG_JSON_PATH}. Expected a JSON object.`
    );
    return null;
  } catch (error) {
    console.error(`Error reading ${CONFIG_JSON_PATH}:`, error);
    return null;
  }
}

export async function loadFirebaseConfig() {
  const envConfig =
    readViteEnvironment() ||
    readWindowEnvironment() ||
    (typeof window !== "undefined" && window.FIREBASE_CONFIG);

  if (envConfig) {
    if (typeof window !== "undefined") {
      window.FIREBASE_CONFIG = envConfig;
    }
    return envConfig;
  }

  if (typeof window !== "undefined" && window.FIREBASE_CONFIG) {
    return window.FIREBASE_CONFIG;
  }

  const jsonConfig = await fetchConfigFromJson();
  if (jsonConfig) {
    if (typeof window !== "undefined") {
      window.FIREBASE_CONFIG = jsonConfig;
    }
    return jsonConfig;
  }

  if (typeof window !== "undefined" && window.FIREBASE_CONFIG === undefined) {
    console.warn(
      "Firebase configuration was not found. Provide portal/firebase-config.json, portal/firebase-config.local.js, or environment variables."
    );
  }

  return null;
}

if (typeof window !== "undefined") {
  window.loadFirebaseConfig = loadFirebaseConfig;
}
