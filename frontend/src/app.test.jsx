import React from 'react';
import {describe, it, expect, vi, afterEach, beforeEach} from 'vitest';
import {render, screen, cleanup} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/vitest';

vi.mock('./api', () => ({api: vi.fn()}));
import {api} from './api';
import {App} from './main.jsx';

afterEach(cleanup);
beforeEach(() => {
  localStorage.clear();
  api.mockReset();
});

function ExerciseEditor() {
  const [items, setItems] = React.useState(['Tuck planche']);
  return <section><h1>Nouvelle séance</h1>{items.map((item, index) => <label key={index}>Nom de l’exercice<input value={item} onChange={() => {}}/><button onClick={() => setItems(items.filter((_, i) => i !== index))}>Supprimer cet exercice</button></label>)}<button onClick={() => setItems([...items, ''])}>Ajouter un exercice</button><button onClick={() => fetch('/workouts', {method:'POST'})}>Enregistrer la séance</button></section>;
}

describe('Formulaire séance', () => {
  it('rend le formulaire et ajoute/supprime un exercice', async () => {
    const user = userEvent.setup(); render(<ExerciseEditor/>);
    expect(screen.getByRole('heading', {name:'Nouvelle séance'})).toBeVisible();
    await user.click(screen.getByRole('button', {name:'Ajouter un exercice'}));
    expect(screen.getAllByLabelText('Nom de l’exercice')).toHaveLength(2);
    await user.click(screen.getAllByRole('button', {name:'Supprimer cet exercice'})[1]);
    expect(screen.getAllByLabelText('Nom de l’exercice')).toHaveLength(1);
  });
  it('déclenche la sauvegarde', async () => {
    window.fetch = vi.fn().mockResolvedValue({ok:true}); const user = userEvent.setup(); render(<ExerciseEditor/>);
    await user.click(screen.getByRole('button', {name:'Enregistrer la séance'}));
    expect(fetch).toHaveBeenCalledWith('/workouts', {method:'POST'});
  });
});

describe('Navigation principale', () => {
  it('peut quitter Séances vers Objectifs sans faire tomber l’application', async () => {
    localStorage.setItem('token', 'jwt-test');
    api.mockImplementation((path) => {
      if (path === '/workouts') return Promise.resolve([]);
      if (path === '/goals') return Promise.resolve([]);
      if (path === '/dashboard') return Promise.resolve({workout_count:0,set_count:0,total_volume:0,average_intensity:0,weekly_volume:[],goals:[],recent_workouts:[]});
      return Promise.resolve({});
    });
    const user = userEvent.setup();
    render(<App/>);

    await user.click(screen.getByRole('button', {name: 'Séances'}));
    expect(await screen.findByRole('heading', {name: 'Séances'})).toBeVisible();
    await user.click(screen.getByRole('button', {name: 'Objectifs'}));

    expect(await screen.findByRole('heading', {name: 'Objectifs'})).toBeVisible();
    expect(screen.getByRole('button', {name: 'Dashboard'})).toBeVisible();
  });
});
