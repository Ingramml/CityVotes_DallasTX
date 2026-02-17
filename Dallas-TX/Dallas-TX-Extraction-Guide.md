# Dallas, TX - Legislative Data Extraction Guide

**Last Updated:** 2026-02-16
**API Status:** Fully Working (Dual Platform)
**Extraction Verified:** Q4 2025 — 629 rows, 236 voted items, 95% cross-platform match, 47 columns
**Vote Data:** Available via Socrata Open Data Portal (per-member YES/NO/ABSTAIN)

---

## Quick Start

```bash
# Test Legistar API access
curl "https://webapi.legistar.com/v1/cityofdallas/bodies"

# Get recent City Council meetings (Legistar)
curl "https://webapi.legistar.com/v1/cityofdallas/events?\$filter=EventBodyId%20eq%20138&\$orderby=EventDate%20desc&\$top=5"

# Get agenda items for a specific meeting (Legistar)
curl "https://webapi.legistar.com/v1/cityofdallas/events/4067/EventItems"

# Test Socrata vote data access (5 records)
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$limit=5"

# Get votes for a specific meeting date (Socrata)
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$where=date%20%3D%20'2025-12-10T00:00:00'&\$limit=5000"
```

If you get JSON data back from both APIs, you are ready to go. No authentication required for either platform.

**CRITICAL:** Dallas uses a **dual-platform architecture**. Per-member vote data is NOT in Legistar -- it lives exclusively in the Socrata Open Data Portal. The extraction script must pull from both sources and correlate them.

---

## CLI Extraction Tool

The parameterized extraction script `extract_dallas.py` supports extracting any quarter/year combination.

### Basic Usage

```bash
# Extract Q4 2025
python extract_dallas.py --year 2025 --quarter 4

# Votes only (skip items without vote records)
python extract_dallas.py --year 2025 --quarter 4 --votes-only

# Include committee meetings (not just City Council)
python extract_dallas.py --year 2025 --quarter 3 --include-committees

# Custom output directory
python extract_dallas.py --year 2024 --quarter 1 --output-dir /path/to/output
```

### CLI Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--year` | Yes | Year to extract (e.g., 2025) |
| `--quarter` | Yes | Quarter 1-4 |
| `--votes-only` | No | Only output items with vote records |
| `--include-committees` | No | Include committee meetings beyond City Council |
| `--output-dir` | No | Override default output directory |

### Output Files

```
Dallas-TX-{YEAR}-Q{QUARTER}-Votes.csv         # All agenda items (Legistar + Socrata merged)
Dallas-TX-{YEAR}-Q{QUARTER}-Voted-Items.csv   # Items with Socrata vote data only
Dallas-TX-{YEAR}-Q{QUARTER}-Persons.csv       # Council member data (from Socrata)
```

---

## Platform Overview

| Field | Value |
|-------|-------|
| **City** | Dallas, TX |
| **Platform** | Legistar (Granicus) + Socrata Open Data Portal |
| **Legistar Client ID** | `cityofdallas` |
| **Legistar Web Portal** | https://cityofdallas.legistar.com/ |
| **Legistar API Base URL** | `https://webapi.legistar.com/v1/cityofdallas/` |
| **Socrata API Base URL** | `https://www.dallasopendata.com/resource/ts5d-gdq6.json` |
| **Authentication** | None required for either API |
| **Platform Type** | Legistar (agenda/legislation) + Socrata (vote data) |
| **Legistar Data Range** | Events: April 2007 - Present; Matters: June 2018 - Present |
| **Socrata Vote Data Range** | September 2016 - December 2025 |
| **Council Size** | 15 members (Mayor + 14 Council Districts) |
| **Meeting Bodies** | 110 (Legistar) |

---

## What Data Can Be Extracted

### Available via Legistar API (Agenda/Legislation Metadata)

| Data Type | Endpoint | Quality |
|-----------|----------|---------|
| Council bodies & committees | `/bodies` | Excellent (110 bodies) |
| Meeting events | `/events` | Excellent (~2,578 events, Apr 2007-present) |
| Agenda items | `/events/{id}/EventItems` | Excellent (119-194 items per meeting) |
| Legislation metadata | `/matters` | Excellent (~18,831 matters, Jun 2018-present) |
| **Matter details** | `/matters/{id}` | **Excellent** (type, status, cost, requester, body, dates) |
| **Matter attachments** | `/matters/{id}/attachments` | **Good** (resolution documents, .docx links) |
| Persons (council + staff) | `/persons` | Fair (1,000 records, noisy - includes system accounts) |
| Vote types | `/VoteTypes` | Excellent (7 types) |
| Matter types | `/MatterTypes` | Excellent (74 types) |
| Matter statuses | `/MatterStatuses` | Excellent (144 statuses) |
| Actions | `/Actions` | Excellent (20 actions) |

### Available via Socrata API (Per-Member Vote Data)

| Data Type | Endpoint | Quality |
|-----------|----------|---------|
| **Per-member votes** | `/resource/ts5d-gdq6.json` | **Excellent** (186,780 records) |
| Council members | Derived from `voter_name` + `district` | **Excellent** |
| Vote outcomes | `final_action_taken` field | **Good** (free-text, not normalized) |
| Meeting dates | `date` field | **Excellent** (332 unique dates) |
| Agenda item descriptions | `agenda_item_description` field | **Excellent** |

### Not Available / Empty in Legistar

| Data Type | Status | Notes |
|-----------|--------|-------|
| **Per-member votes** | **EMPTY** | `/EventItems/{id}/Votes` always returns `[]` for Dallas |
| **Roll calls** | **EMPTY** | `/EventItems/{id}/RollCalls` always returns `[]` |
| **Action names** | **Always null** | `EventItemActionName` is null for all items |
| **Passed flag** | **Always null** | `EventItemPassedFlagName` is null for all items |
| **Matter history** | **EMPTY** | `/matters/{id}/histories` returns `[]` |
| **Matter sponsors** | **EMPTY** | `/matters/{id}/sponsors` returns `[]` |
| **Matter texts** | **405 Error** | `/matters/{id}/texts` returns Method Not Allowed |
| Mover/Seconder | Always null | `EventItemMoverId` and `EventItemSeconderId` are null |
| Tally | Always null | `EventItemTally` is null for all items |

---

## Council Structure

**Dallas City Council** - 15 members (Mayor + 14 Council Districts)

### Current Council Members (Dec 2025, from Socrata)

| District | Name | Title |
|----------|------|-------|
| 1 | Chad West | Councilmember |
| 2 | Jesse Moreno | Mayor Pro Tem |
| 3 | Zarin D. Gracey | Councilmember |
| 4 | Maxie Johnson | Councilmember |
| 5 | Jaime Resendez | Councilmember |
| 6 | Laura Cadena | Councilmember |
| 7 | Adam Bazaldua | Councilmember |
| 8 | Lorie Blair | Councilmember |
| 9 | Paula Blackmon | Councilmember |
| 10 | Kathy Stewart | Councilmember |
| 11 | William Roth | Councilmember |
| 12 | Cara Mendelsohn | Councilmember |
| 13 | Gay Donnell Willis | Deputy Mayor Pro Tem |
| 14 | Paul Ridley | Councilmember |
| 15 | Eric Johnson | Mayor |

**Note:** Council membership changes over time (elections every 2 years). The extraction script dynamically discovers members from Socrata vote records for each time period.

### Key Bodies (Legistar)

| BodyId | Name | Type |
|--------|------|------|
| 138 | City Council | Primary Legislative Body |
| (varies) | Standing committees | Committee |
| (varies) | Boards & Commissions (~30) | Board |
| (varies) | Reinvestment Zone boards (~20) | Board |

---

## API Endpoints Reference

### Legistar API Endpoints

#### 1. Bodies (Committees & Councils)

```bash
# Get all bodies
curl "https://webapi.legistar.com/v1/cityofdallas/bodies"

# Get specific body
curl "https://webapi.legistar.com/v1/cityofdallas/bodies/138"
```

**Response fields:**
- `BodyId` - Unique integer identifier
- `BodyName` - Name of body
- `BodyTypeName` - Type (Committee, Council, Board, etc.)
- `BodyActiveFlag` - 1 if active, 0 if inactive

---

#### 2. Events (Meetings)

```bash
# Get recent meetings
curl "https://webapi.legistar.com/v1/cityofdallas/events?\$top=20&\$orderby=EventDate%20desc"

# Get City Council meetings only
curl "https://webapi.legistar.com/v1/cityofdallas/events?\$filter=EventBodyId%20eq%20138&\$orderby=EventDate%20desc"

# Get meetings in date range
curl "https://webapi.legistar.com/v1/cityofdallas/events?\$filter=EventDate%20ge%20datetime'2025-01-01'%20and%20EventDate%20lt%20datetime'2026-01-01'&\$orderby=EventDate%20asc"
```

**Response fields:**
- `EventId` - Unique identifier (use for EventItems lookup)
- `EventDate` - Meeting date (ISO format)
- `EventTime` - Meeting time (e.g., "9:00 AM")
- `EventBodyId` / `EventBodyName` - Body holding the meeting
- `EventAgendaFile` - URL to agenda PDF (if available)
- `EventMinutesFile` - URL to minutes PDF (if available)
- `EventVideoPath` - URL to video recording
- `EventLocation` - Meeting location (e.g., "COUNCIL CHAMBERS, CITY HALL")
- `EventInSiteURL` - Link to web portal meeting page
- `EventAgendaStatusName` - "Final" or "Draft"
- `EventMinutesStatusName` - Always "Draft" for Dallas

---

#### 3. Event Items (Agenda Items)

```bash
# Get agenda items for a specific meeting
curl "https://webapi.legistar.com/v1/cityofdallas/events/4067/EventItems"
```

**Note:** The top-level `/EventItems/` endpoint returns 404. Agenda items are ONLY accessible nested under events.

**Response fields:**
- `EventItemId` - Unique identifier
- `EventItemTitle` - Agenda item title/description
- `EventItemAgendaNumber` - Agenda number (e.g., "1.", "62.")
- `EventItemAgendaSequence` - Numeric ordering
- `EventItemMatterId` - Link to legislation matter (nullable)
- `EventItemMatterFile` - File number (e.g., "25-3336A")
- `EventItemMatterType` - Matter type name
- `EventItemMatterStatus` - Matter status name
- `EventItemConsent` - Consent flag (0 or 1)
- `EventItemActionName` - **ALWAYS NULL** for Dallas
- `EventItemPassedFlagName` - **ALWAYS NULL** for Dallas
- `EventItemRollCallFlag` - **ALWAYS 0** for Dallas
- `EventItemTally` - **ALWAYS NULL** for Dallas
- `EventItemMoverId` - **ALWAYS NULL** for Dallas
- `EventItemSeconderId` - **ALWAYS NULL** for Dallas

---

#### 4. Matters (Legislation)

```bash
# Get recent legislation
curl "https://webapi.legistar.com/v1/cityofdallas/matters?\$top=50&\$orderby=MatterLastModifiedUtc%20desc"

# Get specific matter
curl "https://webapi.legistar.com/v1/cityofdallas/matters/22932"

# Get matters by date range
curl "https://webapi.legistar.com/v1/cityofdallas/matters?\$filter=MatterIntroDate%20ge%20datetime'2025-01-01'%20and%20MatterIntroDate%20lt%20datetime'2026-01-01'"
```

**Response fields:**
- `MatterId` - Unique identifier
- `MatterFile` - File number (format: `YY-NNNNA`, e.g., "25-3343A")
- `MatterTitle` - Full descriptive title
- `MatterTypeId` / `MatterTypeName` - Type (74 types: CONSENT AGENDA, Items for Individual Consideration, Zoning Cases, etc.)
- `MatterStatusId` / `MatterStatusName` - Status (144 statuses)
- `MatterBodyId` / `MatterBodyName` - Originating department body
- `MatterIntroDate` - Introduction date
- `MatterAgendaDate` - Agenda date
- `MatterPassedDate` - Date passed (if applicable)
- `MatterEnactmentNumber` - Enactment number with status (e.g., "25-1824; APPROVED")
- `MatterRequester` - Originating department (e.g., "Dallas Fire-Rescue Department (DFD)")
- `MatterCost` - Financial cost of the item
- `MatterText1` - Additional text (often revenue info)
- `MatterText2` - Additional text (often contact email)

---

#### 5. Matter Attachments

```bash
curl "https://webapi.legistar.com/v1/cityofdallas/matters/22932/attachments"
```

Returns resolution documents and supporting files. `MatterAttachmentHyperlink` contains direct download URLs. Not all matters have attachments.

---

#### 6. Persons (Council Members & Staff)

```bash
# Get all persons
curl "https://webapi.legistar.com/v1/cityofdallas/persons"
```

Returns 1,000 records including system accounts ("Daystar", "View Only", "Legistar System"), staff, and former members. **Not recommended** for council member identification -- use Socrata `voter_name` + `district` fields instead.

---

### Socrata API Endpoints

#### 1. Vote Records (PRIMARY Vote Data Source)

```bash
# Get all votes for a specific date
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$where=date='2025-12-10T00:00:00'&\$limit=5000"

# Get votes for a date range (quarterly)
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$where=date>='2025-01-01T00:00:00'%20AND%20date<'2025-04-01T00:00:00'&\$limit=50000&\$offset=0"

# Count total records
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$select=count(*)"

# Get unique meeting dates
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$select=date,count(*)&\$group=date&\$order=date%20DESC&\$limit=1000"

# Get NO votes only
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$where=vote='NO'&\$limit=5000"

# Dataset metadata
curl "https://www.dallasopendata.com/api/views/ts5d-gdq6.json"
```

**Response fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `date` | calendar_date | Meeting date | `2025-12-10T00:00:00.000` |
| `agenda_item_number` | text | Item number on agenda | `62`, `Z15` |
| `item_type` | text | Type of agenda | `AGENDA`, `ADDENDUM`, `SPECIAL AGENDA` |
| `district` | number | Council district (1-14) or 15 for Mayor | `2` |
| `title` | text | Council role | `Mayor`, `Mayor Pro Tem`, `Councilmember` |
| `voter_name` | text | Full name of council member | `Jesse  Moreno` |
| `vote` | text | Vote cast | `YES`, `NO`, `AWVT`, `ABSNT`, `ABST` |
| `final_action_taken` | text | Final action on item | `APPROVED`, `DENIED`, `AMENDED` |
| `agenda_item_description` | text | Full description of item | (long text) |
| `agenda_id` | text | Composite: `MMDDYY_AG_ItemNum` | `121025_AG_62` |
| `vote_id` | text | Composite: `MMDDYY_AG_ItemNum_District` | `121025_AG_62_2` |

---

## Vote Data Path (CRITICAL)

Dallas requires a **dual-source extraction strategy**:

### Path 1: Per-Member Votes (Socrata - PRIMARY)

```
1. GET https://www.dallasopendata.com/resource/ts5d-gdq6.json
      ?$where=date >= '2024-01-01T00:00:00' AND date < '2024-04-01T00:00:00'
      &$limit=50000
      &$offset=0
   -> Returns per-member vote records with:
      date, agenda_item_number, voter_name, district, vote,
      final_action_taken, agenda_item_description, agenda_id, vote_id
```

### Path 2: Legislation Metadata (Legistar - SUPPLEMENTAL)

```
1. GET /events?$filter=EventBodyId eq 138 and EventDate ge datetime'2024-01-01' and EventDate lt datetime'2024-04-01'
   -> Get City Council meeting list (EventId, Date)

2. GET /events/{EventId}/EventItems
   -> Get agenda items for meeting (EventItemId, MatterId, MatterFile)

3. GET /matters/{MatterId}
   -> Get full matter details (type, status, cost, requester, body, dates)

4. GET /matters/{MatterId}/attachments
   -> Get document attachments (resolution files, etc.)
```

### Cross-Platform Correlation Strategy

There is **no direct foreign key** between Legistar and Socrata. To correlate records:

1. **Match on date:** Socrata `date` = Legistar `EventDate` (same meeting date)
2. **Match on agenda item number:** Socrata `agenda_item_number` (e.g., "62") corresponds to Legistar `EventItemAgendaNumber` (e.g., "62.")
3. **Fallback text similarity:** Compare Socrata `agenda_item_description` with Legistar `MatterTitle` or `EventItemTitle` for fuzzy matching

The extraction script normalizes agenda numbers (stripping trailing periods and leading zeros) to maximize matching accuracy.

---

## Query Parameters

### Legistar (OData)

Charlotte/Columbus standard OData syntax applies:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `$top` | `$top=1000` | Limit results (max 1,000 per page) |
| `$skip` | `$skip=1000` | Pagination offset |
| `$orderby` | `$orderby=EventDate desc` | Sort results |
| `$filter` | `$filter=EventBodyId eq 138` | Filter results |
| `$select` | `$select=MatterId,MatterTitle` | Select specific fields |

**Date filter format:** `datetime'YYYY-MM-DD'`

```
$filter=EventDate ge datetime'2025-01-01' and EventDate lt datetime'2025-04-01'
```

**Pagination:** Increment `$skip` by `$top` until fewer than `$top` results returned.

### Socrata (SoQL)

| Parameter | Example | Description |
|-----------|---------|-------------|
| `$where` | `$where=date >= '2025-01-01T00:00:00'` | SQL-like WHERE clause |
| `$select` | `$select=count(*)` | Columns to return / aggregates |
| `$group` | `$group=date` | GROUP BY clause |
| `$order` | `$order=date DESC` | Sort results |
| `$limit` | `$limit=50000` | Max rows returned (default: 1,000; max: 50,000) |
| `$offset` | `$offset=50000` | Pagination offset |

**Date format:** `'YYYY-MM-DDT00:00:00'` or `'YYYY-MM-DD'`

**Important:** Default `$limit` is 1,000. Always set `$limit=50000` for bulk extraction to avoid truncated results.

**Rate limits:** Generous for unauthenticated access. No throttling observed.

---

## Complete Extraction Workflow (Four-Phase)

### Phase 1: Fetch Legistar Data (Meetings, Agenda Items, Matter Details)

**Step 1: Get City Council meetings for the target quarter**
```bash
curl "https://webapi.legistar.com/v1/cityofdallas/events?\$filter=EventBodyId%20eq%20138%20and%20EventDate%20ge%20datetime'2025-01-01'%20and%20EventDate%20lt%20datetime'2025-04-01'&\$orderby=EventDate%20asc"
```

**Step 2: For each meeting, get agenda items**
```bash
curl "https://webapi.legistar.com/v1/cityofdallas/events/{EventId}/EventItems"
```

**Step 3: For each unique matter, get details and attachments**
```bash
curl "https://webapi.legistar.com/v1/cityofdallas/matters/{MatterId}"
curl "https://webapi.legistar.com/v1/cityofdallas/matters/{MatterId}/attachments"
```

Cache results by `MatterId` to avoid duplicate calls.

### Phase 2: Fetch Socrata Vote Data

**Step 4: Bulk-fetch all votes for the date range**
```bash
curl "https://www.dallasopendata.com/resource/ts5d-gdq6.json?\$where=date>='2025-01-01T00:00:00'%20AND%20date<'2025-04-01T00:00:00'&\$limit=50000&\$offset=0"
```

Paginate with `$offset` if more than 50,000 records. Typically a quarter has 3,000-5,000 vote records (200-350 items x 15 members).

### Phase 3: Correlate Legistar Items with Socrata Votes

**Step 5: Match by date + agenda item number**

For each Socrata vote record:
1. Find the Legistar meeting with the same date
2. Find the EventItem with a matching agenda number
3. Attach Legistar matter metadata (type, status, cost, file number, attachments) to the Socrata vote record
4. Build per-member vote columns from Socrata vote records grouped by `agenda_id`

### Phase 4: Write Output CSVs

Write three output files:
- `Dallas-TX-{year}-Q{quarter}-Votes.csv` -- all agenda items
- `Dallas-TX-{year}-Q{quarter}-Voted-Items.csv` -- items with Socrata vote data
- `Dallas-TX-{year}-Q{quarter}-Persons.csv` -- council member data

---

## Data Dictionary

Complete reference for every column in the Votes CSV output.

### Meeting-Level Columns (5 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 1 | `event_id` | integer | 98% | Legistar `EventId` | Unique Legistar meeting identifier. Empty for Socrata-only items without a Legistar match. | `4067`, `4068` |
| 2 | `event_date` | date | 100% | Legistar `EventDate` or Socrata `date` | Meeting date in YYYY-MM-DD format. | `2025-12-10`, `2025-11-12` |
| 3 | `event_time` | string | 98% | Legistar `EventTime` | Scheduled start time of meeting. Empty for unmatched Socrata items. | `9:00 AM` |
| 4 | `event_body` | string | 100% | Legistar `EventBodyName` | Name of the legislative body. | `City Council` |
| 5 | `event_location` | string | 98% | Legistar `EventLocation` | Physical location / streaming URL. | `COUNCIL CHAMBERS, CITY HALL\r\nbit.ly/cityofdallastv` |

### Agenda Item Columns (4 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 6 | `event_item_id` | integer | 98% | Legistar `EventItemId` | Unique Legistar agenda item identifier. Empty for unmatched Socrata items. | `101424`, `101429` |
| 7 | `agenda_number` | string | 46% | Legistar `EventItemAgendaNumber` or Socrata `agenda_item_number` | Displayed agenda number. Many Legistar section headers have no number. | `1.`, `62.`, `Z15` |
| 8 | `agenda_sequence` | integer | 98% | Legistar `EventItemAgendaSequence` | Numeric ordering of items on the agenda. | `1`, `18`, `50` |
| 9 | `title` | string | 100% | Legistar `EventItemTitle` or Socrata `agenda_item_description` | Full title/description of the agenda item. | `Authorize a five-year master agreement...` |

### Matter Columns -- from Legistar EventItem (3 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 10 | `matter_file` | string | 44% | Legistar `EventItemMatterFile` | Legistar file number. Format: `YY-NNNNA`. Empty for section headers, presentations, and unmatched items. 281/629 items have matter records. | `25-3336A`, `25-3343A` |
| 11 | `matter_type` | string | 44% | Legistar `EventItemMatterType` | Matter type from EventItem. | `MINUTES`, `CONSENT AGENDA` |
| 12 | `matter_status` | string | 44% | Legistar `EventItemMatterStatus` | Matter status from EventItem. | `Approved`, `Filed` |

### Matter Columns -- from `/matters/{id}` (6 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 13 | `matter_id` | integer | 44% | Legistar `MatterId` | Legistar internal matter ID. | `22925`, `22932` |
| 14 | `matter_title` | string | 44% | Legistar `MatterTitle` | Full descriptive title from matter detail. Often includes contract names, amounts, and department references. | `Authorize (1) a two-year interlocal Agreement with Dallas College...` |
| 15 | `matter_intro_date` | date | 44% | Legistar `MatterIntroDate` | Date the matter was introduced. YYYY-MM-DD. | `2025-11-10` |
| 16 | `matter_enactment_number` | string | 38% | Legistar `MatterEnactmentNumber` | Enactment number with status. Dallas uses format `YY-NNNN; ACTION`. | `25-1824; APPROVED` |
| 17 | `matter_requester` | string | 33% | Legistar `MatterRequester` | Originating city department. | `Dallas Fire-Rescue Department (DFD)`, `Office of Management Services` |
| 18 | `matter_body_name` | string | 44% | Legistar `MatterBodyName` | Body the matter is assigned to. | `Dallas Fire-Rescue Department`, `City Council` |

### Action & Vote Columns (7 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 19 | `passed` | integer | 37% | Derived from Socrata `final_action_taken` | Vote outcome: `1` = approved/passed, `0` = denied/failed, empty = no vote data. Derived from Socrata `final_action_taken` field. | `1`, `0`, *(empty)* |
| 20 | `vote_type` | string | 37% | Derived | How the vote was conducted. `Socrata Roll Call` when Socrata votes exist, empty otherwise. | `Socrata Roll Call`, *(empty)* |
| 21 | `consent` | integer | 0% | Legistar `EventItemConsent` | **Dallas does not populate this field.** Always 0. Consent items can be identified from `matter_type` containing "CONSENT". | `0` |
| 22 | `tally` | string | 0% | Legistar `EventItemTally` | **Dallas does not populate this field.** | *(always empty)* |
| 23 | `mover` | string | 0% | Legistar `EventItemMover` | **Dallas does not populate this field.** | *(always empty)* |
| 24 | `seconder` | string | 0% | Legistar `EventItemSeconder` | **Dallas does not populate this field.** | *(always empty)* |
| 25 | `roll_call_flag` | integer | ~85% | Legistar `EventItemRollCallFlag` | **Always 0** for Dallas (votes are in Socrata, not Legistar). | `0` |

### Socrata Vote Fields (3 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 26 | `socrata_item_number` | string | 37% | Socrata `agenda_item_number` | Agenda item number from Socrata vote records. | `62`, `Z15`, `1` |
| 27 | `socrata_agenda_info` | string | 37% | Socrata `item_type` | Type of agenda from Socrata. | `AGENDA`, `ADDENDUM`, `SPECIAL AGENDA`, `AGENDA DATE` |
| 28 | `socrata_final_action` | string | 37% | Socrata `final_action_taken` | Final action taken on the item. Free-text, not normalized. Contains occasional typos (e.g., "CORREDTED"). | `APPROVED`, `DENIED`, `AMENDED`, `DEFERRED TO 12/11/24` |

### Links & Enrichment Columns (4 columns)

| # | Column | Type | Fill Rate | Source | Description | Example Values |
|---|--------|------|-----------|--------|-------------|----------------|
| 29 | `agenda_link` | URL | 98% | Legistar `EventAgendaFile` | Direct URL to the meeting's agenda PDF. | `https://cityofdallas.legistar1.com/...` |
| 30 | `minutes_link` | URL | 99% | City Secretary website scraping (fallback: Legistar `EventMinutesFile`) | URL to minutes PDF. Scraped from the City Secretary's website at `dallascityhall.com/government/citysecretary/Pages/CCMeeting_{YEAR}.aspx`. PDFs hosted on `citysecretary2.dallascityhall.com/pdf/CC{YEAR}/`. Legistar `EventMinutesFile` is always empty for Dallas. The 1% gap is cancelled meetings with no minutes. | `https://citysecretary2.dallascityhall.com/pdf/CC2025/121025Min.pdf` |
| 31 | `video_link` | URL | 98% | Swagit archive scraping (fallback: Legistar `EventVideoPath`) | URL to Swagit video recording. Scraped from the Swagit archive at `dallastx.new.swagit.com/views/113` by matching meeting dates. 241 City Council videos available (Apr 2013-present). The 2% gap is Socrata-only items from special/closed session meetings not listed as "City Council Agenda Meetings" on Swagit. | `https://dallastx.new.swagit.com/videos/357579` |
| 32 | `attachment_links` | string | 14% | Legistar `/matters/{id}/attachments` | Pipe-delimited (`|`) list of direct download URLs for supporting documents. | `https://cityofdallas.legistar1.com/...resolution.docx` |

### Dynamic Member Vote Columns (15 columns for current council)

One column per council member discovered in Socrata vote records. Column name = member display name from Socrata `voter_name`. Values come from the Socrata `vote` field.

| # | Column | Fill Rate | Possible Values | Notes |
|---|--------|-----------|-----------------|-------|
| 33 | `Chad West` | 37% | `YES`, `NO`, `AWVT`, `ABSNT`, `ABST`, `N/A`, `ABSNT_CB` | District 1 |
| 34 | `Jesse  Moreno` | 37% | `YES`, `NO`, `AWVT`, `ABSNT`, `ABST`, `N/A` | District 2 (Mayor Pro Tem). Note double space in name. |
| 35 | `Zarin D. Gracey` | 37% | `YES`, `NO`, `AWVT`, `ABSNT`, `ABST`, `N/A` | District 3 |
| ... | *(12 more members)* | 37% | Same values | Districts 4-14 + Mayor (15). All 15 members have identical vote count (236/236). |

**Member column value definitions:**

| Value | Meaning | Frequency |
|-------|---------|-----------|
| `YES` | Voted in favor | 90.4% of all votes |
| `NO` | Voted against | 0.8% |
| `AWVT` | Away when vote taken | 3.7% |
| `ABSNT` | Absent (personal reasons) | 1.3% |
| `N/A` | Not applicable (member not yet seated, etc.) | 3.3% |
| `ABSNT_CB` | Absent on city business | 0.4% |
| `ABST` | Abstain | 0.1% |
| *(empty)* | No Socrata vote data for this member on this item | Legistar-only items without Socrata match |

### Persons CSV (separate file)

| # | Column | Type | Description | Example |
|---|--------|------|-------------|---------|
| 1 | `district` | integer | Council district number | `1`, `2`, `15` |
| 2 | `voter_name` | string | Full display name from Socrata | `Chad West`, `Jesse  Moreno` |
| 3 | `title` | string | Council role/title | `Councilmember`, `Mayor`, `Mayor Pro Tem` |
| 4 | `first_seen` | date | Earliest vote date in extraction period | `2025-10-01` |
| 5 | `last_seen` | date | Latest vote date in extraction period | `2025-12-10` |
| 6 | `vote_count` | integer | Total votes cast in extraction period | `450` |

---

## Data Quality Notes

### Strengths
- Socrata vote data is highly structured with composite IDs (`vote_id`, `agenda_id`)
- 186,780 total vote records spanning Sep 2016 to Dec 2025
- Every vote record includes district, title, and council member name
- Legistar matter data is rich: `MatterCost`, `MatterRequester`, `MatterEnactmentNumber`, `MatterBodyName`
- Both APIs require no authentication and have generous rate limits
- 15 members per meeting (Mayor + 14 districts) -- consistent council size

### Limitations
- No direct foreign key between Legistar and Socrata -- cross-platform matching is approximate
- Legistar vote fields (`EventItemActionName`, `EventItemPassedFlag`, all Votes/RollCalls endpoints) are completely empty
- Matter histories and sponsors are empty in Legistar
- `/matters/{id}/texts` returns 405 (Method Not Allowed)
- All Legistar event minutes have "Draft" status regardless of age (minutes sourced from City Secretary website instead)
- Legistar persons endpoint returns 1,000 records including system accounts (noisy)
- Socrata `final_action_taken` is free text, not normalized codes -- includes values like "REMANDED TO THE CITY PLAN AND ZONING COMMISSION"
- Socrata data appears to update periodically with potential delays after meetings

### Gotchas

1. **Vote data is NOT in Legistar.** Despite having a full Legistar instance, Dallas does not populate vote/roll-call fields. All vote data comes from Socrata.

2. **No direct linkage between systems.** Legistar and Socrata do not share IDs. Correlation requires matching on date + agenda item number. Some items may not match (different numbering conventions, special items).

3. **Socrata voter names have inconsistencies.** Some names have double spaces (e.g., "Jesse  Moreno"). The extraction script preserves names as-is from Socrata.

4. **Socrata `agenda_item_number` format varies.** Most are plain numbers ("62"), but zoning cases use letter prefixes ("Z15"). The Legistar `EventItemAgendaNumber` uses trailing periods ("62."). Matching logic must normalize both.

5. **Socrata `final_action_taken` is not normalized.** Beyond simple APPROVED/DENIED, there are many specific free-text values. The `passed` column in the CSV is derived by checking for known approval/denial keywords.

6. **Legistar EventItems include section headers.** Not all EventItems are voteable legislation -- many are section headers ("CONSENT AGENDA", "ITEMS FOR INDIVIDUAL CONSIDERATION") with no matter attached.

7. **Socrata record count per item varies.** Most items have 15 vote records (one per council seat), but some items have fewer (e.g., when members are N/A).

8. **Matter data starts June 2018.** Legistar matters only go back to mid-2018, while Socrata votes go back to September 2016. Early Socrata records will not have Legistar enrichment.

---

## Sample API Responses

### Legistar Event (Meeting)
```json
{
  "EventId": 4067,
  "EventGuid": "1A6CE33A-...",
  "EventBodyId": 138,
  "EventBodyName": "City Council",
  "EventDate": "2025-12-10T00:00:00",
  "EventTime": "9:00 AM",
  "EventAgendaStatusName": "Final",
  "EventMinutesStatusName": "Draft",
  "EventLocation": "COUNCIL CHAMBERS, CITY HALL\r\nbit.ly/cityofdallastv",
  "EventInSiteURL": "https://cityofdallas.legistar.com/MeetingDetail.aspx?LEGID=4067&GID=713..."
}
```

### Legistar EventItem (Agenda Item)
```json
{
  "EventItemId": 101424,
  "EventItemEventId": 4067,
  "EventItemAgendaSequence": 18,
  "EventItemAgendaNumber": "1.",
  "EventItemActionId": null,
  "EventItemActionName": null,
  "EventItemPassedFlag": null,
  "EventItemPassedFlagName": null,
  "EventItemRollCallFlag": 0,
  "EventItemTitle": "Approval of Minutes of the November 12, 2025 City Council Meeting",
  "EventItemTally": null,
  "EventItemConsent": 0,
  "EventItemMoverId": null,
  "EventItemSeconderId": null,
  "EventItemMatterId": 22925,
  "EventItemMatterFile": "25-3336A",
  "EventItemMatterType": "MINUTES",
  "EventItemMatterStatus": "Approved"
}
```

### Legistar Matter Detail
```json
{
  "MatterId": 22932,
  "MatterFile": "25-3343A",
  "MatterTitle": "Authorize (1) a two-year interlocal Agreement with Dallas College...",
  "MatterTypeId": 53,
  "MatterTypeName": "CONSENT AGENDA",
  "MatterStatusId": 87,
  "MatterStatusName": "Approved",
  "MatterBodyId": 466,
  "MatterBodyName": "Dallas Fire-Rescue Department",
  "MatterIntroDate": "2025-11-10T00:00:00",
  "MatterAgendaDate": "2025-12-10T00:00:00",
  "MatterEnactmentNumber": "25-1824; APPROVED",
  "MatterRequester": "Dallas Fire-Rescue Department (DFD)",
  "MatterCost": 240000.0,
  "MatterText1": "REV $1,000,000.00",
  "MatterText2": "richard.matthews@dallascityhall.com"
}
```

### Socrata Vote Record (YES)
```json
{
  "date": "2025-12-10T00:00:00.000",
  "agenda_item_number": "62",
  "item_type": "AGENDA",
  "district": "2",
  "title": "Mayor Pro Tem",
  "voter_name": "Jesse  Moreno",
  "vote": "YES",
  "final_action_taken": "APPROVED",
  "agenda_item_description": "Authorize a five-year master agreement for the purchase of Jet A fuel...",
  "agenda_id": "121025_AG_62",
  "vote_id": "121025_AG_62_2"
}
```

### Socrata Vote Record (NO)
```json
{
  "date": "2025-12-10T00:00:00.000",
  "agenda_item_number": "Z15",
  "item_type": "AGENDA",
  "district": "11",
  "title": "Councilmember",
  "voter_name": "William Roth",
  "vote": "NO",
  "final_action_taken": "AMENDED",
  "agenda_item_description": "A public hearing to receive comments regarding an application for...",
  "agenda_id": "121025_AG_Z15",
  "vote_id": "121025_AG_Z15_11"
}
```

---

## Dependencies

```bash
pip install requests
```

No Playwright dependency required. Dallas vote data comes from the Socrata API. Meeting video links are scraped from the Swagit archive and minutes links from the City Secretary website (plain HTTP, no JS rendering).

---

## Lessons Learned

### 1. Vote Data Is NOT in Legistar
Despite having a full Legistar instance with events, matters, and persons, Dallas does not populate the vote/roll-call fields in Legistar. All `EventItemActionName`, `EventItemPassedFlagName`, `Votes`, and `RollCalls` are empty or null. This is the single most critical finding.

### 2. Cross-Platform Match Rate Is 95%
The date + agenda number matching strategy works well: Q4 2025 achieved 224/236 (95%) Socrata items matched to Legistar. The 12 unmatched items are all procedural (minutes approvals, TOMA closed session items, board appointments) that exist in Socrata but have no corresponding Legistar EventItems. This is expected — not a data quality issue.

### 3. Socrata API Is Simpler Than Legistar
The Socrata API uses SQL-like SoQL queries, has no pagination complexity (just `$limit` + `$offset`), and returns flat denormalized data. It is faster and easier to work with than Legistar's OData-based API.

### 4. Dallas Legistar Client ID Is `cityofdallas`
Tested variations: `dallas` (500), `dallastx` (500), `dallascityhall` (500), `dallasgov` (500), `dallas-tx` (500). Only `cityofdallas` returns 200.

### 5. Socrata Vote Codes Need Normalization
The raw vote codes (`YES`, `NO`, `AWVT`, `ABSNT`, `ABSNT_CB`, `ABST`, `N/A`) are Dallas-specific. Map to CityVotes standard: `YES` -> Yes, `NO` -> No, `AWVT` -> Absent, `ABSNT` -> Absent, `ABSNT_CB` -> Absent, `ABST` -> Abstain, `N/A` -> Not Applicable.

### 6. final_action_taken Is Free Text with Typos
Unlike other cities with normalized action codes, Dallas's `final_action_taken` includes highly specific values like "REMANDED TO THE CITY PLAN AND ZONING COMMISSION" and "DEFERRED TO 12/11/24". The `passed` column in the CSV is derived by checking for keywords (APPROVED/ADOPTED -> 1, DENIED/FAILED -> 0). Source data contains typos (e.g., "APPROVED CORREDTED") and inconsistent date formatting ("DEFERRED TO 1/28/26" vs "DEFERRED TO 1/28/2026"). These are Socrata source issues, not extraction bugs.

### 7. Matter Data Enrichment Is Optional but Valuable
Legistar adds: `MatterCost`, `MatterRequester`, `MatterEnactmentNumber`, `MatterTypeName`, `MatterStatusName`, `MatterBodyName`, and document attachment links. The Socrata dataset alone provides date, item description, per-member votes, final action, and council member info.

### 8. Socrata Data Has a Double-Space Name Issue
Multiple voter names contain double spaces (e.g., "Jesse  Moreno", "Adam  Bazaldua"). Confirmed in Q4 2025 extraction — 2 of 15 members affected. The extraction script preserves these as-is to maintain consistency with the source data.

### 9. Retry Logic Is Essential for Legistar
The Legistar API occasionally returns 429 (rate limit) and 5xx errors. Using `requests.Session` with `Retry` (5 retries, exponential backoff) handles these reliably. The Socrata API is more reliable.

### 10. Socrata Provides Cleaner Council Member Data
The Legistar `/persons` endpoint returns 1,000 records including system accounts. Use Socrata's `voter_name` + `district` + `title` for clean, authoritative council member data. Q4 2025: all 15 members had exactly 236 votes each — perfectly uniform.

### 11. Many Legistar Fields Are Structurally Empty for Dallas
Q4 2025 extraction confirmed these fields are **always 0%**: `consent`, `tally`, `mover`, `seconder`. Five additional 0%-fill columns (`matter_name`, `matter_passed_date`, `matter_enactment_date`, `action`, `action_text`) were **dropped from the schema** to reduce noise — Dallas never populates them. This reduced the column count from 54 to 49.

### 12. Matter Metadata Fill Rate Is ~44%, Which Is Correct
Only 281 of 629 agenda items (44%) have formal matter records in Legistar. The remaining 348 are non-legislative (presentations, briefings, section headers) that don't generate matter files. This ratio is structurally correct for Dallas.

### 13. Vote Distribution Shows Strong Consensus Pattern
Q4 2025 vote breakdown: YES 84%, AWVT 7%, N/A 6%, NO 0.7% (27 dissenting votes across 236 items), ABSNT 0.2%, ABST 0.1%. The very low NO rate is a notable characteristic of Dallas City Council.

### 14. Socrata Occasionally Has More Meeting Dates Than Legistar
Q4 2025: Socrata had 6 unique meeting dates vs 5 Legistar meetings. The extra Socrata date likely corresponds to a special/emergency meeting not captured in the standard Legistar body filter. Consider expanding the Legistar body ID list or checking for special meeting bodies.

### 15. `MatterCost` Is Available but Not Yet Extracted
The Dallas Legistar API exposes `MatterCost` (fiscal impact) on matter details — a unique field not available in most other cities. This was confirmed in the API response (e.g., $240,000 for a Dallas College agreement) but is not currently included in the CSV output. Future enhancement opportunity.

### 16. Minutes Available via City Secretary Website
Legistar `EventMinutesFile` is always empty for Dallas (all minutes have permanent "Draft" status). However, the City Secretary publishes minutes PDFs at `citysecretary2.dallascityhall.com/pdf/CC{YEAR}/`. The per-year listing pages use HTML entity encoding for URLs (`&#58;` for `:`), requiring `html.unescape()` before regex matching. URL naming convention for year pages is inconsistent: `CCMeeting_{YEAR}.aspx` for 2023+, `CCMeetings_{YEAR}.aspx` (with 's') for older years. The script tries both patterns. Minutes coverage: 99% (627/629 items; 2 missing are from the cancelled Dec 24 meeting).

---

## Q4 2025 Extraction Results (Reference)

**Run date:** 2026-02-16

| Metric | Value |
|--------|-------|
| Meetings (Legistar) | 5 |
| Legistar items | 617 |
| Socrata vote records | 3,540 |
| Socrata unique items | 236 |
| Cross-platform match rate | 224/236 (95%) |
| Unmatched Socrata items | 12 (procedural) |
| Final merged rows | 629 |
| Council members | 15 |
| CSV columns | 47 |

**Vote distribution:**

| Value | Count | Pct |
|-------|-------|-----|
| YES | 2,969 | 84% |
| AWVT | 242 | 7% |
| N/A | 225 | 6% |
| NO | 27 | 0.7% |
| ABSNT | 7 | 0.2% |
| ABST | 4 | 0.1% |
