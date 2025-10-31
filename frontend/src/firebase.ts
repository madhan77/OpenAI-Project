import { initializeApp, getApps, FirebaseOptions } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

export function initFirebase() {
  const requiredConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string | undefined,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string | undefined,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string | undefined,
    appId: import.meta.env.VITE_FIREBASE_APP_ID as string | undefined
  };

  const optionalConfig = {
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string | undefined,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string | undefined,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID as string | undefined
  };

  const missingKeys = Object.entries(requiredConfig)
    .filter(([, value]) => !value)
    .map(([key]) => key);

  if (missingKeys.length > 0) {
    throw new Error(
      `Missing Firebase configuration values for: ${missingKeys.join(', ')}. Check your Vite environment variables.`
    );
  }

  const firebaseConfig: FirebaseOptions = {
    apiKey: requiredConfig.apiKey!,
    authDomain: requiredConfig.authDomain!,
    projectId: requiredConfig.projectId!,
    appId: requiredConfig.appId!,
    ...(optionalConfig.storageBucket ? { storageBucket: optionalConfig.storageBucket } : {}),
    ...(optionalConfig.messagingSenderId ? { messagingSenderId: optionalConfig.messagingSenderId } : {}),
    ...(optionalConfig.measurementId ? { measurementId: optionalConfig.measurementId } : {})
  };

  const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });

  return { app, auth, provider };
}
