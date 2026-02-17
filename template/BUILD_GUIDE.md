# CityVotes Build & Deployment Guide

Step-by-step instructions to build and deploy a CityVotes website for a new city.
This guide is designed to be followed by Claude or any developer.

---

## Prerequisites

- A GitHub account (for Vercel deployment)
- A Vercel account (free tier works)
- City council voting data in any structured format (CSV, JSON, spreadsheet)
- The contents of this `template/` folder

---

## Quick Start (5 Steps)

```
1. Copy this template/ folder to a new repository
2. Replace {CityName} in all HTML files with your city name
3. Set city brand colors in css/theme.css
4. Generate and place JSON data files in data/
5. Push to GitHub → connect to Vercel → deploy
```

---

## Step 1: Create New Repository

1. Create a new GitHub repository (e.g., `cityvotes-longbeach`)
2. Copy the entire contents of this `template/` folder into the repo root:

```
your-new-repo/
├── index.html
├── council.html
├── council-member.html
├── meetings.html
├── meeting-detail.html
├── votes.html
├── vote-detail.html
├── agenda-search.html
├── about.html
├── contact.html
├── vercel.json
├── css/
│   └── theme.css
├── js/
│   └── api.js
└── data/
    ├── stats.json
    ├── council.json
    ├── council/
    │   └── {1..N}.json
    ├── meetings.json
    ├── votes.json
    ├── votes-index.json
    ├── votes-{year}.json (one per year)
    ├── votes/
    │   └── {1..N}.json
    └── alignment.json
```

---

## Step 2: Customize City Name

Find-and-replace `{CityName}` with your city's name across ALL HTML files.

**Files to update:**
- `index.html`
- `council.html`
- `council-member.html`
- `meetings.html`
- `meeting-detail.html`
- `votes.html`
- `vote-detail.html`
- `agenda-search.html`
- `about.html`
- `contact.html`

**What to replace:**

| Find | Replace With | Example |
|------|-------------|---------|
| `{CityName}` | Your city name | "Long Beach" |

This appears in:
- `<title>` tags
- `<meta>` description and Open Graph tags
- Navbar city badge text
- Footer text
- Page headers and descriptions

---

## Step 3: Set City Brand Colors

Edit `css/theme.css` and update the CSS custom properties at the top:

```css
:root {
    --city-primary: #1f4e79;       /* Main brand color (navbar, headers) */
    --city-primary-light: #2d6da3; /* Hover state for primary */
    --city-primary-dark: #163a5c;  /* Active state for primary */
    --city-accent: #f4b942;        /* Accent color (highlights, links) */
    --city-accent-light: #f7ca6e;  /* Lighter accent variant */
}
```

**How to choose colors:**
- `--city-primary`: Use the city's official brand color (check city website/logo)
- `--city-accent`: A contrasting highlight color that pairs with the primary
- Ensure sufficient contrast ratio (4.5:1 minimum for WCAG AA compliance)

---

## Step 4: Generate Data Files

You need to generate 9 types of JSON files. See `data/Template_ReadMe.md` for complete schemas and field glossary.

### 4.1 Required Raw Data

Before generating JSON, you need this source data:

| Data | Where to Find It |
|------|-------------------|
| Council member names, positions, terms | City website, clerk's office |
| Meeting dates and types | Meeting calendars, agendas |
| Document URLs (agenda PDFs, minutes, videos) | City website, YouTube channel |
| Vote records (item#, title, outcome, tally) | Official meeting minutes |
| Individual member votes per item | Official meeting minutes |
| Vote descriptions | Agenda packets |

### 4.2 Data Files to Generate

Generate these files in order (later files depend on earlier ones):

#### Step A: Core Data

**`data/council.json`** — All council members with pre-computed stats
- List every council member (current and former)
- Calculate stats for each: aye_count, nay_count, abstain_count, absent_count, recusal_count
- Calculate: aye_percentage, participation_rate, dissent_rate

**`data/meetings.json`** — All meetings
- One entry per meeting date with type, document URLs, vote count

**`data/votes.json`** — All votes combined
- One entry per agenda item vote with outcome, tally, section, topics

#### Step B: Split/Detail Files

**`data/votes-index.json`** — List of years
```json
{ "success": true, "available_years": [2024, 2023, 2022] }
```

**`data/votes-{year}.json`** — Votes filtered by year (one file per year)
- Same schema as votes.json but only votes from that year

**`data/council/{id}.json`** — One file per council member
- Full member details plus complete voting history (all_votes/recent_votes array)

**`data/votes/{id}.json`** — One file per vote
- Full vote details including member_votes array (who voted what)

#### Step C: Computed Data

**`data/stats.json`** — Global statistics
```
total_meetings = count of meetings
total_votes = count of votes
total_council_members = count of members
pass_rate = (PASS outcomes / total_votes) × 100
unanimous_rate = (votes where noes=0 AND abstain=0 / total_votes) × 100
date_range = { start: earliest date, end: latest date }
```

**`data/alignment.json`** — Voting alignment pairs
- For every pair of members, calculate:
  - shared_votes = votes where both participated (not ABSENT/ABSTAIN/RECUSAL)
  - agreements = shared_votes where both chose same option
  - agreement_rate = (agreements / shared_votes) × 100
- Sort pairs by agreement_rate
- `most_aligned` = top 3 pairs
- `least_aligned` = bottom 3 pairs

### 4.3 Calculated Metrics Reference

| Metric | Formula |
|--------|---------|
| Aye % | `(aye_count / total_votes) × 100` |
| Participation % | `((total - absent - abstain) / total) × 100` |
| Dissent % | `(votes_on_losing_side / valid_votes) × 100` |
| Pass Rate | `(PASS outcomes / total_votes) × 100` |
| Unanimous Rate | `(votes where noes=0 AND abstain=0 / total) × 100` |
| Agreement Rate | `(agreements / shared_votes) × 100` |

**Dissent = voting against the winning side:**
- NAY on a PASS outcome, OR AYE on a FAIL outcome
- Exclude ABSENT, ABSTAIN, and special outcomes from valid_votes

**Special outcomes** (not PASS/FAIL): CONTINUED, REMOVED, FLAG, TABLED, WITHDRAWN

### 4.4 Topic Assignment

Assign 0-3 topic categories to each vote based on keyword analysis of the title.

**16 Categories:**
1. Appointments
2. Budget & Finance
3. Community Services
4. Contracts & Agreements
5. Economic Development
6. Emergency Services
7. Health & Safety
8. Housing
9. Infrastructure
10. Ordinances & Resolutions
11. Parks & Recreation
12. Planning & Development
13. Property & Real Estate
14. Public Works
15. Transportation
16. General (fallback)

See `TOPIC_CLASSIFICATION_PLAN.md` (if available) for keyword dictionaries and classification approaches.

### 4.5 Data Folder Structure

After generation, your `data/` folder should look like:

```
data/
├── stats.json                    (1 file)
├── council.json                  (1 file)
├── council/
│   ├── 1.json                    (1 file per member)
│   ├── 2.json
│   └── ...
├── meetings.json                 (1 file)
├── votes.json                    (1 file — all votes)
├── votes-index.json              (1 file)
├── votes-2024.json               (1 file per year)
├── votes-2023.json
├── votes-2022.json
├── votes/
│   ├── 1.json                    (1 file per vote)
│   ├── 2.json
│   └── ...
└── alignment.json                (1 file)
```

**Total files:** ~3 + (number of members) + (number of years) + (number of votes)

---

## Step 5: Deploy to Vercel

### Option A: Vercel CLI

```bash
npm i -g vercel
cd your-new-repo
vercel
```

### Option B: GitHub Integration (Recommended)

1. Push your repo to GitHub
2. Go to [vercel.com](https://vercel.com) and sign in with GitHub
3. Click "New Project" → Import your repository
4. Framework Preset: **Other** (this is a static site, no build step)
5. Root Directory: `.` (leave as default)
6. Build Command: leave empty (no build needed)
7. Output Directory: `.` (leave as default)
8. Click **Deploy**

Vercel will auto-deploy on every push to the main branch.

### Vercel Configuration

The included `vercel.json` configures:
- Clean URLs (removes .html extensions)
- Cache headers for JSON data (1 hour), HTML (5 min), CSS/JS (24 hours)

---

## Step 6: Verify Deployment

After deployment, check every page:

| Page | URL | What to Verify |
|------|-----|----------------|
| Home | `/` | Stats load, council grid shows, meetings list populates, alignment cards show |
| Council | `/council` | All members display with correct stats |
| Member Profile | `/council-member?id=1` | Header, stats, filters, vote table, alignment sidebar |
| Meetings | `/meetings` | Year filter works, document badges show, pagination works |
| Meeting Detail | `/meeting-detail?id=1` | Agenda items load, vote tallies display |
| Votes | `/votes` | Search works, year/topic/outcome filters work, pagination |
| Vote Detail | `/vote-detail?id=1` | Tally card, member votes, grouped cards |
| Agenda Search | `/agenda-search` | KPI cards, sortable columns, URL persistence |
| About | `/about` | Content displays, accordion works |
| Contact | `/contact` | Form validates, submit works |

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Blank page / no data | JSON files missing from `data/` | Check file paths and names |
| "Failed to fetch" errors | CORS or incorrect paths | Ensure data files are in `data/` relative to root |
| Broken styling | Wrong CSS file path | Verify `css/theme.css` exists and is linked |
| Member links return 404 | Missing `council/{id}.json` | Generate individual member files |
| Vote detail blank | Missing `votes/{id}.json` | Generate individual vote files |
| Wrong city name showing | Incomplete find-and-replace | Search all HTML for remaining `{CityName}` |

---

## File Reference

| File | Purpose | Documentation |
|------|---------|---------------|
| `FEATURE_SPECIFICATION.md` | All features, visualizations, data relationships | What each page does |
| `WIREFRAMES.md` | ASCII wireframes for every page | How each page looks |
| `data/Template_ReadMe.md` | Complete JSON schemas + field glossary | Every data field explained |
| `BUILD_GUIDE.md` | This file | How to build and deploy |
| `TESTING_GUIDE.md` | Testing procedure + automated test suite | How to verify the site |
| `tests/test_site.spec.js` | Playwright automated test script | 58 tests across all pages |
| `playwright.config.js` | Playwright test runner configuration | Test settings |
| `vercel.json` | Vercel deployment configuration | Cache headers, clean URLs |
| `css/theme.css` | City-branded CSS with custom properties | Colors and styling |
| `js/api.js` | Static JSON data API client | Data loading layer |

---

## Updating Data

To update the site with new voting data:

1. Add new meeting/vote records to your source data
2. Re-generate all JSON files (stats change, member stats change, etc.)
3. Push updated `data/` folder to GitHub
4. Vercel auto-deploys within ~30 seconds

**Files that change on every update:**
- `stats.json` (totals change)
- `council.json` (member stats change)
- `council/{id}.json` (vote history grows)
- `meetings.json` (new meetings)
- `votes.json` (new votes)
- `votes-{year}.json` (current year file changes)
- `votes-index.json` (if new year added)
- `votes/{id}.json` (new vote detail files)
- `alignment.json` (agreement rates shift)
