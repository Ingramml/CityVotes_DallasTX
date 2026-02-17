# CityVotes Website Wireframes

ASCII wireframes for every page. Use as a template when building for another city.
Replace `{CityName}`, `{AppName}`, and `{Color}` placeholders with your city's values.

All data placeholders (e.g., `{TotalVotes}`, `{MemberName}`) map to fields documented
in `template/data/README.md`. See the **Data source** notes below each wireframe,
and the [Placeholder Glossary](#placeholder-glossary) at the end for a complete reference.

---

## Shared Components

### Navigation Bar (all pages)
```
+============================================================================+
| [ICON] {AppName}   | Home | Council | Meetings | Votes | Search |  [Help]  |
|                                                              [PIN] {City}  |
+============================================================================+
```
**Data:** Static links. City name from config.
**CSS:** `bg-city-primary`, `text-city-accent` (defined in `css/theme.css`)

### Footer (all pages)
```
+============================================================================+
| {AppName} - {CityName} Voting Transparency          Want another city?     |
| Data sourced from official records.                  [Contact us]    {Year} |
+============================================================================+
```

---

## Page 1: HOME / DASHBOARD (`index.html`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
|                                                                            |
|            [ICON] {CityName} City Council                                  |
|              Voting Records & Transparency                                 |
|                                                                            |
+============================================================================+
|                           STATISTICS BAR                                   |
|  +------------------+ +------------------+ +--------------+ +------------+ |
|  | {TotalVotes}     | | {TotalMeetings}  | | {PassRate}%  | |{Unanim.}% | |
|  |   Total Votes    | |     Meetings     | |  Pass Rate   | | Unanimous  | |
|  +------------------+ +------------------+ +--------------+ +------------+ |
+============================================================================+
|                                                                            |
|  CITY COUNCIL                                      [View All ->]           |
|  +-------------+ +-------------+ +-------------+ +-------------+          |
|  | [AVATAR]    | | [AVATAR]    | | [AVATAR]    | | [AVATAR]    |          |
|  | {Name}      | | {Name}      | | {Name}      | | {Name}      |          |
|  | [Current]   | | [Current]   | | [Current]   | | [Current]   |          |
|  | {Position}  | | {Position}  | | {Position}  | | {Position}  |          |
|  |             | |             | |             | |             |          |
|  | [V] {Aye%} | | [V] {Aye%} | | [V] {Aye%} | | [V] {Aye%} |          |
|  | [~] {Part%}| | [~] {Part%}| | [~] {Part%}| | [~] {Part%}|          |
|  +-------------+ +-------------+ +-------------+ +-------------+          |
|                                                                            |
|  RECENT MEETINGS                                   [View All ->]           |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}   [{Type}]    {N} votes   [Agenda] [Minutes] [Video]   |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}   [{Type}]    {N} votes   [Agenda] [Minutes] [Video]   |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}   [{Type}]    {N} votes   [Agenda] [Minutes] [Video]   |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}   [{Type}]    {N} votes   [Agenda] [Minutes] [Video]   |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}   [{Type}]    {N} votes   [Agenda] [Minutes] [Video]   |  |
|  +---------------------------------------------------------------------------+
|                                                                            |
|  VOTING ALIGNMENT                                                          |
|  +-----------------------------------+ +-----------------------------------+
|  | [GREEN] MOST ALIGNED              | | [YELLOW] LEAST ALIGNED            |
|  |                                   | |                                   |
|  | {Name1} & {Name2}  {AgreeRate}%  | | {Name1} & {Name2}  {AgreeRate}%  |
|  | {N shared votes}                 | | {N shared votes}                 |
|  |                                   | |                                   |
|  | {Name3} & {Name4}  {AgreeRate}%  | | {Name3} & {Name4}  {AgreeRate}%  |
|  | {N shared votes}                 | | {N shared votes}                 |
|  |                                   | |                                   |
|  | {Name5} & {Name6}  {AgreeRate}%  | | {Name5} & {Name6}  {AgreeRate}%  |
|  | {N shared votes}                 | | {N shared votes}                 |
|  +-----------------------------------+ +-----------------------------------+
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Data sources:**
- Statistics bar: `stats.json` -> total_votes, total_meetings, pass_rate, unanimous_rate
- Council grid: `council.json` -> members[] (name, position, aye_percentage, participation_rate)
- Recent meetings: `meetings.json` -> first 5 meetings (date, type, vote_count, document URLs)
- Alignment: `alignment.json` -> most_aligned[], least_aligned[]

---

## Page 2: COUNCIL (`council.html`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
| [ICON] City Council Members                                                |
| Voting records and statistics for {CityName} City Council                  |
+============================================================================+
|                                                                            |
|  +----------------------------------+ +----------------------------------+ |
|  | [AVATAR]  {FullName}   [Current] | | [AVATAR]  {FullName}   [Current] | |
|  |           {Position}             | |           {Position}             | |
|  |                                  | |                                  | |
|  |  +-------+ +-------+ +--------+ | |  +-------+ +-------+ +--------+ | |
|  |  |{AyeN} | | {NayN}| |{AbstN} | | |  |{AyeN} | | {NayN}| |{AbstN} | | |
|  |  |  Aye  | |  Nay  | |Abstain | | |  |  Aye  | |  Nay  | |Abstain | | |
|  |  +-------+ +-------+ +--------+ | |  +-------+ +-------+ +--------+ | |
|  |                                  | |                                  | |
|  |  [====GREEN====|RED|GRAY]  bar   | |  [====GREEN====|RED|GRAY]  bar   | |
|  |                                  | |                                  | |
|  |  Aye: {AyePct}%                  | |  Aye: {AyePct}%                  | |
|  |  Dissent: {DissentPct}%          | |  Dissent: {DissentPct}%          | |
|  |  Participation: {PartPct}%       | |  Participation: {PartPct}%       | |
|  |                                  | |                                  | |
|  |        [View Profile ->]         | |        [View Profile ->]         | |
|  |                                  | |                                  | |
|  |  {TotalVotes} total votes        | |  {TotalVotes} total votes        | |
|  +----------------------------------+ +----------------------------------+ |
|                                                                            |
|  +----------------------------------+ +----------------------------------+ |
|  | [AVATAR]  {FullName}   [Current] | | [AVATAR]  {FullName}   [Current] | |
|  |           ...same layout...      | |           ...same layout...      | |
|  +----------------------------------+ +----------------------------------+ |
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Layout:** 3 columns desktop (col-lg-4), 2 columns tablet (col-md-6), 1 column mobile.

**Data source:** `council.json` -> members[]
- Card header: full_name, position, is_current
- Stats row: aye_count, nay_count, abstain_count
- Progress bar: aye_percentage (green), nay (red), absent/abstain (gray)
- Summary: aye_percentage, dissent_rate, participation_rate
- Footer: total_votes
- Link: `council-member.html?id={member.id}`

---

## Page 3: COUNCIL MEMBER PROFILE (`council-member.html?id={id}`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
| Home > Council > {MemberName}                          (breadcrumb)       |
+============================================================================+
|                                                                            |
|  [AVATAR 5x]  {FullName}                                                 |
|               {Position}                                                   |
|               {StartYear} - {EndYear|Present}                              |
|                                                                            |
+----------------------------------------------------------------------------+
|                           STATS CARDS (dynamic)                            |
|  +------------------+ +------------------+ +--------------+ +------------+ |
|  |       {N}        | |     {N}%         | |    {N}%      | |  {N}%      | |
|  |  Matching Votes  | |    Aye Rate      | | Participation| |  Dissent   | |
|  |                  | |                  | |              | | {n of n}   | |
|  +------------------+ +------------------+ +--------------+ +------------+ |
+----------------------------------------------------------------------------+
|                            FILTERS                                         |
|  +----------------------------------------------------------------------+  |
|  | [Search votes...]    [Topic v]    [Year v]    [Vote v]    [Clear]    |  |
|  +----------------------------------------------------------------------+  |
+----------------------------------------------------------------------------+
|                                                                            |
|  VOTING HISTORY                                    {Showing X of Y votes}  |
|  +----------+------+------+----------------------------+--------+--------+ |
|  |   Date   | Item | Vote |          Title             | Choice | Result | |
|  +----------+------+------+----------------------------+--------+--------+ |
|  | {Date}   | {N}  | link | {VoteTitle}                | [AYE]  | [PASS] | |
|  | {Date}   | {N}  | link | {VoteTitle}                | [AYE]  | [PASS] | |
|  | {Date}   | {N}  | link | {VoteTitle}                | [NAY]  | [PASS] | |
|  | {Date}   | {N}  | link | {VoteTitle}                | [AYE]  | [FAIL] | |
|  | {Date}   | {N}  | link | {VoteTitle}                | [AYE]  | [PASS] | |
|  |  ...     | ...  | ...  | ...                        |  ...   |  ...   | |
|  +----------+------+------+----------------------------+--------+--------+ |
|                                                                            |
|  [<< Previous]  [1] [2] [3] ... [n]  [Next >>]                            |
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Filter behavior:** All filters update table AND recalculate stats cards dynamically.

**Data source:** `council/{id}.json`
- Header: member.full_name, position, start_date, end_date
- Stats cards: Calculated from filtered votes (aye_rate, participation, dissent_rate)
- Filters: Year from vote dates, Topic from 16 categories, Vote choice dropdown
- Table: member.recent_votes[] or all_votes[] (vote_id, meeting_date, item_number, title, vote_choice, outcome)
- Vote choice badges: AYE=green, NAY=red, ABSTAIN=yellow, ABSENT=gray
- Outcome badges: PASS=green, FAIL=red

---

## Page 4: MEETINGS LIST (`meetings.html`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
| [ICON] City Council Meetings                                               |
| Complete meeting history with agenda items and voting records               |
+============================================================================+
|                                                                            |
|  +------------------+ +------------------+ +--------------+ +------------+ |
|  | [Year Filter v]  | | {TotalMeetings}  | | {TotalVotes} | | {DateRange}| |
|  | All Years        | |    Meetings      | |  Total Votes | | {YY - YY}  | |
|  +------------------+ +------------------+ +--------------+ +------------+ |
|                                                                            |
|  ALL MEETINGS                                                              |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}     [{Type}]    {N} votes                              |  |
|  |   [Agenda] [Minutes] [Video]   (badges - green=avail, gray=unavail)  |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}     [{Type}]    {N} votes                              |  |
|  |   [Agenda] [Minutes] [Video]                                         |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}     [{Type}]    {N} votes                              |  |
|  |   [Agenda] [Minutes] [Video]                                         |  |
|  +---------------------------------------------------------------------------+
|  | {MeetingDate}     [{Type}]    {N} votes                              |  |
|  |   [Agenda] [Minutes] [Video]                                         |  |
|  +---------------------------------------------------------------------------+
|  |  ...more meetings...                                                 |  |
|  +---------------------------------------------------------------------------+
|                                                                            |
|  [<< Previous]  [1] [2] [3] ... [n]  [Next >>]                            |
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**KPI behavior:** Stats update when year filter changes.

**Data source:** `meetings.json`
- KPIs: Count meetings, sum vote_count, date range (calculated from filtered results)
- Year filter: Derived from meeting_date years
- Meeting list: meeting_date, meeting_type, vote_count
- Document badges: agenda_url, minutes_url, video_url (clickable if URL present, grayed if null)
- Row click: `meeting-detail.html?id={meeting.id}`

---

## Page 5: MEETING DETAIL (`meeting-detail.html?id={id}`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
| Home > Meetings > {MeetingDate}                        (breadcrumb)       |
+============================================================================+
|                                                                            |
|  [ICON] {FullDate}                                                        |
|  {MeetingType} Meeting                                                    |
|                                                                            |
|  [View Agenda]  [View Minutes]  [Watch Video]                              |
|  (buttons - shown only when URL available)                                 |
|                                                                            |
+----------------------------------------------------------------------------+
|                           STATS CARDS                                      |
|  +------------------------+ +--------------------+ +---------------------+ |
|  |      {VoteCount}       | |    {PassedCount}   | |   {AgendaItems}     | |
|  |       Votes Taken       | |       Passed       | |    Agenda Items     | |
|  +------------------------+ +--------------------+ +---------------------+ |
+----------------------------------------------------------------------------+
|                                                                            |
|  AGENDA ITEMS & VOTES                                                      |
|  +---------------------------------------------------------------------------+
|  | [{ItemN}] {Section}                                       [PASS]      |  |
|  | {AgendaItemTitle}                                     {A} - {N} - {Ab}|  |
|  |                                                       [View Details]  |  |
|  +---------------------------------------------------------------------------+
|  | [{ItemN}] {Section}                                       [PASS]      |  |
|  | {AgendaItemTitle}                                     {A} - {N} - {Ab}|  |
|  |                                                       [View Details]  |  |
|  +---------------------------------------------------------------------------+
|  | [{ItemN}] {Section}                                       [PASS]      |  |
|  | {AgendaItemTitle}                                     {A} - {N} - {Ab}|  |
|  |                                                       [View Details]  |  |
|  +---------------------------------------------------------------------------+
|  |  ...more agenda items...                                              |  |
|  +---------------------------------------------------------------------------+
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Data source:** CityVotesAPI.getMeeting(id) which combines:
- `meetings.json` -> single meeting (date, type, agenda_url, minutes_url, video_url)
- `votes.json` -> filtered by meeting_date (item_number, section, title, outcome, ayes, noes, abstain)
- Stats: Calculated from agenda_items (vote_count, passed count, item count)
- Detail link: `vote-detail.html?id={vote.id}`

---

## Page 6: VOTES LIST (`votes.html`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
|                                                                            |
|  SEARCH & FILTERS                                                          |
|  +----------------------------------------------------------------------+  |
|  | [Search votes by title...]                                           |  |
|  |                                                                      |  |
|  | [Year v]     [Topic v]      [Outcome v]         [Search] [Clear]     |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|                                      {Showing N of {TotalVotes} votes}    |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|  | Date | Item |          Title            | Result | Tally | Docs| Act |  |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|  |{Date}| {N}  | {VoteTitle}               | [PASS] |{A}-{N}-{Ab}|[A][M][V]|  |
|  |      |      |                           |        |       |avail/gray|  |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|  |{Date}| {N}  | {VoteTitle}               | [PASS] |{A}-{N}-{Ab}|[A][M][V]|  |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|  |{Date}| {N}  | {VoteTitle}               | [PASS] |{A}-{N}-{Ab}|[A][M][V]|  |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|  |{Date}| {N}  | {VoteTitle}               | [PASS] |{A}-{N}-{Ab}|[A][M][V]|  |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|  |  ... | ...  | ...                       |  ...   | ...   | ...  |...|  |
|  +------+------+---------------------------+--------+-------+-----+-----+  |
|                                                                            |
|  [<< Previous]  [1] [2] [3] ... [n]  [Next >>]                            |
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Document icons legend:**
- `[A]` = Agenda (file icon) - clickable button if URL exists, gray badge if null
- `[M]` = Minutes (clipboard icon) - clickable button if URL exists, gray badge if null
- `[V]` = Video (camera icon, red) - clickable button if URL exists, gray badge if null

**Special outcomes:** CONTINUED, REMOVED, FLAG, TABLED, WITHDRAWN show "[FLAG]" badge instead of tally.

**Data sources:**
- `votes-index.json` -> available_years (for Year dropdown)
- `votes-{year}.json` -> votes[] (paginated, filtered client-side)
- `meetings.json` -> meetingsData map by meeting_date (for document URLs)
- Topic dropdown: 16 predefined AVAILABLE_TOPICS constant
- Outcome dropdown: PASS, FAIL, SPECIAL (procedural)
- Title links to: `vote-detail.html?id={vote.id}`

---

## Page 7: AGENDA SEARCH (`agenda-search.html`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
|                                                                            |
|  AGENDA ITEM SEARCH                                                        |
|  +----------------------------------------------------------------------+  |
|  | [Search agenda items by keyword...]                                  |  |
|  |                                                                      |  |
|  | [Year v]  [Topic v]  [Meeting Type v]  [Outcome v]   [Clear Filters] |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|                                       {Showing N of {TotalVotes} items}   |
|  +------+------+----------------------+--------+------+------+-----+---+  |
|  |Date* |Item* |       Title*         |Topic   |Type  |Result| Docs|[E]|  |
|  +------+------+----------------------+--------+------+------+-----+---+  |
|  |{Date}| {N}  |{VoteTitle}           |[{Topic}]|{Type}|[PASS]|[A][M][V]|  |
|  +------+------+----------------------+--------+------+------+-----+---+  |
|  |{Date}| {N}  |{VoteTitle}           |[{Topic}]|{Type}|[PASS]|[A][M][V]|  |
|  +------+------+----------------------+--------+------+------+-----+---+  |
|  |{Date}| {N}  |{VoteTitle}           |[{Topic}]|{Type}|[PASS]|[A][M][V]|  |
|  +------+------+----------------------+--------+------+------+-----+---+  |
|  | ...  | ...  | ...                  | ...    | ...  | ...  | ...  |...|  |
|  +------+------+----------------------+--------+------+------+-----+---+  |
|                                                                            |
|  (* = sortable column, click to toggle asc/desc)                           |
|                                                                            |
|  [<< Previous]  [1] [2] [3] ... [n]  [Next >>]                            |
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Differences from Votes page:**
- Topic column shows first 2 topics as badges
- Meeting Type column (regular/special)
- Sortable columns: Date, Item#, Title (click header to sort)
- URL state: Filters preserved in query string for sharing/bookmarking
- Loads all votes at once (not year-by-year)

**Data sources:**
- `votes.json` -> all votes
- `meetings.json` -> meetingsData map by meeting_date (for document URLs)
- Topics: 16 predefined categories list
- Meeting types: regular, special
- Outcomes: PASS, FAIL, SPECIAL

---

## Page 8: VOTE DETAIL (`vote-detail.html?id={id}`)

```
+============================================================================+
|                              NAVIGATION BAR                                |
+============================================================================+
| Home > Votes > Item {ItemNumber}                       (breadcrumb)       |
+============================================================================+
|                                                                            |
|  [{ItemNumber}]  [{OUTCOME}]                                               |
|                                                                            |
|  {Full Title of Vote}                                                      |
|  {Long description with recommended actions and minutes...}                |
|                                                                            |
|  [ICON] {FullDate}               |   {MeetingType} Meeting                |
|                                                                            |
+----------------------------------------------------------------------------+
|                                                                            |
|  +-----------------------------------+ +-----------------------------------+
|  | VOTE TALLY                        | | INDIVIDUAL VOTES                  |
|  |                                   | |                                   |
|  | +------+ +------+ +-----+ +-----+| | {MemberName}           [AYE]     |
|  | |{Ayes}| |{Noes}| |{Abs}| |{Abs}|| | {MemberName}           [AYE]     |
|  | | Ayes | | Noes | |Abst | | Abs || | {MemberName}           [NAY]     |
|  | +------+ +------+ +-----+ +-----+| | {MemberName}           [AYE]     |
|  |                                   | | {MemberName}           [AYE]     |
|  | [====GREEN==========]  progress   | | {MemberName}           [AYE]     |
|  |                                   | | {MemberName}           [AYE]     |
|  +-----------------------------------+ +-----------------------------------+
|                                                                            |
|  +----------------------+ +-------------------+ +------------------------+ |
|  | [GREEN] VOTED AYE    | | [RED] VOTED NAY   | | [GRAY] ABSTAIN/ABSENT  | |
|  |                      | |                   | |                        | |
|  | {MemberName} (link)  | | {MemberName}(link)| | {None}                 | |
|  | {MemberName} (link)  | |                   | |                        | |
|  | {MemberName} (link)  | |                   | |                        | |
|  | {MemberName} (link)  | |                   | |                        | |
|  | {MemberName} (link)  | |                   | |                        | |
|  | {MemberName} (link)  | |                   | |                        | |
|  +----------------------+ +-------------------+ +------------------------+ |
|                                                                            |
+============================================================================+
|                              FOOTER                                        |
+============================================================================+
```

**Data source:** `votes/{id}.json`
- Header: item_number, outcome, title, description, meeting_date, meeting_type
- Tally card: ayes, noes, abstain, absent (numbers + progress bar)
- Individual votes: member_votes[] (full_name, vote_choice with colored badge)
- Grouped cards: member_votes filtered by AYE / NAY / other
- Member links: `council-member.html?id={member_id}`
- Meeting link: `meeting-detail.html?id={meeting_id}`
- Badge colors: AYE=green, NAY=red, ABSTAIN=yellow, ABSENT=gray, RECUSAL=purple

---

## Responsive Breakpoints

| Breakpoint | Nav | Cards | Tables |
|------------|-----|-------|--------|
| Desktop (lg+) | Horizontal | 3-4 columns | Full table |
| Tablet (md) | Horizontal | 2 columns | Full table |
| Mobile (sm) | Hamburger | 1 column | Horizontal scroll |

---

## Color Coding Reference

| Element | Color | CSS Class |
|---------|-------|-----------|
| AYE / Pass / Success | Green | `bg-success` |
| NAY / Fail | Red | `bg-danger` |
| Abstain | Yellow | `bg-warning` |
| Absent | Gray | `bg-secondary` |
| Recusal | Teal | `bg-info` |
| Special/Flag | Yellow text-dark | `bg-warning text-dark` |
| Primary/Links | Blue | `bg-primary` / `btn-outline-primary` |
| City Brand | Custom | `bg-city-primary` (defined in `css/theme.css`) |
| City Accent | Custom | `text-city-accent` (defined in `css/theme.css`) |

---

## Badge Types Reference

| Badge | Used On | Meaning |
|-------|---------|---------|
| `[Current]` green | Council cards | Active member |
| `[Former]` gray | Council cards | Past member |
| `[regular]` light | Meetings | Regular session |
| `[special]` info | Meetings | Special session |
| `[PASS]` green | Vote outcomes | Motion passed |
| `[FAIL]` red | Vote outcomes | Motion failed |
| `[FLAG]` yellow | Special outcomes | Procedural - data unreliable |
| `[AYE]` green | Member votes | Voted yes |
| `[NAY]` red | Member votes | Voted no |
| `[ABSTAIN]` yellow | Member votes | Abstained |
| `[ABSENT]` gray | Member votes | Was absent |
| `[Agenda]` outline | Documents | Agenda PDF link |
| `[Minutes]` outline | Documents | Minutes PDF link |
| `[Video]` red outline | Documents | Video link (YouTube) |
| `[Agenda]` gray | Documents | Agenda not available |
| `[Minutes]` gray | Documents | Minutes not available |
| `[Video]` gray | Documents | Video not available |

---

## Page Flow / Navigation Map

```
                    +----------+
                    |   HOME   |
                    +----+-----+
                         |
          +--------------+---------------+------------------+
          |              |               |                  |
     +----v-----+  +----v------+  +-----v-----+  +--------v--------+
     | COUNCIL  |  | MEETINGS  |  |   VOTES   |  | AGENDA SEARCH   |
     +----+-----+  +----+------+  +-----+-----+  +--------+--------+
          |              |               |                  |
     +----v---------+   +----v------+   +v-----------------v+
     |COUNCIL MEMBER|   | MEETING   |   |   VOTE DETAIL     |
     |  PROFILE     |   |  DETAIL   |   |                   |
     +--------------+   +----+------+   +-------------------+
                              |                  |
                              +---->  VOTE DETAIL <---+
                                                      |
                              VOTE DETAIL ----> COUNCIL MEMBER
```

**Every page links to:** Home, Council, Meetings, Votes, Search (via navbar)

---

## Data Requirements Summary (for new city)

To replicate this site for a different city, you need:

| Data | Source | Format |
|------|--------|--------|
| Council members | City website / clerk | Name, position, start/end dates |
| Meeting dates | Agendas / minutes | Date, type (regular/special) |
| Meeting documents | City website | URLs to agenda PDF, minutes PDF, video |
| Vote records | Meeting minutes | Item#, title, outcome, ayes/noes/abstain/absent |
| Individual votes | Meeting minutes | Member name + vote choice per item |
| Vote descriptions | Agenda packets | Full text of recommended actions |

### Calculated (scripts generate these):
- Member stats (aye%, participation%, dissent%)
- Alignment pairs (agreement rates between all member pairs)
- Topic assignments (keyword-based or AI classification)
- Global stats (totals, pass rate, unanimous rate)

---

## Placeholder Glossary

Every `{Placeholder}` used in the wireframes above maps to a specific JSON field or
a value calculated at render time. **Config** placeholders are set once per city deployment.
**Data** placeholders come from JSON files (see `template/data/README.md` for full schemas).

### Config Placeholders (set once per city)

| Placeholder | Meaning | Where Set |
|-------------|---------|-----------|
| `{CityName}` | Full city name (e.g., "Long Beach") | Find-and-replace in all HTML files |
| `{AppName}` | Application title (e.g., "CityVotes") | Navbar brand text |
| `{Color}` | City brand colors | `css/theme.css` CSS custom properties (`--city-primary`, `--city-accent`) |
| `{Year}` | Footer copyright / data year | Footer element, updated by JS or statically |

### Global Stats Placeholders

| Placeholder | JSON Source | Field Path |
|-------------|------------|------------|
| `{TotalVotes}` | `stats.json` | `stats.total_votes` |
| `{TotalMeetings}` | `stats.json` | `stats.total_meetings` |
| `{PassRate}` | `stats.json` | `stats.pass_rate` |
| `{Unanim.}` | `stats.json` | `stats.unanimous_rate` |
| `{DateRange}` | `stats.json` | `stats.date_range.start` — `stats.date_range.end` |

### Council Member Placeholders

| Placeholder | JSON Source | Field Path |
|-------------|------------|------------|
| `{Name}` / `{FullName}` | `council.json` | `members[].full_name` |
| `{Position}` | `council.json` | `members[].position` (e.g., "Mayor", "Council Member") |
| `{StartYear}` | `council/{id}.json` | `member.start_date` (year portion) |
| `{EndYear}` | `council/{id}.json` | `member.end_date` (year portion, or "Present" if null) |
| `{AyeN}` | `council.json` | `members[].stats.aye_count` |
| `{NayN}` | `council.json` | `members[].stats.nay_count` |
| `{AbstN}` | `council.json` | `members[].stats.abstain_count` |
| `{AyePct}` / `{Aye%}` | `council.json` | `members[].stats.aye_percentage` |
| `{DissentPct}` | `council.json` | `members[].stats.dissent_rate` |
| `{PartPct}` / `{Part%}` | `council.json` | `members[].stats.participation_rate` |

### Meeting Placeholders

| Placeholder | JSON Source | Field Path |
|-------------|------------|------------|
| `{MeetingDate}` | `meetings.json` | `meetings[].meeting_date` (formatted for display) |
| `{FullDate}` | `meetings.json` | `meetings[].meeting_date` (long format, e.g., "January 15, 2024") |
| `{Type}` / `{MeetingType}` | `meetings.json` | `meetings[].meeting_type` ("regular" or "special") |
| `{N} votes` | `meetings.json` | `meetings[].vote_count` |
| `{VoteCount}` | Calculated | Count of votes for a specific meeting |
| `{PassedCount}` | Calculated | Count of PASS outcomes for a specific meeting |
| `{AgendaItems}` | `meetings.json` | `meetings[].agenda_item_count` |

### Vote / Agenda Item Placeholders

| Placeholder | JSON Source | Field Path |
|-------------|------------|------------|
| `{VoteTitle}` | `votes.json` | `votes[].title` |
| `{ItemNumber}` / `{ItemN}` / `{N}` | `votes.json` | `votes[].item_number` |
| `{Section}` | `votes.json` | `votes[].section` (CONSENT, GENERAL, PUBLIC_HEARING) |
| `{AgendaItemTitle}` | `votes.json` | `votes[].title` (same as VoteTitle, used in meeting detail context) |
| `{OUTCOME}` | `votes.json` | `votes[].outcome` (PASS, FAIL, or special outcomes) |
| `{Ayes}` / `{A}` | `votes.json` | `votes[].ayes` |
| `{Noes}` / `{N}` | `votes.json` | `votes[].noes` |
| `{Abs}` / `{Ab}` | `votes.json` | `votes[].abstain` |
| `{Topic}` | `votes.json` | `votes[].topics[]` (from 16 predefined categories) |
| `{Date}` | `votes.json` | `votes[].meeting_date` (short format) |

### Vote Detail Placeholders

| Placeholder | JSON Source | Field Path |
|-------------|------------|------------|
| `{MemberName}` | `votes/{id}.json` | `vote.member_votes[].full_name` |
| Vote choice badges | `votes/{id}.json` | `vote.member_votes[].vote_choice` (AYE/NAY/ABSTAIN/ABSENT/RECUSAL) |

### Alignment Placeholders

| Placeholder | JSON Source | Field Path |
|-------------|------------|------------|
| `{Name1}` & `{Name2}` | `alignment.json` | `most_aligned[].member1`, `most_aligned[].member2` |
| `{AgreeRate}` | `alignment.json` | `alignment_pairs[].agreement_rate` |
| `{N shared votes}` | `alignment.json` | `alignment_pairs[].shared_votes` |

---

### Template Files
All HTML templates are in `template/` with `{CityName}` placeholders.
CSS theme colors are configured in `template/css/theme.css` via CSS custom properties.
Data schemas are documented in `template/data/README.md`.
