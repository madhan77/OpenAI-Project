import type { PropsWithChildren } from 'react';
import './AppShell.css';

export function AppShell({ children }: PropsWithChildren) {
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
        <div className="app-shell__status">
          <span className="app-shell__status-indicator" aria-hidden />
          <span>Backend connected</span>
        </div>
      </header>
      <main className="app-shell__content">{children}</main>
    </div>
  );
}
