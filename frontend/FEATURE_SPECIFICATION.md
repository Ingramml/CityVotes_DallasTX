# CityVotes Website Feature Specification

This document describes all features, visualizations, and data relationships for the CityVotes civic transparency platform. Use this specification to replicate the website for another city.

---

## Table of Contents
1. [Data Architecture](#data-architecture)
2. [Pages Overview](#pages-overview)
3. [Feature Details by Page](#feature-details-by-page)
4. [Data Schema Reference](#data-schema-reference)
5. [Calculated Metrics](#calculated-metrics)

---

## Data Architecture

### Data Files Structure
```
data/
├── stats.json              # Global statistics
├── council.json            # All council members (summary)
├── council/
│   └── {id}.json           # Individual member details + all votes
├── meetings.json           # All meetings list
├── votes.json              # All votes (combined)
├── votes-{year}.json       # Votes by year (for performance)
├── votes-index.json        # Available years index
├── votes/
│   └── {id}.json           # Individual vote details
└── alignment.json          # Voting alignment pairs
```

### Core Entities
| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Council Member** | Elected official | id, full_name, short_name, position, start_date, end_date, is_current |
| **Meeting** | Council session | id, meeting_date, meeting_type, agenda_url, minutes_url, video_url |
| **Vote** | Agenda item vote | id, title, outcome, ayes, noes, abstain, absent, meeting_date, topics |
| **Member Vote** | Individual vote cast | member_id, vote_choice (AYE/NAY/ABSTAIN/ABSENT/RECUSAL) |

---

## Pages Overview

| Page | URL | Purpose |
|------|-----|---------|
| Home | `index.html` | Dashboard with KPIs, council preview, alignment |
| Council | `council.html` | All council members grid |
| Council Member | `council-member.html?id={id}` | Individual member profile |
| Meetings | `meetings.html` | All meetings with filters |
| Meeting Detail | `meeting-detail.html?id={id}` | Single meeting agenda |
| Votes | `votes.html` | Searchable votes list |
| Agenda Search | `agenda-search.html` | Advanced vote search |
| Vote Detail | `vote-detail.html?id={id}` | Single vote breakdown |
| About | `about.html` | Information page |
| Contact | `contact.html` | Contact form |

---

## Feature Details by Page

### 1. HOME PAGE (`index.html`)

#### 1.1 Global Statistics Bar
**Visualization:** 4 KPI stat cards in a row
**Data Source:** `stats.json`

| Metric | Field | Calculation |
|--------|-------|-------------|
| Total Votes | `total_votes` | Count of all votes |
| Meetings | `total_meetings` | Count of all meetings |
| Pass Rate | `pass_rate` | (PASS outcomes / total votes) × 100 |
| Unanimous Rate | `unanimous_rate` | (votes where noes=0 AND abstain=0 / total) × 100 |

**Display:** Large number with label below

#### 1.2 Council Members Grid
**Visualization:** Card grid (4 columns on desktop)
**Data Source:** `council.json`

Each card shows:
- Member name
- Position (Mayor, Council Member)
- Current/Former badge
- Aye percentage (green checkmark icon)
- Participation rate (chart icon)
- Link to member profile

#### 1.3 Recent Meetings List
**Visualization:** List group with 5 most recent meetings
**Data Source:** `meetings.json` (sorted by date descending, limit 5)

Each item shows:
- Meeting date
- Meeting type badge (regular/special)
- Vote count
- Document badges (Agenda, Minutes, Video) - clickable links when available

#### 1.4 Voting Alignment Cards
**Visualization:** Two side-by-side cards
**Data Source:** `alignment.json`

| Card | Data Field | Shows |
|------|------------|-------|
| Most Aligned | `most_aligned` array | Top 3 pairs with highest agreement_rate |
| Least Aligned | `least_aligned` array | Top 3 pairs with lowest agreement_rate |

Each pair displays: Member1 + Member2, agreement percentage, shared votes count

---

### 2. COUNCIL PAGE (`council.html`)

#### 2.1 Council Members Grid
**Visualization:** Card grid (responsive columns)
**Data Source:** `council.json`

Each member card includes:

| Element | Data Field | Display |
|---------|------------|---------|
| Name | `full_name` | Card title |
| Position | `position` | Subtitle |
| Status | `is_current` | Green "Current" or gray "Former" badge |
| Photo placeholder | - | User icon |
| Aye Rate | `stats.aye_percentage` | Percentage |
| Dissent Rate | `stats.dissent_rate` | Percentage |
| Participation | `stats.participation_rate` | Percentage |

**Voting Pattern Bar:**
- Green segment: Aye percentage
- Red segment: Nay percentage
- Gray segment: Absent/Abstain percentage

**Link:** Card links to `council-member.html?id={member.id}`

---

### 3. COUNCIL MEMBER PAGE (`council-member.html?id={id}`)

#### 3.1 Member Header
**Data Source:** `council/{id}.json`

Displays:
- Full name
- Position
- Term dates (start_date - end_date or "Present")
- Current status badge

#### 3.2 Statistics Cards (4 KPIs)
**Visualization:** 4 stat cards in a row
**Data Source:** `council/{id}.json` → `member.stats`

| Card | Field | Color | Detail |
|------|-------|-------|--------|
| Aye Rate | `aye_percentage` | Green | "{aye_count} of {total_votes}" |
| Participation | `participation_rate` | Blue | "{total - absent - abstain} of {total_votes}" |
| Dissent Rate | `dissent_rate` | Yellow/Warning | "{votes_on_losing_side} of {valid_votes}" |
| Total Votes | `total_votes` | Primary | - |

#### 3.3 Filters
**Filters Available:**
- Year dropdown (populated from vote dates)
- Topic dropdown (16 categories)
- Outcome dropdown (PASS/FAIL/SPECIAL)

**Behavior:** Filters update the votes table AND recalculate statistics dynamically

#### 3.4 Voting History Table
**Visualization:** Paginated table
**Data Source:** `council/{id}.json` → `member.recent_votes` (or all_votes)

| Column | Field | Notes |
|--------|-------|-------|
| Date | `meeting_date` | Formatted |
| Item | `item_number` | Badge |
| Title | `title` | Truncated, links to vote detail |
| Vote | `vote_choice` | Color-coded badge |
| Outcome | `outcome` | Color-coded badge |

---

### 4. MEETINGS PAGE (`meetings.html`)

#### 4.1 KPI Cards
**Visualization:** 3 stat cards
**Data Source:** `meetings.json` (calculated)

| Metric | Calculation |
|--------|-------------|
| Total Meetings | Count of meetings (filtered) |
| Total Votes | Sum of vote_count (filtered) |
| Regular/Special | Count by meeting_type |

**Dynamic:** KPIs update when year filter changes

#### 4.2 Year Filter
**Visualization:** Dropdown
**Data Source:** Derived from `meetings.json` meeting dates

#### 4.3 Meetings List
**Visualization:** List group with accordions
**Data Source:** `meetings.json`

Each meeting item shows:
- Meeting date (formatted)
- Meeting type badge
- Vote count
- **Document Badges:**
  - Agenda (file icon) - links to `agenda_url`
  - Minutes (clipboard icon) - links to `minutes_url`
  - Video (video icon, red) - links to `video_url`
  - Gray badges shown when URL is null

**Link:** Clicking row expands or navigates to `meeting-detail.html?id={id}`

---

### 5. MEETING DETAIL PAGE (`meeting-detail.html?id={id}`)

#### 5.1 Meeting Header
**Data Source:** Meeting lookup from `meetings.json` or API

Displays:
- Meeting date
- Meeting type
- Document links (Agenda, Minutes, Video)

#### 5.2 Agenda Items Table
**Visualization:** Table of votes from that meeting
**Data Source:** Votes filtered by `meeting_date`

| Column | Description |
|--------|-------------|
| Item # | Agenda item number |
| Title | Vote title/description |
| Outcome | PASS/FAIL badge |
| Tally | Ayes-Noes-Abstain format |
| Action | Link to vote detail |

---

### 6. VOTES PAGE (`votes.html`)

#### 6.1 Search and Filters
**Filters:**

| Filter | Type | Data Source |
|--------|------|-------------|
| Search | Text input | Searches title/description |
| Year | Dropdown | `votes-index.json` available_years |
| Topic | Dropdown | 16 predefined categories |
| Outcome | Dropdown | PASS, FAIL, SPECIAL (procedural) |

**SPECIAL Outcomes:** CONTINUED, REMOVED, FLAG, TABLED, WITHDRAWN

#### 6.2 Results Count
**Display:** "Showing X of Y votes"

#### 6.3 Votes Table
**Visualization:** Paginated table (25 per page)
**Data Source:** `votes-{year}.json` or `votes.json`

| Column | Field | Display |
|--------|-------|---------|
| Date | `meeting_date` | Formatted date + meeting_type |
| Item | `item_number` | Badge |
| Title | `title` | Truncated, links to detail |
| Outcome | `outcome` | Color-coded badge |
| Tally | ayes/noes/abstain | "7-0-0" format, or "Flag" for special |
| Documents | meeting URLs | Icon buttons/badges |
| Action | - | Eye icon link to detail |

**Document Icons:**
- Available: Clickable outline buttons
- Unavailable: Grayed badge with tooltip

---

### 7. AGENDA SEARCH PAGE (`agenda-search.html`)

#### 7.1 Advanced Search Interface
**Filters:**

| Filter | Description |
|--------|-------------|
| Search text | Keyword search in title |
| Year | Filter by year |
| Topic | 16-category dropdown |
| Meeting Type | Regular/Special |
| Outcome | PASS/FAIL/SPECIAL |

#### 7.2 Sortable Results Table
**Columns:** (click to sort)
- Date (default: descending)
- Item #
- Title
- Topic (badge, first 2 topics)
- Type
- Outcome
- Documents
- Action

#### 7.3 URL State
Filters are reflected in URL query params for bookmarking/sharing

---

### 8. VOTE DETAIL PAGE (`vote-detail.html?id={id}`)

#### 8.1 Vote Header
**Data Source:** `votes/{id}.json`

Displays:
- Title (full text)
- Description (full text)
- Meeting date and type
- Item number

#### 8.2 Outcome Summary
**Visualization:** Large outcome badge + tally

| Element | Display |
|---------|---------|
| Outcome | Large colored badge (PASS=green, FAIL=red) |
| Tally | "7 Ayes, 0 Noes, 0 Abstain, 0 Absent" |

#### 8.3 Member Votes Breakdown
**Visualization:** List or grid of all council member votes
**Data Source:** `votes/{id}.json` → `member_votes` array

Each member shows:
- Name (links to member profile)
- Vote choice badge:
  - AYE = Green
  - NAY = Red
  - ABSTAIN = Yellow
  - ABSENT = Gray
  - RECUSAL = Purple

#### 8.4 Topics
**Visualization:** Badge list
**Data Source:** `votes/{id}.json` → `topics` array

---

## Data Schema Reference

### stats.json
```json
{
  "success": true,
  "stats": {
    "total_meetings": 70,
    "total_votes": 1244,
    "total_council_members": 7,
    "pass_rate": 95.1,
    "unanimous_rate": 73.8,
    "date_range": {
      "start": "2022-01-04",
      "end": "2024-12-17"
    }
  }
}
```

### council.json
```json
{
  "success": true,
  "members": [
    {
      "id": 1,
      "full_name": "Name",
      "short_name": "LastName",
      "position": "Mayor|Council Member",
      "start_date": "YYYY-MM-DD",
      "end_date": null,
      "is_current": true,
      "stats": {
        "total_votes": 1244,
        "aye_count": 1148,
        "nay_count": 54,
        "abstain_count": 8,
        "absent_count": 26,
        "recusal_count": 8,
        "aye_percentage": 94.9,
        "participation_rate": 97.3,
        "dissent_rate": 4.4,
        "votes_on_losing_side": 52,
        "close_vote_dissents": 7
      }
    }
  ]
}
```

### council/{id}.json
```json
{
  "success": true,
  "member": {
    "id": 1,
    "full_name": "Name",
    "short_name": "LastName",
    "position": "Mayor",
    "start_date": "YYYY-MM-DD",
    "end_date": null,
    "is_current": true,
    "stats": { /* same as above */ },
    "recent_votes": [
      {
        "vote_id": 123,
        "meeting_date": "YYYY-MM-DD",
        "item_number": "10",
        "title": "Vote title...",
        "vote_choice": "AYE",
        "outcome": "PASS"
      }
    ]
  }
}
```

### meetings.json
```json
{
  "success": true,
  "meetings": [
    {
      "id": 1,
      "meeting_date": "YYYY-MM-DD",
      "meeting_type": "regular|special",
      "agenda_url": "https://...|null",
      "minutes_url": "https://...|null",
      "video_url": "https://...|null",
      "agenda_item_count": 23,
      "vote_count": 23
    }
  ]
}
```

### votes.json / votes-{year}.json
```json
{
  "success": true,
  "votes": [
    {
      "id": 1,
      "outcome": "PASS|FAIL|CONTINUED|REMOVED|FLAG|TABLED|WITHDRAWN",
      "ayes": 7,
      "noes": 0,
      "abstain": 0,
      "absent": 0,
      "item_number": "10",
      "section": "CONSENT|GENERAL|PUBLIC_HEARING",
      "title": "Vote title...",
      "meeting_date": "YYYY-MM-DD",
      "meeting_type": "regular|special",
      "topics": ["Budget & Finance", "Housing"]
    }
  ]
}
```

### votes/{id}.json
```json
{
  "success": true,
  "vote": {
    "id": 1,
    "item_number": "10",
    "title": "Full title...",
    "description": "Full description with details...",
    "outcome": "PASS",
    "ayes": 7,
    "noes": 0,
    "abstain": 0,
    "absent": 0,
    "meeting_id": 7,
    "meeting_date": "YYYY-MM-DD",
    "meeting_type": "regular",
    "member_votes": [
      {
        "member_id": 1,
        "full_name": "Member Name",
        "vote_choice": "AYE|NAY|ABSTAIN|ABSENT|RECUSAL"
      }
    ],
    "topics": ["Topic1", "Topic2"]
  }
}
```

### alignment.json
```json
{
  "success": true,
  "members": ["Lastname1", "Lastname2"],
  "alignment_pairs": [
    {
      "member1": "Lastname1",
      "member2": "Lastname2",
      "shared_votes": 1226,
      "agreements": 1208,
      "agreement_rate": 98.6
    }
  ],
  "most_aligned": [ /* top 3 pairs */ ],
  "least_aligned": [ /* bottom 3 pairs */ ]
}
```

---

## Calculated Metrics

### Aye Percentage
```
aye_percentage = (aye_count / total_votes) × 100
```

### Participation Rate
```
participation_rate = ((total_votes - absent_count - abstain_count) / total_votes) × 100
```

### Dissent Rate
A council member "dissents" when they vote against the winning side:
- Votes NAY on a PASS outcome, OR
- Votes AYE on a FAIL outcome

```
dissent_rate = (votes_on_losing_side / valid_votes) × 100

Where valid_votes excludes:
- ABSENT votes
- ABSTAIN votes
- Special outcomes (CONTINUED, REMOVED, FLAG, TABLED, WITHDRAWN)
```

### Agreement Rate (Alignment)
For a pair of members:
```
shared_votes = votes where both members participated (not ABSENT/ABSTAIN)
agreements = votes where both chose the same option (both AYE or both NAY)
agreement_rate = (agreements / shared_votes) × 100
```

### Pass Rate
```
pass_rate = (PASS outcomes / total_votes) × 100
```

### Unanimous Rate
```
unanimous_rate = (votes where noes=0 AND abstain=0 / total_votes) × 100
```

---

## Topic Categories (16)

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
16. General

Topics are assigned via keyword analysis of vote titles.

---

## Technology Stack

- **Frontend:** HTML5, Bootstrap 5, Font Awesome 6
- **Data:** Static JSON files (no backend required)
- **API:** `js/api.js` - CityVotesAPI object with fetch methods
- **Hosting:** Static hosting (Vercel, Netlify, GitHub Pages)
- **Styling:** Custom CSS (`css/theme.css`) with CSS custom properties for city branding

---

## Replication Steps for New City

1. **Data Collection:**
   - Gather meeting records, agendas, minutes
   - Extract vote records with member-level votes
   - Collect council member information

2. **Data Transformation:**
   - Format data into JSON schema above
   - Calculate statistics (aye rates, dissent, alignment)
   - Assign topics via keyword analysis

3. **Customization:**
   - Update city name in HTML/meta tags
   - Update color scheme in `css/theme.css` CSS custom properties (`--city-primary`, `--city-accent`)
   - Update footer and contact information

4. **Deployment:**
   - Host static files on any web server
   - No database or backend required
