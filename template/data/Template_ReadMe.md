# Data Files Required

Place these JSON files in this folder to populate the website.

## File List

| File | Description |
|------|-------------|
| `stats.json` | Global KPI statistics |
| `council.json` | All council members summary |
| `council/{id}.json` | Individual member details + vote history |
| `meetings.json` | All meetings list |
| `votes.json` | All votes combined |
| `votes-{year}.json` | Votes split by year (for performance) |
| `votes-index.json` | Available years index |
| `votes/{id}.json` | Individual vote detail with member votes |
| `alignment.json` | Voting alignment between member pairs |

---

## Schemas

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

**Field Glossary — stats.json:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` — indicates valid response |
| `stats.total_meetings` | integer | Total number of council meetings in the dataset |
| `stats.total_votes` | integer | Total number of individual vote items across all meetings |
| `stats.total_council_members` | integer | Number of council members (current + former) in the dataset |
| `stats.pass_rate` | float | Percentage of votes with PASS outcome: `(PASS count / total_votes) × 100` |
| `stats.unanimous_rate` | float | Percentage of votes where noes=0 AND abstain=0: `(unanimous / total_votes) × 100` |
| `stats.date_range.start` | string | Earliest meeting date in the dataset (ISO format YYYY-MM-DD) |
| `stats.date_range.end` | string | Most recent meeting date in the dataset (ISO format YYYY-MM-DD) |

---

### council.json
```json
{
  "success": true,
  "members": [
    {
      "id": 1,
      "full_name": "First Last",
      "short_name": "Last",
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

**Field Glossary — council.json:**

| Field | Type | Description |
|-------|------|-------------|
| `members[]` | array | List of all council members (current and former) |
| `members[].id` | integer | Unique identifier for this member (used in URLs: `council-member.html?id={id}`) |
| `members[].full_name` | string | Full display name (e.g., "Jane Smith") — shown on cards and headers |
| `members[].short_name` | string | Last name only (e.g., "Smith") — used in alignment pair labels |
| `members[].position` | string | Official title: "Mayor", "Vice Mayor", or "Council Member" |
| `members[].start_date` | string | Date this member began serving (ISO format YYYY-MM-DD) |
| `members[].end_date` | string\|null | Date member left office, or `null` if still serving |
| `members[].is_current` | boolean | `true` if actively serving — controls "Current"/"Former" badge color |
| `members[].stats.total_votes` | integer | Total number of vote items during this member's term |
| `members[].stats.aye_count` | integer | Number of times this member voted AYE |
| `members[].stats.nay_count` | integer | Number of times this member voted NAY |
| `members[].stats.abstain_count` | integer | Number of times this member abstained |
| `members[].stats.absent_count` | integer | Number of times this member was absent |
| `members[].stats.recusal_count` | integer | Number of times this member recused themselves (conflict of interest) |
| `members[].stats.aye_percentage` | float | `(aye_count / total_votes) × 100` — shown as "Aye Rate" |
| `members[].stats.participation_rate` | float | `((total_votes - absent_count - abstain_count) / total_votes) × 100` |
| `members[].stats.dissent_rate` | float | Percentage of times member voted against the winning side (see Calculated Metrics) |
| `members[].stats.votes_on_losing_side` | integer | Count of votes where member was NAY on PASS or AYE on FAIL |
| `members[].stats.close_vote_dissents` | integer | Dissents on votes decided by 1-2 vote margin |

---

### council/{id}.json
```json
{
  "success": true,
  "member": {
    "id": 1,
    "full_name": "First Last",
    "short_name": "Last",
    "position": "Mayor",
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
      "votes_on_losing_side": 52,
      "votes_on_winning_side": 1132,
      "dissent_rate": 4.4,
      "close_vote_dissents": 7
    },
    "recent_votes": [
      {
        "vote_id": 123,
        "meeting_date": "YYYY-MM-DD",
        "item_number": "10",
        "title": "Vote title text",
        "vote_choice": "AYE|NAY|ABSTAIN|ABSENT|RECUSAL",
        "outcome": "PASS|FAIL",
        "topics": ["Topic1", "Topic2"],
        "meeting_type": "regular|special"
      }
    ]
  }
}
```

**Field Glossary — council/{id}.json:**

Same fields as `council.json` member object, plus:

| Field | Type | Description |
|-------|------|-------------|
| `member.stats.votes_on_winning_side` | integer | Count of votes where member agreed with the final outcome |
| `member.recent_votes[]` | array | Complete voting history for this member (all votes, not just recent) |
| `member.recent_votes[].vote_id` | integer | Links to `votes/{vote_id}.json` for full vote details |
| `member.recent_votes[].meeting_date` | string | Date of the meeting where this vote occurred (ISO format) |
| `member.recent_votes[].item_number` | string | Agenda item number (e.g., "10", "5A") — may contain letters |
| `member.recent_votes[].title` | string | Short title of the vote/agenda item |
| `member.recent_votes[].vote_choice` | string | How this member voted: `AYE`, `NAY`, `ABSTAIN`, `ABSENT`, or `RECUSAL` |
| `member.recent_votes[].outcome` | string | Final result of the vote: `PASS` or `FAIL` |
| `member.recent_votes[].topics` | array | Topic categories assigned to this vote (from 16 predefined categories) |
| `member.recent_votes[].meeting_type` | string | `"regular"` or `"special"` session |

---

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

**Field Glossary — meetings.json:**

| Field | Type | Description |
|-------|------|-------------|
| `meetings[]` | array | All council meetings, sorted by date descending (newest first) |
| `meetings[].id` | integer | Unique meeting identifier (used in URLs: `meeting-detail.html?id={id}`) |
| `meetings[].meeting_date` | string | Date the meeting occurred (ISO format YYYY-MM-DD) |
| `meetings[].meeting_type` | string | `"regular"` = scheduled session; `"special"` = called outside normal schedule |
| `meetings[].agenda_url` | string\|null | URL to the agenda PDF document, or `null` if not available. When `null`, the UI shows a grayed-out badge. |
| `meetings[].minutes_url` | string\|null | URL to the approved minutes PDF, or `null` if not available |
| `meetings[].video_url` | string\|null | URL to the video recording (typically YouTube), or `null` if not available |
| `meetings[].agenda_item_count` | integer | Number of agenda items discussed at this meeting |
| `meetings[].vote_count` | integer | Number of formal votes taken at this meeting |

---

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
      "title": "Vote title text",
      "meeting_date": "YYYY-MM-DD",
      "meeting_type": "regular|special",
      "topics": ["Budget & Finance", "Housing"]
    }
  ]
}
```

**Field Glossary — votes.json:**

| Field | Type | Description |
|-------|------|-------------|
| `votes[]` | array | All vote records. `votes.json` has every vote; `votes-{year}.json` has one year only (for faster loading). |
| `votes[].id` | integer | Unique vote identifier (used in URLs: `vote-detail.html?id={id}`) |
| `votes[].outcome` | string | Final result of the vote. Standard: `PASS`, `FAIL`. Special/procedural: `CONTINUED`, `REMOVED`, `FLAG`, `TABLED`, `WITHDRAWN`. Special outcomes display a yellow "Flag" badge instead of vote tallies. |
| `votes[].ayes` | integer | Number of council members who voted AYE (yes) |
| `votes[].noes` | integer | Number of council members who voted NAY (no) |
| `votes[].abstain` | integer | Number of council members who abstained |
| `votes[].absent` | integer | Number of council members who were absent for this vote |
| `votes[].item_number` | string | Agenda item number (e.g., "10", "5A", "PH-3"). String type because it may contain letters. |
| `votes[].section` | string | Agenda section: `CONSENT` (routine/bundled items), `GENERAL` (regular business), or `PUBLIC_HEARING` (public comment required) |
| `votes[].title` | string | Short description of what was voted on |
| `votes[].meeting_date` | string | Date of the meeting where this vote occurred (ISO format) — used to join with meetings.json for document URLs |
| `votes[].meeting_type` | string | `"regular"` or `"special"` — inherited from the meeting |
| `votes[].topics` | array | 0-3 topic categories from the 16 predefined list (see Topic Categories below). Assigned by keyword analysis or AI classification. |

**Outcome values explained:**

| Outcome | Meaning | UI Display |
|---------|---------|------------|
| `PASS` | Motion approved by majority | Green "Pass" badge + vote tally |
| `FAIL` | Motion did not receive enough votes | Red "Fail" badge + vote tally |
| `CONTINUED` | Item postponed to future meeting | Yellow "Flag" badge, no tally |
| `REMOVED` | Item removed from agenda before vote | Yellow "Flag" badge, no tally |
| `FLAG` | Data quality issue — vote record may be unreliable | Yellow "Flag" badge, no tally |
| `TABLED` | Discussion/vote deferred indefinitely | Yellow "Flag" badge, no tally |
| `WITHDRAWN` | Item withdrawn by the person who proposed it | Yellow "Flag" badge, no tally |

**Section values explained:**

| Section | Meaning |
|---------|---------|
| `CONSENT` | Routine items bundled for single vote (e.g., approving minutes, routine contracts) |
| `GENERAL` | Regular business items discussed and voted individually |
| `PUBLIC_HEARING` | Items requiring public testimony before vote (e.g., zoning changes, permits) |

---

### votes-index.json
```json
{
  "success": true,
  "available_years": [2024, 2023, 2022]
}
```

**Field Glossary — votes-index.json:**

| Field | Type | Description |
|-------|------|-------------|
| `available_years` | array of integers | Years for which vote data exists, sorted descending (newest first). Used to populate year filter dropdowns and to know which `votes-{year}.json` files exist. |

---

### votes/{id}.json
```json
{
  "success": true,
  "vote": {
    "id": 1,
    "item_number": "10",
    "title": "Full title text",
    "description": "Full description with recommended actions, minutes text, etc.",
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
        "full_name": "First Last",
        "vote_choice": "AYE|NAY|ABSTAIN|ABSENT|RECUSAL"
      }
    ],
    "topics": ["Topic1", "Topic2"]
  }
}
```

**Field Glossary — votes/{id}.json:**

Same tally fields as `votes.json`, plus:

| Field | Type | Description |
|-------|------|-------------|
| `vote.description` | string | Full text of the agenda item — typically includes the staff recommendation, background, and any minutes notes. Shown on the vote detail page. May be empty string if no description available. |
| `vote.meeting_id` | integer | Links to the meeting in `meetings.json` — used to generate "View Meeting" link (`meeting-detail.html?id={meeting_id}`) |
| `vote.member_votes[]` | array | How each council member voted on this item. One entry per member present/expected. |
| `vote.member_votes[].member_id` | integer | Links to `council/{member_id}.json` — used to generate member profile links |
| `vote.member_votes[].full_name` | string | Member's display name (e.g., "Jane Smith") |
| `vote.member_votes[].vote_choice` | string | Individual vote cast. Values and their UI colors: |

**Vote choice values:**

| Choice | Meaning | Badge Color |
|--------|---------|-------------|
| `AYE` | Voted yes / in favor | Green (`bg-success`) |
| `NAY` | Voted no / against | Red (`bg-danger`) |
| `ABSTAIN` | Chose not to vote (present but not voting) | Yellow (`bg-warning`) |
| `ABSENT` | Not present at time of vote | Gray (`bg-secondary`) |
| `RECUSAL` | Recused due to conflict of interest | Teal (`bg-info`) |

---

### alignment.json
```json
{
  "success": true,
  "members": ["Last1", "Last2", "Last3"],
  "alignment_pairs": [
    {
      "member1": "Last1",
      "member2": "Last2",
      "shared_votes": 1226,
      "agreements": 1208,
      "agreement_rate": 98.6
    }
  ],
  "most_aligned": [],
  "least_aligned": []
}
```

**Field Glossary — alignment.json:**

| Field | Type | Description |
|-------|------|-------------|
| `members` | array of strings | Short names (last names) of all council members in the alignment dataset |
| `alignment_pairs[]` | array | Every unique pair of council members with their voting agreement statistics |
| `alignment_pairs[].member1` | string | Short name of first member in the pair |
| `alignment_pairs[].member2` | string | Short name of second member in the pair |
| `alignment_pairs[].shared_votes` | integer | Number of votes where both members participated (excludes votes where either was ABSENT, ABSTAIN, or RECUSAL) |
| `alignment_pairs[].agreements` | integer | Number of shared votes where both members chose the same option (both AYE or both NAY) |
| `alignment_pairs[].agreement_rate` | float | `(agreements / shared_votes) × 100` — how often these two members vote the same way |
| `most_aligned` | array | Top 3 pairs with the highest agreement_rate — shown on the home page "Most Aligned" card. Same structure as `alignment_pairs[]`. |
| `least_aligned` | array | Top 3 pairs with the lowest agreement_rate — shown on the home page "Least Aligned" card. Same structure as `alignment_pairs[]`. |

---

## Calculated Metrics

These values are pre-computed and stored in the JSON files. Here are the formulas used:

### Aye Percentage
```
aye_percentage = (aye_count / total_votes) × 100
```
How often a member votes YES. Displayed on council cards and member profiles.

### Participation Rate
```
participation_rate = ((total_votes - absent_count - abstain_count) / total_votes) × 100
```
How often a member actively participates (votes AYE or NAY, not absent or abstaining).

### Dissent Rate
```
dissent_rate = (votes_on_losing_side / valid_votes) × 100

valid_votes = total_votes MINUS:
  - ABSENT votes
  - ABSTAIN votes
  - Votes with special outcomes (CONTINUED, REMOVED, FLAG, TABLED, WITHDRAWN)

votes_on_losing_side = votes where:
  (outcome = PASS AND vote_choice = NAY) OR
  (outcome = FAIL AND vote_choice = AYE)
```
How often a member votes against the majority. A high dissent rate means the member frequently disagrees with the council's decisions.

### Agreement Rate (Alignment)
```
shared_votes = votes where BOTH members participated (not ABSENT/ABSTAIN/RECUSAL)
agreements = shared_votes where both chose the SAME option (both AYE or both NAY)
agreement_rate = (agreements / shared_votes) × 100
```
How often two members vote the same way. Used for "Most Aligned" and "Least Aligned" displays.

### Pass Rate
```
pass_rate = (PASS outcomes / total_votes) × 100
```
What percentage of all votes result in approval.

### Unanimous Rate
```
unanimous_rate = (votes where noes=0 AND abstain=0 / total_votes) × 100
```
What percentage of votes had no opposition or abstentions.

---

## Topic Categories (16)

Topics are assigned to each vote based on keyword analysis of the vote title. A vote may have 0-3 topics.

| # | Category | Description |
|---|----------|-------------|
| 1 | Appointments | Board/commission appointments, staffing decisions |
| 2 | Budget & Finance | Annual budget, appropriations, revenue, financial reports |
| 3 | Community Services | Libraries, social services, community programs, nonprofits |
| 4 | Contracts & Agreements | Vendor contracts, service agreements, MOUs |
| 5 | Economic Development | Business incentives, redevelopment, commercial projects |
| 6 | Emergency Services | Police, fire, EMS, disaster preparedness |
| 7 | Health & Safety | Public health, code enforcement, safety regulations |
| 8 | Housing | Affordable housing, tenant protections, residential projects |
| 9 | Infrastructure | Roads, bridges, water systems, sewer, utilities |
| 10 | Ordinances & Resolutions | Municipal code changes, formal declarations |
| 11 | Parks & Recreation | Parks, trails, recreation centers, youth sports |
| 12 | Planning & Development | Zoning, land use, environmental review, permits |
| 13 | Property & Real Estate | City property sales/purchases, easements, leases |
| 14 | Public Works | Street maintenance, waste management, city facilities |
| 15 | Transportation | Transit, bike lanes, traffic signals, parking |
| 16 | General | Fallback category for items that don't match other topics |

---

## Data File Dependencies

This diagram shows which pages load which data files:

```
index.html          → stats.json, council.json, meetings.json, alignment.json
council.html        → council.json
council-member.html → council/{id}.json, alignment.json, council.json (for filtered alignment)
meetings.html       → meetings.json, stats.json
meeting-detail.html → meetings.json, votes.json (joined by meeting_date)
votes.html          → votes-index.json, votes-{year}.json, meetings.json (for doc URLs)
vote-detail.html    → votes/{id}.json
agenda-search.html  → votes.json, meetings.json (for doc URLs)
```

---

## Null / Missing Value Handling

| Field | When Null/Missing | UI Behavior |
|-------|-------------------|-------------|
| `end_date` | Member still serving | Displays "Present" |
| `agenda_url` | No agenda document available | Grayed-out badge (not clickable) |
| `minutes_url` | No minutes document available | Grayed-out badge (not clickable) |
| `video_url` | No video recording available | Grayed-out badge (not clickable) |
| `description` | No detailed description | Description section hidden on vote detail page |
| `topics` | Empty array `[]` | No topic badges shown |
