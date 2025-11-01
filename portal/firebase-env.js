(function () {
  if (window.FIREBASE_CONFIG || window.FIREBASE_ENV) {
    return;
  }

  const embeddedEnv = {
    VITE_FIREBASE_API_KEY: "AIzaSyB-bo4wgmeLm0Wg1eTiiFe69l6fuXRGCns",
    VITE_FIREBASE_AUTH_DOMAIN: "open-ai-project-723a7.firebaseapp.com",
    VITE_FIREBASE_PROJECT_ID: "open-ai-project-723a7",
    VITE_FIREBASE_APP_ID: "project-299553862015"
  };

  window.FIREBASE_ENV = embeddedEnv;
  window.FIREBASE_CONFIG = {
    apiKey: embeddedEnv.VITE_FIREBASE_API_KEY,
    authDomain: embeddedEnv.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: embeddedEnv.VITE_FIREBASE_PROJECT_ID,
    appId: embeddedEnv.VITE_FIREBASE_APP_ID
  };

  console.info(
    "Loaded embedded Firebase configuration for the shared review environment. " +
      "Override by providing portal/.env.local or portal/firebase-config.json if needed."
  );
})();
