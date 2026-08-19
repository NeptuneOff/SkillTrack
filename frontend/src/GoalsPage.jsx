import React, {useCallback, useEffect, useState} from 'react';
import {CheckCircle, Pencil, Trash2} from 'lucide-react';
import {api} from './api';
import {EmptyState, ErrorState, Header, Loader} from './ui';

const emptyGoal = {
  skill: '',
  goal_type: 'figure',
  target: '',
  current_level: '',
  current_value: 0,
  target_value: 1,
  unit: 'secondes',
  priority: 'moyenne',
  notes: '',
  deadline: '',
  status: 'actif',
  is_done: false,
};

const statusLabels = {actif: 'actif', termine: 'terminé', archive: 'archivé'};

function goalToForm(goal) {
  return Object.fromEntries(
    Object.keys(emptyGoal).map((key) => [key, key === 'deadline' ? goal[key] || '' : goal[key]]),
  );
}

export default function GoalsPage({setToast}) {
  const [goals, setGoals] = useState([]);
  const [form, setForm] = useState(emptyGoal);
  const [editingId, setEditingId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [busyId, setBusyId] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setGoals(await api('/goals'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function change(key, value) {
    setForm((current) => ({...current, [key]: value}));
  }

  function resetForm() {
    setForm(emptyGoal);
    setEditingId('');
    setError('');
  }

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const payload = {
        ...form,
        deadline: form.deadline || null,
        is_done: form.status === 'termine',
      };
      await api(editingId ? `/goals/${editingId}` : '/goals', {
        method: editingId ? 'PUT' : 'POST',
        body: JSON.stringify(payload),
      });
      const wasEditing = Boolean(editingId);
      resetForm();
      await load();
      setToast(wasEditing ? 'Objectif modifié' : 'Objectif ajouté');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function edit(goal) {
    setEditingId(goal.id);
    setForm(goalToForm(goal));
    setError('');
    window.requestAnimationFrame(() => document.querySelector('#goal-form-title')?.focus());
  }

  async function toggleComplete(goal) {
    setBusyId(goal.id);
    setError('');
    try {
      const {id: _id, ...values} = goal;
      const completed = !goal.is_done;
      await api(`/goals/${goal.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          ...values,
          status: completed ? 'termine' : 'actif',
          is_done: completed,
        }),
      });
      await load();
      setToast(completed ? 'Objectif terminé' : 'Objectif réouvert');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId('');
    }
  }

  async function remove(goal) {
    if (!window.confirm(`Supprimer définitivement l’objectif « ${goal.skill} » ?`)) return;
    setBusyId(goal.id);
    setError('');
    try {
      await api(`/goals/${goal.id}`, {method: 'DELETE'});
      if (editingId === goal.id) resetForm();
      await load();
      setToast('Objectif supprimé');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId('');
    }
  }

  return (
    <>
      <Header
        title="Objectifs"
        sub="Créez une cible mesurable, suivez sa progression et gérez son cycle de vie."
      />
      <form className="card form" onSubmit={submit} aria-describedby="goal-form-help">
        <h2 id="goal-form-title" tabIndex="-1">
          {editingId ? 'Modifier l’objectif' : 'Créer un objectif'}
        </h2>
        <p className="small" id="goal-form-help">
          Exemple : « Tenir une full planche 5 secondes ». Les champs marqués * sont obligatoires.
        </p>
        {error && <p role="alert" className="error-message">{error}</p>}
        <div className="fields">
          <label htmlFor="goal-skill">
            Skill ou exercice *
            <input
              id="goal-skill"
              required
              minLength="2"
              maxLength="120"
              placeholder="Ex. Full planche"
              value={form.skill}
              onChange={(event) => change('skill', event.target.value)}
            />
          </label>
          <label htmlFor="goal-type">
            Type *
            <select
              id="goal-type"
              required
              value={form.goal_type}
              onChange={(event) => change('goal_type', event.target.value)}
            >
              {['figure', 'force', 'mobilité', 'volume', 'régularité'].map((type) => (
                <option key={type}>{type}</option>
              ))}
            </select>
          </label>
          <label htmlFor="goal-target">
            Description de la cible *
            <input
              id="goal-target"
              required
              minLength="2"
              maxLength="160"
              placeholder="Ex. Tenir 5 secondes"
              value={form.target}
              onChange={(event) => change('target', event.target.value)}
            />
          </label>
          <label htmlFor="goal-level">
            Niveau actuel
            <input
              id="goal-level"
              maxLength="160"
              placeholder="Ex. Straddle 2 secondes"
              value={form.current_level}
              onChange={(event) => change('current_level', event.target.value)}
            />
          </label>
          <label htmlFor="goal-deadline">
            Date cible
            <input
              id="goal-deadline"
              type="date"
              value={form.deadline}
              onChange={(event) => change('deadline', event.target.value)}
            />
          </label>
        </div>
        <div className="fields">
          <label htmlFor="goal-current-value">
            Valeur actuelle
            <input
              id="goal-current-value"
              type="number"
              min="0"
              step="0.1"
              placeholder="0"
              value={form.current_value}
              onChange={(event) => change('current_value', Number(event.target.value))}
            />
          </label>
          <label htmlFor="goal-target-value">
            Valeur cible *
            <input
              id="goal-target-value"
              required
              type="number"
              min="0.1"
              step="0.1"
              placeholder="5"
              value={form.target_value}
              onChange={(event) => change('target_value', Number(event.target.value))}
            />
          </label>
          <label htmlFor="goal-unit">
            Unité *
            <select
              id="goal-unit"
              required
              value={form.unit}
              onChange={(event) => change('unit', event.target.value)}
            >
              {['secondes', 'répétitions', 'kg', 'séances/semaine', 'autre'].map((unit) => (
                <option key={unit}>{unit}</option>
              ))}
            </select>
          </label>
          <label htmlFor="goal-priority">
            Priorité *
            <select
              id="goal-priority"
              required
              value={form.priority}
              onChange={(event) => change('priority', event.target.value)}
            >
              {['basse', 'moyenne', 'haute'].map((priority) => (
                <option key={priority}>{priority}</option>
              ))}
            </select>
          </label>
          <label htmlFor="goal-status">
            Statut *
            <select
              id="goal-status"
              required
              value={form.status}
              onChange={(event) => change('status', event.target.value)}
            >
              <option value="actif">actif</option>
              <option value="termine">terminé</option>
              <option value="archive">archivé</option>
            </select>
          </label>
        </div>
        <label htmlFor="goal-notes">
          Notes
          <textarea
            id="goal-notes"
            maxLength="2000"
            placeholder="Plan d’action, fréquence, contraintes…"
            value={form.notes}
            onChange={(event) => change('notes', event.target.value)}
          />
        </label>
        <div className="actions">
          <button className="primary" type="submit" disabled={submitting}>
            {submitting
              ? 'Enregistrement…'
              : editingId
                ? 'Enregistrer les modifications'
                : 'Ajouter l’objectif'}
          </button>
          {editingId && (
            <button type="button" onClick={resetForm} disabled={submitting}>
              Annuler la modification
            </button>
          )}
        </div>
      </form>

      <section className="card" aria-labelledby="goals-list-title">
        <h2 id="goals-list-title">Mes objectifs</h2>
        {loading ? (
          <Loader label="Chargement des objectifs…" />
        ) : error && !goals.length ? (
          <ErrorState message={error} onRetry={load} />
        ) : goals.length ? (
          goals.map((goal) => {
            const progress = Math.min(
              100,
              Math.max(0, Math.round((goal.current_value / goal.target_value) * 100)),
            );
            return (
              <article className="goal" key={goal.id}>
                <div>
                  <h3>
                    {goal.skill} <small>· {statusLabels[goal.status] || goal.status}</small>
                  </h3>
                  <p>
                    {goal.current_level || 'Départ non renseigné'} → {goal.target}
                  </p>
                  <div
                    className="progress"
                    role="progressbar"
                    aria-label={`Progression de ${goal.skill}`}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={progress}
                    aria-valuetext={`${progress} %`}
                  >
                    <span style={{width: `${progress}%`}} />
                  </div>
                  <p className="small">
                    {goal.current_value} / {goal.target_value} {goal.unit} · priorité {goal.priority}
                    {goal.deadline ? ` · échéance ${goal.deadline}` : ''}
                  </p>
                  {goal.notes && <p>{goal.notes}</p>}
                </div>
                <div className="actions">
                  <button type="button" onClick={() => edit(goal)} disabled={busyId === goal.id}>
                    <Pencil aria-hidden="true" />
                    Modifier
                  </button>
                  <button
                    type="button"
                    onClick={() => toggleComplete(goal)}
                    disabled={busyId === goal.id}
                  >
                    <CheckCircle aria-hidden="true" />
                    {goal.is_done ? 'Réouvrir' : 'Terminer'}
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={() => remove(goal)}
                    disabled={busyId === goal.id}
                  >
                    <Trash2 aria-hidden="true" />
                    Supprimer
                  </button>
                </div>
              </article>
            );
          })
        ) : (
          <EmptyState title="Aucun objectif">
            Utilisez le formulaire ci-dessus pour définir votre première cible.
          </EmptyState>
        )}
      </section>
    </>
  );
}
