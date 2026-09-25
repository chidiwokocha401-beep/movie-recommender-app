import { expect, test } from '@playwright/test';

test('search, rate, recommendations refresh', async ({ page }) => {
  await page.goto('/search');
  await page.getByLabel('Search movies').fill('Star Wars');
  await page.getByRole('link', { name: /Star Wars/ }).first().click();
  await expect(page.getByRole('heading', { name: /Star Wars/ })).toBeVisible();

  await page.getByRole('radio', { name: '5 stars' }).click();
  await expect(page.getByRole('radio', { name: '5 stars' })).toBeChecked();
  await expect(page.getByText(/recommendations will refresh/)).toBeVisible();

  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: /Recommended for you/ }),
  ).toBeVisible();
  await expect(page.getByText(/User \d+/).first()).toBeVisible();
});
