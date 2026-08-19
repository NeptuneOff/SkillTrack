import React from 'react';
import {Pencil, Trash2} from 'lucide-react';

export default function WorkoutCard({workout, onEdit, onDelete, busy = false}) {
  const sets = workout.sets || [];
  return (
    <article className="workout">
      <div>
        <h3>{workout.title}</h3>
        <p className="workout-meta">
          <time dateTime={workout.date}>{workout.date}</time> · {workout.type} · intensité{' '}
          {workout.intensity}/10 · {workout.duration_minutes} min · volume {workout.volume ?? 0}
        </p>
        {workout.notes && <p>{workout.notes}</p>}
        {sets.length ? (
          <ul className="exercise-summary" aria-label={`Exercices de ${workout.title}`}>
            {sets.map((set, index) => (
              <li key={set.id || `${set.exercise}-${index}`}>
                {set.set_count || 1} série(s) de {set.exercise} — {set.reps} répétition(s) ·{' '}
                {set.load_kg} kg · {set.duration_seconds} s · RPE {set.difficulty}/10
              </li>
            ))}
          </ul>
        ) : (
          <p className="small">Aucun exercice renseigné.</p>
        )}
      </div>
      {(onEdit || onDelete) && (
        <div className="actions workout-actions">
          {onEdit && (
            <button type="button" onClick={() => onEdit(workout)} disabled={busy}>
              <Pencil size={16} aria-hidden="true" />
              Modifier
            </button>
          )}
          {onDelete && (
            <button
              type="button"
              className="danger"
              aria-label={`Supprimer la séance ${workout.title}`}
              onClick={() => onDelete(workout)}
              disabled={busy}
            >
              <Trash2 size={16} aria-hidden="true" />
              <span className="button-label">Supprimer</span>
            </button>
          )}
        </div>
      )}
    </article>
  );
}
