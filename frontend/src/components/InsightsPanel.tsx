import type { ReactNode } from 'react';
import './InsightsPanel.css';

type Insight = {
  id: string;
  category: string;
  message: string;
  severity: string;
};

type InsightsPanelProps = {
  title: string;
  subtitle?: ReactNode;
  insights: Insight[];
};

export function InsightsPanel({ title, subtitle, insights }: InsightsPanelProps) {
  return (
    <section className="insights-panel">
      <header>
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <span className="insights-panel__badge">AI Coach</span>
      </header>
      <ul>
        {insights.map((insight) => (
          <li key={insight.id} className={`insights-panel__item insights-panel__item--${insight.severity.toLowerCase()}`}>
            <div>
              <p className="insights-panel__category">{insight.category}</p>
              <p className="insights-panel__message">{insight.message}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
