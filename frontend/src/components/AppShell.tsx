import type { PropsWithChildren } from 'react';
import { useAuth } from '../contexts/AuthContext.tsx';
import './AppShell.css';

export function AppShell({ children }: PropsWithChildren) {
  const { user, signOut } = useAuth();
  const userLabel = user?.displayName ?? user?.email ?? 'Signed in';
  const avatarLetter = user?.displayName?.charAt(0) ?? user?.email?.charAt(0) ?? 'U';

  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <div className="app-shell__brand">
          <div className="app-shell__logo">WT</div>
          <div>
            <h1>Wellness Tracker Agent</h1>
            <p>Your daily health companion</p>
          </div>
        </div>
        <div className="app-shell__meta">
          <div className="app-shell__status">
            <span className="app-shell__status-indicator" aria-hidden />
            <span>Backend connected</span>
          </div>
          <div className="app-shell__user">
            <div className="app-shell__avatar" aria-hidden>
              {user?.photoURL ? (
                <img src={user.photoURL} alt="" referrerPolicy="no-referrer" />
              ) : (
                avatarLetter.toUpperCase()
              )}
            </div>
            <div className="app-shell__user-info">
              <span className="app-shell__user-name">{userLabel}</span>
              <button
                type="button"
                className="app-shell__signout"
                onClick={() => {
                  void signOut();
                }}
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>
      <main className="app-shell__content">{children}</main>
    </div>
  );
}
