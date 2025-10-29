import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app';
import {
  getAuth,
  type Auth,
  GoogleAuthProvider,
  browserLocalPersistence,
  setPersistence,
} from 'firebase/auth';

let firebaseApp: FirebaseApp | null = null;
let firebaseAuth: Auth | null = null;
let persistenceConfigured = false;

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
};

function assertFirebaseConfig() {
  const requiredKeys: Array<keyof typeof firebaseConfig> = [
    'apiKey',
    'authDomain',
    'projectId',
    'appId',
  ];

  const missing = requiredKeys.filter((key) => !firebaseConfig[key]);
  if (missing.length) {
    const joined = missing.join(', ');
    throw new Error(
      `Missing Firebase configuration values: ${joined}. Populate them in your frontend environment (.env).`
    );
  }
}

export function initFirebaseApp(): FirebaseApp {
  if (firebaseApp) {
    return firebaseApp;
  }

  assertFirebaseConfig();

  if (getApps().length) {
    firebaseApp = getApp();
  } else {
    firebaseApp = initializeApp(firebaseConfig);
  }

  return firebaseApp;
}

export function getFirebaseAuth(): Auth {
  if (firebaseAuth) {
    return firebaseAuth;
  }

  const app = initFirebaseApp();
  firebaseAuth = getAuth(app);

  if (!persistenceConfigured) {
    setPersistence(firebaseAuth, browserLocalPersistence).catch((error) => {
      console.warn('Failed to enable Firebase local persistence', error);
    });
    persistenceConfigured = true;
  }

  return firebaseAuth;
}

export const googleAuthProvider = new GoogleAuthProvider();
googleAuthProvider.setCustomParameters({ prompt: 'select_account' });
