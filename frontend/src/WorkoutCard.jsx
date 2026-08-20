import React from 'react';
import {Eye, Pencil, Trash2} from 'lucide-react';
import {groupWorkoutSets} from './workoutData';

export default function WorkoutCard({workout, onView, onEdit, onDelete, busy = false}) {
  const exercises = groupWorkoutSets(workout.sets || []);
  const seriesCount = exercises.reduce((total, exercise) => total + exercise.series.length, 0);
  return (
    <article className="workout">
      <div>
        <h3>{workout.title}</h3>
        <p className="workout-meta">
          <time dateTime={workout.date}>{workout.date}</time> · {workout.type} · intensité{' '}
          {workout.intensity}/10 · {workout.duration_minutes} min · volume {workout.volume ?? 0} ·{' '}
          {exercises.length} exercice(s) · {seriesCount} série(s)
        </p>
        {workout.notes && <p>{workout.notes}</p>}
        {exercises.length ? (
          <ul className="exercise-summary" aria-label={`Exercices de ${workout.title}`}>
            {exercises.map((exercise, index) => (
              <li key={`${exercise.exercise}-${index}`}>
                <b>{exercise.exercise}</b> — {exercise.series.length} série(s) · catégorie{' '}
                {exercise.category}
              </li>
            ))}
          </ul>
        ) : (
          <p className="small">Aucun exercice renseigné.</p>
        )}
      </div>
      {(onView || onEdit || onDelete) && (
        <div className="actions workout-actions">
          {onView && (
            <button type="button" onClick={() => onView(workout)} disabled={busy}>
              <Eye size={16} aria-hidden="true" />
              Voir le détail
            </button>
          )}
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
