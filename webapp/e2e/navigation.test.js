const { test, expect } = require('@playwright/test');

test.describe('Navigation Tests', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Chess Trainer/);
  });

  test('should navigate to players page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=学员管理');
    await expect(page.url()).toContain('players');
  });

  test('should navigate to library page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=棋谱库');
    await expect(page.url()).toContain('library');
  });

  test('should navigate to plan page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=训练计划');
    await expect(page.url()).toContain('plan');
  });

  test('should navigate to exercises page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=习题练习');
    await expect(page.url()).toContain('exercises');
  });

  test('should navigate to profile page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=个人中心');
    await expect(page.url()).toContain('profile');
  });
});

test.describe('Player Management Tests', () => {
  test('should show players list', async ({ page }) => {
    await page.goto('/#players');
    const playersList = page.locator('.player-item');
    await expect(playersList).toHaveCount(0);
  });

  test('should open add player modal', async ({ page }) => {
    await page.goto('/#players');
    await page.click('text=添加学员');
    const modal = page.locator('.modal');
    await expect(modal).toBeVisible();
  });
});

test.describe('Exercise Tests', () => {
  test('should show exercises list', async ({ page }) => {
    await page.goto('/#exercises');
    const exercises = page.locator('.exercise-card');
    await expect(exercises).toHaveCount(0);
  });
});