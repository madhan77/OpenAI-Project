import { useEffect, useMemo, useState } from 'react';
import { onAuthStateChanged, signInWithPopup, signOut, type User } from 'firebase/auth';
import { initFirebase } from './firebase';
import IssueDashboard from './components/IssueDashboard';
import { mockIssues } from './data/mockData';
import './styles/app.css';

interface FirebaseState {
  status: 'loading' | 'ready' | 'error';
  error?: string;
}

export default function App() {
  const [firebaseState, setFirebaseState] = useState<FirebaseState>({ status: 'loading' });
  const [user, setUser] = useState<User | null>(null);
  const [authBundle, setAuthBundle] = useState<ReturnType<typeof initFirebase>>();
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const bundle = initFirebase();
      setAuthBundle(bundle);
      setFirebaseState({ status: 'ready' });
      const unsubscribe = onAuthStateChanged(bundle.auth, (nextUser) => {
        setUser(nextUser);
        setAuthError(null);
      });
      return unsubscribe;
    } catch (error) {
      console.error(error);
      setFirebaseState({
        status: 'error',
        error: error instanceof Error ? error.message : 'Unable to initialise Firebase.'
      });
      return undefined;
    }
  }, []);

  const issueCounts = useMemo(
    () => ({
      total: mockIssues.length,
      critical: mockIssues.filter((issue) => issue.severity === 'critical').length
    }),
    []
  );

  const loginLink = useMemo(() => {
    if (typeof window === 'undefined') {
      return '';
    }
    const url = new URL(window.location.href);
    url.pathname = '/login';
    url.search = '';
    url.hash = '';
    return url.toString();
  }, []);

  const handleSignIn = async () => {
    if (!authBundle) {
      return;
    }

    try {
      await signInWithPopup(authBundle.auth, authBundle.provider);
    } catch (error) {
      console.error(error);
      setAuthError(error instanceof Error ? error.message : 'Authentication failed.');
    }
  };

  const handleSignOut = async () => {
    if (!authBundle) {
      return;
    }
    try {
      await signOut(authBundle.auth);
    } catch (error) {
      console.error(error);
      setAuthError(error instanceof Error ? error.message : 'Unable to sign out.');
    }
  };

  if (firebaseState.status === 'loading') {
    return (
      <div className="app-state">
        <p>Loading authentication…</p>
      </div>
    );
  }

  if (firebaseState.status === 'error') {
    return (
      <div className="app-state app-state--error">
        <h1>Configuration required</h1>
        <p>{firebaseState.error}</p>
        <p>
          Add your Firebase web credentials to a <code>.env.local</code> file in the <code>frontend</code> directory:
        </p>
        <pre>
{`VITE_FIREBASE_API_KEY=...`
}{`
VITE_FIREBASE_AUTH_DOMAIN=...`
}{`
VITE_FIREBASE_PROJECT_ID=...`
}{`
VITE_FIREBASE_APP_ID=...`}
        </pre>
        <p>You can continue using the mock Single Issue Management dashboard once credentials are present.</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="app-state">
        <header className="app-state__header">
          <h1>Single Issue Management</h1>
          <p>Authenticate with your organisation&apos;s Google Workspace identity.</p>
        </header>
        <button className="button" onClick={handleSignIn}>
          Sign in with Google
        </button>
        {authError && <p className="app-state__error">{authError}</p>}
        <div className="app-state__summary">
          <p>Preview data</p>
          <p>
            {issueCounts.total} mock incidents · {issueCounts.critical} critical
          </p>
        </div>
        {loginLink && (
          <p className="app-state__login-link">
            Shareable login link:{' '}
            <a href={loginLink} target="_blank" rel="noopener noreferrer">
              {loginLink}
            </a>
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <div>
          <h2>Single Issue Management</h2>
          <p className="app-shell__subtitle">Operational control room</p>
        </div>
        <div className="app-shell__user">
          <img src={user.photoURL ?? undefined} alt="User avatar" referrerPolicy="no-referrer" />
          <div>
            <p className="app-shell__user-name">{user.displayName}</p>
            <p className="app-shell__user-email">{user.email}</p>
          </div>
        </div>
        <button className="button button--secondary" onClick={handleSignOut}>
          Sign out
        </button>
        {authError && <p className="app-shell__error">{authError}</p>}
      </aside>
      <main className="app-shell__content">
        <IssueDashboard issues={mockIssues} />
      </main>
    </div>
  );
}
