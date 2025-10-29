import { useCallback, useState } from 'react';
import { DashboardPage } from './pages/DashboardPage.tsx';
import { AppShell } from './components/AppShell.tsx';
import { SignInPanel } from './components/SignInPanel.tsx';
import { useAuth } from './contexts/AuthContext.tsx';

function App() {
  const { user, loading, signInWithGoogle, initializationError } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);
  const [signInLoading, setSignInLoading] = useState(false);

  const handleSignIn = useCallback(async () => {
    setAuthError(null);
    setSignInLoading(true);
    try {
      await signInWithGoogle();
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'Unable to complete Google sign-in. Please try again.';
      setAuthError(message);
    } finally {
      setSignInLoading(false);
    }
  }, [signInWithGoogle]);

  if (loading) {
    return (
      <div className="app-loading" role="status" aria-live="polite">
        Connecting to Firebase…
      </div>
    );
  }

  if (!user) {
    return (
      <div className="app-auth">
        <SignInPanel
          onGoogleSignIn={handleSignIn}
          loading={signInLoading}
          error={authError}
          initializationError={initializationError?.message ?? null}
        />
      </div>
    );
  }

  return (
    <AppShell>
      <DashboardPage />
    </AppShell>
  );
}

export default App;
