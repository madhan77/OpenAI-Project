import type { ReactNode } from 'react';
import './SummaryCard.css';

type SummaryCardProps = {
  title: string;
  value: ReactNode;
  helper?: ReactNode;
  accent?: 'blue' | 'green' | 'purple' | 'orange';
};

export function SummaryCard({ title, value, helper, accent = 'blue' }: SummaryCardProps) {
  return (
    <article className={`summary-card summary-card--${accent}`}>
      <header>
        <h3>{title}</h3>
        {helper && <span className="summary-card__helper">{helper}</span>}
      </header>
      <div className="summary-card__value">{value}</div>
    </article>
  );
}
