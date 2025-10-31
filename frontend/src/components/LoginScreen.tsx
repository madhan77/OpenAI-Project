import { useMemo, useState } from 'react';

interface LoginScreenProps {
  onSignIn: () => void;
  authError: string | null;
  issueCounts: {
    total: number;
    critical: number;
  };
  loginLink: string;
}

export default function LoginScreen({ onSignIn, authError, issueCounts, loginLink }: LoginScreenProps) {
  const [copied, setCopied] = useState(false);
  const isCopySupported = useMemo(
    () => typeof navigator !== 'undefined' && typeof navigator.clipboard?.writeText === 'function',
    []
  );

  const handleCopyLink = async () => {
    if (!isCopySupported) {
      return;
    }

    try {
      await navigator.clipboard.writeText(loginLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Unable to copy login link', error);
    }
  };

  return (
    <div className="app-state">
      <header className="app-state__header">
        <h1>Single Issue Management</h1>
        <p>Authenticate with your organisation&apos;s Google Workspace identity.</p>
      </header>
      <button className="button" onClick={onSignIn}>
        Sign in with Google
      </button>
      {authError && <p className="app-state__error">{authError}</p>}
      <div className="app-state__summary">
        <p>Preview data</p>
        <p>
          {issueCounts.total} mock incidents · {issueCounts.critical} critical
        </p>
      </div>
      <div className="app-state__login-link">
        <p>Shareable login link:</p>
        <div className="app-state__login-link-row">
          <a href={loginLink} target="_blank" rel="noopener noreferrer">
            {loginLink}
          </a>
          {isCopySupported && (
            <button className="button button--secondary" onClick={handleCopyLink} type="button">
              {copied ? 'Copied!' : 'Copy link'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
