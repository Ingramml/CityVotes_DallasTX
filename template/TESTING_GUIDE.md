# CityVotes Testing Guide

Comprehensive testing procedure for verifying a CityVotes deployment. Covers all 10 pages, every interactive feature, and cross-page navigation.

---

## Prerequisites

- Node.js 18+ installed
- The site running locally (or deployed URL)
- Playwright installed:

```bash
npm init -y
npm install @playwright/test
npx playwright install chromium
```

---

## Quick Start

```bash
# 1. Start a local server from the template/ folder
cd template/
python3 -m http.server 8080 &

# 2. Run the automated test suite
npx playwright test tests/test_site.spec.js

# 3. View HTML report
npx playwright show-report
```

---

## What Gets Tested

### Test Coverage Matrix

| Page | Elements Tested | Interactive Features |
|------|----------------|---------------------|
| **Homepage** | 4 KPI cards, council grid, meetings list, alignment cards, nav links | Current/Former/All filter buttons |
| **Council** | Member card grid, badges (Current/Former), stat bars | Filter buttons (Current/Former/All) |
| **Council Member** | Stats cards, breadcrumb, vote history table, alignment sidebar | Topic dropdown, Year dropdown, Clear filters, Pagination |
| **Meetings** | KPI cards, meeting list, document badges (Agenda/Minutes/Video) | Year filter dropdown, Pagination |
| **Meeting Detail** | Breadcrumb, stats cards, agenda item list, vote tallies | Agenda item expand/collapse |
| **Votes** | Vote cards, outcome badges, tally bars, document links | Search box, Year dropdown, Topic dropdown, Outcome dropdown, Clear, Pagination |
| **Vote Detail** | Tally card, progress bars, member vote cards, grouped sections | Links to member profiles, meeting detail |
| **Agenda Search** | KPI cards, results table, column headers | Search box, Type dropdown, Year dropdown, Sortable columns, Pagination |
| **About** | Content sections, FAQ accordion | Accordion expand/collapse |
| **Contact** | Form fields, validation, submit button | Form validation, submit flow |
| **Cross-Page Nav** | All navigation links between pages | Council->Member, Member->Vote, Vote->Meeting |

### Additional Checks

- **Console Errors**: Every page is checked for JavaScript errors
- **Broken Links**: Navigation links verified across all pages
- **Responsive**: Tests run at default viewport (1280x720)

---

## Manual Testing Checklist

Use this checklist for quick manual verification after deployment.

### Global (All Pages)

- [ ] Navbar displays with city name badge
- [ ] All 5 nav links work (Home, Council, Meetings, Votes, Search)
- [ ] Help button links to About page
- [ ] Footer displays with correct city name
- [ ] No JavaScript console errors
- [ ] Page titles include city name

### Homepage (`/` or `/index.html`)

- [ ] 4 KPI stat cards show numbers (Total Votes, Meetings, Pass Rate, Unanimous Rate)
- [ ] Council member cards display with avatars and names
- [ ] "Current" / "Former" badges on member cards
- [ ] Current/Former/All filter buttons toggle cards
- [ ] Recent Meetings list shows meeting dates with document badges
- [ ] Meeting links navigate to meeting detail
- [ ] Most Aligned / Least Aligned cards show member pairs with percentages
- [ ] Council member card links navigate to member detail

### Council Page (`/council.html`)

- [ ] All council members displayed in card grid
- [ ] Each card shows: name, position, avatar, stat bars
- [ ] Current/Former/All filter buttons work
- [ ] Card links navigate to individual member pages

### Council Member Detail (`/council-member.html?id=1`)

- [ ] Breadcrumb shows: Home > Council > Member Name
- [ ] Stats cards show: Total Votes, Aye %, Participation, Dissent Rate
- [ ] Vote history table populates with rows
- [ ] Topic filter dropdown has options and filters correctly
- [ ] Year filter dropdown has options and filters correctly
- [ ] Clear Filters button resets both dropdowns
- [ ] Pagination works (if enough votes)
- [ ] Alignment sidebar shows aligned/divergent members

### Meetings Page (`/meetings.html`)

- [ ] 3 KPI cards: Meeting count, Total Votes, Date Range
- [ ] Year filter dropdown populates with available years
- [ ] Selecting a year filters meetings list and updates KPIs
- [ ] "All Years" option resets to full list
- [ ] Each meeting row shows: date, type, document badges
- [ ] Document badges (Agenda, Minutes, Video) link to correct URLs
- [ ] Meeting links navigate to meeting detail
- [ ] Pagination works

### Meeting Detail (`/meeting-detail.html?id=1`)

- [ ] Breadcrumb shows: Home > Meetings > Date
- [ ] Stats cards show: Total Items, Voted Items, Pass Rate
- [ ] Agenda items list populates
- [ ] Voted items show tally (Ayes/Nays) and outcome badge (PASS/FAIL)
- [ ] Non-voted items show appropriate status
- [ ] Vote links navigate to vote detail

### Votes Page (`/votes.html`)

- [ ] Vote cards display with title, outcome badge, tally bar
- [ ] Search box filters by text
- [ ] Year dropdown filters by year
- [ ] Topic dropdown filters by topic category
- [ ] Outcome dropdown filters by PASS/FAIL
- [ ] Clear All button resets all filters
- [ ] Pagination updates with filter changes
- [ ] Vote card links navigate to vote detail

### Vote Detail (`/vote-detail.html?id=1`)

- [ ] Breadcrumb shows: Home > Votes > Item title
- [ ] Tally card shows: Ayes, Nays, Abstentions, Absent counts
- [ ] Progress bar visualizes vote split
- [ ] Outcome badge shows PASS/FAIL
- [ ] Member votes grouped by choice (AYE, NAY, ABSENT, etc.)
- [ ] Each member vote card links to member profile
- [ ] Meeting link navigates to meeting detail

### Agenda Search (`/agenda-search.html`)

- [ ] KPI cards show totals
- [ ] Search box filters results
- [ ] Type dropdown filters by item type
- [ ] Year dropdown filters by year
- [ ] Column headers are sortable (click to sort)
- [ ] Sort indicators show direction
- [ ] Pagination works
- [ ] Results update correctly with combined filters

### About Page (`/about.html`)

- [ ] Content sections display
- [ ] FAQ accordion items expand/collapse on click
- [ ] Contact link works

### Contact Page (`/contact.html`)

- [ ] Name, Email, Message fields present
- [ ] Required field validation works (submit empty form)
- [ ] Email format validation works
- [ ] Success message appears on valid submit
- [ ] Back to Home link works

---

## Automated Test Script

The automated test suite is in `tests/test_site.spec.js`. It uses Playwright Test runner.

### Configuration

The test looks for the site at `http://localhost:8080` by default. To change this, set the `BASE_URL` environment variable:

```bash
BASE_URL=https://your-deployed-site.vercel.app npx playwright test tests/test_site.spec.js
```

### Test Structure

```
tests/test_site.spec.js
├── Homepage
│   ├── loads with correct title
│   ├── displays 4 KPI stat cards
│   ├── shows council member cards
│   ├── filter buttons toggle cards
│   ├── displays recent meetings
│   └── shows alignment cards
├── Council Page
│   ├── loads with member grid
│   ├── shows Current/Former badges
│   └── filter buttons work
├── Council Member Detail
│   ├── loads with breadcrumb and stats
│   ├── displays vote history table
│   ├── topic dropdown filters
│   ├── year dropdown filters
│   └── clear filters resets
├── Meetings Page
│   ├── loads with KPI cards
│   ├── year filter populates and works
│   ├── meeting rows have document badges
│   └── pagination works
├── Meeting Detail
│   ├── loads with breadcrumb and stats
│   └── shows agenda items
├── Votes Page
│   ├── loads with vote cards
│   ├── search box filters
│   ├── year/topic/outcome dropdowns work
│   └── clear resets all filters
├── Vote Detail
│   ├── loads with tally card
│   ├── shows member vote cards
│   └── links to member profiles
├── Agenda Search
│   ├── loads with KPI cards
│   ├── search and filters work
│   └── sortable columns work
├── About Page
│   ├── loads with content
│   └── accordion toggles
├── Contact Page
│   ├── loads with form
│   └── validates required fields
├── Cross-Page Navigation
│   ├── council card → member detail
│   ├── member vote → vote detail
│   └── vote detail → meeting detail
└── Console Errors
    └── no JS errors on any page
```

### Running Individual Tests

```bash
# Run all tests
npx playwright test tests/test_site.spec.js

# Run a specific test group
npx playwright test tests/test_site.spec.js -g "Homepage"
npx playwright test tests/test_site.spec.js -g "Meetings"

# Run with headed browser (visible)
npx playwright test tests/test_site.spec.js --headed

# Run with debug mode (step through)
npx playwright test tests/test_site.spec.js --debug
```

### Expected Results

All tests should pass with output like:

```
  ✓ Homepage > loads with correct title (1.2s)
  ✓ Homepage > displays 4 KPI stat cards (0.8s)
  ✓ Homepage > filter buttons toggle council cards (1.1s)
  ...
  ✓ Console Errors > no JavaScript errors on any page (5.3s)

  16 passed (28.4s)
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Tests timeout waiting for data | JSON files missing or malformed | Check `data/` folder has all required files |
| Year filter has no options | `meetings.json` missing `available_years` | Regenerate meetings.json with available_years array |
| Console errors about fetch | Data file path incorrect | Verify `js/api.js` DATA_BASE_PATH matches folder structure |
| Member links 404 | Missing `council/{id}.json` files | Generate individual member JSON files |
| Vote detail blank | Missing `votes/{id}.json` files | Generate individual vote JSON files |
| Tests pass locally, fail deployed | Different base URL | Set `BASE_URL` env variable to deployed URL |
| Dropdown select timeout | Options populated dynamically | Tests use `waitForSelector` before selecting |

---

## CI/CD Integration

To run tests automatically on every push, add to your GitHub Actions workflow:

```yaml
name: Test CityVotes
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install chromium
      - name: Start server
        run: python3 -m http.server 8080 &
      - name: Run tests
        run: npx playwright test tests/test_site.spec.js
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Adding New Tests

When adding features to CityVotes, add corresponding tests:

1. Open `tests/test_site.spec.js`
2. Add a new `test.describe()` block for the feature
3. Use `page.goto()` to navigate, `page.locator()` to find elements
4. Use `expect()` assertions to verify behavior
5. Run `npx playwright test` to verify

### Example: Testing a new filter

```javascript
test('new status filter works', async ({ page }) => {
    await page.goto('/votes.html');
    // Wait for data to load
    await page.waitForSelector('.vote-card');
    // Select filter option
    await page.selectOption('#statusFilter', 'pending');
    // Verify results filtered
    const cards = page.locator('.vote-card');
    await expect(cards.first()).toBeVisible();
});
```
