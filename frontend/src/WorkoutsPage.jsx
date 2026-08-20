import React, {useCallback, useEffect, useState} from 'react';
import {CalendarPlus, Plus, Trash2} from 'lucide-react';
import {api} from './api';
import WorkoutCard from './WorkoutCard';
import {blankExercise, blankSeries, editableWorkout, groupWorkoutSets, newWorkout, workoutPayload} from './workoutData';
import {ConfirmDialog, Dialog, EmptyState, ErrorState, Header, Loader} from './ui';

export default function WorkoutsPage({setToast}) {
  const [items, setItems] = useState([]);
  const [editing, setEditing] = useState(null);
  const [selected, setSelected] = useState(null);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setItems(await api('/workouts'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function remove() {
    if (!pendingDelete) return;
    const workout = pendingDelete;
    setDeletingId(workout.id);
    setError('');
    try {
      await api(`/workouts/${workout.id}`, {method: 'DELETE'});
      if (editing?.id === workout.id) setEditing(null);
      if (selected?.id === workout.id) setSelected(null);
      setPendingDelete(null);
      setToast('Séance supprimée avec succès');
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId('');
    }
  }

  function startEditing(workout) {
    setEditing(workout);
    window.requestAnimationFrame(() => document.querySelector('#workout-form-title')?.focus());
  }

  return (
    <>
      <Header title="Séances" sub="Créez, consultez, modifiez et supprimez des entraînements complets." />
      <WorkoutForm
        editing={editing}
        onCancel={() => setEditing(null)}
        onSaved={async (wasEditing) => {
          setEditing(null);
          setToast(wasEditing ? 'Séance modifiée avec succès' : 'Séance enregistrée avec succès');
          await load();
        }}
      />
      <section className="card" aria-labelledby="workout-history-title">
        <div className="section-heading">
          <div>
            <h2 id="workout-history-title">Historique des séances</h2>
            <p className="small">Chaque fiche donne accès au détail, à la modification et à la suppression.</p>
          </div>
          <div className="actions">
            <span className="count-badge">{items.length} séance(s)</span>
            <button
              type="button"
              onClick={() => document.querySelector('#workout-form-title')?.focus()}
            >
              <Plus aria-hidden="true" />
              Ajouter une séance
            </button>
          </div>
        </div>
        {error && items.length > 0 && <p className="error-message" role="alert">{error}</p>}
        {loading ? (
          <Loader label="Chargement des séances…" />
        ) : error && !items.length ? (
          <ErrorState message={error} onRetry={load} />
        ) : items.length ? (
          items.map((workout) => (
            <WorkoutCard
              workout={workout}
              key={workout.id}
              onView={setSelected}
              onEdit={startEditing}
              onDelete={setPendingDelete}
              busy={deletingId === workout.id}
            />
          ))
        ) : (
          <EmptyState title="Aucune séance">
            Utilisez le formulaire ci-dessus pour enregistrer votre premier entraînement.
          </EmptyState>
        )}
      </section>

      <WorkoutDetailDialog workout={selected} onClose={() => setSelected(null)} />
      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Supprimer cette séance ?"
        confirmLabel="Supprimer définitivement"
        onCancel={() => setPendingDelete(null)}
        onConfirm={remove}
        busy={Boolean(deletingId)}
      >
        <p>
          La séance <b>« {pendingDelete?.title} »</b>, ses exercices et toutes ses séries seront
          supprimés. Cette action est irréversible.
        </p>
      </ConfirmDialog>
    </>
  );
}

export function WorkoutForm({editing, onCancel, onSaved}) {
  const [form, setForm] = useState(() => editableWorkout(editing));
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [pendingExerciseIndex, setPendingExerciseIndex] = useState(null);

  useEffect(() => {
    setForm(editableWorkout(editing));
    setError('');
  }, [editing]);

  function change(key, value) {
    setForm((current) => ({...current, [key]: value}));
  }

  function changeExercise(index, key, value) {
    setForm((current) => ({
      ...current,
      exercises: current.exercises.map((exercise, exerciseIndex) =>
        exerciseIndex === index ? {...exercise, [key]: value} : exercise,
      ),
    }));
  }

  function changeSeries(exerciseIndex, seriesIndex, key, value) {
    setForm((current) => ({
      ...current,
      exercises: current.exercises.map((exercise, currentExerciseIndex) =>
        currentExerciseIndex === exerciseIndex
          ? {
              ...exercise,
              series: exercise.series.map((series, currentSeriesIndex) =>
                currentSeriesIndex === seriesIndex ? {...series, [key]: value} : series,
              ),
            }
          : exercise,
      ),
    }));
  }

  function addSeries(exerciseIndex) {
    setForm((current) => ({
      ...current,
      exercises: current.exercises.map((exercise, currentExerciseIndex) =>
        currentExerciseIndex === exerciseIndex
          ? {...exercise, series: [...exercise.series, blankSeries()]}
          : exercise,
      ),
    }));
  }

  function removeSeries(exerciseIndex, seriesIndex) {
    setForm((current) => ({
      ...current,
      exercises: current.exercises.map((exercise, currentExerciseIndex) =>
        currentExerciseIndex === exerciseIndex
          ? {
              ...exercise,
              series: exercise.series.filter((_, currentSeriesIndex) => currentSeriesIndex !== seriesIndex),
            }
          : exercise,
      ),
    }));
  }

  function requestExerciseRemoval(index) {
    if (form.exercises.length === 1) {
      setError('Une séance doit contenir au moins un exercice. Ajoutez-en un autre avant de supprimer celui-ci.');
      return;
    }
    setPendingExerciseIndex(index);
  }

  function confirmExerciseRemoval() {
    setForm((current) => ({
      ...current,
      exercises: current.exercises.filter((_, index) => index !== pendingExerciseIndex),
    }));
    setPendingExerciseIndex(null);
    setError('');
  }

  async function submit(event) {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    const wasEditing = Boolean(editing);
    try {
      await api(editing ? `/workouts/${editing.id}` : '/workouts', {
        method: editing ? 'PUT' : 'POST',
        body: JSON.stringify(workoutPayload(form)),
      });
      setForm(newWorkout());
      await onSaved(wasEditing);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card form" onSubmit={submit} aria-describedby="workout-form-help">
      <h2 id="workout-form-title" tabIndex="-1">
        {editing ? 'Modifier la séance' : 'Ajouter une séance'}
      </h2>
      <p className="small" id="workout-form-help">
        Les champs marqués * sont obligatoires. Le RPE va de 1 (très facile) à 10 (maximal).
        Chaque série peut avoir ses propres répétitions, durée, charge, assistance et difficulté.
      </p>
      {error && <p role="alert" className="error-message">{error}</p>}

      <fieldset>
        <legend>Informations générales</legend>
        <div className="fields workout-general-fields">
          <label htmlFor="workout-title">
            Titre *
            <input
              id="workout-title"
              required
              minLength="2"
              maxLength="160"
              placeholder="Ex. Planche technique"
              value={form.title}
              onChange={(event) => change('title', event.target.value)}
            />
          </label>
          <label htmlFor="workout-date">
            Date *
            <input
              id="workout-date"
              required
              type="date"
              value={form.date}
              onChange={(event) => change('date', event.target.value)}
            />
          </label>
          <label htmlFor="workout-type">
            Type *
            <select
              id="workout-type"
              required
              value={form.type}
              onChange={(event) => change('type', event.target.value)}
            >
              {['Push', 'Pull', 'Legs', 'Skill', 'Mobilité', 'Mixte'].map((type) => (
                <option key={type}>{type}</option>
              ))}
            </select>
          </label>
          <label htmlFor="workout-intensity">
            Difficulté globale (RPE) *
            <input
              id="workout-intensity"
              required
              type="number"
              min="1"
              max="10"
              placeholder="7"
              value={form.intensity}
              onChange={(event) => change('intensity', event.target.value)}
            />
          </label>
          <label htmlFor="workout-duration">
            Durée (minutes) *
            <input
              id="workout-duration"
              required
              type="number"
              min="1"
              max="1440"
              placeholder="60"
              value={form.duration_minutes}
              onChange={(event) => change('duration_minutes', event.target.value)}
            />
          </label>
        </div>
        <label htmlFor="workout-notes">
          Notes de séance
          <textarea
            id="workout-notes"
            maxLength="4000"
            placeholder="Sensations, douleurs, points techniques…"
            value={form.notes}
            onChange={(event) => change('notes', event.target.value)}
          />
        </label>
      </fieldset>

      <div>
        <h3>Exercices et séries</h3>
        <p className="small">Ajoutez les exercices, puis détaillez chaque série de travail.</p>
      </div>
      {form.exercises.map((exercise, exerciseIndex) => (
        <fieldset className="exercise" key={exerciseIndex}>
          <legend>Exercice {exerciseIndex + 1}</legend>
          <div className="exercise-fields">
            <label htmlFor={`exercise-name-${exerciseIndex}`}>
              Nom *
              <input
                id={`exercise-name-${exerciseIndex}`}
                required
                minLength="2"
                maxLength="160"
                placeholder="Ex. Tuck planche hold"
                value={exercise.exercise}
                onChange={(event) => changeExercise(exerciseIndex, 'exercise', event.target.value)}
              />
            </label>
            <label htmlFor={`exercise-category-${exerciseIndex}`}>
              Catégorie
              <input
                id={`exercise-category-${exerciseIndex}`}
                maxLength="40"
                placeholder="Ex. planche"
                value={exercise.category}
                onChange={(event) => changeExercise(exerciseIndex, 'category', event.target.value)}
              />
            </label>
            <label className="field-wide" htmlFor={`exercise-notes-${exerciseIndex}`}>
              Notes de l’exercice
              <textarea
                id={`exercise-notes-${exerciseIndex}`}
                maxLength="2000"
                placeholder="Tempo, technique, récupération…"
                value={exercise.notes}
                onChange={(event) => changeExercise(exerciseIndex, 'notes', event.target.value)}
              />
            </label>
          </div>

          <div className="series-heading">
            <h4>Séries de travail</h4>
            <span className="count-badge">{exercise.series.length} série(s)</span>
          </div>
          <div className="series-list">
            {exercise.series.map((series, seriesIndex) => (
              <fieldset className="series-row" key={seriesIndex}>
                <legend>Série {seriesIndex + 1}</legend>
                <div className="series-fields">
                  <label htmlFor={`series-reps-${exerciseIndex}-${seriesIndex}`}>
                    Répétitions
                    <input
                      id={`series-reps-${exerciseIndex}-${seriesIndex}`}
                      type="number"
                      min="0"
                      max="1000"
                      placeholder="8"
                      value={series.reps}
                      onChange={(event) => changeSeries(exerciseIndex, seriesIndex, 'reps', event.target.value)}
                    />
                  </label>
                  <label htmlFor={`series-duration-${exerciseIndex}-${seriesIndex}`}>
                    Durée (secondes)
                    <input
                      id={`series-duration-${exerciseIndex}-${seriesIndex}`}
                      type="number"
                      min="0"
                      max="86400"
                      placeholder="20"
                      value={series.duration_seconds}
                      onChange={(event) => changeSeries(exerciseIndex, seriesIndex, 'duration_seconds', event.target.value)}
                    />
                  </label>
                  <label htmlFor={`series-load-${exerciseIndex}-${seriesIndex}`}>
                    Charge (kg)
                    <input
                      id={`series-load-${exerciseIndex}-${seriesIndex}`}
                      type="number"
                      min="0"
                      max="1000"
                      step="0.1"
                      placeholder="0"
                      value={series.load_kg}
                      onChange={(event) => changeSeries(exerciseIndex, seriesIndex, 'load_kg', event.target.value)}
                    />
                  </label>
                  <label htmlFor={`series-assistance-${exerciseIndex}-${seriesIndex}`}>
                    Assistance (kg)
                    <input
                      id={`series-assistance-${exerciseIndex}-${seriesIndex}`}
                      type="number"
                      min="0"
                      max="1000"
                      step="0.1"
                      placeholder="0"
                      value={series.assistance_kg}
                      onChange={(event) => changeSeries(exerciseIndex, seriesIndex, 'assistance_kg', event.target.value)}
                    />
                  </label>
                  <label htmlFor={`series-rpe-${exerciseIndex}-${seriesIndex}`}>
                    RPE *
                    <input
                      id={`series-rpe-${exerciseIndex}-${seriesIndex}`}
                      required
                      type="number"
                      min="1"
                      max="10"
                      placeholder="6"
                      value={series.difficulty}
                      onChange={(event) => changeSeries(exerciseIndex, seriesIndex, 'difficulty', event.target.value)}
                    />
                  </label>
                </div>
                {exercise.series.length > 1 && (
                  <button
                    type="button"
                    className="series-remove"
                    onClick={() => removeSeries(exerciseIndex, seriesIndex)}
                    disabled={submitting}
                  >
                    <Trash2 size={16} aria-hidden="true" />
                    Supprimer la série {seriesIndex + 1}
                  </button>
                )}
              </fieldset>
            ))}
          </div>
          <div className="actions exercise-actions">
            <button type="button" onClick={() => addSeries(exerciseIndex)} disabled={submitting}>
              <Plus size={16} aria-hidden="true" />
              Ajouter une série
            </button>
            <button
              type="button"
              className="danger"
              onClick={() => requestExerciseRemoval(exerciseIndex)}
              disabled={submitting}
            >
              <Trash2 size={16} aria-hidden="true" />
              Supprimer cet exercice
            </button>
          </div>
        </fieldset>
      ))}

      <div className="actions form-actions">
        <button
          type="button"
          onClick={() => change('exercises', [...form.exercises, blankExercise()])}
          disabled={submitting}
        >
          <Plus size={16} aria-hidden="true" />
          Ajouter un exercice
        </button>
        <button className="primary" type="submit" disabled={submitting}>
          <CalendarPlus size={16} aria-hidden="true" />
          {submitting ? 'Enregistrement…' : editing ? 'Enregistrer les modifications' : 'Enregistrer la séance'}
        </button>
        {editing && (
          <button type="button" onClick={onCancel} disabled={submitting}>
            Annuler la modification
          </button>
        )}
      </div>

      <ConfirmDialog
        open={pendingExerciseIndex !== null}
        title="Supprimer cet exercice ?"
        confirmLabel="Supprimer l’exercice"
        onCancel={() => setPendingExerciseIndex(null)}
        onConfirm={confirmExerciseRemoval}
      >
        <p>
          L’exercice <b>« {form.exercises[pendingExerciseIndex]?.exercise || `Exercice ${(pendingExerciseIndex ?? 0) + 1}`} »</b>
          {' '}et toutes ses séries seront retirés du formulaire.
        </p>
      </ConfirmDialog>
    </form>
  );
}

function WorkoutDetailDialog({workout, onClose}) {
  const exercises = groupWorkoutSets(workout?.sets || []);
  const seriesCount = exercises.reduce((total, exercise) => total + exercise.series.length, 0);
  return (
    <Dialog
      open={Boolean(workout)}
      title={workout ? `Détail — ${workout.title}` : 'Détail de la séance'}
      onClose={onClose}
      className="workout-detail-dialog"
      actions={<button type="button" onClick={onClose}>Fermer le détail</button>}
    >
      {workout && (
        <>
          <dl className="detail-metrics">
            <div><dt>Date</dt><dd>{workout.date}</dd></div>
            <div><dt>Type</dt><dd>{workout.type}</dd></div>
            <div><dt>Durée</dt><dd>{workout.duration_minutes} min</dd></div>
            <div><dt>Difficulté</dt><dd>RPE {workout.intensity}/10</dd></div>
            <div><dt>Volume</dt><dd>{workout.volume ?? 0}</dd></div>
            <div><dt>Séries</dt><dd>{seriesCount}</dd></div>
          </dl>
          <section aria-labelledby="detail-notes-title">
            <h3 id="detail-notes-title">Notes de séance</h3>
            <p>{workout.notes || 'Aucune note pour cette séance.'}</p>
          </section>
          <section aria-labelledby="detail-exercises-title">
            <h3 id="detail-exercises-title">Exercices et séries</h3>
            {exercises.map((exercise, exerciseIndex) => (
              <article className="detail-exercise" key={`${exercise.exercise}-${exerciseIndex}`}>
                <h4>{exercise.exercise} <small>· {exercise.category}</small></h4>
                {exercise.notes && <p>{exercise.notes}</p>}
                <ol>
                  {exercise.series.map((series, seriesIndex) => (
                    <li key={seriesIndex}>
                      <b>Série {seriesIndex + 1}</b> — {series.reps} répétition(s), {series.duration_seconds} s,
                      {' '}{series.load_kg} kg, assistance {series.assistance_kg} kg, RPE {series.difficulty}/10
                    </li>
                  ))}
                </ol>
              </article>
            ))}
          </section>
        </>
      )}
    </Dialog>
  );
}
