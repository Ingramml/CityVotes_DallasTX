// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests',
    timeout: 30000,
    retries: 1,
    use: {
        baseURL: process.env.BASE_URL || 'http://localhost:8080',
        headless: true,
        viewport: { width: 1280, height: 720 },
        screenshot: 'only-on-failure',
    },
    reporter: [
        ['list'],
        ['html', { open: 'never' }],
    ],
});
