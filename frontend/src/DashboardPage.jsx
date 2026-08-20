import React, {useCallback, useEffect, useState} from 'react';
import {api} from './api';
import WorkoutCard from './WorkoutCard';
import {EmptyState, ErrorState, Header, Loader} from './ui';

function Metric({label, value, suffix = ''}) {
  return (
    <div className="metric" role="group" aria-label={`${label} : ${value}${suffix}`}>
      <span>{label}</span>
      <b>
        {value}
        {suffix && <small>{suffix}</small>}
      </b>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setData(await api('/dashboard'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <>
      <Header title="Tableau de bord" sub="Vue globale de votre charge, fréquence et progression." />
      {loading ? (
        <Loader label="Chargement du tableau de bord…" />
      ) : error ? (
        <ErrorState message={error} onRetry={load} />
      ) : (
        <>
          <section className="grid4" aria-label="Indicateurs clés">
            <Metric label="Séances" value={data.workout_count ?? 0} />
            <Metric label="Séries" value={data.set_count ?? 0} />
            <Metric label="Exercices" value={data.exercise_count ?? 0} />
            <Metric label="Volume" value={data.total_volume ?? 0} />
            <Metric label="Durée totale" value={data.total_duration_minutes ?? 0} suffix=" min" />
            <Metric label="Intensité moyenne" value={data.average_intensity ?? 0} suffix="/10" />
            <Metric label="Objectifs actifs" value={data.goals?.length ?? 0} />
            <Metric label="Progression récente" value={data.recent_progress_percent ?? 0} suffix=" %" />
          </section>

          <section className="card dashboard-latest" aria-labelledby="latest-workout-title">
            <div>
              <p className="eyebrow">Dernière activité</p>
              <h2 id="latest-workout-title">Dernière séance</h2>
            </div>
            {data.last_workout ? (
              <div className="latest-workout-summary">
                <div>
                  <b>{data.last_workout.title}</b>
                  <span>{data.last_workout.type} · {data.last_workout.date}</span>
                </div>
                <div>
                  <b>{data.last_workout.duration_minutes} min</b>
                  <span>RPE {data.last_workout.intensity}/10 · volume {data.last_workout.volume ?? 0}</span>
                </div>
              </div>
            ) : (
              <p className="small">Aucune séance enregistrée pour le moment.</p>
            )}
          </section>

          <div className="cols">
            <section className="card" aria-labelledby="weekly-volume-title">
              <h2 id="weekly-volume-title">Volume hebdomadaire</h2>
              {data.weekly_volume?.length ? (
                <ul className="bars" aria-label="Volume par semaine">
                  {data.weekly_volume.map((week) => (
                    <li key={week.week} aria-label={`${week.week} : ${week.volume} unités de volume`}>
                      <span
                        aria-hidden="true"
                        style={{height: `${Math.min(160, Math.max(8, week.volume / 10))}px`}}
                      />
                      <small>{week.week.slice(5)}</small>
                      <span className="visually-hidden">{week.volume}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <EmptyState title="Pas encore de tendance">
                  Enregistrez une séance pour faire apparaître le volume hebdomadaire.
                </EmptyState>
              )}
            </section>

            <section className="card" aria-labelledby="active-goals-title">
              <h2 id="active-goals-title">Objectifs actifs</h2>
              {data.goals?.length ? (
                data.goals.map((goal) => (
                  <div className="row" key={goal.id}>
                    <b>{goal.skill}</b>
                    <span>
                      {goal.current_level || 'Départ non renseigné'} → {goal.target}
                    </span>
                  </div>
                ))
              ) : (
                <EmptyState title="Aucun objectif actif">
                  Créez un objectif mesurable depuis la page Objectifs.
                </EmptyState>
              )}
            </section>
          </div>

          <section className="card dashboard-history" aria-labelledby="recent-workouts-title">
            <h2 id="recent-workouts-title">Dernières séances</h2>
            {data.recent_workouts?.length ? (
              data.recent_workouts.map((workout) => (
                <WorkoutCard workout={workout} key={workout.id} />
              ))
            ) : (
              <EmptyState title="Aucune séance enregistrée">
                Votre historique apparaîtra ici après la première séance.
              </EmptyState>
            )}
          </section>
        </>
      )}
    </>
  );
}
