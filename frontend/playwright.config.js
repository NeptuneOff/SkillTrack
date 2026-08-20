import {defineConfig} from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 45_000,
  expect: {timeout: 8_000},
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['html', {open: 'never'}], ['line']] : 'list',
  webServer: process.env.PLAYWRIGHT_START_SERVER
    ? {
        command: 'npm run dev -- --host 0.0.0.0',
        url: process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5173',
        reuseExistingServer: false,
        timeout: 30_000,
      }
    : undefined,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{name: 'chromium', use: {browserName: 'chromium'}}],
});
