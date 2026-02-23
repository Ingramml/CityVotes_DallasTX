# Dallas City Council - Data Structure Analysis

This document provides a comprehensive analysis of the CSV data files used to build the CityVotes Dallas static website. It covers file structure, column definitions, data quality observations, and key patterns.

---

## File Organization

### Naming Convention
```
Dallas-TX-{YEAR}-Q{QUARTER}-{TYPE}.csv
```
- **YEAR**: 2020-2025
- **QUARTER**: 1-4
- **TYPE**: `Votes`, `Persons`, or `Voted-Items`

### Files Per Quarter (3 files)
| File Type    | Purpose                                              |
|-------------|------------------------------------------------------|
| Votes.csv   | ALL agenda rows for the quarter (voted + non-voted)  |
| Voted-Items.csv | Filtered subset: only rows with roll-call votes  |
| Persons.csv | Council member roster for that quarter               |

### Current Data Range (with YEAR_RANGE filter active: 2022-2023)
- **24 CSV source files** (8 quarters x 3 types)
- **72 CSV files total** on disk (2020-2025, all preserved)

---

## CSV Column Definitions

### Votes.csv / Voted-Items.csv (Identical Schema)

These two files share the same column structure. Voted-Items.csv is simply a filtered version containing only rows where members actually cast votes.

#### Fixed Metadata Columns (32 columns)

| Column                  | Type    | Description                                           | Empty Rate |
|------------------------|---------|-------------------------------------------------------|------------|
| event_id               | int     | Legistar meeting ID                                   | 3.5%       |
| event_date             | date    | Meeting date (YYYY-MM-DD)                             | 0%         |
| event_time             | string  | Meeting time (e.g., "9:00 AM")                        | varies     |
| event_body             | string  | Always "City Council"                                 | 0%         |
| event_location         | string  | Meeting location (may contain newlines)               | varies     |
| event_item_id          | int     | Legistar agenda item ID                               | 3.5%       |
| agenda_number          | string  | Item number (e.g., "1.", "2.")                        | varies     |
| agenda_sequence        | int     | Numeric sequence position on agenda                   | varies     |
| title                  | string  | Full text of agenda item                              | ~0%        |
| matter_file            | string  | Filing number (e.g., "22-30")                         | 3.5%       |
| matter_type            | string  | Category (CONSENT AGENDA, VOTING AGENDA, etc.)        | 3.5%       |
| matter_status          | string  | Outcome status (Approved, Deleted, etc.)              | 3.5%       |
| matter_id              | int     | Legistar matter ID                                    | 3.5%       |
| matter_title           | string  | Full title of the matter                              | varies     |
| matter_intro_date      | date    | Date matter was introduced                            | varies     |
| matter_enactment_number| string  | Enactment/resolution number                           | varies     |
| matter_requester       | string  | Requesting department                                 | varies     |
| matter_body_name       | string  | Department name                                       | varies     |
| passed                 | int     | 1=passed, 0=failed, empty=no vote                     | 8.4%       |
| vote_type              | string  | Always "Socrata Roll Call"                            | 0%         |
| consent                | string  | **Always empty** (unused placeholder)                 | 100%       |
| tally                  | string  | **Always empty** (unused placeholder)                 | 100%       |
| mover                  | string  | **Always empty** (unused placeholder)                 | 100%       |
| seconder               | string  | **Always empty** (unused placeholder)                 | 100%       |
| roll_call_flag         | string  | Always "0"                                            | 0%         |
| socrata_item_number    | int     | Socrata-sourced item number                           | varies     |
| socrata_agenda_info    | string  | e.g., "AGENDA"                                        | varies     |
| socrata_final_action   | string  | e.g., "APPROVED", "DENIED", "DELETED"                 | varies     |
| agenda_link            | url     | URL to PDF agenda                                     | varies     |
| minutes_link           | url     | URL to PDF minutes                                    | varies     |
| video_link             | url     | URL to meeting video                                  | varies     |
| attachment_links       | string  | Pipe-delimited attachment URLs                        | varies     |

#### Member Vote Columns (columns 32+)

After the 32 fixed columns, each remaining column is named after a council member. The number of member columns varies by quarter (15 normally, up to 20 during transition quarters).

**Vote Values**:
| Value   | Meaning                          | Frequency |
|---------|----------------------------------|-----------|
| YES     | Voted in favor                   | 89.0%     |
| NO      | Voted against                    | 0.4%      |
| AWVT    | Away from vote (not at seat)     | 5.1%      |
| ABSNT   | Absent from meeting              | 1.9%      |
| ABST    | Abstained                        | 0.1%      |
| N/A     | Not on council for this vote     | 3.6%      |
| (empty) | No vote data (non-voted item)    | varies    |

### Persons.csv (6 columns)

| Column     | Type   | Description                                              |
|-----------|--------|----------------------------------------------------------|
| district  | int    | Council district number (1-14 for members, 15 for Mayor) |
| voter_name| string | Full name of council member                               |
| title     | string | "Mayor", "Mayor Pro Tem", "Deputy Mayor Pro Tem", or "Councilmember" |
| first_seen| date   | First meeting date the member voted in this quarter       |
| last_seen | date   | Last meeting date the member voted in this quarter        |
| vote_count| int    | Total vote records for this member in the quarter         |

Normally 15 rows per quarter. Transition quarters (Q2 of election years) may have up to 20 rows.

---

## Row Counts (2022-2023)

### Votes.csv (all agenda rows)
| Quarter | Data Rows |
|---------|----------:|
| 2022-Q1 |       585 |
| 2022-Q2 |       767 |
| 2022-Q3 |       606 |
| 2022-Q4 |       513 |
| 2023-Q1 |       527 |
| 2023-Q2 |       815 |
| 2023-Q3 |       539 |
| 2023-Q4 |       502 |
| **Total** | **4,854** |

### Voted-Items.csv (voted items only)
| Quarter | Data Rows |
|---------|----------:|
| 2022-Q1 |       314 |
| 2022-Q2 |       404 |
| 2022-Q3 |       327 |
| 2022-Q4 |       263 |
| 2023-Q1 |       259 |
| 2023-Q2 |       346 |
| 2023-Q3 |       299 |
| 2023-Q4 |       261 |
| **Total** | **2,473** |

### Persons.csv
| Quarter | Data Rows |
|---------|----------:|
| 2022-Q1 |        15 |
| 2022-Q2 |        16 |
| 2022-Q3 |        15 |
| 2022-Q4 |        15 |
| 2023-Q1 |        15 |
| 2023-Q2 |        20 |
| 2023-Q3 |        15 |
| 2023-Q4 |        15 |

---

## Generated Output (2022-2023 filtered build)

| Metric              | Value    |
|---------------------|----------|
| Meetings            | 75       |
| Voted items         | 2,386    |
| Total agenda items  | 4,854    |
| Non-voted items     | 2,468    |
| Council members     | 17       |
| Date range          | 2022-01-05 to 2023-12-13 |
| Pass rate           | 94.3%    |
| Unanimous rate      | 90.5%    |

---

## Council Member Roster (2022-2023)

### Full Term (2022-2023)
| District | Member              | Title                     |
|----------|---------------------|---------------------------|
| 1        | Chad West           | Mayor Pro Tem (2022), then Councilmember |
| 2        | Jesse Moreno        | Councilmember             |
| 4        | Carolyn King Arnold | Councilmember, then Mayor Pro Tem, then Deputy Mayor Pro Tem |
| 5        | Jaime Resendez      | Deputy Mayor Pro Tem (2022), then Councilmember |
| 6        | Omar Narvaez        | Councilmember, then Deputy Mayor Pro Tem |
| 7        | Adam Bazaldua       | Councilmember             |
| 8        | Tennell Atkins      | Councilmember, then Mayor Pro Tem |
| 9        | Paula Blackmon      | Councilmember             |
| 11       | Jaynie Shultz       | Councilmember             |
| 12       | Cara Mendelsohn     | Councilmember             |
| 13       | Gay Donnell Willis  | Councilmember             |
| 14       | Paul Ridley         | Councilmember             |
| 15       | Eric Johnson        | Mayor                     |

### Departed Mid-2023 (served through Q2)
| District | Member              |
|----------|---------------------|
| 3        | Casey Thomas II     |
| 10       | Adam McGough        |

### Joined Mid-2023 (started Q2/Q3)
| District | Member              |
|----------|---------------------|
| 3        | Zarin Gracey        |
| 10       | Kathy Stewart       |

---

## Meeting Patterns

| Quarter | Meeting Count | Date Range            | Notes                          |
|---------|:------------:|-----------------------|--------------------------------|
| 2022-Q1 |      9       | Jan 5 - Mar 9         |                                |
| 2022-Q2 |     14       | Apr 6 - Jun 27        | Most active (budget season)    |
| 2022-Q3 |      8       | Aug 10 - Sep 28       | July recess                    |
| 2022-Q4 |      7       | Oct 12 - Dec 14       |                                |
| 2023-Q1 |      7       | Jan 11 - Mar 8        |                                |
| 2023-Q2 |     12       | Apr 4 - Jun 28        | Council transition quarter     |
| 2023-Q3 |      7       | Aug 9 - Sep 27        | July recess                    |
| 2023-Q4 |      7       | Oct 11 - Dec 13       |                                |

- Meetings are typically held on **Wednesdays**, roughly bi-weekly
- **Q2 quarters** are busiest (budget season + fiscal year end)
- **July** is always a recess month (no meetings)
- **44 unique Legistar event IDs** across 2022-2023

---

## Matter Type Distribution (2022-2023 Voted Items)

| Matter Type                                          | Count  | % of Total |
|------------------------------------------------------|-------:|-----------:|
| CONSENT AGENDA                                       | 1,701  | 68.8%      |
| ITEMS FOR INDIVIDUAL CONSIDERATION                   |   211  | 8.5%       |
| ZONING CASES - INDIVIDUAL                            |   162  | 6.6%       |
| ZONING CASES - CONSENT                               |   125  | 5.1%       |
| MISCELLANEOUS HEARINGS                               |    74  | 3.0%       |
| ZONING CASES - UNDER ADVISEMENT - INDIVIDUAL         |    53  | 2.1%       |
| ITEMS FOR FURTHER CONSIDERATION                      |    49  | 2.0%       |
| VOTING AGENDA                                        |    39  | 1.6%       |
| PUBLIC HEARINGS AND RELATED ACTIONS                  |    25  | 1.0%       |
| Other (9 types, each <1%)                            |    34  | 1.4%       |

---

## Dissent Analysis

- **97 items** had at least one NO vote (3.9% of 2,473 voted items)
- Distribution: 68 items with 1 NO, 12 with 2, 6 with 3, 5 with 4, 4 with 5, 1 with 6, 1 with 7
- Most contentious item (7 NO votes): A public hearing on 2023-12-13
- Budget/tax rate votes on 2023-09-20 had 5 NO votes each

---

## Data Quality Notes

### Name Inconsistencies (Critical)
The source data contains inconsistent member name formatting across quarters. The build script (`build_site.py`) handles this via `NAME_ALIASES`:

| Canonical Name        | Variant(s) in CSV                    | Issue           |
|-----------------------|--------------------------------------|-----------------|
| Carolyn King Arnold   | `Carolyn King  Arnold`               | Extra space     |
| Adam Bazaldua         | `Adam  Bazaldua`                     | Extra space     |
| Tennell Atkins        | `Tennell  Atkins`, `Tennel Atkins`   | Extra space / typo |
| Adam McGough          | `B. Adam McGough`                    | Name prefix     |
| Gay Donnell Willis    | `Gay Donnel Willis`                  | Typo            |
| Jaynie Shultz         | `Jaynie Schultz`                     | Spelling variant|
| Zarin Gracey          | `Zarin D. Gracey`                    | Middle initial  |
| Jennifer S. Gates     | `Jennifer S.  Gates`                 | Extra space     |
| Jesse Moreno          | `Jesse  Moreno`                      | Extra space     |

### Socrata-Only Records
86 rows (3.5%) lack Legistar metadata (event_id, matter_type, matter_id, etc.). These are sourced from Dallas Open Data (Socrata) roll-call records that couldn't be matched to Legistar events. They still contain vote data, dates, and socrata_final_action.

### Always-Empty Columns
Three columns are **never populated** across the entire dataset:
- `tally` - Schema placeholder
- `mover` - Schema placeholder
- `seconder` - Schema placeholder

### Multiline CSV Values
The `title` and `event_location` fields frequently contain embedded newlines within quoted CSV fields. Standard CSV parsers handle this correctly, but line-counting tools (like `wc -l`) will overcount rows.

---

## Data Pipeline: CSV to JSON

The build script (`build_site.py`) processes CSVs and generates JSON files for the static frontend:

```
Dallas-TX/*.csv  -->  build_site.py  -->  frontend/data/*.json
                                           frontend/data/votes/{id}.json
                                           frontend/data/meetings/{id}.json
                                           frontend/data/council/{id}.json
```

### Key Processing Steps
1. **Name normalization** via `NAME_ALIASES` dictionary
2. **Vote value mapping**: YES->AYE, NO->NAY, AWVT/ABSNT->ABSENT, ABST->ABSTAIN
3. **Outcome derivation** from `passed`, `socrata_final_action`, and `matter_status` fields
4. **Topic classification** via keyword matching on titles (16 topic categories)
5. **Section classification** into CONSENT, GENERAL, or PUBLIC_HEARING
6. **Year filtering** via `YEAR_RANGE` config (currently set to `(2022, 2023)`)

### Generated Files
| File                    | Content                                    |
|------------------------|--------------------------------------------|
| stats.json             | Aggregate statistics                        |
| council.json           | All members with voting stats               |
| council/{id}.json      | Individual member detail + vote history     |
| meetings.json          | All meetings list                           |
| meetings/{id}.json     | Individual meeting + full agenda            |
| votes.json             | All votes (summary view)                    |
| votes-{year}.json      | Votes filtered by year                      |
| votes-index.json       | Available years list                        |
| votes/{id}.json        | Individual vote detail + member votes       |
| alignment.json         | Pairwise voting alignment for current members|
| agenda-items.json      | Non-voted agenda items (capped at 5,000)    |
