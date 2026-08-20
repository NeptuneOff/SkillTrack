import fs from 'node:fs/promises';
import path from 'node:path';
import {expect, test} from '@playwright/test';
import {apiUrl, installContainerApiProxy} from './support';

test.use({
  viewport: {width: 1600, height: 1100},
  deviceScaleFactor: 1,
  locale: 'fr-FR',
  timezoneId: 'Europe/Paris',
  reducedMotion: 'reduce',
  colorScheme: 'dark',
});

test.setTimeout(180_000);

const captureDir = process.env.RNCP_CAPTURE_DIR
  || path.resolve(process.cwd(), '../artifacts/rncp/screenshots');
const prefix = 'CAPTURE RNCP';

async function screenshot(page, filename, options = {}) {
  const destination = path.join(captureDir, filename);
  await page.waitForTimeout(120);
  if (options.locator) {
    await options.locator.scrollIntoViewIfNeeded();
    await expect(options.locator).toBeVisible();
    await options.locator.screenshot({path: destination, animations: 'disabled'});
    return;
  }
  await page.screenshot({
    path: destination,
    fullPage: options.fullPage ?? false,
    animations: 'disabled',
  });
}

async function authenticatedRequest(request, method, route, token, data) {
  const response = await request[method](`${apiUrl}${route}`, {
    headers: {Authorization: `Bearer ${token}`},
    ...(data === undefined ? {} : {data}),
  });
  expect(response.ok(), `${method.toUpperCase()} ${route} doit réussir`).toBeTruthy();
  return response.status() === 204 ? null : response.json();
}

async function cleanupCaptureData(request, token) {
  const headers = {Authorization: `Bearer ${token}`};
  const importsResponse = await request.get(`${apiUrl}/imports/history`, {headers}).catch(() => null);
  if (importsResponse?.ok()) {
    const imports = await importsResponse.json();
    for (const item of imports.filter((entry) => entry.filename.startsWith('rncp-capture-'))) {
      await request.delete(`${apiUrl}/imports/history/${item.id}`, {headers}).catch(() => null);
    }
  }

  const workoutsResponse = await request.get(`${apiUrl}/workouts`, {headers}).catch(() => null);
  if (workoutsResponse?.ok()) {
    const workouts = await workoutsResponse.json();
    for (const workout of workouts.filter((entry) => entry.title.startsWith(prefix))) {
      await request.delete(`${apiUrl}/workouts/${workout.id}`, {headers}).catch(() => null);
    }
  }

  const goalsResponse = await request.get(`${apiUrl}/goals`, {headers}).catch(() => null);
  if (goalsResponse?.ok()) {
    const goals = await goalsResponse.json();
    for (const goal of goals.filter((entry) => entry.skill.startsWith(prefix))) {
      await request.delete(`${apiUrl}/goals/${goal.id}`, {headers}).catch(() => null);
    }
  }
}

async function createFixtures(request, token) {
  const workout = await authenticatedRequest(request, 'post', '/workouts', token, {
    title: `${prefix} · Handstand et planche`,
    date: '2026-08-20',
    type: 'Skill',
    intensity: 8,
    duration_minutes: 75,
    notes: 'Lignes propres, meilleure stabilité et aucune douleur signalée.',
    sets: [
      {
        exercise: 'Handstand hold', category: 'équilibre', set_count: 4, reps: 0,
        load_kg: 0, duration_seconds: 35, difficulty: 7, assistance_kg: 0,
        notes: 'Sortie contrôlée contre le mur.',
      },
      {
        exercise: 'Advanced tuck planche', category: 'planche', set_count: 5, reps: 0,
        load_kg: 0, duration_seconds: 9, difficulty: 9, assistance_kg: 8,
        notes: 'Bassin aligné et protraction active.',
      },
      {
        exercise: 'Dips lestés', category: 'poussée', set_count: 4, reps: 5,
        load_kg: 13, duration_seconds: 0, difficulty: 8, assistance_kg: 0,
        notes: 'Amplitude complète et descente contrôlée.',
      },
    ],
  });

  const goalBase = {
    goal_type: 'figure',
    unit: 'secondes',
    priority: 'haute',
    deadline: '2026-12-20',
    notes: 'Suivi de démonstration pour le dossier RNCP.',
  };
  const goals = [];
  goals.push(await authenticatedRequest(request, 'post', '/goals', token, {
    ...goalBase,
    skill: `${prefix} · Full planche`,
    target: 'Tenir une full planche 5 secondes',
    current_level: 'Straddle planche 3 secondes',
    current_value: 3,
    target_value: 5,
    status: 'actif',
    is_done: false,
  }));
  goals.push(await authenticatedRequest(request, 'post', '/goals', token, {
    ...goalBase,
    skill: `${prefix} · Front lever`,
    target: 'Tenir un front lever 20 secondes',
    current_level: 'Objectif atteint',
    current_value: 20,
    target_value: 20,
    status: 'termine',
    is_done: true,
  }));
  goals.push(await authenticatedRequest(request, 'post', '/goals', token, {
    ...goalBase,
    skill: `${prefix} · Mobilité épaules`,
    goal_type: 'mobilité',
    target: 'Routine complète trois fois par semaine',
    current_level: 'Objectif mis en pause',
    current_value: 1,
    target_value: 3,
    unit: 'séances/semaine',
    priority: 'basse',
    status: 'archive',
    is_done: false,
  }));
  return {workout, goals};
}

test('génère les 32 preuves visuelles RNCP depuis l’interface réelle', async ({page, request}) => {
  test.skip(!process.env.RNCP_CAPTURE_DIR, 'Définir RNCP_CAPTURE_DIR pour générer les preuves PNG.');
  await fs.mkdir(captureDir, {recursive: true});
  const loginResponse = await request.post(`${apiUrl}/auth/login`, {
    data: {email: 'demo@skilltrack.dev', password: 'DemoPassword123!'},
  });
  expect(loginResponse.ok()).toBeTruthy();
  const {access_token: token} = await loginResponse.json();

  await cleanupCaptureData(request, token);
  await createFixtures(request, token);

  try {
    await installContainerApiProxy(page);
    await page.addInitScript(() => localStorage.removeItem('token'));
    await page.goto('/');
    await expect(page.getByRole('heading', {name: 'Connexion'})).toBeVisible();
    await screenshot(page, 'P01_page_connexion.png');

    await page.getByRole('button', {name: 'Se connecter'}).click();
    await expect(page.getByRole('heading', {name: 'Tableau de bord'})).toBeVisible();
    await expect(page.getByText('Dernière séance', {exact: true})).toBeVisible();
    await screenshot(page, 'P02_dashboard_apres_connexion.png');
    await screenshot(page, 'P03_navigation_generale.png', {
      locator: page.getByRole('complementary', {name: 'Présentation et navigation SkillTrack'}),
    });
    await screenshot(page, 'P04_dashboard_stats_detaillees.png', {
      locator: page.locator('section.grid4'),
    });
    await page.getByRole('button', {name: 'Fermer la notification'}).click().catch(() => null);

    await page.getByRole('button', {name: 'Séances'}).click();
    const workoutHistory = page.locator('section.card').filter({has: page.getByRole('heading', {name: 'Historique des séances'})});
    await expect(workoutHistory).toBeVisible();
    await screenshot(page, 'P05_page_seances_liste.png', {locator: workoutHistory});

    const workoutForm = page.locator('form.card.form');
    await screenshot(page, 'P06_formulaire_creation_seance_vide.png', {locator: workoutForm});
    await page.getByLabel('Titre *').fill(`${prefix} · Séance Planche / Front Lever`);
    await page.getByLabel('Date *').fill('2026-08-20');
    await page.getByLabel('Type *').selectOption({label: 'Skill'});
    await page.getByLabel('Difficulté globale (RPE) *').fill('8');
    await page.getByLabel('Durée (minutes) *').fill('80');
    await page.getByLabel('Notes de séance').fill('Travail technique : planche, front lever et gainage sans douleur.');
    await screenshot(page, 'P07_formulaire_creation_seance_rempli.png', {
      locator: workoutForm.locator('fieldset').first(),
    });

    await page.locator('#exercise-name-0').fill('Full planche hold');
    await page.locator('#exercise-category-0').fill('planche');
    await page.locator('#exercise-notes-0').fill('Protraction forte, bassin aligné, repos 2 min 30.');
    await page.locator('#series-reps-0-0').fill('0');
    await page.locator('#series-duration-0-0').fill('8');
    await page.locator('#series-load-0-0').fill('0');
    await page.locator('#series-assistance-0-0').fill('12');
    await page.locator('#series-rpe-0-0').fill('8');
    const firstExercise = page.locator('fieldset.exercise').first();
    await page.getByRole('button', {name: 'Ajouter un exercice'}).click();
    await page.locator('#exercise-name-1').fill('Front lever rows');
    await page.locator('#exercise-category-1').fill('front lever');
    await page.locator('#exercise-notes-1').fill('Tirage contrôlé, maintien horizontal et repos 2 minutes.');
    await page.locator('#series-reps-1-0').fill('5');
    await page.locator('#series-duration-1-0').fill('0');
    await page.locator('#series-load-1-0').fill('0');
    await page.locator('#series-assistance-1-0').fill('0');
    await page.locator('#series-rpe-1-0').fill('8');
    await screenshot(page, 'P08_ajout_exercice_dans_seance.png', {
      locator: page.locator('fieldset.exercise').nth(1),
    });

    await firstExercise.getByRole('button', {name: 'Ajouter une série'}).click();
    await firstExercise.getByRole('button', {name: 'Ajouter une série'}).click();
    await page.locator('#series-duration-0-1').fill('7');
    await page.locator('#series-assistance-0-1').fill('10');
    await page.locator('#series-rpe-0-1').fill('9');
    await page.locator('#series-duration-0-2').fill('6');
    await page.locator('#series-assistance-0-2').fill('8');
    await page.locator('#series-rpe-0-2').fill('9');
    await screenshot(page, 'P09_ajout_series_exercice.png', {locator: firstExercise});

    await page.getByRole('button', {name: 'Ajouter un exercice'}).click();
    await page.locator('#exercise-name-2').fill('Pseudo planche push-ups');
    await page.locator('#exercise-category-2').fill('planche');
    await page.locator('fieldset.exercise').nth(2).getByRole('button', {name: 'Supprimer cet exercice'}).click();
    await expect(page.getByRole('dialog', {name: 'Supprimer cet exercice ?'})).toBeVisible();
    await screenshot(page, 'P10_suppression_exercice.png');
    await page.getByRole('button', {name: 'Supprimer l’exercice'}).click();

    const createWorkoutResponse = page.waitForResponse((response) =>
      response.url().endsWith('/workouts') && response.request().method() === 'POST',
    );
    await page.getByRole('button', {name: 'Enregistrer la séance'}).click();
    const createdWorkoutResponse = await createWorkoutResponse;
    expect(createdWorkoutResponse.ok()).toBeTruthy();
    const createdWorkout = await createdWorkoutResponse.json();
    const createdWorkoutCard = page.locator('article.workout').filter({hasText: `${prefix} · Séance Planche / Front Lever`});
    await expect(createdWorkoutCard).toBeVisible();
    await createdWorkoutCard.scrollIntoViewIfNeeded();
    await expect(page.getByRole('status')).toContainText('Séance enregistrée avec succès');
    await screenshot(page, 'P11_enregistrement_seance_succes.png');
    await page.getByRole('button', {name: 'Fermer la notification'}).click();
    await screenshot(page, 'P12_seance_visible_dans_liste.png', {locator: createdWorkoutCard});

    await createdWorkoutCard.getByRole('button', {name: 'Voir le détail'}).click();
    const workoutDetail = page.getByRole('dialog', {name: /Détail/});
    await expect(workoutDetail).toBeVisible();
    const plancheSeries = workoutDetail.locator('article.detail-exercise')
      .filter({hasText: 'Full planche hold'})
      .locator('li');
    await expect(plancheSeries).toHaveCount(3);
    await expect(plancheSeries.nth(0)).toContainText('8 s');
    await expect(plancheSeries.nth(1)).toContainText('7 s');
    await expect(plancheSeries.nth(2)).toContainText('6 s');
    await screenshot(page, 'P13_detail_seance.png');
    await page.getByRole('button', {name: 'Fermer le détail'}).click();

    await createdWorkoutCard.getByRole('button', {name: 'Modifier'}).click();
    await expect(page.getByRole('heading', {name: 'Modifier la séance'})).toBeVisible();
    await expect(page.getByLabel('Titre *')).toHaveValue(`${prefix} · Séance Planche / Front Lever`);
    await screenshot(page, 'P14_modification_seance.png', {locator: page.locator('form.card.form')});

    await createdWorkoutCard.getByRole('button', {name: `Supprimer la séance ${prefix} · Séance Planche / Front Lever`}).click();
    await expect(page.getByRole('dialog', {name: 'Supprimer cette séance ?'})).toBeVisible();
    await screenshot(page, 'P15_suppression_seance_confirmation.png');
    await page.getByRole('dialog', {name: 'Supprimer cette séance ?'})
      .getByRole('button', {name: 'Annuler', exact: true}).click();

    await page.getByRole('button', {name: 'Objectifs'}).click();
    const goalsList = page.locator('section.card').filter({has: page.getByRole('heading', {name: 'Mes objectifs'})});
    await expect(goalsList).toContainText('actif');
    await expect(goalsList).toContainText('terminé');
    await expect(goalsList).toContainText('archivé');
    await screenshot(page, 'P16_page_objectifs.png', {locator: goalsList});

    const goalForm = page.locator('form.card.form');
    await screenshot(page, 'P17_creation_objectif_vide.png', {locator: goalForm});
    await page.getByLabel(/Nom de l’objectif \/ skill ou exercice/).fill(`${prefix} · Tractions lestées +40 kg`);
    await page.getByLabel('Type *').selectOption({label: 'force'});
    await page.getByLabel('Description de la cible *').fill('Réaliser 5 répétitions avec +40 kg');
    await page.getByLabel('Niveau actuel').fill('3 répétitions propres avec +40 kg');
    await page.getByLabel('Date cible').fill('2026-11-30');
    await page.getByLabel('Valeur actuelle').fill('3');
    await page.getByLabel('Valeur cible *').fill('5');
    await page.getByLabel('Unité *').selectOption({label: 'répétitions'});
    await page.getByLabel('Priorité *').selectOption({label: 'haute'});
    await page.getByLabel('Notes').fill('Une séance de force par semaine, progression de 2,5 kg.');
    await screenshot(page, 'P18_creation_objectif_rempli.png', {locator: goalForm});

    const createGoalResponse = page.waitForResponse((response) =>
      response.url().endsWith('/goals') && response.request().method() === 'POST',
    );
    await page.getByRole('button', {name: 'Ajouter l’objectif'}).click();
    const createdGoalResponse = await createGoalResponse;
    expect(createdGoalResponse.ok()).toBeTruthy();
    const createdGoal = await createdGoalResponse.json();
    let createdGoalCard = page.locator('article.goal').filter({hasText: `${prefix} · Tractions lestées +40 kg`});
    await expect(createdGoalCard).toBeVisible();
    await expect(createdGoalCard.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '60');
    await screenshot(page, 'P19_objectif_actif_progression.png', {locator: createdGoalCard});
    await createdGoalCard.getByRole('button', {name: 'Terminer'}).click();
    createdGoalCard = page.locator('article.goal').filter({hasText: `${prefix} · Tractions lestées +40 kg`});
    await expect(createdGoalCard).toContainText('terminé');
    await screenshot(page, 'P20_objectif_termine.png', {locator: createdGoalCard});
    await createdGoalCard.getByRole('button', {name: 'Supprimer'}).click();
    await expect(page.getByRole('dialog', {name: 'Supprimer cet objectif ?'})).toBeVisible();
    await screenshot(page, 'P21_archivage_ou_suppression_objectif.png');
    await page.getByRole('dialog', {name: 'Supprimer cet objectif ?'})
      .getByRole('button', {name: 'Annuler', exact: true}).click();
    await page.getByRole('button', {name: 'Fermer la notification'}).click().catch(() => null);

    await page.getByRole('button', {name: 'Import / Export'}).click();
    await expect(page.getByRole('heading', {name: 'Importer un CSV'})).toBeVisible();
    await screenshot(page, 'P22_page_import_export.png');
    await screenshot(page, 'P23_format_csv_attendu.png', {locator: page.locator('#csv-format-help')});

    const validCsvName = 'rncp-capture-seances-valides.csv';
    const importedWorkoutTitle = `${prefix} · Séance importée CSV`;
    const validCsv = `date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,reps,load_kg,duration_seconds,difficulty,assistance_kg,set_notes\n2026-08-18,${importedWorkoutTitle},Pull,7,55,Import validé,Front lever row,front lever,3,5,0,0,8,0,Exécution propre\n`;
    await page.getByLabel('Fichier CSV UTF-8').setInputFiles({
      name: validCsvName,
      mimeType: 'text/csv',
      buffer: Buffer.from(validCsv, 'utf-8'),
    });
    await expect(page.locator('#csv-file-selection')).toContainText(validCsvName);
    await expect(page.locator('#csv-import-submit')).toBeEnabled();
    await screenshot(page, 'P24_import_csv_selection_fichier.png', {
      locator: page.locator('section.card').filter({has: page.getByRole('heading', {name: 'Importer un CSV'})}),
    });
    await page.locator('#csv-import-submit').click();
    await expect(page.locator('#csv-import-report')).toContainText('1 ligne(s) importée(s)');
    await expect(page.locator('#csv-import-report')).toContainText('0 en erreur');
    await screenshot(page, 'P25_import_csv_succes.png', {locator: page.locator('#csv-import-report')});

    const invalidCsvName = 'rncp-capture-colonnes-manquantes.csv';
    await page.getByLabel('Fichier CSV UTF-8').setInputFiles({
      name: invalidCsvName,
      mimeType: 'text/csv',
      buffer: Buffer.from('date,title\n2026-08-20,Colonnes manquantes\n', 'utf-8'),
    });
    await page.locator('#csv-import-submit').click();
    await expect(page.locator('#csv-import-error')).toBeVisible();
    await expect(page.locator('#csv-import-error')).toContainText(/colonne|exercise/i);
    await screenshot(page, 'P26_import_csv_erreur.png', {locator: page.locator('#csv-import-error')});

    const exportSection = page.locator('section.card').filter({has: page.getByRole('heading', {name: 'Exporter mes données'})});
    let downloadPromise = page.waitForEvent('download');
    await exportSection.getByRole('button', {name: 'Export CSV'}).click();
    let download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.csv$/i);
    await expect(page.locator('#data-export-feedback')).toContainText('succès');
    await screenshot(page, 'P27_export_csv.png', {locator: exportSection});

    downloadPromise = page.waitForEvent('download');
    await exportSection.getByRole('button', {name: 'Export JSON'}).click();
    download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.json$/i);
    await expect(page.locator('#data-export-feedback')).toContainText('succès');
    await screenshot(page, 'P28_export_json.png', {locator: exportSection});

    await page.getByRole('button', {name: 'Profil RGPD'}).click();
    const profileCard = page.locator('section.card').filter({has: page.getByRole('heading', {name: 'Mes informations'})});
    await expect(profileCard).toContainText('demo@skilltrack.dev');
    await screenshot(page, 'P29_page_profil.png', {locator: profileCard});
    downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', {name: 'Exporter mes données'}).click();
    download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/\.json$/i);
    await expect(page.locator('#profile-export-feedback')).toBeVisible();
    await screenshot(page, 'P30_export_donnees_personnelles.png', {locator: profileCard});
    await page.getByRole('button', {name: 'Supprimer mon compte et mes données'}).click();
    await expect(page.getByRole('dialog', {name: 'Supprimer mon compte et mes données ?'})).toBeVisible();
    await screenshot(page, 'P31_confirmation_suppression_donnees.png');
    await page.getByRole('dialog', {name: 'Supprimer mon compte et mes données ?'})
      .getByRole('button', {name: 'Annuler', exact: true}).click();
    await screenshot(page, 'P32_message_rgpd.png', {locator: page.locator('.rgpd-notice')});

    expect(createdWorkout.id).toBeTruthy();
    expect(createdGoal.id).toBeTruthy();
  } finally {
    await cleanupCaptureData(request, token);
  }

  const generated = (await fs.readdir(captureDir)).filter((filename) => /^P\d{2}_.*\.png$/.test(filename));
  expect(generated).toHaveLength(32);
});
