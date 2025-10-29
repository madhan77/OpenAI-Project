import type { MouseEventHandler } from 'react';
import './SignInPanel.css';

interface SignInPanelProps {
  onGoogleSignIn: MouseEventHandler<HTMLButtonElement>;
  error?: string | null;
  initializationError?: string | null;
  loading?: boolean;
}

export function SignInPanel({
  onGoogleSignIn,
  error,
  initializationError,
  loading = false,
}: SignInPanelProps): JSX.Element {
  return (
    <div className="sign-in-panel" role="group" aria-labelledby="sign-in-heading">
      <div className="sign-in-panel__badge">WT</div>
      <h1 id="sign-in-heading">Welcome to Wellness Tracker Agent</h1>
      <p className="sign-in-panel__subheading">
        Connect with your Firebase account to personalise your wellness dashboard.
      </p>

      {initializationError && (
        <p className="sign-in-panel__error" role="alert">
          {initializationError}
        </p>
      )}

      {error && !initializationError && (
        <p className="sign-in-panel__error" role="alert">
          {error}
        </p>
      )}

      <button
        type="button"
        className="sign-in-panel__button"
        onClick={onGoogleSignIn}
        disabled={loading || Boolean(initializationError)}
      >
        {loading ? 'Signing in…' : 'Sign in with Google'}
      </button>
      <p className="sign-in-panel__helper">
        We use Firebase Authentication to protect your data. You can disconnect at any time from your
        account settings.
      </p>
    </div>
  );
}
