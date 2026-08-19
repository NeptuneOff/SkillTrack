import React, {useState} from 'react';
import {act, cleanup, render, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/vitest';
import axe from 'axe-core';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

vi.mock('./api', () => ({api: vi.fn()}));
import {api} from './api';
import {App} from './main.jsx';
import {Toast} from './ui';

const dashboard = {
  workout_count: 2,
  set_count: 7,
  exercise_count: 3,
  total_volume: 420,
  total_duration_minutes: 135,
  average_intensity: 7,
  recent_progress_percent: 12,
  weekly_volume: [{week: '2026-W34', volume: 420}],
  goals: [
    {
      id: 'goal-dashboard',
      skill: 'Full planche',
      current_level: 'Straddle',
      target: 'Tenir 5 secondes',
    },
  ],
  recent_workouts: [],
};

const workoutFixture = {
  id: 'workout-1',
  title: 'Séance existante',
  date: '2026-08-19',
  type: 'Skill',
  intensity: 7,
  duration_minutes: 60,
  notes: 'Technique',
  volume: 30,
  sets: [
    {
      id: 'set-1',
      exercise: 'Tuck planche',
      category: 'planche',
      set_count: 3,
      reps: 0,
      load_kg: 0,
      assistance_kg: 0,
      duration_seconds: 20,
      difficulty: 7,
      notes: '',
    },
  ],
};

const goalFixture = {
  id: 'goal-1',
  skill: 'Full planche',
  goal_type: 'figure',
  target: 'Tenir 5 secondes',
  current_level: 'Straddle',
  current_value: 2,
  target_value: 5,
  unit: 'secondes',
  priority: 'haute',
  notes: '',
  deadline: null,
  status: 'actif',
  is_done: false,
};

function defaultApi(path) {
  if (path === '/dashboard') return Promise.resolve(dashboard);
  if (path === '/workouts') return Promise.resolve([]);
  if (path === '/goals') return Promise.resolve([]);
  if (path === '/imports/history') return Promise.resolve([]);
  if (path === '/users/me') {
    return Promise.resolve({
      id: 'user-1',
      email: 'demo@skilltrack.dev',
      display_name: 'Compte démo',
      created_at: '2026-08-19T10:00:00Z',
    });
  }
  return Promise.resolve({});
}

function renderAuthenticated() {
  localStorage.setItem('token', 'jwt-test');
  return render(<App />);
}

beforeEach(() => {
  localStorage.clear();
  api.mockReset();
  api.mockImplementation(defaultApi);
  vi.spyOn(window, 'confirm').mockReturnValue(true);
  vi.stubGlobal('requestAnimationFrame', vi.fn((callback) => {
    callback();
    return 1;
  }));
  document.documentElement.lang = 'fr';
  document.title = 'SkillTrack — Test';
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe('Authentification et session', () => {
  it('valide le formulaire, connecte le compte et affiche de vraies données du dashboard', async () => {
    api.mockImplementation((path) => {
      if (path === '/auth/login') return Promise.resolve({access_token: 'jwt-valid'});
      return defaultApi(path);
    });
    const user = userEvent.setup();
    render(<App />);

    const email = screen.getByLabelText('Adresse email *');
    expect(email).toHaveAttribute('type', 'email');
    expect(screen.getByLabelText('Mot de passe *')).toHaveAttribute('minlength', '8');
    await user.clear(email);
    await user.click(screen.getByRole('button', {name: 'Se connecter'}));
    expect(api).not.toHaveBeenCalled();

    await user.type(email, 'demo@skilltrack.dev');
    await user.click(screen.getByRole('button', {name: 'Se connecter'}));

    expect(await screen.findByRole('heading', {name: 'Tableau de bord'})).toBeVisible();
    expect(localStorage.getItem('token')).toBe('jwt-valid');
    expect(screen.getByLabelText('Séances : 2')).toBeVisible();
    expect(screen.getByLabelText('Volume : 420')).toBeVisible();
    expect(screen.getByRole('status')).toHaveTextContent('Connexion réussie');
  });

  it('déconnecte réellement l’interface lorsqu’une réponse 401 est signalée', async () => {
    renderAuthenticated();
    expect(await screen.findByRole('heading', {name: 'Tableau de bord'})).toBeVisible();

    act(() => window.dispatchEvent(new Event('skilltrack:unauthorized')));

    expect(await screen.findByRole('heading', {name: 'Connexion'})).toBeVisible();
    expect(localStorage.getItem('token')).toBeNull();
    expect(screen.getByRole('alert')).toHaveTextContent('Session expirée');
  });

  it('fait disparaître automatiquement une notification et permet de la fermer', () => {
    vi.useFakeTimers();
    function ToastHarness() {
      const [message, setMessage] = useState('Action terminée');
      return <Toast message={message} onClose={() => setMessage('')} />;
    }
    render(<ToastHarness />);
    expect(screen.getByRole('status')).toBeVisible();
    act(() => vi.advanceTimersByTime(4500));
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });
});

describe('Séances réelles', () => {
  it('crée, modifie et supprime une séance avec ajout et suppression d’exercice', async () => {
    let workouts = [structuredClone(workoutFixture)];
    api.mockImplementation((path, options = {}) => {
      if (path === '/dashboard') return Promise.resolve(dashboard);
      if (path === '/workouts' && !options.method) return Promise.resolve(structuredClone(workouts));
      if (path === '/workouts' && options.method === 'POST') {
        const created = {...JSON.parse(options.body), id: 'workout-created', volume: 0};
        created.sets = created.sets.map((set, index) => ({...set, id: `new-set-${index}`}));
        workouts = [...workouts, created];
        return Promise.resolve(created);
      }
      if (path.startsWith('/workouts/') && options.method === 'PUT') {
        const id = path.split('/').at(-1);
        const updated = {...JSON.parse(options.body), id, volume: 0};
        workouts = workouts.map((workout) => (workout.id === id ? updated : workout));
        return Promise.resolve(updated);
      }
      if (path.startsWith('/workouts/') && options.method === 'DELETE') {
        const id = path.split('/').at(-1);
        workouts = workouts.filter((workout) => workout.id !== id);
        return Promise.resolve({deleted: true});
      }
      return defaultApi(path);
    });
    const user = userEvent.setup();
    renderAuthenticated();
    await user.click(screen.getByRole('button', {name: 'Séances'}));
    expect(await screen.findByRole('heading', {name: 'Historique des séances'})).toBeVisible();

    await user.click(screen.getByRole('button', {name: 'Ajouter un exercice'}));
    expect(screen.getAllByLabelText('Nom *')).toHaveLength(2);
    await user.click(screen.getAllByRole('button', {name: 'Supprimer cet exercice'})[1]);
    expect(screen.getAllByLabelText('Nom *')).toHaveLength(1);
    expect(window.confirm).toHaveBeenCalledWith('Supprimer l’exercice 2 de cette séance ?');

    await user.clear(screen.getByLabelText('Titre *'));
    await user.type(screen.getByLabelText('Titre *'), 'Séance créée');
    await user.click(screen.getByRole('button', {name: 'Enregistrer la séance'}));
    expect(await screen.findByRole('heading', {name: 'Séance créée'})).toBeVisible();
    expect(api).toHaveBeenCalledWith('/workouts', expect.objectContaining({method: 'POST'}));

    let card = screen.getByRole('heading', {name: 'Séance créée'}).closest('article');
    await user.click(within(card).getByRole('button', {name: 'Modifier'}));
    await user.clear(screen.getByLabelText('Titre *'));
    await user.type(screen.getByLabelText('Titre *'), 'Séance modifiée');
    await user.click(screen.getByRole('button', {name: 'Enregistrer les modifications'}));
    expect(await screen.findByRole('heading', {name: 'Séance modifiée'})).toBeVisible();
    expect(api).toHaveBeenCalledWith(
      '/workouts/workout-created',
      expect.objectContaining({method: 'PUT'}),
    );

    card = screen.getByRole('heading', {name: 'Séance modifiée'}).closest('article');
    await user.click(within(card).getByRole('button', {name: 'Supprimer la séance Séance modifiée'}));
    await waitFor(() => expect(screen.queryByRole('heading', {name: 'Séance modifiée'})).not.toBeInTheDocument());
    expect(api).toHaveBeenCalledWith('/workouts/workout-created', {method: 'DELETE'});
  });
});

describe('Objectifs réels', () => {
  it('crée, modifie, termine puis supprime un objectif', async () => {
    let goals = [];
    api.mockImplementation((path, options = {}) => {
      if (path === '/dashboard') return Promise.resolve(dashboard);
      if (path === '/goals' && !options.method) return Promise.resolve(structuredClone(goals));
      if (path === '/goals' && options.method === 'POST') {
        const created = {...JSON.parse(options.body), id: 'goal-created'};
        goals = [...goals, created];
        return Promise.resolve(created);
      }
      if (path.startsWith('/goals/') && options.method === 'PUT') {
        const id = path.split('/').at(-1);
        const updated = {...JSON.parse(options.body), id};
        goals = goals.map((goal) => (goal.id === id ? updated : goal));
        return Promise.resolve(updated);
      }
      if (path.startsWith('/goals/') && options.method === 'DELETE') {
        const id = path.split('/').at(-1);
        goals = goals.filter((goal) => goal.id !== id);
        return Promise.resolve({deleted: true});
      }
      return defaultApi(path);
    });
    const user = userEvent.setup();
    renderAuthenticated();
    await user.click(screen.getByRole('button', {name: 'Objectifs'}));
    expect(await screen.findByRole('heading', {name: 'Mes objectifs'})).toBeVisible();

    await user.type(screen.getByLabelText('Skill ou exercice *'), 'Front lever');
    await user.type(screen.getByLabelText('Description de la cible *'), 'Tenir 8 secondes');
    await user.click(screen.getByRole('button', {name: 'Ajouter l’objectif'}));
    expect(await screen.findByRole('heading', {name: /Front lever/})).toBeVisible();

    let card = screen.getByRole('heading', {name: /Front lever/}).closest('article');
    await user.click(within(card).getByRole('button', {name: 'Modifier'}));
    await user.clear(screen.getByLabelText('Description de la cible *'));
    await user.type(screen.getByLabelText('Description de la cible *'), 'Tenir 10 secondes');
    await user.click(screen.getByRole('button', {name: 'Enregistrer les modifications'}));
    card = screen.getByRole('heading', {name: /Front lever/}).closest('article');
    expect(within(card).getByText(/Tenir 10 secondes/)).toBeVisible();

    await user.click(within(card).getByRole('button', {name: 'Terminer'}));
    card = screen.getByRole('heading', {name: /Front lever/}).closest('article');
    expect(within(card).getByRole('button', {name: 'Réouvrir'})).toBeVisible();
    expect(within(card).getByText(/terminé/)).toBeVisible();

    await user.click(within(card).getByRole('button', {name: 'Supprimer'}));
    expect(await screen.findByRole('heading', {name: 'Aucun objectif'})).toBeVisible();
    expect(api).toHaveBeenCalledWith('/goals/goal-created', {method: 'DELETE'});
  });
});

describe('Import, export et profil', () => {
  it('importe un CSV, affiche son rapport et son historique, puis déclenche les trois exports', async () => {
    let history = [
      {
        id: 'import-old',
        filename: 'ancien.csv',
        imported_rows: 3,
        rejected_rows: 0,
        ignored_rows: 0,
        errors: [],
        created_at: '2026-08-18T10:00:00Z',
      },
    ];
    api.mockImplementation((path, options = {}) => {
      if (path === '/dashboard') return Promise.resolve(dashboard);
      if (path === '/imports/history') return Promise.resolve(structuredClone(history));
      if (path === '/imports/csv' && options.method === 'POST') {
        history = [
          {
            id: 'import-new',
            filename: 'jury.csv',
            imported_rows: 1,
            rejected_rows: 1,
            ignored_rows: 0,
            errors: ['Ligne 3 : date invalide'],
            created_at: '2026-08-19T10:00:00Z',
          },
          ...history,
        ];
        return Promise.resolve({
          id: 'import-new',
          import_id: 'import-new',
          imported_rows: 1,
          rejected_rows: 1,
          ignored_rows: 0,
          errors: ['Ligne 3 : date invalide'],
        });
      }
      if (path.startsWith('/imports/history/') && options.method === 'DELETE') {
        const id = path.split('/').at(-1);
        history = history.filter((item) => item.id !== id);
        return Promise.resolve({deleted: true});
      }
      if (options.download) return Promise.resolve(null);
      return defaultApi(path);
    });
    const user = userEvent.setup();
    renderAuthenticated();
    await user.click(screen.getByRole('button', {name: 'Import / Export'}));
    expect(await screen.findByRole('rowheader', {name: 'ancien.csv'})).toBeVisible();

    const file = new File(
      ['date,title,exercise\n2026-08-19,Import test,Pull-up\n'],
      'jury.csv',
      {type: 'text/csv'},
    );
    await user.upload(screen.getByLabelText('Fichier CSV UTF-8'), file);
    expect(await screen.findByRole('heading', {name: 'Rapport du dernier import'})).toBeVisible();
    expect(screen.getAllByText('Ligne 3 : date invalide')).toHaveLength(2);
    expect(await screen.findByRole('rowheader', {name: 'jury.csv'})).toBeVisible();

    for (const [name, path] of [
      ['Télécharger un CSV d’exemple', '/imports/example'],
      ['Export CSV', '/exports/csv'],
      ['Export JSON', '/exports/json'],
    ]) {
      await user.click(screen.getByRole('button', {name}));
      expect(api).toHaveBeenCalledWith(path, {download: true});
    }

    await user.click(screen.getByRole('button', {name: 'Supprimer l’historique jury.csv'}));
    await waitFor(() => expect(screen.queryByRole('rowheader', {name: 'jury.csv'})).not.toBeInTheDocument());
    expect(api).toHaveBeenCalledWith('/imports/history/import-new', {method: 'DELETE'});
  });

  it('affiche le profil, exporte les données et confirme la suppression du compte', async () => {
    api.mockImplementation((path, options = {}) => {
      if (path === '/dashboard') return Promise.resolve(dashboard);
      if (path === '/users/me' && options.method === 'DELETE') {
        return Promise.resolve({deleted: true});
      }
      if (path === '/exports/json' && options.download) return Promise.resolve(null);
      return defaultApi(path);
    });
    const user = userEvent.setup();
    renderAuthenticated();
    await user.click(screen.getByRole('button', {name: 'Profil RGPD'}));
    expect(await screen.findByText('demo@skilltrack.dev')).toBeVisible();

    await user.click(screen.getByRole('button', {name: 'Exporter mes données'}));
    expect(api).toHaveBeenCalledWith('/exports/json', {download: true});
    await user.click(screen.getByRole('button', {name: 'Supprimer mon compte et mes données'}));

    expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining('action est irréversible'));
    expect(await screen.findByRole('heading', {name: 'Connexion'})).toBeVisible();
    expect(api).toHaveBeenCalledWith('/users/me', {method: 'DELETE'});
  });
});

describe('Navigation et accessibilité', () => {
  it('n’effondre pas l’application en naviguant depuis Séances vers toutes les pages', async () => {
    const user = userEvent.setup();
    renderAuthenticated();
    await user.click(screen.getByRole('button', {name: 'Séances'}));
    expect(await screen.findByRole('heading', {name: 'Séances'})).toBeVisible();

    for (const [button, heading] of [
      ['Objectifs', 'Objectifs'],
      ['Import / Export', 'Import / Export'],
      ['Profil RGPD', 'Profil et RGPD'],
      ['Dashboard', 'Tableau de bord'],
    ]) {
      await user.click(screen.getByRole('button', {name: button}));
      expect(await screen.findByRole('heading', {name: heading})).toBeVisible();
      expect(screen.getByRole('navigation', {name: 'Navigation principale'})).toBeVisible();
    }
  });

  it('ne présente aucune violation axe sur les vues principales', async () => {
    const axeOptions = {rules: {'color-contrast': {enabled: false}}};
    render(<App />);
    expect(await screen.findByRole('heading', {name: 'Connexion'})).toBeVisible();
    expect((await axe.run(document.body, axeOptions)).violations).toEqual([]);
    cleanup();

    api.mockImplementation((path) => {
      if (path === '/workouts') return Promise.resolve([workoutFixture]);
      if (path === '/goals') return Promise.resolve([goalFixture]);
      if (path === '/imports/history') {
        return Promise.resolve([
          {
            id: 'axe-import',
            filename: 'accessibilite.csv',
            imported_rows: 1,
            rejected_rows: 0,
            ignored_rows: 0,
            errors: [],
            created_at: '2026-08-19T10:00:00Z',
          },
        ]);
      }
      return defaultApi(path);
    });
    const user = userEvent.setup();
    renderAuthenticated();
    expect(await screen.findByRole('heading', {name: 'Tableau de bord'})).toBeVisible();
    expect((await axe.run(document.body, axeOptions)).violations).toEqual([]);

    for (const [button, heading] of [
      ['Séances', 'Séances'],
      ['Objectifs', 'Objectifs'],
      ['Import / Export', 'Import / Export'],
      ['Profil RGPD', 'Profil et RGPD'],
    ]) {
      await user.click(screen.getByRole('button', {name: button}));
      expect(await screen.findByRole('heading', {name: heading})).toBeVisible();
      expect((await axe.run(document.body, axeOptions)).violations).toEqual([]);
    }
  });
});
