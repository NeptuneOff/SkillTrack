import {expect, test} from '@playwright/test';
import {apiUrl, installContainerApiProxy} from './support';

async function cleanupCreatedData(page, suffix) {
  const token = await page.evaluate(() => localStorage.getItem('token')).catch(() => null);
  if (!token) return;
  const headers = {Authorization: `Bearer ${token}`};

  const workoutsResponse = await page.request.get(`${apiUrl}/workouts`, {headers}).catch(() => null);
  if (workoutsResponse?.ok()) {
    const workouts = await workoutsResponse.json();
    for (const workout of workouts.filter((item) => item.title.includes(suffix))) {
      await page.request.delete(`${apiUrl}/workouts/${workout.id}`, {headers}).catch(() => null);
    }
  }

  const goalsResponse = await page.request.get(`${apiUrl}/goals`, {headers}).catch(() => null);
  if (goalsResponse?.ok()) {
    const goals = await goalsResponse.json();
    for (const goal of goals.filter((item) => item.skill.includes(suffix))) {
      await page.request.delete(`${apiUrl}/goals/${goal.id}`, {headers}).catch(() => null);
    }
  }

  const importsResponse = await page.request.get(`${apiUrl}/imports/history`, {headers}).catch(() => null);
  if (importsResponse?.ok()) {
    const imports = await importsResponse.json();
    for (const item of imports.filter((entry) => entry.filename.includes(suffix))) {
      await page.request.delete(`${apiUrl}/imports/history/${item.id}`, {headers}).catch(() => null);
    }
  }
}

test('parcours jury : authentification, CRUD, import, export et profil', async ({page}) => {
  const suffix = Date.now();
  const workoutTitle = `Jury E2E ${suffix}`;
  const updatedWorkoutTitle = `${workoutTitle} modifiée`;
  const goalSkill = `Objectif E2E ${suffix}`;
  const importedWorkoutTitle = `Import E2E ${suffix}`;

  try {
    await installContainerApiProxy(page);
    await page.goto('/');
    await expect(page.getByRole('heading', {name: 'Connexion'})).toBeVisible();
    await page.getByRole('button', {name: 'Se connecter'}).click();
    await expect(page.getByRole('heading', {name: 'Tableau de bord'})).toBeVisible();

    await page.getByRole('button', {name: 'Séances'}).click();
    await page.getByLabel('Titre *').fill(workoutTitle);
    await page.getByLabel('Nom *').fill('Tuck planche hold');
    await page.getByRole('button', {name: 'Ajouter une série'}).click();
    await page.getByLabel('Durée (secondes)').nth(0).fill('15');
    await page.getByLabel('Durée (secondes)').nth(1).fill('12');
    await page.getByRole('button', {name: 'Ajouter un exercice'}).click();
    await page.getByLabel('Nom *').nth(1).fill('Tractions lestées');
    await page.getByLabel('Répétitions').nth(1).fill('5');
    await page.getByRole('button', {name: 'Enregistrer la séance'}).click();
    let workout = page.locator('article.workout').filter({hasText: workoutTitle});
    await expect(workout).toBeVisible();

    await workout.getByRole('button', {name: 'Modifier'}).click();
    await page.getByLabel('Titre *').fill(updatedWorkoutTitle);
    await page.getByRole('button', {name: 'Enregistrer les modifications'}).click();
    workout = page.locator('article.workout').filter({hasText: updatedWorkoutTitle});
    await expect(workout).toBeVisible();

    await page.getByRole('button', {name: 'Objectifs'}).click();
    await page.getByLabel(/Nom de l’objectif \/ skill ou exercice/).fill(goalSkill);
    await page.getByLabel('Description de la cible *').fill('Tenir 8 secondes');
    await page.getByRole('button', {name: 'Ajouter l’objectif'}).click();
    let goal = page.locator('article.goal').filter({hasText: goalSkill});
    await expect(goal).toBeVisible();
    await goal.getByRole('button', {name: 'Modifier'}).click();
    await page.getByLabel('Description de la cible *').fill('Tenir 10 secondes');
    await page.getByRole('button', {name: 'Enregistrer les modifications'}).click();
    goal = page.locator('article.goal').filter({hasText: goalSkill});
    await expect(goal).toContainText('Tenir 10 secondes');
    await goal.getByRole('button', {name: 'Terminer'}).click();
    await expect(goal).toContainText('terminé');

    await page.getByRole('button', {name: 'Import / Export'}).click();
    await page.getByLabel('Fichier CSV UTF-8').setInputFiles({
      name: `jury-${suffix}.csv`,
      mimeType: 'text/csv',
      buffer: Buffer.from(
        `date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,reps,load_kg,duration_seconds,difficulty,assistance_kg,set_notes\n2026-08-19,${importedWorkoutTitle},Pull,6,45,Import Playwright,Pull-up,traction,3,5,0,0,6,0,Propre\nligne-invalide,Rejet,Push,7,45,Rejet,Dips,poussée,3,8,0,0,7,0,Date invalide\n`,
        'utf-8',
      ),
    });
    await page.getByRole('button', {name: 'Importer le fichier'}).click();
    await expect(page.getByRole('heading', {name: /Import terminé/})).toBeVisible();
    await expect(page.getByText('1 ligne(s) importée(s)')).toBeVisible();
    await expect(page.getByRole('rowheader', {name: `jury-${suffix}.csv`})).toBeVisible();

    for (const buttonName of ['Télécharger un CSV d’exemple', 'Export CSV', 'Export JSON']) {
      const downloadPromise = page.waitForEvent('download');
      await page.getByRole('button', {name: buttonName}).click();
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toBeTruthy();
      // Playwright conserve le téléchargement dans son répertoire temporaire ; aucun saveAs n’est effectué.
    }

    const importRow = page.getByRole('row').filter({hasText: `jury-${suffix}.csv`});
    page.once('dialog', (dialog) => dialog.accept());
    await importRow.getByRole('button', {name: `Supprimer l’historique jury-${suffix}.csv`}).click();
    await expect(importRow).toHaveCount(0);

    await page.getByRole('button', {name: 'Profil RGPD'}).click();
    await expect(page.getByRole('heading', {name: 'Mes informations'})).toBeVisible();
    await expect(page.getByText('demo@skilltrack.dev')).toBeVisible();

    await page.getByRole('button', {name: 'Séances'}).click();
    for (const title of [updatedWorkoutTitle, importedWorkoutTitle]) {
      const card = page.locator('article.workout').filter({hasText: title});
      await card.getByRole('button', {name: `Supprimer la séance ${title}`}).click();
      await page.getByRole('button', {name: 'Supprimer définitivement'}).click();
      await expect(card).toHaveCount(0);
    }

    await page.getByRole('button', {name: 'Objectifs'}).click();
    goal = page.locator('article.goal').filter({hasText: goalSkill});
    await goal.getByRole('button', {name: 'Supprimer'}).click();
    await page.getByRole('button', {name: 'Supprimer définitivement'}).click();
    await expect(goal).toHaveCount(0);
  } finally {
    await cleanupCreatedData(page, String(suffix));
  }
});
