import {expect, test} from '@playwright/test';
import axe from 'axe-core';

import {installContainerApiProxy} from './support';

const views = [
  ['Dashboard', 'Tableau de bord'],
  ['Séances', 'Séances'],
  ['Objectifs', 'Objectifs'],
  ['Import / Export', 'Import / Export'],
  ['Profil RGPD', 'Profil et RGPD'],
];

async function waitForViewReady(page) {
  await expect(page.getByRole('status').filter({hasText: /Chargement/})).toHaveCount(0);
}

async function auditCurrentView(page, label, testInfo) {
  const results = await page.evaluate(async () => window.axe.run(document));
  console.info(
    `[axe] ${label}: ${results.passes.length} règles validées, ${results.incomplete.length} à revoir (${results.incomplete.map(({id}) => id).join(', ') || 'aucune'}), ${results.violations.length} violation`,
  );
  await testInfo.attach(`axe-${label}`, {
    body: JSON.stringify(
      {
        url: results.url,
        testedAt: results.timestamp,
        passes: results.passes.length,
        incomplete: results.incomplete.map(({id, impact}) => ({id, impact})),
        violations: results.violations,
      },
      null,
      2,
    ),
    contentType: 'application/json',
  });
  expect(
    results.violations,
    results.violations.map(({id, help, nodes}) => `${id}: ${help} (${nodes.length})`).join('\n'),
  ).toEqual([]);
  expect(
    results.incomplete,
    results.incomplete.map(({id, nodes}) => `${id}: contrôle manuel requis (${nodes.length})`).join('\n'),
  ).toEqual([]);
}

test('accessibilité navigateur : axe, clavier et reflow équivalent zoom 400 %', async ({page}, testInfo) => {
  await installContainerApiProxy(page);
  await page.goto('/');

  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', {name: 'Aller au contenu principal'})).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();

  await page.getByLabel('Adresse email *').focus();
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Mot de passe *')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', {name: 'Se connecter'})).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', {name: 'Tableau de bord'})).toBeVisible();
  await waitForViewReady(page);

  await page.addScriptTag({content: axe.source});
  await auditCurrentView(page, 'dashboard', testInfo);

  for (const [buttonName, headingName] of views.slice(1)) {
    const navigationButton = page.getByRole('button', {name: buttonName});
    await navigationButton.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('heading', {name: headingName, level: 1})).toBeVisible();
    await waitForViewReady(page);
    await auditCurrentView(page, buttonName.toLowerCase().replaceAll(/[^a-z]+/g, '-'), testInfo);
  }

  await page.setViewportSize({width: 320, height: 800});
  for (const [buttonName, headingName] of views) {
    await page.getByRole('button', {name: buttonName}).click();
    await expect(page.getByRole('heading', {name: headingName, level: 1})).toBeVisible();
    await waitForViewReady(page);
    const overflow = await page.evaluate(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
    }));
    expect(overflow.scrollWidth, `${buttonName} déborde à 320 px`).toBeLessThanOrEqual(
      overflow.clientWidth + 1,
    );
  }
  await testInfo.attach('reflow-320px', {
    body: await page.screenshot({fullPage: true}),
    contentType: 'image/png',
  });
});
