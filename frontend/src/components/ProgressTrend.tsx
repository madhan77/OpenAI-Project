import './ProgressTrend.css';

type ProgressDay = {
  date: string;
  steps: number;
  caloriesBurned: number;
  sleepHours: number;
  hydrationOz: number;
  mindfulnessMinutes: number;
  averageMood: number;
  averageStressLevel: number;
};

type ProgressTrendProps = {
  days: ProgressDay[];
};

export function ProgressTrend({ days }: ProgressTrendProps) {
  return (
    <section className="progress-trend">
      <header>
        <div>
          <h2>Weekly Progress</h2>
          <p>Compare core wellness metrics over the past 7 days.</p>
        </div>
      </header>
      <div className="progress-trend__grid" role="list">
        {days.map((day) => (
          <article key={day.date} className="progress-trend__card" role="listitem">
            <header>
              <h3>{new Date(day.date).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</h3>
              <p>{day.steps.toLocaleString()} steps</p>
            </header>
            <dl>
              <div>
                <dt>Calories burned</dt>
                <dd>{Math.round(day.caloriesBurned)} kcal</dd>
              </div>
              <div>
                <dt>Sleep</dt>
                <dd>{day.sleepHours.toFixed(1)} hrs</dd>
              </div>
              <div>
                <dt>Hydration</dt>
                <dd>{day.hydrationOz.toFixed(0)} oz</dd>
              </div>
              <div>
                <dt>Mindfulness</dt>
                <dd>{day.mindfulnessMinutes} min</dd>
              </div>
              <div>
                <dt>Mood / Stress</dt>
                <dd>
                  {day.averageMood.toFixed(1)} / {day.averageStressLevel.toFixed(1)}
                </dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
