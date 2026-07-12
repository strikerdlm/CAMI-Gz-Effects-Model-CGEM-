import { expect, test } from '@playwright/test';
import { installApiFixtures } from './fixtures/api';

test.beforeEach(async ({ page }) => {
  await installApiFixtures(page);
});

test('the research shell never creates document-level horizontal overflow', async ({ page }) => {
  for (const path of ['/', '/simulator', '/prediction', '/dashboard', '/batch', '/analysis', '/settings', '/about']) {
    await page.goto(path);
    await expect(page.locator('main')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  }
});

test('mobile drawer traps focus, closes on Escape, and restores its trigger', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile-390', 'Mobile drawer is present below 768 px.');
  await page.goto('/');
  const trigger = page.getByRole('button', { name: 'Open navigation' });
  await trigger.click();
  const dialog = page.getByRole('dialog', { name: 'Navigation' });
  await expect(dialog).toBeVisible();
  await expect(page.getByRole('button', { name: 'Close navigation' })).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(dialog.getByRole('link', { name: 'About' })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(trigger).toBeFocused();
});

test('keyboard search navigates to a shareable simulator selection', async ({ page }) => {
  test.skip(test.info().project.name === 'mobile-390', 'Global search is shown from the 768 px tablet breakpoint.');
  await page.goto('/');
  const search = page.getByRole('combobox', { name: 'Search maneuvers' });
  await search.fill('hammerhead');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/simulator\?maneuver=hammerhead$/);
  await expect(page.getByText('HAMMERHEAD', { exact: true }).first()).toBeVisible();
});

test('URL state survives reload and browser back/forward navigation', async ({ page }) => {
  await page.goto('/prediction?maneuver=hammerhead&pilot=2&view=surrogate');
  await page.getByRole('combobox', { name: 'Maneuver profile' }).click();
  await page.getByRole('option', { name: /^Split S Roll inverted/i }).click();
  await expect(page).toHaveURL(/maneuver=split_s/);
  await page.reload();
  await expect(page.getByRole('combobox', { name: 'Maneuver profile' })).toContainText(/split s/i);
  await page.goBack();
  await expect(page).toHaveURL(/maneuver=hammerhead/);
  await page.goForward();
  await expect(page).toHaveURL(/maneuver=split_s/);
});

test('Explore to Predict to Verify to Compare preserves evidence and working actions', async ({ page }) => {
  test.skip(test.info().project.name === 'mobile-390', 'The keyboard workflow uses global search from the 768 px breakpoint.');
  await page.goto('/');
  await page.getByRole('combobox', { name: 'Search maneuvers' }).fill('hammerhead');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'TACTICAL SIMULATOR' })).toBeVisible();
  await page.goto('/prediction?maneuver=hammerhead');
  await expect(page.getByRole('heading', { name: 'CGEM PREDICTION' })).toBeVisible();

  await page.getByRole('button', { name: /Predict \(surrogate/i }).click();
  const surrogateEvidence = page.getByRole('complementary', { name: 'Result evidence' });
  await expect(surrogateEvidence).toContainText('Surrogate');
  await expect(surrogateEvidence).toContainText('Calibration scope');
  await expect(surrogateEvidence).toContainText('training envelope');
  await expect(page.getByRole('button', { name: 'Export current result' })).toBeVisible();

  await page.getByRole('button', { name: 'authoritative', exact: true }).click();
  await page.getByRole('button', { name: /Run authoritative CGEM/i }).click();
  await expect(surrogateEvidence).toContainText('Fortran / authoritative CGEM');
  await expect(surrogateEvidence).toContainText('CGEM binary SHA');

  await page.getByRole('button', { name: 'comparison', exact: true }).click();
  const comparisonEvidence = page.getByRole('complementary', { name: 'Result evidence' });
  await expect(comparisonEvidence).toHaveCount(2);
  await expect(comparisonEvidence.nth(0)).toContainText('Surrogate');
  await expect(comparisonEvidence.nth(1)).toContainText('Fortran / authoritative CGEM');

  await page.goto('/batch');
  await page.getByRole('button', { name: 'Run All Profiles' }).click();
  await expect(page.getByRole('complementary', { name: 'Result evidence' })).toContainText('Surrogate batch');

  await page.getByRole('button', { name: 'Refresh API status' }).click();
  await expect(page.locator('header [role="status"]')).toContainText('API status refreshed');
  await expect(page.getByRole('link', { name: 'Help' })).toHaveAttribute('href', /\/about#batch$/);
});
