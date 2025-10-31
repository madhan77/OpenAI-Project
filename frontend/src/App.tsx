import { useCallback, useEffect, useMemo, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { onAuthStateChanged, signInWithPopup, signOut, type User } from 'firebase/auth';
import { initFirebase } from './firebase';
import IssueDashboard from './components/IssueDashboard';
import LoginScreen from './components/LoginScreen';
import { mockIssues } from './data/mockData';
import './styles/app.css';

interface FirebaseState {
  status: 'loading' | 'ready' | 'error';
  error?: string;
}

interface ProtectedRouteProps {
  user: User | null;
  children: (user: User) => JSX.Element;
}

function ProtectedRoute({ user, children }: ProtectedRouteProps) {
  const location = useLocation();

  if (!user) {
    return (
      <Navigate
        to="/login"
        state={{ from: `${location.pathname}${location.search}` }}
        replace
      />
    );
  }

  return children(user);
}

interface LoginRouteProps {
  user: User | null;
  onSignIn: () => void;
  authError: string | null;
  issueCounts: {
    total: number;
    critical: number;
  };
  loginLink: string;
}

function LoginRoute({ user, onSignIn, authError, issueCounts, loginLink }: LoginRouteProps) {
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? '/';

  if (user) {
    return <Navigate to={from} replace />;
  }

  return (
    <LoginScreen
      onSignIn={onSignIn}
      authError={authError}
      issueCounts={issueCounts}
      loginLink={loginLink}
    />
  );
}

interface DashboardViewProps {
  user: User;
  onSignOut: () => void;
  authError: string | null;
}

function DashboardView({ user, onSignOut, authError }: DashboardViewProps) {
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
        <button className="button button--secondary" onClick={onSignOut}>
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
      return '/login';
    }
    const origin = window.location.origin.replace(/\/$/, '');
    return `${origin}/login`;
  }, []);

  const handleSignIn = useCallback(async () => {
    if (!authBundle) {
      return;
    }

    try {
      setAuthError(null);
      await signInWithPopup(authBundle.auth, authBundle.provider);
    } catch (error) {
      console.error(error);
      setAuthError(error instanceof Error ? error.message : 'Authentication failed.');
    }
  }, [authBundle]);

  const handleSignOut = useCallback(async () => {
    if (!authBundle) {
      return;
    }
    try {
      setAuthError(null);
      await signOut(authBundle.auth);
    } catch (error) {
      console.error(error);
      setAuthError(error instanceof Error ? error.message : 'Unable to sign out.');
    }
  }, [authBundle]);

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
        <pre>{`VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_APP_ID=...`}</pre>
        <p>You can continue using the mock Single Issue Management dashboard once credentials are present.</p>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            <LoginRoute
              user={user}
              onSignIn={() => {
                void handleSignIn();
              }}
              authError={authError}
              issueCounts={issueCounts}
              loginLink={loginLink}
            />
          }
        />
        <Route
          path="/*"
          element={
            <ProtectedRoute user={user}>
              {(nextUser) => (
                <DashboardView
                  user={nextUser}
                  onSignOut={() => {
                    void handleSignOut();
                  }}
                  authError={authError}
                />
              )}
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
