import React, {useCallback, useEffect, useState} from 'react';
import {CalendarPlus, Plus, Trash2} from 'lucide-react';
import {api} from './api';
import WorkoutCard from './WorkoutCard';
import {EmptyState, ErrorState, Header, Loader} from './ui';

const emptyExercise = {
  exercise: '',
  category: 'autre',
  set_count: 1,
  reps: 0,
  load_kg: 0,
  duration_seconds: 0,
  difficulty: 5,
  assistance_kg: 0,
  notes: '',
};

function newWorkout() {
  return {
    title: 'Séance planche',
    date: new Date().toISOString().slice(0, 10),
    type: 'Skill',
    intensity: 7,
    duration_minutes: 70,
    notes: '',
    sets: [
      {
        ...emptyExercise,
        exercise: 'Tuck planche hold',
        category: 'planche',
        duration_seconds: 20,
        difficulty: 7,
      },
    ],
  };
}

function editableWorkout(workout) {
  if (!workout) return newWorkout();
  return {
    title: workout.title,
    date: workout.date,
    type: workout.type,
    intensity: workout.intensity,
    duration_minutes: workout.duration_minutes,
    notes: workout.notes || '',
    sets: workout.sets.map((exercise) => ({...emptyExercise, ...exercise})),
  };
}

export default function WorkoutsPage({setToast}) {
  const [items, setItems] = useState([]);
  const [editing, setEditing] = useState(null);
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

  async function remove(workout) {
    const accepted = window.confirm(
      `Supprimer définitivement la séance « ${workout.title} » et tous ses exercices ?`,
    );
    if (!accepted) return;
    setDeletingId(workout.id);
    setError('');
    try {
      await api(`/workouts/${workout.id}`, {method: 'DELETE'});
      if (editing?.id === workout.id) setEditing(null);
      setToast('Séance supprimée');
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
      <Header title="Séances" sub="Créez, modifiez et supprimez des entraînements complets." />
      <WorkoutForm
        editing={editing}
        onCancel={() => setEditing(null)}
        onSaved={async (wasEditing) => {
          setEditing(null);
          setToast(wasEditing ? 'Séance modifiée' : 'Séance ajoutée');
          await load();
        }}
      />
      <section className="card" aria-labelledby="workout-history-title">
        <h2 id="workout-history-title">Historique des séances</h2>
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
              onEdit={startEditing}
              onDelete={remove}
              busy={deletingId === workout.id}
            />
          ))
        ) : (
          <EmptyState title="Aucune séance">
            Utilisez le formulaire ci-dessus pour enregistrer votre premier entraînement.
          </EmptyState>
        )}
      </section>
    </>
  );
}

export function WorkoutForm({editing, onCancel, onSaved}) {
  const [form, setForm] = useState(() => editableWorkout(editing));
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

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
      sets: current.sets.map((exercise, exerciseIndex) =>
        exerciseIndex === index ? {...exercise, [key]: value} : exercise,
      ),
    }));
  }

  function removeExercise(index) {
    if (form.sets.length === 1) {
      setError('Une séance doit contenir au moins un exercice.');
      return;
    }
    if (!window.confirm(`Supprimer l’exercice ${index + 1} de cette séance ?`)) return;
    change(
      'sets',
      form.sets.filter((_, exerciseIndex) => exerciseIndex !== index),
    );
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
        body: JSON.stringify(form),
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
      </p>
      {error && <p role="alert" className="error-message">{error}</p>}

      <fieldset>
        <legend>Informations générales</legend>
        <div className="fields">
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
            RPE global *
            <input
              id="workout-intensity"
              required
              type="number"
              min="1"
              max="10"
              placeholder="7"
              value={form.intensity}
              onChange={(event) => change('intensity', Number(event.target.value))}
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
              onChange={(event) => change('duration_minutes', Number(event.target.value))}
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

      <h3>Exercices</h3>
      <p className="small">Renseignez au minimum un exercice et son nombre de séries.</p>
      {form.sets.map((exercise, index) => (
        <fieldset className="exercise" key={index}>
          <legend>Exercice {index + 1}</legend>
          <div className="set">
            <label htmlFor={`exercise-name-${index}`}>
              Nom *
              <input
                id={`exercise-name-${index}`}
                required
                minLength="2"
                maxLength="160"
                placeholder="Ex. Tuck planche hold"
                value={exercise.exercise}
                onChange={(event) => changeExercise(index, 'exercise', event.target.value)}
              />
            </label>
            <label htmlFor={`exercise-category-${index}`}>
              Catégorie
              <input
                id={`exercise-category-${index}`}
                maxLength="40"
                placeholder="Ex. planche"
                value={exercise.category}
                onChange={(event) => changeExercise(index, 'category', event.target.value)}
              />
            </label>
            <label htmlFor={`exercise-sets-${index}`}>
              Séries *
              <input
                id={`exercise-sets-${index}`}
                required
                type="number"
                min="1"
                max="50"
                placeholder="3"
                value={exercise.set_count}
                onChange={(event) => changeExercise(index, 'set_count', Number(event.target.value))}
              />
            </label>
            <label htmlFor={`exercise-reps-${index}`}>
              Répétitions
              <input
                id={`exercise-reps-${index}`}
                type="number"
                min="0"
                max="1000"
                placeholder="8"
                value={exercise.reps}
                onChange={(event) => changeExercise(index, 'reps', Number(event.target.value))}
              />
            </label>
            <label htmlFor={`exercise-load-${index}`}>
              Charge (kg)
              <input
                id={`exercise-load-${index}`}
                type="number"
                min="0"
                max="1000"
                step="0.1"
                placeholder="0"
                value={exercise.load_kg}
                onChange={(event) => changeExercise(index, 'load_kg', Number(event.target.value))}
              />
            </label>
            <label htmlFor={`exercise-assistance-${index}`}>
              Assistance (kg)
              <input
                id={`exercise-assistance-${index}`}
                type="number"
                min="0"
                max="1000"
                step="0.1"
                placeholder="0"
                value={exercise.assistance_kg}
                onChange={(event) => changeExercise(index, 'assistance_kg', Number(event.target.value))}
              />
            </label>
            <label htmlFor={`exercise-duration-${index}`}>
              Durée (secondes)
              <input
                id={`exercise-duration-${index}`}
                type="number"
                min="0"
                max="86400"
                placeholder="20"
                value={exercise.duration_seconds}
                onChange={(event) =>
                  changeExercise(index, 'duration_seconds', Number(event.target.value))
                }
              />
            </label>
            <label htmlFor={`exercise-rpe-${index}`}>
              RPE *
              <input
                id={`exercise-rpe-${index}`}
                required
                type="number"
                min="1"
                max="10"
                placeholder="6"
                value={exercise.difficulty}
                onChange={(event) => changeExercise(index, 'difficulty', Number(event.target.value))}
              />
            </label>
            <label className="field-wide" htmlFor={`exercise-notes-${index}`}>
              Notes de l’exercice
              <textarea
                id={`exercise-notes-${index}`}
                maxLength="2000"
                placeholder="Tempo, technique, récupération…"
                value={exercise.notes}
                onChange={(event) => changeExercise(index, 'notes', event.target.value)}
              />
            </label>
          </div>
          <button
            type="button"
            className="danger"
            onClick={() => removeExercise(index)}
            disabled={submitting}
          >
            <Trash2 size={16} aria-hidden="true" />
            Supprimer cet exercice
          </button>
        </fieldset>
      ))}

      <div className="actions">
        <button
          type="button"
          onClick={() => change('sets', [...form.sets, {...emptyExercise}])}
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
    </form>
  );
}
