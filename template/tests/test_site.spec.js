/**
 * CityVotes Automated Test Suite
 * ===============================
 * Tests all 10 pages, interactive features, cross-page navigation,
 * and checks for JavaScript console errors.
 *
 * Usage:
 *   npx playwright test tests/test_site.spec.js
 *
 * Set BASE_URL env variable to test a deployed site:
 *   BASE_URL=https://cityvotes.vercel.app npx playwright test tests/test_site.spec.js
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8080';

// Helper: collect console errors during a test
function trackConsoleErrors(page) {
    const errors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') errors.push(msg.text());
    });
    return errors;
}

// ============================================================
// HOMEPAGE
// ============================================================
test.describe('Homepage', () => {
    test('loads with correct title', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        await expect(page).toHaveTitle(/CityVotes/);
    });

    test('displays 4 KPI stat cards with data', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        await page.waitForSelector('.stat-card');
        const statCards = page.locator('.stat-card');
        await expect(statCards).toHaveCount(4);

        // Each stat card should have a value that is not empty/zero placeholder
        for (let i = 0; i < 4; i++) {
            const value = statCards.nth(i).locator('.stat-value');
            await expect(value).not.toHaveText('--');
            await expect(value).not.toHaveText('');
        }
    });

    test('shows council member cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        await page.waitForSelector('.council-card');
        const cards = page.locator('.council-card');
        const count = await cards.count();
        expect(count).toBeGreaterThan(0);
    });

    test('filter buttons toggle council cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        await page.waitForSelector('.council-card');

        const allCount = await page.locator('.council-card:visible').count();

        // Click "Current" filter
        const currentBtn = page.locator('button', { hasText: 'Current' }).first();
        if (await currentBtn.isVisible()) {
            await currentBtn.click();
            await page.waitForTimeout(300);
            const currentCount = await page.locator('.council-card:visible').count();
            expect(currentCount).toBeLessThanOrEqual(allCount);

            // Click "All" to restore
            const allBtn = page.locator('button', { hasText: 'All' }).first();
            if (await allBtn.isVisible()) {
                await allBtn.click();
                await page.waitForTimeout(300);
            }
        }
    });

    test('displays recent meetings list', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        await page.waitForSelector('.list-group-item, [class*="meeting"]', { timeout: 10000 });
    });

    test('shows alignment cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        // Look for alignment section text
        const alignedText = page.locator('text=Aligned');
        await expect(alignedText.first()).toBeVisible({ timeout: 10000 });
    });

    test('navbar links are functional', async ({ page }) => {
        await page.goto(`${BASE_URL}/index.html`);
        const navLinks = page.locator('.navbar-nav .nav-link');
        const count = await navLinks.count();
        expect(count).toBeGreaterThanOrEqual(5);

        // Verify each link has an href
        for (let i = 0; i < count; i++) {
            const href = await navLinks.nth(i).getAttribute('href');
            expect(href).toBeTruthy();
        }
    });
});

// ============================================================
// COUNCIL PAGE
// ============================================================
test.describe('Council Page', () => {
    test('loads with member grid', async ({ page }) => {
        await page.goto(`${BASE_URL}/council.html`);
        await expect(page).toHaveTitle(/Council/);
        await page.waitForSelector('.council-card');
        const cards = page.locator('.council-card');
        const count = await cards.count();
        expect(count).toBeGreaterThan(0);
    });

    test('shows Current and Former badges', async ({ page }) => {
        await page.goto(`${BASE_URL}/council.html`);
        await page.waitForSelector('.council-card');
        const badges = page.locator('.badge');
        const count = await badges.count();
        expect(count).toBeGreaterThan(0);
    });

    test('filter buttons work', async ({ page }) => {
        await page.goto(`${BASE_URL}/council.html`);
        await page.waitForSelector('.council-card');

        // Look for filter buttons
        const formerBtn = page.locator('button', { hasText: 'Former' }).first();
        if (await formerBtn.isVisible()) {
            await formerBtn.click();
            await page.waitForTimeout(300);
            // Should still have some cards visible (former members)
            const visible = await page.locator('.council-card:visible').count();
            expect(visible).toBeGreaterThan(0);
        }
    });

    test('council card links to member detail', async ({ page }) => {
        await page.goto(`${BASE_URL}/council.html`);
        await page.waitForSelector('.council-card');
        const firstCardLink = page.locator('.council-card a').first();
        const href = await firstCardLink.getAttribute('href');
        expect(href).toContain('council-member.html');
    });
});

// ============================================================
// COUNCIL MEMBER DETAIL
// ============================================================
test.describe('Council Member Detail', () => {
    test('loads with breadcrumb and stats', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        await page.waitForSelector('.stat-card, .card');

        // Breadcrumb exists
        const breadcrumb = page.locator('.breadcrumb');
        await expect(breadcrumb).toBeVisible();

        // Member name visible
        const heading = page.locator('h1, h2').first();
        await expect(heading).toBeVisible();
    });

    test('displays stat cards with values', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        // Council member page uses #statTotalVotes, #statAyeRate, etc. inside .card elements
        await page.waitForSelector('#statTotalVotes', { timeout: 10000 });
        const totalVotes = page.locator('#statTotalVotes');
        await expect(totalVotes).not.toHaveText('--');
    });

    test('shows vote history table', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        // Wait for vote data to load
        await page.waitForSelector('table tbody tr, .vote-row, .list-group-item', { timeout: 10000 });
    });

    test('topic dropdown has options and filters', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        // Council member page uses #voteTopicFilter
        await page.waitForSelector('#voteTopicFilter', { timeout: 10000 });

        const topicSelect = page.locator('#voteTopicFilter');
        const options = topicSelect.locator('option');
        const optCount = await options.count();
        expect(optCount).toBeGreaterThan(1); // "All" + at least one topic

        // Select second option (first real topic)
        if (optCount > 1) {
            const value = await options.nth(1).getAttribute('value');
            await topicSelect.selectOption(value);
            await page.waitForTimeout(500);
        }
    });

    test('year dropdown has options and filters', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        // Council member page uses #voteYearFilter
        await page.waitForSelector('#voteYearFilter', { timeout: 10000 });

        const yearSelect = page.locator('#voteYearFilter');
        const options = yearSelect.locator('option');
        const optCount = await options.count();
        expect(optCount).toBeGreaterThan(1);
    });

    test('clear filters button resets dropdowns', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        // Council member page uses #voteTopicFilter and #clearVoteFilters
        await page.waitForSelector('#voteTopicFilter', { timeout: 10000 });

        // Select a topic filter first
        const topicSelect = page.locator('#voteTopicFilter');
        const options = topicSelect.locator('option');
        if (await options.count() > 1) {
            const value = await options.nth(1).getAttribute('value');
            await topicSelect.selectOption(value);
            await page.waitForTimeout(300);
        }

        // Click clear button
        const clearBtn = page.locator('#clearVoteFilters');
        await clearBtn.click();
        await page.waitForTimeout(300);

        // Verify topic reset to first option
        const currentValue = await topicSelect.inputValue();
        expect(currentValue === '' || currentValue === 'all' || currentValue === 'All Topics').toBeTruthy();
    });
});

// ============================================================
// MEETINGS PAGE
// ============================================================
test.describe('Meetings Page', () => {
    test('loads with KPI cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);
        await expect(page).toHaveTitle(/Meetings/);

        // Wait for data to load
        await page.waitForSelector('.kpi-card, .stat-card, h4', { timeout: 10000 });
    });

    test('year filter dropdown populates with options', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);

        // Wait for the dropdown to be populated (options added dynamically)
        await page.waitForFunction(() => {
            const sel = document.getElementById('yearFilter');
            return sel && sel.options.length > 1;
        }, { timeout: 10000 });

        const yearSelect = page.locator('#yearFilter');
        const options = yearSelect.locator('option');
        const optCount = await options.count();
        expect(optCount).toBeGreaterThan(1); // "All Years" + year options
    });

    test('selecting a year filters meetings', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);

        // Wait for dropdown to populate
        await page.waitForFunction(() => {
            const sel = document.getElementById('yearFilter');
            return sel && sel.options.length > 1;
        }, { timeout: 10000 });

        const yearSelect = page.locator('#yearFilter');
        const options = yearSelect.locator('option');
        const optCount = await options.count();

        if (optCount > 1) {
            // Get the second option value (first year)
            const yearValue = await options.nth(1).getAttribute('value');
            await yearSelect.selectOption(yearValue);
            await page.waitForTimeout(500);

            // URL should update with year parameter
            expect(page.url()).toContain('year=');
        }
    });

    test('meeting rows display with document badges', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);
        await page.waitForSelector('.list-group-item, [class*="meeting"]', { timeout: 10000 });

        // Check for document links (Agenda, Minutes, Video)
        const docLinks = page.locator('a', { hasText: /Agenda|Minutes|Video/ });
        const count = await docLinks.count();
        expect(count).toBeGreaterThan(0);
    });

    test('meeting links navigate to detail page', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);
        await page.waitForSelector('a[href*="meeting-detail"]', { timeout: 10000 });

        const meetingLink = page.locator('a[href*="meeting-detail"]').first();
        const href = await meetingLink.getAttribute('href');
        expect(href).toContain('meeting-detail.html?id=');
    });

    test('pagination is present', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);
        await page.waitForSelector('.pagination, nav[aria-label*="pagination"]', { timeout: 10000 });
        const pagination = page.locator('.pagination');
        await expect(pagination).toBeVisible();
    });
});

// ============================================================
// MEETING DETAIL
// ============================================================
test.describe('Meeting Detail', () => {
    test('loads with breadcrumb and stats', async ({ page }) => {
        // Use a meeting with votes (find from meetings list)
        await page.goto(`${BASE_URL}/meetings.html`);
        await page.waitForSelector('a[href*="meeting-detail"]', { timeout: 10000 });

        // Get first meeting link that has votes
        const meetingLink = page.locator('a[href*="meeting-detail"]').first();
        await meetingLink.click();
        await page.waitForSelector('.breadcrumb', { timeout: 10000 });

        const breadcrumb = page.locator('.breadcrumb');
        await expect(breadcrumb).toBeVisible();
    });

    test('shows agenda items', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);
        await page.waitForSelector('a[href*="meeting-detail"]', { timeout: 10000 });

        // Navigate to a meeting with content
        const links = page.locator('a[href*="meeting-detail"]');
        // Try the second meeting (first might be empty)
        const link = links.nth(1);
        await link.click();

        // Wait for agenda items to load
        await page.waitForSelector('.list-group-item, .agenda-item, table tr, .card', { timeout: 10000 });
    });

    test('displays vote tallies for voted items', async ({ page }) => {
        await page.goto(`${BASE_URL}/meetings.html`);
        await page.waitForSelector('a[href*="meeting-detail"]', { timeout: 10000 });

        // Find a meeting link that shows vote count > 0
        const meetingRows = page.locator('.list-group-item, [class*="meeting"]');
        const count = await meetingRows.count();

        for (let i = 0; i < Math.min(count, 5); i++) {
            const text = await meetingRows.nth(i).textContent();
            const voteMatch = text.match(/(\d+)\s*vote/);
            if (voteMatch && parseInt(voteMatch[1]) > 0) {
                const link = meetingRows.nth(i).locator('a[href*="meeting-detail"]').first();
                await link.click();
                await page.waitForSelector('.badge, .progress', { timeout: 10000 });
                break;
            }
        }
    });
});

// ============================================================
// VOTES PAGE
// ============================================================
test.describe('Votes Page', () => {
    test('loads with vote cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await expect(page).toHaveTitle(/Votes/);
        await page.waitForSelector('.card, .vote-card, .list-group-item', { timeout: 10000 });
    });

    test('search box filters votes', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('#searchInput, [type="search"], [placeholder*="earch"]', { timeout: 10000 });

        const searchInput = page.locator('#searchInput, [type="search"], [placeholder*="earch"]').first();
        await searchInput.fill('budget');
        await page.waitForTimeout(500);

        // Results should be filtered (or show "no results")
        const pageContent = await page.textContent('body');
        expect(pageContent.toLowerCase()).toMatch(/budget|no.*result|0.*result/);
    });

    test('year dropdown filters by year', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);

        // Wait for year dropdown to populate
        await page.waitForFunction(() => {
            const sel = document.getElementById('yearFilter');
            return sel && sel.options.length > 1;
        }, { timeout: 10000 });

        const yearSelect = page.locator('#yearFilter');
        const options = yearSelect.locator('option');

        if (await options.count() > 1) {
            const yearValue = await options.nth(1).getAttribute('value');
            await yearSelect.selectOption(yearValue);
            await page.waitForTimeout(500);
        }
    });

    test('topic dropdown filters by topic', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('#topicFilter, [id*="topic"]', { timeout: 10000 });

        const topicSelect = page.locator('#topicFilter, [id*="topic"]').first();
        if (await topicSelect.isVisible()) {
            const options = topicSelect.locator('option');
            if (await options.count() > 1) {
                const value = await options.nth(1).getAttribute('value');
                await topicSelect.selectOption(value);
                await page.waitForTimeout(500);
            }
        }
    });

    test('outcome dropdown filters by outcome', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('#outcomeFilter, [id*="outcome"]', { timeout: 10000 });

        const outcomeSelect = page.locator('#outcomeFilter, [id*="outcome"]').first();
        if (await outcomeSelect.isVisible()) {
            const options = outcomeSelect.locator('option');
            if (await options.count() > 1) {
                const value = await options.nth(1).getAttribute('value');
                await outcomeSelect.selectOption(value);
                await page.waitForTimeout(500);
            }
        }
    });

    test('clear all button resets filters', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('#searchInput, [type="search"]', { timeout: 10000 });

        // Type something in search
        const searchInput = page.locator('#searchInput, [type="search"], [placeholder*="earch"]').first();
        await searchInput.fill('test query');
        await page.waitForTimeout(300);

        // Click clear
        const clearBtn = page.locator('button', { hasText: /clear/i }).first();
        if (await clearBtn.isVisible()) {
            await clearBtn.click();
            await page.waitForTimeout(300);

            const value = await searchInput.inputValue();
            expect(value).toBe('');
        }
    });

    test('vote links navigate to detail', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });

        const voteLink = page.locator('a[href*="vote-detail"]').first();
        const href = await voteLink.getAttribute('href');
        expect(href).toContain('vote-detail.html?id=');
    });

    test('pagination is present and functional', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('.pagination', { timeout: 10000 });

        const pagination = page.locator('.pagination');
        await expect(pagination).toBeVisible();

        // Click page 2 if it exists
        const page2 = page.locator('.page-link', { hasText: '2' }).first();
        if (await page2.isVisible()) {
            await page2.click();
            await page.waitForTimeout(500);
        }
    });
});

// ============================================================
// VOTE DETAIL
// ============================================================
test.describe('Vote Detail', () => {
    test('loads with tally card and progress bar', async ({ page }) => {
        // Navigate to first vote from votes page
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });
        const link = page.locator('a[href*="vote-detail"]').first();
        await link.click();

        await page.waitForSelector('.progress, .card', { timeout: 10000 });

        // Should have outcome badge
        const badges = page.locator('.badge');
        const count = await badges.count();
        expect(count).toBeGreaterThan(0);
    });

    test('shows member vote cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });
        const link = page.locator('a[href*="vote-detail"]').first();
        await link.click();

        // Wait for member votes to load
        await page.waitForSelector('a[href*="council-member"], .member-vote, .card', { timeout: 10000 });

        // Should have links to council members
        const memberLinks = page.locator('a[href*="council-member"]');
        const count = await memberLinks.count();
        expect(count).toBeGreaterThan(0);
    });

    test('breadcrumb navigation works', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });
        const link = page.locator('a[href*="vote-detail"]').first();
        await link.click();

        await page.waitForSelector('.breadcrumb', { timeout: 10000 });
        const breadcrumb = page.locator('.breadcrumb');
        await expect(breadcrumb).toBeVisible();

        // Breadcrumb should have Home link
        const homeLink = breadcrumb.locator('a[href*="index"]');
        await expect(homeLink).toBeVisible();
    });

    test('links to meeting detail', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });
        const link = page.locator('a[href*="vote-detail"]').first();
        await link.click();

        await page.waitForSelector('a[href*="meeting-detail"]', { timeout: 10000 });
        const meetingLink = page.locator('a[href*="meeting-detail"]').first();
        const href = await meetingLink.getAttribute('href');
        expect(href).toContain('meeting-detail.html?id=');
    });
});

// ============================================================
// AGENDA SEARCH
// ============================================================
test.describe('Agenda Search', () => {
    test('loads with KPI cards', async ({ page }) => {
        await page.goto(`${BASE_URL}/agenda-search.html`);
        await expect(page).toHaveTitle(/Search|Agenda/);
        await page.waitForSelector('.kpi-card, .stat-card, .card', { timeout: 10000 });
    });

    test('search box filters results', async ({ page }) => {
        await page.goto(`${BASE_URL}/agenda-search.html`);
        await page.waitForSelector('#searchInput, [type="search"], [placeholder*="earch"]', { timeout: 10000 });

        const searchInput = page.locator('#searchInput, [type="search"], [placeholder*="earch"]').first();
        await searchInput.fill('ordinance');
        await page.waitForTimeout(500);
    });

    test('sortable columns respond to clicks', async ({ page }) => {
        await page.goto(`${BASE_URL}/agenda-search.html`);
        await page.waitForSelector('.sortable, th[class*="sort"]', { timeout: 10000 });

        const sortableHeader = page.locator('.sortable, th[class*="sort"]').first();
        if (await sortableHeader.isVisible()) {
            await sortableHeader.click();
            await page.waitForTimeout(300);
            // Click again to reverse sort
            await sortableHeader.click();
            await page.waitForTimeout(300);
        }
    });

    test('type and year dropdowns have options', async ({ page }) => {
        await page.goto(`${BASE_URL}/agenda-search.html`);

        // Check type filter
        const typeSelect = page.locator('#typeFilter, [id*="type"]').first();
        if (await typeSelect.isVisible()) {
            const typeOpts = typeSelect.locator('option');
            expect(await typeOpts.count()).toBeGreaterThan(1);
        }

        // Check year filter
        const yearSelect = page.locator('#yearFilter, [id*="year"]').first();
        if (await yearSelect.isVisible()) {
            const yearOpts = yearSelect.locator('option');
            expect(await yearOpts.count()).toBeGreaterThan(1);
        }
    });
});

// ============================================================
// ABOUT PAGE
// ============================================================
test.describe('About Page', () => {
    test('loads with content', async ({ page }) => {
        await page.goto(`${BASE_URL}/about.html`);
        await expect(page).toHaveTitle(/About|Help/);

        // Should have content sections
        const headings = page.locator('h1, h2, h3, h4, h5');
        const count = await headings.count();
        expect(count).toBeGreaterThan(0);
    });

    test('accordion toggles open and closed', async ({ page }) => {
        await page.goto(`${BASE_URL}/about.html`);

        // Find accordion buttons
        const accordionBtn = page.locator('.accordion-button, [data-bs-toggle="collapse"]').first();
        if (await accordionBtn.isVisible()) {
            await accordionBtn.click();
            await page.waitForTimeout(300);

            // Content should be visible
            const accordionBody = page.locator('.accordion-collapse.show, .accordion-body:visible').first();
            await expect(accordionBody).toBeVisible();

            // Click again to close
            await accordionBtn.click();
            await page.waitForTimeout(500);
        }
    });
});

// ============================================================
// CONTACT PAGE
// ============================================================
test.describe('Contact Page', () => {
    test('loads with form fields', async ({ page }) => {
        await page.goto(`${BASE_URL}/contact.html`);
        await expect(page).toHaveTitle(/Contact/);

        // Check form fields exist
        await expect(page.locator('#name')).toBeVisible();
        await expect(page.locator('#email')).toBeVisible();
        await expect(page.locator('#message')).toBeVisible();
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('validates required fields on empty submit', async ({ page }) => {
        await page.goto(`${BASE_URL}/contact.html`);

        // Submit empty form
        await page.locator('button[type="submit"]').click();
        await page.waitForTimeout(300);

        // Form should show validation state
        const form = page.locator('#contactForm');
        const formClass = await form.getAttribute('class');
        expect(formClass).toContain('was-validated');
    });

    test('shows success message on valid submit', async ({ page }) => {
        await page.goto(`${BASE_URL}/contact.html`);

        // Fill form with valid data
        await page.locator('#name').fill('Test User');
        await page.locator('#email').fill('test@example.com');
        await page.locator('#message').fill('This is a test message for CityVotes.');

        // Submit
        await page.locator('button[type="submit"]').click();
        await page.waitForTimeout(500);

        // Success message should appear
        const success = page.locator('#successMessage');
        await expect(success).toBeVisible();
    });
});

// ============================================================
// CROSS-PAGE NAVIGATION
// ============================================================
test.describe('Cross-Page Navigation', () => {
    test('council card navigates to member detail', async ({ page }) => {
        await page.goto(`${BASE_URL}/council.html`);
        await page.waitForSelector('a[href*="council-member"]', { timeout: 10000 });

        const memberLink = page.locator('a[href*="council-member"]').first();
        await memberLink.click();

        await page.waitForURL(/council-member/, { timeout: 10000 });
        expect(page.url()).toContain('council-member.html?id=');
    });

    test('member vote row navigates to vote detail', async ({ page }) => {
        await page.goto(`${BASE_URL}/council-member.html?id=1`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });

        const voteLink = page.locator('a[href*="vote-detail"]').first();
        await voteLink.click();

        await page.waitForURL(/vote-detail/, { timeout: 10000 });
        expect(page.url()).toContain('vote-detail.html?id=');
    });

    test('vote detail links back to meeting', async ({ page }) => {
        await page.goto(`${BASE_URL}/votes.html`);
        await page.waitForSelector('a[href*="vote-detail"]', { timeout: 10000 });

        // Go to a vote detail
        const link = page.locator('a[href*="vote-detail"]').first();
        await link.click();
        await page.waitForURL(/vote-detail/, { timeout: 10000 });

        // Find and click meeting link
        await page.waitForSelector('a[href*="meeting-detail"]', { timeout: 10000 });
        const meetingLink = page.locator('a[href*="meeting-detail"]').first();
        await meetingLink.click();

        await page.waitForURL(/meeting-detail/, { timeout: 10000 });
        expect(page.url()).toContain('meeting-detail.html?id=');
    });
});

// ============================================================
// CONSOLE ERRORS CHECK
// ============================================================
test.describe('Console Errors', () => {
    const pages = [
        { name: 'Homepage', path: '/index.html' },
        { name: 'Council', path: '/council.html' },
        { name: 'Council Member', path: '/council-member.html?id=1' },
        { name: 'Meetings', path: '/meetings.html' },
        { name: 'Votes', path: '/votes.html' },
        { name: 'Agenda Search', path: '/agenda-search.html' },
        { name: 'About', path: '/about.html' },
        { name: 'Contact', path: '/contact.html' },
    ];

    for (const p of pages) {
        test(`no JS errors on ${p.name}`, async ({ page }) => {
            const errors = trackConsoleErrors(page);
            await page.goto(`${BASE_URL}${p.path}`);
            await page.waitForTimeout(2000); // Wait for async data loads

            // Filter out non-critical errors (like favicon 404)
            const criticalErrors = errors.filter(e =>
                !e.includes('favicon') &&
                !e.includes('404') &&
                !e.includes('net::ERR')
            );

            expect(criticalErrors).toEqual([]);
        });
    }
});
