import { useEffect, useMemo, useState } from 'react';
import type { Issue, Task, TimelineEvent } from '../data/mockData';
import '../styles/dashboard.css';

interface Props {
  issues: Issue[];
}

const severityOrder: Record<Issue['severity'], number> = {
  critical: 0,
  high: 1,
  medium: 2
};

const statusLabels: Record<Issue['status'], string> = {
  open: 'Open',
  mitigated: 'Mitigated',
  resolved: 'Resolved'
};

const taskStatusLabels: Record<Task['status'], string> = {
  pending: 'Pending',
  in_progress: 'In Progress',
  completed: 'Completed'
};

const formatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short'
});

function getTimeRemaining(issue: Issue) {
  if (!issue.targetResolutionAt) {
    return '—';
  }

  const target = new Date(issue.targetResolutionAt).getTime();
  const now = Date.now();
  const diffMinutes = Math.round((target - now) / 60000);

  if (diffMinutes < 0) {
    return `${Math.abs(diffMinutes)} min past target`;
  }

  return `${diffMinutes} min remaining`;
}

function summaryMetrics(issues: Issue[]) {
  const openCount = issues.filter((issue) => issue.status === 'open').length;
  const mitigatedCount = issues.filter((issue) => issue.status === 'mitigated').length;
  const resolvedCount = issues.filter((issue) => issue.status === 'resolved').length;
  const breachedCount = issues.filter((issue) => {
    if (!issue.targetResolutionAt) {
      return false;
    }
    const breachTime = new Date(issue.openedAt).getTime() + issue.slaMinutes * 60000;
    return new Date(issue.lastUpdatedAt).getTime() > breachTime;
  }).length;

  return {
    openCount,
    mitigatedCount,
    resolvedCount,
    breachedCount
  };
}

function timelineIcon(event: TimelineEvent) {
  switch (event.category) {
    case 'milestone':
      return '⭐';
    case 'decision':
      return '⚖️';
    case 'risk':
      return '⚠️';
    default:
      return '📝';
  }
}

export function IssueDashboard({ issues }: Props) {
  const [selectedIssueId, setSelectedIssueId] = useState(issues[0]?.id);
  const [severityFilter, setSeverityFilter] = useState<'all' | Issue['severity']>('all');

  const filteredIssues = useMemo(() => {
    const sorted = [...issues].sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
    if (severityFilter === 'all') {
      return sorted;
    }
    return sorted.filter((issue) => issue.severity === severityFilter);
  }, [issues, severityFilter]);

  useEffect(() => {
    if (!filteredIssues.find((issue) => issue.id === selectedIssueId)) {
      setSelectedIssueId(filteredIssues[0]?.id);
    }
  }, [filteredIssues, selectedIssueId]);

  const metrics = useMemo(() => summaryMetrics(issues), [issues]);

  const selectedIssue = filteredIssues.find((issue) => issue.id === selectedIssueId) ?? filteredIssues[0];

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>Single Issue Management</h1>
        <p className="dashboard__subtitle">Operational view of high-impact customer incidents</p>
      </header>

      <section className="dashboard__metrics">
        <div className="metric-card">
          <p className="metric-card__label">Open</p>
          <p className="metric-card__value">{metrics.openCount}</p>
        </div>
        <div className="metric-card">
          <p className="metric-card__label">Mitigated</p>
          <p className="metric-card__value">{metrics.mitigatedCount}</p>
        </div>
        <div className="metric-card">
          <p className="metric-card__label">Resolved</p>
          <p className="metric-card__value">{metrics.resolvedCount}</p>
        </div>
        <div className="metric-card metric-card--alert">
          <p className="metric-card__label">SLA Breaches</p>
          <p className="metric-card__value">{metrics.breachedCount}</p>
        </div>
      </section>

      <section className="dashboard__layout">
        <aside className="issue-list">
          <div className="issue-list__controls">
            <label htmlFor="severity-filter">Severity</label>
            <select
              id="severity-filter"
              value={severityFilter}
              onChange={(event) => setSeverityFilter(event.target.value as typeof severityFilter)}
            >
              <option value="all">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
            </select>
          </div>
          <ul>
            {filteredIssues.map((issue) => (
              <li
                key={issue.id}
                className={issue.id === selectedIssue?.id ? 'issue-list__item issue-list__item--active' : 'issue-list__item'}
                onClick={() => setSelectedIssueId(issue.id)}
              >
                <div className="issue-list__title">
                  <span className={`badge badge--${issue.severity}`}>{issue.severity.toUpperCase()}</span>
                  <h3>{issue.title}</h3>
                </div>
                <p className="issue-list__meta">
                  {issue.id} · {statusLabels[issue.status]} · Updated {formatter.format(new Date(issue.lastUpdatedAt))}
                </p>
              </li>
            ))}
          </ul>
        </aside>

        {selectedIssue && (
          <article className="issue-detail">
            <header className="issue-detail__header">
              <div>
                <h2>{selectedIssue.title}</h2>
                <p className="issue-detail__id">{selectedIssue.id}</p>
              </div>
              <div className="issue-detail__header-meta">
                <span className={`badge badge--${selectedIssue.severity}`}>{selectedIssue.severity.toUpperCase()}</span>
                <span className="status-chip">{statusLabels[selectedIssue.status]}</span>
              </div>
            </header>

            <section className="issue-detail__section">
              <h3>Summary</h3>
              <p>{selectedIssue.description}</p>
              <p className="issue-detail__impact">Impact: {selectedIssue.serviceImpact}</p>
              <dl className="issue-detail__dates">
                <div>
                  <dt>Opened</dt>
                  <dd>{formatter.format(new Date(selectedIssue.openedAt))}</dd>
                </div>
                <div>
                  <dt>Target Resolution</dt>
                  <dd>{selectedIssue.targetResolutionAt ? formatter.format(new Date(selectedIssue.targetResolutionAt)) : '—'}</dd>
                </div>
                <div>
                  <dt>Time Remaining</dt>
                  <dd>{getTimeRemaining(selectedIssue)}</dd>
                </div>
              </dl>
            </section>

            <section className="issue-detail__section">
              <h3>Tasks</h3>
              <ul className="task-list">
                {selectedIssue.tasks.map((task) => (
                  <li key={task.id} className={`task-list__item task-list__item--${task.status}`}>
                    <div>
                      <p className="task-list__title">{task.title}</p>
                      <p className="task-list__meta">Owner: {task.owner}</p>
                    </div>
                    <div className="task-list__status">
                      <span>{taskStatusLabels[task.status]}</span>
                      {task.dueDate && <small>Due {formatter.format(new Date(task.dueDate))}</small>}
                    </div>
                  </li>
                ))}
              </ul>
            </section>

            <section className="issue-detail__section">
              <h3>Timeline</h3>
              <ul className="timeline">
                {selectedIssue.timeline.map((event) => (
                  <li key={event.id} className="timeline__item">
                    <span className="timeline__icon" aria-hidden="true">
                      {timelineIcon(event)}
                    </span>
                    <div>
                      <p className="timeline__timestamp">{formatter.format(new Date(event.timestamp))}</p>
                      <p>{event.summary}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </section>

            <section className="issue-detail__section">
              <h3>Escalations</h3>
              {selectedIssue.escalations.length === 0 ? (
                <p className="issue-detail__empty">No active escalations.</p>
              ) : (
                <ul className="escalation-list">
                  {selectedIssue.escalations.map((escalation) => (
                    <li key={escalation.id} className="escalation-list__item">
                      <div>
                        <p className="escalation-list__level">Level {escalation.level.toUpperCase()}</p>
                        <p className="escalation-list__meta">
                          Owner: {escalation.owner} · Opened {formatter.format(new Date(escalation.openedAt))}
                        </p>
                      </div>
                      <span className={`status-chip status-chip--${escalation.status}`}>{escalation.status.toUpperCase()}</span>
                      {escalation.notes && <p className="escalation-list__notes">{escalation.notes}</p>}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </article>
        )}
      </section>
    </div>
  );
}

export default IssueDashboard;
