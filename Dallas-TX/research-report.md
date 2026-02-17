
# Dallas, TX - Legislative System Research Report

**Date:** 2026-02-16
**Researcher:** Municipality Research Agent

## Platform Identification

| Property | Value |
|----------|-------|
| **Platform** | Legistar (Granicus) + Dallas Open Data (Socrata) |
| **Platform Type** | Legistar (agenda/legislation management) + Socrata (vote data) |
| **Web Portal** | https://cityofdallas.legistar.com/ |
| **Legistar API Base URL** | `https://webapi.legistar.com/v1/cityofdallas/` |
| **Socrata API Base URL** | `https://www.dallasopendata.com/resource/ts5d-gdq6.json` |
| **API Documentation** | Legistar: https://webapi.legistar.com/Help | Socrata: https://dev.socrata.com/ |
| **Authentication** | None required for either API |
| **Data Format** | JSON |

### Platform Notes

- Dallas uses a **dual-platform architecture**: Legistar for agenda/legislation management and a separate Socrata open data portal for per-member vote records.
- Legistar client ID: `cityofdallas` (tested: `dallas` = 500, `dallastx` = 500, `dallascityhall` = 500, `dallasgov` = 500, `dallas-tx` = 500, `cityofdallas` = **200**)
- **CRITICAL FINDING:** Legistar stores agendas, meetings, matters, and council member info, but does **NOT** contain per-member vote data. The `/EventItems/{id}/Votes` endpoint consistently returns empty arrays `[]` across all tested items and time periods. The `EventItemActionName` field is always `null`. No `EventItemRollCallFlag` is ever set to 1. Matter histories are empty `[]` for all tested matters. Matter sponsors are empty `[]` for all tested matters.
- **Per-member vote data lives exclusively in the Socrata portal** at dataset ID `ts5d-gdq6` with 186,780 records covering Sep 2016 to Dec 2025.
- The Socrata dataset is the **official City of Dallas Open Data** voting record, updated by the City Secretary's Office.

## Data Storage Model

### Legistar Entity Structure

Dallas Legistar organizes data around these primary entities:

1. **Bodies** (110 total) - Organizational units including City Council (BodyId=138), committees, boards, commissions, and reinvestment zones.
   - City Council is the `Primary Legislative Body` (BodyId=138)
   - 6+ active standing committees
   - ~30 Boards and Commissions
   - ~20 Reinvestment Zone boards

2. **Events** (~2,578 total) - Meetings of various bodies, dating back to April 2007.
   - Linked to Bodies via `EventBodyId`
   - Contain agenda items via `/events/{EventId}/EventItems`
   - All minutes status is "Draft" (no minutes are marked "Final")

3. **Matters** (~18,831 total) - Legislation items, dating back to June 2018.
   - 74 distinct MatterTypes (Consent Agenda, Items for Individual Consideration, Zoning Cases, etc.)
   - Linked to Events via EventItems
   - Contain attachments (resolutions, documents)
   - `MatterRequester` field tracks the originating department

4. **Persons** (1,000 total) - All people in the system including council members, staff, system accounts.
   - Includes council members, department heads, and administrative users
   - Not filtered to just elected officials

5. **EventItems** - Agenda line items linking Events to Matters.
   - Accessed only through `/events/{EventId}/EventItems`
   - Top-level `/EventItems/` endpoint returns 404
   - Contains `EventItemMatterId` when linked to legislation
   - `EventItemActionName` is always `null` (votes not recorded here)
   - `EventItemPassedFlagName` is always `null`

### Socrata Vote Data Structure

The Socrata dataset is a flat, denormalized table with one row per council-member per agenda-item:

| Field | Type | Description |
|-------|------|-------------|
| `date` | calendar_date | Meeting date (e.g., `2025-12-10T00:00:00.000`) |
| `agenda_item_number` | text | Item number on agenda (e.g., `62`, `Z15`) |
| `item_type` | text | AGENDA, AGENDA DATE, ADDENDUM, SPECIAL AGENDA |
| `district` | number | Council district number (1-14) or 15 for Mayor |
| `title` | text | Role: Mayor, Mayor Pro Tem, Deputy Mayor Pro Tem, Councilmember |
| `voter_name` | text | Full name of council member |
| `vote` | text | YES, NO, AWVT, ABSNT, ABSNT_CB, ABST, N/A |
| `final_action_taken` | text | APPROVED, AMENDED, DENIED, DELETED, etc. |
| `agenda_item_description` | text | Full description of the agenda item |
| `agenda_id` | text | Composite ID: `MMDDYY_AG_ItemNum` (e.g., `121025_AG_62`) |
| `vote_id` | text | Composite ID: `MMDDYY_AG_ItemNum_District` (e.g., `121025_AG_62_2`) |

### Key Relationships

```
Legistar:
  Body (BodyId=138 for City Council)
    |-- Events (EventId, filtered by EventBodyId=138)
    |     |-- EventItems (EventItemId, via /events/{id}/EventItems)
    |     |     |-- Matter (MatterId, via EventItemMatterId)
    |     |     |     |-- Attachments (via /matters/{id}/attachments)
    |     |     |-- Votes → EMPTY (not populated in Dallas Legistar)
    |     |     |-- RollCalls → EMPTY (not populated in Dallas Legistar)

Socrata (vote data):
  Meeting Date
    |-- Agenda Items (by agenda_item_number within date)
    |     |-- Per-Member Votes (15 rows per item, one per council seat)
```

### ID System
- **Legistar IDs**: Integer (EventId, MatterId, PersonId, BodyId, EventItemId)
- **Legistar File Numbers**: Format `YY-NNNA` (e.g., `25-3343A`, `26-703A`)
- **Socrata agenda_id**: Composite `MMDDYY_AG_ItemNum` (e.g., `121025_AG_62`)
- **Socrata vote_id**: Composite `MMDDYY_AG_ItemNum_District` (e.g., `121025_AG_62_2`)
- **No direct foreign key** between Legistar and Socrata (must join on date + item description text matching)

## API Endpoint Testing Results

### Legistar API Endpoints

| Endpoint | Method | Status | Records | Notes |
|----------|--------|--------|---------|-------|
| `/bodies` | GET | 200 | 110 | All bodies including council, committees, boards |
| `/events?$top=5&$orderby=EventDate desc` | GET | 200 | 5 | Recent events across all bodies |
| `/events?$filter=EventBodyId eq 138&$top=5&$orderby=EventDate desc` | GET | 200 | 5 | City Council meetings only |
| `/events/{EventId}/EventItems` | GET | 200 | 119-194 | Agenda items; section headers + matter items |
| `/EventItems/{EventItemId}/Votes` | GET | 200 | **0** | **ALWAYS EMPTY** - no vote data in Legistar |
| `/EventItems/{EventItemId}/RollCalls` | GET | 200 | **0** | **ALWAYS EMPTY** - no roll call data |
| `/persons` | GET | 200 | 1,000 | All persons (staff + council + system accounts) |
| `/matters?$top=5&$orderby=MatterLastModifiedUtc desc` | GET | 200 | 5 | Recent legislation items |
| `/matters/{MatterId}` | GET | 200 | 1 | Single matter detail with full metadata |
| `/matters/{MatterId}/histories` | GET | 200 | **0** | **ALWAYS EMPTY** - no legislative history |
| `/matters/{MatterId}/sponsors` | GET | 200 | **0** | **ALWAYS EMPTY** - no sponsor data |
| `/matters/{MatterId}/attachments` | GET | 200 | 0-1+ | Attachments available (resolutions, documents) |
| `/matters/{MatterId}/texts` | GET | **405** | N/A | Method not allowed |
| `/VoteTypes` | GET | 200 | 7 | Yes, No, Present, Absent, Excused, Abstain, Recused |
| `/MatterTypes` | GET | 200 | 74 | Full taxonomy of matter types |
| `/MatterStatuses` | GET | 200 | 144 | Comprehensive status list |
| `/Actions` | GET | 200 | 20 | Action types (adopted, approved, denied, etc.) |
| `/EventItems` (top-level) | GET | **404** | N/A | Top-level EventItems endpoint does not exist |

### Legistar Vote Testing Detail

Tested votes on event items spanning multiple years and meeting types:

| EventItemId | Event Date | Description | Votes Found |
|-------------|-----------|-------------|-------------|
| 101424 | 2025-12-10 | Minutes approval | 0 |
| 101429 | 2025-12-10 | Consent agenda item | 0 |
| 101431 | 2025-12-10 | Consent agenda item | 0 |
| 103034+ | 2026-01-14 | Various items | 0 (no actions on any of 119 items) |
| 103690+ | 2026-01-28 | Various items | 0 (no actions on any items) |
| 97721 | 2025-09-10 | Consent agenda item | 0 |

**Conclusion**: Dallas does not populate vote data in Legistar. All `EventItemActionName`, `EventItemPassedFlagName`, `EventItemMoverId`, `EventItemSeconderId`, and `EventItemTally` fields are `null` for every tested item across all time periods.

### Socrata API Endpoints

| Endpoint | Method | Status | Records | Notes |
|----------|--------|--------|---------|-------|
| `/resource/ts5d-gdq6.json` | GET | 200 | 186,780 total | Full voting record dataset |
| `/resource/ts5d-gdq6.json?$limit=5` | GET | 200 | 5 | Basic pagination works |
| `/resource/ts5d-gdq6.json?$select=count(*)` | GET | 200 | 1 | Aggregate queries work |
| `/resource/ts5d-gdq6.json?$where=vote='NO'` | GET | 200 | 1,507 | SoQL filtering works |
| `/resource/ts5d-gdq6.json?$select=...&$group=...` | GET | 200 | varies | GROUP BY queries work |
| `/resource/ts5d-gdq6.json?$select=min(date),max(date)` | GET | 200 | 1 | Date range: 2016-09-07 to 2025-12-10 |
| `/api/views/ts5d-gdq6.json` | GET | 200 | 1 | Dataset metadata endpoint |

## Data Availability

| Data Type | Available | Source | Notes |
|-----------|-----------|--------|-------|
| Meetings | Yes | Legistar API | Events endpoint with body filter; back to Apr 2007 |
| Agenda Items | Yes | Legistar API | EventItems nested under events; include section headers and matter items |
| Per-Member Votes | **Yes** | **Socrata API** | 186,780 records, Sep 2016 - Dec 2025; 15 votes per item |
| Council Members | Yes | Socrata API + Legistar | Socrata has district/name/title; Legistar has 1,000 persons (unfiltered) |
| Legislation Metadata | Yes | Legistar API | Matter type, status, intro date, requester, body, cost, enactment number |
| Full Text | No | N/A | `/matters/{id}/texts` returns 405; matter bodies/texts not available |
| Attachments | Partial | Legistar API | Some matters have resolution documents (.docx links) |
| Sponsors | No | N/A | `/matters/{id}/sponsors` always returns empty |
| Legislative History | No | N/A | `/matters/{id}/histories` always returns empty |
| Roll Calls/Attendance | Partial | Socrata API | ABSNT and AWVT vote codes indicate non-attendance |

## Data Scope

| Metric | Value |
|--------|-------|
| **Legistar Events Date Range** | April 25, 2007 to February 11, 2026 (future scheduled) |
| **Legistar Matters Date Range** | June 19, 2018 to present |
| **Socrata Vote Date Range** | September 7, 2016 to December 10, 2025 |
| **Total Legistar Events** | ~2,578 (all bodies) |
| **Total Legistar Matters** | ~18,831 |
| **Total Socrata Vote Records** | 186,780 |
| **Total Socrata Meeting Dates** | 332 unique dates |
| **Total Socrata Agenda Items** | 12,452 unique agenda items (by agenda_id) |
| **Council Size** | 15 members (Mayor + 14 council districts) |
| **Legistar Bodies** | 110 (1 Primary Legislative Body, committees, boards, commissions) |
| **Legistar Persons** | 1,000 (includes staff and system accounts) |
| **Legistar MatterTypes** | 74 |
| **Legistar MatterStatuses** | 144 |
| **Legistar Actions** | 20 |

### Current Council Members (as of Dec 2025)

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

## Vote Data Path

Dallas requires a **dual-source extraction strategy** because vote data and legislation metadata live in separate systems:

### Path 1: Per-Member Votes (Socrata - PRIMARY)
```
1. GET https://www.dallasopendata.com/resource/ts5d-gdq6.json
      ?$where=date >= '2024-01-01T00:00:00'
      &$limit=50000
      &$offset=0
   -> Returns per-member vote records with:
      date, agenda_item_number, voter_name, district, vote,
      final_action_taken, agenda_item_description, agenda_id, vote_id
```

### Path 2: Legislation Metadata (Legistar - SUPPLEMENTAL)
```
1. GET /events?$filter=EventBodyId eq 138&$orderby=EventDate desc
   -> Get City Council meeting list (EventId, Date)

2. GET /events/{EventId}/EventItems
   -> Get agenda items for meeting (EventItemId, MatterId, MatterFile)

3. GET /matters/{MatterId}
   -> Get full matter details (type, status, cost, requester, body, dates)

4. GET /matters/{MatterId}/attachments
   -> Get document attachments (resolution files, etc.)
```

### Joining the Two Sources

There is **no direct foreign key** between Legistar and Socrata. To correlate:
- Match on `date` (Socrata) = `EventDate` (Legistar)
- Match on `agenda_item_description` (Socrata) ~ `MatterTitle` (Legistar) via text similarity
- The Socrata `agenda_item_number` (e.g., `62`) corresponds to `EventItemAgendaNumber` in Legistar

## Query Parameter Notes

### Legistar (OData)
- Uses `$` prefix for OData parameters: `$filter`, `$top`, `$orderby`, `$skip`, `$select`
- URL encoding: `$` must be `%24` in some contexts, or escaped as `\$` in bash
- Date filter format: `datetime'YYYY-MM-DD'` (e.g., `EventDate ge datetime'2025-01-01'`)
- String filter: `EventBodyId eq 138`
- Max page size: 1,000 records per request (use `$skip` for pagination)
- Sort: `$orderby=EventDate desc` or `$orderby=MatterLastModifiedUtc desc`

### Socrata (SoQL)
- Uses `$` prefix: `$where`, `$select`, `$group`, `$order`, `$limit`, `$offset`
- Date format in `$where`: `date = '2025-12-10T00:00:00'` or `date >= '2024-01-01'`
- Supports SQL-like aggregation: `$select=count(*)`, `count(distinct field)`
- Default limit: 1,000 records (set `$limit=50000` for bulk extraction)
- Max limit: 50,000 per request
- No authentication required; rate limits are generous for unauthenticated access

## Key Findings / Gotchas

1. **Vote data is NOT in Legistar.** This is the most critical finding. Despite having a full Legistar instance with events, matters, and persons, Dallas does not populate the vote/roll-call fields in Legistar. All vote-related fields (`EventItemActionName`, `EventItemPassedFlagName`, `EventItemMoverId`, `EventItemSeconderId`, `EventItemTally`, `Votes`, `RollCalls`) are empty or null.

2. **Vote data lives in Socrata.** The `ts5d-gdq6` dataset on `dallasopendata.com` contains the comprehensive per-member voting record with 186,780 records from Sep 2016 to Dec 2025.

3. **No direct linkage between systems.** Legistar and Socrata do not share IDs. Correlating records requires matching on date and text similarity of item descriptions.

4. **Vote code meanings:**
   - `YES` = Voted yes (168,839 records, 90.4%)
   - `NO` = Voted no (1,507 records, 0.8%)
   - `AWVT` = Away when vote taken (6,965 records, 3.7%)
   - `ABSNT` = Absent for personal reasons (2,521 records, 1.3%)
   - `N/A` = Not applicable (6,073 records, 3.3%)
   - `ABSNT_CB` = Absent on city business (685 records, 0.4%)
   - `ABST` = Abstain (186 records, 0.1%)

5. **Socrata data is highly structured.** Each row represents one council member's vote on one agenda item. The `vote_id` field is a composite key (`MMDDYY_AG_ItemNum_District`) that uniquely identifies each vote record.

6. **Legistar matter data is rich.** Despite missing votes, Legistar has excellent legislation metadata: `MatterCost`, `MatterRequester`, `MatterEnactmentNumber`, `MatterTypeName`, `MatterStatusName`, `MatterBodyName`, and attachment links.

7. **Minutes never finalized.** All Legistar events show `EventMinutesStatusName: "Draft"` regardless of age.

8. **Matter histories and sponsors are empty.** The `/histories` and `/sponsors` sub-endpoints return empty arrays for all tested matters. Dallas does not use these Legistar features.

9. **Matter texts endpoint returns 405.** The `/matters/{id}/texts` endpoint returns "Method Not Allowed" (HTTP 405).

10. **Person data is noisy.** The Legistar `/persons` endpoint returns 1,000 records including system accounts ("Daystar", "View Only", "Legistar System"), staff, and former members. Use Socrata's `voter_name` + `district` fields for clean council member data.

11. **Socrata data appears to update periodically.** The latest date in the dataset is Dec 10, 2025, suggesting there may be a delay in data availability after council meetings.

12. **The `final_action_taken` field contains many unique values.** Beyond simple APPROVED/DENIED, there are highly specific actions like "REMANDED TO THE CITY PLAN AND ZONING COMMISSION" and "DEFERRED TO 12/11/24". These are entered as free text, not normalized codes.

## Sample Data

### Sample Meeting Record (Legistar Event)
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

### Sample EventItem (Legistar)
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

### Sample Vote Record (Socrata)
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
  "agenda_item_description": "Authorize a five-year master agreement for the purchase of Jet A fuel for the Dallas Police Department - Avfuel Corporation, lowest responsible bidder of four - Estimated amount of $588,451.30 - Financing:  General Fund",
  "agenda_id": "121025_AG_62",
  "vote_id": "121025_AG_62_2"
}
```

### Sample NO Vote Record (Socrata)
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
  "agenda_item_description": "A public hearing to receive comments regarding an application for and an ordinance granting RR Regional Retail District and a resolution accepting deed restrictions volunteered by the applicant on property zoned NO (A) Neighborhood Office District, on the southeast corner of Hillcrest Road and LBJ Freeway",
  "agenda_id": "121025_AG_Z15",
  "vote_id": "121025_AG_Z15_11"
}
```

### Sample Matter Record (Legistar)
```json
{
  "MatterId": 22932,
  "MatterFile": "25-3343A",
  "MatterTitle": "Authorize (1) a two-year interlocal Agreement with Dallas College in the amount of $1,000,000.00 for reimbursement to the City for Dallas Fire Rescue Department instructional services...",
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

## Extraction Feasibility

| Criteria | Assessment |
|----------|------------|
| API Access | **Yes** - Both Legistar (agenda/legislation) and Socrata (votes) have open APIs |
| Vote Data | **Full** - Per-member votes via Socrata with 186,780 records, all 15 council seats |
| Historical Data | **Moderate** - Votes from Sep 2016; Legistar matters from Jun 2018; events from Apr 2007 |
| Rate Limits | **None observed** - Both APIs responded promptly with no throttling |
| Data Quality | **Good** - Socrata vote data is well-structured with composite IDs; Legistar matter data is complete |
| Cross-Platform Linkage | **Challenging** - No shared IDs; requires date + text matching to correlate |
| **Overall** | **Ready for extraction - Dual-source approach required** |

## Recommended Next Steps

1. **Build Socrata extractor first.** The vote data is the primary target and is cleanly available via the Socrata API. Use `$limit=50000&$offset=N` for bulk extraction. Estimated ~4 API calls to pull all 186,780 records.

2. **Build Legistar supplemental extractor.** Pull matters and events to enrich vote data with legislation metadata (type, status, cost, requester, attachments).

3. **Develop cross-platform matching logic.** Create a join strategy using:
   - Meeting date (Socrata `date` = Legistar `EventDate`)
   - Agenda item number (Socrata `agenda_item_number` ~ Legistar `EventItemAgendaNumber`)
   - Text similarity between `agenda_item_description` and `MatterTitle`

4. **Normalize vote codes.** Map Socrata vote codes to standard CityVotes schema:
   - YES -> Yes
   - NO -> No
   - AWVT -> Absent (away when vote taken)
   - ABSNT -> Absent
   - ABSNT_CB -> Absent (city business)
   - ABST -> Abstain
   - N/A -> Not Applicable

5. **Monitor Socrata update frequency.** Track how quickly new meeting votes appear in the dataset after council meetings to determine expected data freshness.

6. **Consider whether Legistar enrichment is worth the complexity.** The Socrata dataset alone provides: date, item description, per-member votes, final action, and council member info. Legistar adds: matter type taxonomy, department/requester info, cost data, file numbers, and document attachments.
