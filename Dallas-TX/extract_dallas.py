#!/usr/bin/env python3
"""
Dallas City Council Data Extraction Script
============================================
Extracts voting data from TWO sources:
  1. Legistar API (agenda/legislation metadata)
  2. Socrata Open Data Portal (per-member vote records)

Legistar API: https://webapi.legistar.com/v1/cityofdallas/
Socrata API:  https://www.dallasopendata.com/resource/ts5d-gdq6.json
Platform: Legistar (Granicus) + Socrata Open Data Portal

CRITICAL: Dallas does NOT store per-member votes in Legistar. The
/EventItems/{id}/Votes and /RollCalls endpoints always return empty.
All vote data comes from the Socrata dataset (ts5d-gdq6).

This script captures:
- Legistar: meetings, agenda items, matter details, attachments
- Socrata: per-member votes (YES/NO/AWVT/ABSNT/ABST/N/A/ABSNT_CB)
- Cross-platform correlation by date + agenda item number
- Dynamic member vote columns (one per council member)
- Legislation metadata enrichment (type, status, cost, requester, body)

Usage:
    python extract_dallas.py --year 2025 --quarter 4
    python extract_dallas.py --year 2025 --quarter 4 --votes-only
    python extract_dallas.py --year 2024 --quarter 1 --include-committees
    python extract_dallas.py --year 2025 --quarter 3 --output-dir /path/to/output

Requirements:
    pip install requests
"""

import argparse
import csv
import html
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LEGISTAR_BASE_URL = "https://webapi.legistar.com/v1/cityofdallas"
SOCRATA_BASE_URL = "https://www.dallasopendata.com/resource/ts5d-gdq6.json"
SWAGIT_ARCHIVE_URL = "https://dallastx.new.swagit.com/views/113"
SWAGIT_VIDEO_BASE = "https://dallastx.new.swagit.com/videos"
CITY_SECRETARY_BASE = "https://dallascityhall.com/government/citysecretary/Pages"

LEGISTAR_PAGE_SIZE = 1000  # Legistar OData max page size
SOCRATA_PAGE_SIZE = 50000  # Socrata max per request
LEGISTAR_REQUEST_DELAY = 0.25  # seconds between Legistar requests
SOCRATA_REQUEST_DELAY = 0.1  # Socrata handles faster requests
REQUEST_TIMEOUT = 30  # seconds

# Dallas City Council body ID in Legistar
CITY_COUNCIL_BODY_ID = 138

# Additional committee body IDs for --include-committees
# (Populated from research; adjust as needed)
COMMITTEE_BODY_IDS = []  # Dallas has ~110 bodies; add specific IDs as needed

QUARTER_DATES = {
    1: ("01-01", "04-01"),
    2: ("04-01", "07-01"),
    3: ("07-01", "10-01"),
    4: ("10-01", "01-01"),
}

# Keywords in final_action_taken that indicate approval
APPROVAL_KEYWORDS = [
    'APPROVED', 'ADOPTED', 'PASSED', 'CONFIRMED', 'ACCEPTED',
    'GRANTED', 'SUSTAINED', 'RATIFIED',
]

# Keywords that indicate denial/failure
DENIAL_KEYWORDS = [
    'DENIED', 'FAILED', 'REJECTED', 'DEFEATED',
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_quarter_dates(year: int, quarter: int) -> tuple:
    """
    Return (start_date, end_date) for the given year/quarter.
    Format: 'YYYY-MM-DD' for OData datetime filter.
    end_date is exclusive (first day of next quarter).
    """
    start = f"{year}-{QUARTER_DATES[quarter][0]}"
    end_year = year + 1 if quarter == 4 else year
    end = f"{end_year}-{QUARTER_DATES[quarter][1]}"
    return start, end


def get_output_paths(output_dir: Path, year: int, quarter: int) -> dict:
    """Generate standardized output file paths."""
    prefix = f"Dallas-TX-{year}-Q{quarter}"
    return {
        'votes': output_dir / f"{prefix}-Votes.csv",
        'voted_items': output_dir / f"{prefix}-Voted-Items.csv",
        'persons': output_dir / f"{prefix}-Persons.csv",
    }


def normalize_agenda_number(raw: str) -> str:
    """
    Normalize agenda number for cross-platform matching.
    Legistar uses trailing periods ('62.'), Socrata uses plain ('62').
    Strip periods, leading/trailing whitespace, and leading zeros.
    """
    if not raw:
        return ''
    cleaned = raw.strip().rstrip('.')
    # Try to normalize numeric-only items by stripping leading zeros
    if cleaned.isdigit():
        cleaned = str(int(cleaned))
    return cleaned


def derive_passed(final_action: str) -> object:
    """
    Derive a passed flag (1/0/None) from Socrata final_action_taken text.
    Returns 1 for approval, 0 for denial, None if unclear.
    """
    if not final_action:
        return None
    upper = final_action.upper()
    for keyword in APPROVAL_KEYWORDS:
        if keyword in upper:
            return 1
    for keyword in DENIAL_KEYWORDS:
        if keyword in upper:
            return 0
    # Ambiguous actions (AMENDED, DEFERRED, etc.) - still treat as passed if
    # the item wasn't denied. AMENDED usually means approved with changes.
    if 'AMENDED' in upper:
        return 1
    return None


# ---------------------------------------------------------------------------
# Main Extraction Workflow
# ---------------------------------------------------------------------------

class DallasExtractionWorkflow:
    """Complete Dallas City Council data extraction workflow."""

    def __init__(
        self,
        year: int,
        quarter: int,
        votes_only: bool = False,
        include_committees: bool = False,
        output_dir: Path = None,
    ):
        self.year = year
        self.quarter = quarter
        self.votes_only = votes_only
        self.include_committees = include_committees

        # Calculate date range
        self.start_date, self.end_date = get_quarter_dates(year, quarter)

        # Set output directory
        self.output_dir = output_dir or Path(__file__).parent
        self.output_paths = get_output_paths(self.output_dir, year, quarter)

        # Initialize HTTP session with retry logic
        self.session = self._create_session()

        # Runtime state
        self.all_members = set()
        self.meeting_links = {}
        self.matter_cache = {}

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    # -------------------------------------------------------------------
    # Legistar API Methods
    # -------------------------------------------------------------------

    def _legistar_get(self, url, params=None):
        """Make a single Legistar API request with rate limiting."""
        time.sleep(LEGISTAR_REQUEST_DELAY)
        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            print(f"  Warning: HTTP {response.status_code} for {url}")
            return None
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            time.sleep(2)
            return None

    def _legistar_get_all(self, url, params=None, sort_field=None):
        """
        Make paginated Legistar API requests using OData $top/$skip.
        Returns all results across all pages.
        """
        if params is None:
            params = {}

        all_results = []
        skip = 0

        while True:
            page_params = dict(params)
            page_params['$top'] = LEGISTAR_PAGE_SIZE
            page_params['$skip'] = skip
            if sort_field and '$orderby' not in page_params:
                page_params['$orderby'] = sort_field

            results = self._legistar_get(url, page_params)
            if results is None:
                break

            all_results.extend(results)

            if len(results) < LEGISTAR_PAGE_SIZE:
                break

            skip += LEGISTAR_PAGE_SIZE
            print(f"    Paginating... fetched {len(all_results)} so far")

        return all_results

    def fetch_legistar_meetings(self) -> list:
        """Get meetings for the configured date range and body filter."""
        body_ids = [CITY_COUNCIL_BODY_ID]
        if self.include_committees and COMMITTEE_BODY_IDS:
            body_ids.extend(COMMITTEE_BODY_IDS)

        all_meetings = []
        for body_id in body_ids:
            print(f"  Fetching meetings for BodyId {body_id}...")
            url = f"{LEGISTAR_BASE_URL}/events"
            params = {
                "$filter": (
                    f"EventBodyId eq {body_id} and "
                    f"EventDate ge datetime'{self.start_date}' and "
                    f"EventDate lt datetime'{self.end_date}'"
                ),
                "$orderby": "EventDate asc",
            }
            meetings = self._legistar_get_all(url, params)
            print(f"    Found {len(meetings)} meetings for BodyId {body_id}")
            all_meetings.extend(meetings)

        all_meetings.sort(key=lambda m: m.get('EventDate', ''))
        print(f"  Total Legistar meetings: {len(all_meetings)}")
        return all_meetings

    def fetch_event_items(self, event_id: int) -> list:
        """Get agenda items for a Legistar meeting."""
        url = f"{LEGISTAR_BASE_URL}/events/{event_id}/EventItems"
        return self._legistar_get(url) or []

    def fetch_matter_details(self, matter_id: int):
        """Get full matter details from Legistar."""
        url = f"{LEGISTAR_BASE_URL}/matters/{matter_id}"
        return self._legistar_get(url)

    def fetch_matter_attachments(self, matter_id: int) -> list:
        """Get attachments for a Legistar matter."""
        url = f"{LEGISTAR_BASE_URL}/matters/{matter_id}/attachments"
        return self._legistar_get(url) or []

    # -------------------------------------------------------------------
    # Socrata API Methods
    # -------------------------------------------------------------------

    def _socrata_get(self, params=None):
        """Make a single Socrata API request."""
        time.sleep(SOCRATA_REQUEST_DELAY)
        try:
            response = self.session.get(
                SOCRATA_BASE_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            print(f"  Warning: Socrata HTTP {response.status_code}")
            return None
        except Exception as e:
            print(f"  Error fetching Socrata: {e}")
            time.sleep(2)
            return None

    def fetch_socrata_votes(self) -> list:
        """
        Fetch all Socrata vote records for the configured date range.
        Paginates with $limit/$offset.
        """
        all_records = []
        offset = 0

        where_clause = (
            f"date >= '{self.start_date}T00:00:00' AND "
            f"date < '{self.end_date}T00:00:00'"
        )

        while True:
            params = {
                '$where': where_clause,
                '$limit': SOCRATA_PAGE_SIZE,
                '$offset': offset,
                '$order': 'date ASC, agenda_item_number ASC',
            }
            results = self._socrata_get(params)
            if results is None:
                break

            all_records.extend(results)

            if len(results) < SOCRATA_PAGE_SIZE:
                break

            offset += SOCRATA_PAGE_SIZE
            print(f"    Paginating Socrata... fetched {len(all_records)} so far")

        return all_records

    # -------------------------------------------------------------------
    # Swagit Video Archive
    # -------------------------------------------------------------------

    def fetch_swagit_videos(self) -> dict:
        """
        Scrape the Swagit video archive for City Council Agenda Meeting
        video links. Returns a dict mapping ISO date (YYYY-MM-DD) to
        full Swagit video URL.

        The archive page at /views/113 includes all videos in the HTML
        (no JS rendering needed). We extract pairs of (video_id, date)
        for rows matching "City Council Agenda Meetings".
        """
        print("\n  Fetching Swagit video archive...")
        try:
            resp = self.session.get(SWAGIT_ARCHIVE_URL, timeout=60)
            if resp.status_code != 200:
                print(f"    Warning: Swagit returned HTTP {resp.status_code}")
                return {}
        except Exception as e:
            print(f"    Warning: Could not fetch Swagit archive: {e}")
            return {}

        # Match table rows: <a href="/videos/ID">City Council Agenda Meetings</a>
        # followed by <td>Mon DD, YYYY</td>
        pattern = (
            r'<a[^>]*href="/videos/(\d+)"[^>]*>\s*City Council Agenda Meetings'
            r'(?:\s+\d{1,2}-\d{1,2}-\d{4})?\s*</a>'
            r'.*?<td[^>]*>\s*'
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
            r'\s+\d{1,2},\s+\d{4})\s*</td>'
        )
        matches = re.findall(pattern, resp.text, re.DOTALL)

        date_to_url = {}
        for video_id, date_str in matches:
            try:
                parsed = datetime.strptime(date_str.strip(), '%b %d, %Y')
                iso_date = parsed.strftime('%Y-%m-%d')
                url = f"{SWAGIT_VIDEO_BASE}/{video_id}"
                date_to_url[iso_date] = url
            except ValueError:
                continue

        print(f"    Found {len(date_to_url)} City Council meeting videos on Swagit")
        return date_to_url

    # -------------------------------------------------------------------
    # City Secretary Minutes Links
    # -------------------------------------------------------------------

    def fetch_minutes_links(self) -> dict:
        """
        Scrape the Dallas City Secretary website for minutes PDF links.

        The site at dallascityhall.com/government/citysecretary/ has per-year
        pages listing meetings with columns for agenda, annotated, video,
        and minutes. Minutes are hosted as PDFs on citysecretary2.dallascityhall.com
        with filenames like {MMDDYY}Min.pdf.

        Returns a dict mapping ISO date (YYYY-MM-DD) to minutes PDF URL.
        """
        # Determine which year pages to scrape
        years = {self.year}
        if self.quarter == 4:
            years.add(self.year + 1)  # Q4 ends in Jan of next year

        date_to_url = {}

        for year in sorted(years):
            # URL naming is inconsistent: newer years use CCMeeting_, older use CCMeetings_
            urls_to_try = [
                f"{CITY_SECRETARY_BASE}/CCMeeting_{year}.aspx",
                f"{CITY_SECRETARY_BASE}/CCMeetings_{year}.aspx",
            ]

            page_html = None
            for url in urls_to_try:
                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code == 200 and len(resp.text) > 1000:
                        page_html = resp.text
                        break
                except Exception:
                    continue

            if not page_html:
                print(f"    Warning: Could not fetch City Secretary page for {year}")
                continue

            # Decode HTML entities (site uses &#58; for colon in URLs)
            decoded = html.unescape(page_html)

            # Find all minutes PDF links in the HTML
            # Pattern: citysecretary2.dallascityhall.com/pdf/CC{YEAR}/{MMDDYY}Min*.pdf
            # Casing varies: Min.pdf, MIN.pdf, MINS.pdf
            pattern = (
                r'(https?://citysecretary2\.dallascityhall\.com'
                r'/pdf/CC\d{4}/(\d{6})Min\w*\.pdf)'
            )
            for match in re.finditer(pattern, decoded, re.IGNORECASE):
                full_url = match.group(1)
                mmddyy = match.group(2)
                try:
                    mm = int(mmddyy[0:2])
                    dd = int(mmddyy[2:4])
                    yy = int(mmddyy[4:6])
                    full_year = 1900 + yy if yy >= 97 else 2000 + yy
                    iso_date = f"{full_year}-{mm:02d}-{dd:02d}"
                    # Keep first match per date (avoid duplicates)
                    if iso_date not in date_to_url:
                        date_to_url[iso_date] = full_url
                except (ValueError, IndexError):
                    continue

        return date_to_url

    # -------------------------------------------------------------------
    # Phase 1: Fetch Legistar Data
    # -------------------------------------------------------------------

    def phase1_legistar(self) -> tuple:
        """
        Phase 1: Fetch Legistar meetings, agenda items, and matter details.
        Returns (legistar_items, meetings).
        """
        print("\n" + "=" * 60)
        print("Phase 1: Fetching Legistar data (meetings, items, matters)")
        print("=" * 60)

        # Step 1: Get meetings
        meetings = self.fetch_legistar_meetings()

        if not meetings:
            print("  No Legistar meetings found for this period.")
            return [], meetings

        # Step 2: Fetch agenda items for each meeting
        legistar_items = []
        for meeting in meetings:
            event_id = meeting['EventId']
            event_date = meeting['EventDate'][:10]
            body_name = meeting.get('EventBodyName', '')
            print(f"\n  Processing {event_date} - {body_name} (EventId: {event_id})...")

            # Store meeting-level data
            self.meeting_links[event_id] = {
                'agenda_link': meeting.get('EventAgendaFile') or '',
                'minutes_link': meeting.get('EventMinutesFile') or '',
                'video_link': meeting.get('EventVideoPath') or '',
                'insite_url': meeting.get('EventInSiteURL') or '',
                'event_location': meeting.get('EventLocation') or '',
                'event_time': meeting.get('EventTime') or '',
                'event_body': body_name,
            }

            items = self.fetch_event_items(event_id)
            print(f"    Found {len(items)} agenda items")

            for item in items:
                title = item.get('EventItemTitle', '') or ''
                if not title.strip():
                    continue

                item_data = {
                    'event_id': event_id,
                    'event_date': event_date,
                    'event_time': self.meeting_links[event_id]['event_time'],
                    'event_body': self.meeting_links[event_id]['event_body'],
                    'event_location': self.meeting_links[event_id]['event_location'],
                    'event_item_id': item['EventItemId'],
                    'agenda_number': item.get('EventItemAgendaNumber', '') or '',
                    'agenda_sequence': item.get('EventItemAgendaSequence', '') or '',
                    'title': title,
                    'matter_file': item.get('EventItemMatterFile', '') or '',
                    'matter_type': item.get('EventItemMatterType', '') or '',
                    'matter_status': item.get('EventItemMatterStatus', '') or '',
                    'matter_id': item.get('EventItemMatterId'),
                    # Vote fields
                    'passed': None,  # Will be set from Socrata data
                    'vote_type': '',
                    'consent': item.get('EventItemConsent', '') or '',
                    'tally': item.get('EventItemTally', '') or '',
                    'mover': item.get('EventItemMover', '') or '',
                    'seconder': item.get('EventItemSeconder', '') or '',
                    'roll_call_flag': item.get('EventItemRollCallFlag', 0),
                    # Matter detail fields (populated in enrichment step)
                    'matter_title': '',
                    'matter_intro_date': '',
                    'matter_enactment_number': '',
                    'matter_requester': '',
                    'matter_body_name': '',
                    # Links
                    'agenda_link': self.meeting_links[event_id]['agenda_link'],
                    'minutes_link': self.meeting_links[event_id]['minutes_link'],
                    'video_link': self.meeting_links[event_id]['video_link'],
                    'attachment_links': '',
                    # Socrata fields (populated in Phase 3)
                    'socrata_item_number': '',
                    'socrata_agenda_info': '',
                    'socrata_final_action': '',
                    # Vote data
                    'item_votes': {},
                }
                legistar_items.append(item_data)

        # Step 3: Enrich with matter details
        self._enrich_matter_data(legistar_items)

        print(f"\n  Phase 1 complete: {len(legistar_items)} Legistar items collected")
        return legistar_items, meetings

    def _enrich_matter_data(self, items: list):
        """Fetch matter details + attachments for all unique matters."""
        unique_matter_ids = set()
        for item in items:
            mid = item.get('matter_id')
            if mid:
                unique_matter_ids.add(mid)

        if not unique_matter_ids:
            return

        print(f"\n  Enriching {len(unique_matter_ids)} unique matters with details...")

        for i, mid in enumerate(sorted(unique_matter_ids), 1):
            if i % 100 == 0 or i == 1:
                print(f"    [{i}/{len(unique_matter_ids)}] Fetching matter details...")
            details = self.fetch_matter_details(mid)
            attachments = self.fetch_matter_attachments(mid)
            self.matter_cache[mid] = {
                'details': details,
                'attachments': attachments,
            }

        # Populate matter fields on each item
        enriched = 0
        for item in items:
            mid = item.get('matter_id')
            if mid and mid in self.matter_cache:
                details = self.matter_cache[mid].get('details')
                if details:
                    item['matter_title'] = details.get('MatterTitle', '') or ''
                    intro = details.get('MatterIntroDate', '') or ''
                    item['matter_intro_date'] = intro[:10] if intro else ''
                    item['matter_enactment_number'] = (
                        details.get('MatterEnactmentNumber', '') or ''
                    )
                    item['matter_requester'] = details.get('MatterRequester', '') or ''
                    item['matter_body_name'] = details.get('MatterBodyName', '') or ''
                    enriched += 1

                attachments = self.matter_cache[mid].get('attachments', [])
                if attachments:
                    links = [
                        a.get('MatterAttachmentHyperlink', '')
                        for a in attachments
                        if a.get('MatterAttachmentHyperlink')
                    ]
                    item['attachment_links'] = '|'.join(links)

        print(f"    Matter details populated for {enriched} items")

    # -------------------------------------------------------------------
    # Phase 2: Fetch Socrata Vote Data
    # -------------------------------------------------------------------

    def phase2_socrata(self) -> list:
        """
        Phase 2: Fetch all Socrata vote records for the date range.
        Returns list of raw Socrata records.
        """
        print("\n" + "=" * 60)
        print("Phase 2: Fetching Socrata vote data")
        print("=" * 60)

        records = self.fetch_socrata_votes()
        print(f"  Fetched {len(records)} Socrata vote records")

        if records:
            # Discover all council members
            for r in records:
                name = r.get('voter_name', '')
                if name:
                    self.all_members.add(name)
            print(f"  Discovered {len(self.all_members)} council members")

            # Count unique agenda items
            unique_items = set(r.get('agenda_id', '') for r in records)
            print(f"  Unique agenda items (by agenda_id): {len(unique_items)}")

            # Count unique meeting dates
            unique_dates = set(r.get('date', '')[:10] for r in records if r.get('date'))
            print(f"  Unique meeting dates: {len(unique_dates)}")

        return records

    # -------------------------------------------------------------------
    # Phase 3: Correlate Legistar + Socrata
    # -------------------------------------------------------------------

    def phase3_correlate(self, legistar_items: list, socrata_records: list) -> list:
        """
        Phase 3: Correlate Legistar items with Socrata votes.
        Merges vote data onto Legistar items and creates new items
        for Socrata records that don't match any Legistar item.

        Returns the final merged list of all items.
        """
        print("\n" + "=" * 60)
        print("Phase 3: Correlating Legistar items with Socrata votes")
        print("=" * 60)

        if not socrata_records:
            print("  No Socrata records to correlate.")
            return legistar_items

        # Build Socrata lookup: group by (date, normalized_agenda_number)
        socrata_by_key = {}
        for r in socrata_records:
            date_str = (r.get('date', '') or '')[:10]
            item_num = normalize_agenda_number(r.get('agenda_item_number', ''))
            key = (date_str, item_num)
            if key not in socrata_by_key:
                socrata_by_key[key] = []
            socrata_by_key[key].append(r)

        # Build Legistar lookup: index by (date, normalized_agenda_number)
        legistar_by_key = {}
        for item in legistar_items:
            date_str = item['event_date']
            raw_num = item.get('agenda_number', '')
            norm_num = normalize_agenda_number(raw_num)
            if norm_num:
                key = (date_str, norm_num)
                legistar_by_key[key] = item

        # Match Socrata records to Legistar items
        matched_keys = set()
        unmatched_socrata_keys = set()

        for key, records in socrata_by_key.items():
            if key in legistar_by_key:
                # Match found: merge Socrata data onto Legistar item
                item = legistar_by_key[key]
                self._merge_socrata_into_item(item, records)
                matched_keys.add(key)
            else:
                unmatched_socrata_keys.add(key)

        print(f"  Matched: {len(matched_keys)} agenda items")
        print(f"  Unmatched Socrata items (no Legistar match): {len(unmatched_socrata_keys)}")

        # Create new items for unmatched Socrata records
        new_items = []
        for key in sorted(unmatched_socrata_keys):
            records = socrata_by_key[key]
            date_str, norm_num = key
            sample = records[0]  # Use first record for metadata

            item_data = {
                'event_id': '',
                'event_date': date_str,
                'event_time': '',
                'event_body': 'City Council',
                'event_location': '',
                'event_item_id': '',
                'agenda_number': sample.get('agenda_item_number', ''),
                'agenda_sequence': '',
                'title': sample.get('agenda_item_description', ''),
                'matter_file': '',
                'matter_type': '',
                'matter_status': '',
                'matter_id': '',
                'passed': None,
                'vote_type': '',
                'consent': '',
                'tally': '',
                'mover': '',
                'seconder': '',
                'roll_call_flag': 0,
                'matter_title': '',
                'matter_intro_date': '',
                'matter_enactment_number': '',
                'matter_requester': '',
                'matter_body_name': '',
                'agenda_link': '',
                'minutes_link': getattr(self, '_minutes_links', {}).get(date_str, ''),
                'video_link': getattr(self, '_swagit_videos', {}).get(date_str, ''),
                'attachment_links': '',
                'socrata_item_number': '',
                'socrata_agenda_info': '',
                'socrata_final_action': '',
                'item_votes': {},
            }
            self._merge_socrata_into_item(item_data, records)
            new_items.append(item_data)

        # Combine all items
        all_items = legistar_items + new_items
        # Sort by date, then agenda sequence/number
        all_items.sort(key=lambda x: (
            x.get('event_date', ''),
            int(x.get('agenda_sequence', 0) or 0),
            x.get('agenda_number', ''),
        ))

        print(f"  Total items after merge: {len(all_items)}")
        print(f"    From Legistar: {len(legistar_items)}")
        print(f"    Socrata-only (unmatched): {len(new_items)}")

        return all_items

    def _merge_socrata_into_item(self, item: dict, socrata_records: list):
        """
        Merge a group of Socrata vote records into a single item dict.
        Each record in the group is one council member's vote on the same
        agenda item.
        """
        if not socrata_records:
            return

        sample = socrata_records[0]

        # Set Socrata-specific fields
        item['socrata_item_number'] = sample.get('agenda_item_number', '')
        item['socrata_agenda_info'] = sample.get('item_type', '')
        item['socrata_final_action'] = sample.get('final_action_taken', '')

        # Derive passed flag from final_action_taken
        item['passed'] = derive_passed(sample.get('final_action_taken', ''))
        item['vote_type'] = 'Socrata Roll Call'

        # Use Socrata description as title if Legistar title is empty
        if not item.get('title'):
            item['title'] = sample.get('agenda_item_description', '')

        # Build per-member vote dict
        votes = {}
        for r in socrata_records:
            name = r.get('voter_name', '')
            vote_val = r.get('vote', '')
            if name:
                votes[name] = vote_val
                self.all_members.add(name)

        item['item_votes'] = votes

    # -------------------------------------------------------------------
    # Phase 4: Write Output CSVs
    # -------------------------------------------------------------------

    def phase4_write_output(self, all_items: list):
        """Phase 4: Write output CSV files."""
        print("\n" + "=" * 60)
        print("Phase 4: Writing output CSV files")
        print("=" * 60)

        members_list = sorted(list(self.all_members))
        print(f"  Found {len(members_list)} council members: {members_list}")
        print(f"  Total items: {len(all_items)}")

        # Filter for votes-only mode
        items_to_write = all_items
        if self.votes_only:
            items_to_write = [i for i in all_items if i.get('item_votes')]
            print(f"  Filtered to {len(items_to_write)} voted items (--votes-only)")

        # Define CSV field names (fixed columns + dynamic member columns)
        fieldnames = [
            # Meeting-level
            'event_id', 'event_date', 'event_time', 'event_body', 'event_location',
            # Agenda item
            'event_item_id', 'agenda_number', 'agenda_sequence', 'title',
            # Matter from EventItem
            'matter_file', 'matter_type', 'matter_status',
            # Matter from /matters/{id}
            'matter_id', 'matter_title',
            'matter_intro_date', 'matter_enactment_number',
            'matter_requester', 'matter_body_name',
            # Vote
            'passed', 'vote_type',
            'consent', 'tally', 'mover', 'seconder', 'roll_call_flag',
            # Socrata fields
            'socrata_item_number', 'socrata_agenda_info', 'socrata_final_action',
            # Links
            'agenda_link', 'minutes_link', 'video_link', 'attachment_links',
        ] + members_list

        # Write main Votes CSV
        output_file = self.output_paths['votes']
        self._write_csv_file(output_file, fieldnames, items_to_write, members_list)
        print(f"\n  Votes CSV written to: {output_file}")
        print(f"    Rows: {len(items_to_write)}, Columns: {len(fieldnames)}")

        # Write Voted Items CSV (unless already in votes-only mode)
        if not self.votes_only:
            voted_items = [i for i in all_items if i.get('item_votes')]
            output_voted = self.output_paths['voted_items']
            self._write_csv_file(output_voted, fieldnames, voted_items, members_list)
            print(f"  Voted items CSV: {output_voted}")
            print(f"    Rows: {len(voted_items)}")

        # Write Persons CSV
        self._write_persons_csv()

    def _write_csv_file(
        self,
        output_path: Path,
        fieldnames: list,
        items: list,
        members_list: list,
    ):
        """Write a CSV file with vote data."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in items:
                row = {}
                for k in fieldnames:
                    if k not in members_list:
                        val = item.get(k, '')
                        # Convert None to empty string for CSV
                        row[k] = '' if val is None else val
                    else:
                        # Member vote column
                        row[k] = item.get('item_votes', {}).get(k, '')
                writer.writerow(row)

    def _write_persons_csv(self):
        """Write Persons CSV with council member data from Socrata."""
        output_persons = self.output_paths['persons']
        person_fields = [
            'district', 'voter_name', 'title', 'first_seen', 'last_seen', 'vote_count',
        ]

        # Build person data from all_members (collected during Socrata fetch)
        # We need the raw Socrata records to compute stats, but we can use
        # the member names we collected
        print(f"  Writing Persons CSV with {len(self.all_members)} members...")

        with open(output_persons, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=person_fields)
            writer.writeheader()
            for name in sorted(self.all_members):
                writer.writerow({
                    'district': '',
                    'voter_name': name,
                    'title': '',
                    'first_seen': '',
                    'last_seen': '',
                    'vote_count': '',
                })

        print(f"  Persons CSV: {output_persons}")

    def _write_persons_csv_from_socrata(self, socrata_records: list):
        """Write Persons CSV with enriched data from Socrata records."""
        output_persons = self.output_paths['persons']
        person_fields = [
            'district', 'voter_name', 'title', 'first_seen', 'last_seen', 'vote_count',
        ]

        # Build person stats from Socrata records
        person_data = {}
        for r in socrata_records:
            name = r.get('voter_name', '')
            if not name:
                continue
            if name not in person_data:
                person_data[name] = {
                    'district': r.get('district', ''),
                    'voter_name': name,
                    'title': r.get('title', ''),
                    'first_seen': (r.get('date', '') or '')[:10],
                    'last_seen': (r.get('date', '') or '')[:10],
                    'vote_count': 0,
                }
            # Update stats
            date_str = (r.get('date', '') or '')[:10]
            if date_str < person_data[name]['first_seen']:
                person_data[name]['first_seen'] = date_str
            if date_str > person_data[name]['last_seen']:
                person_data[name]['last_seen'] = date_str
            person_data[name]['vote_count'] += 1

        with open(output_persons, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=person_fields)
            writer.writeheader()
            for name in sorted(person_data.keys()):
                writer.writerow(person_data[name])

        print(f"  Persons CSV: {output_persons} ({len(person_data)} members)")

    # -------------------------------------------------------------------
    # Main Workflow
    # -------------------------------------------------------------------

    def run(self):
        """Execute the complete extraction workflow."""
        print("=" * 70)
        print(f"Dallas City Council Data Extraction - {self.year} Q{self.quarter}")
        print(f"Date range: {self.start_date} to {self.end_date}")
        if self.include_committees:
            print("Including committee meetings")
        if self.votes_only:
            print("Votes-only mode enabled")
        print("=" * 70)

        # Phase 1: Legistar data
        legistar_items, meetings = self.phase1_legistar()

        # Phase 1b: Swagit video links
        swagit_videos = self.fetch_swagit_videos()
        if swagit_videos:
            # Apply to meeting_links cache and existing items
            for eid, mdata in self.meeting_links.items():
                meeting_date = None
                for item in legistar_items:
                    if item.get('event_id') == eid:
                        meeting_date = item.get('event_date')
                        break
                if meeting_date and meeting_date in swagit_videos:
                    mdata['video_link'] = swagit_videos[meeting_date]
            for item in legistar_items:
                date = item.get('event_date', '')
                if date in swagit_videos:
                    item['video_link'] = swagit_videos[date]
            # Store for Phase 3 unmatched items
            self._swagit_videos = swagit_videos
        else:
            self._swagit_videos = {}

        # Phase 1c: City Secretary minutes links
        print("\n  Fetching City Secretary minutes links...")
        minutes_links = self.fetch_minutes_links()
        if minutes_links:
            print(f"    Found {len(minutes_links)} minutes PDFs")
            # Apply to meeting_links cache and existing items
            for eid, mdata in self.meeting_links.items():
                meeting_date = None
                for item in legistar_items:
                    if item.get('event_id') == eid:
                        meeting_date = item.get('event_date')
                        break
                if meeting_date and meeting_date in minutes_links:
                    mdata['minutes_link'] = minutes_links[meeting_date]
            for item in legistar_items:
                date = item.get('event_date', '')
                if date in minutes_links:
                    item['minutes_link'] = minutes_links[date]
            self._minutes_links = minutes_links
        else:
            print("    No minutes links found")
            self._minutes_links = {}

        # Phase 2: Socrata vote data
        socrata_records = self.phase2_socrata()

        # Phase 3: Correlate
        all_items = self.phase3_correlate(legistar_items, socrata_records)

        # Phase 4: Write output
        self.phase4_write_output(all_items)

        # Write enriched persons CSV using Socrata data
        if socrata_records:
            self._write_persons_csv_from_socrata(socrata_records)

        # Summary
        print("\n" + "=" * 70)
        print("Extraction complete!")
        print(f"  Legistar items: {len(legistar_items)}")
        print(f"  Socrata records: {len(socrata_records)}")
        print(f"  Final merged items: {len(all_items)}")
        print(f"  Council members: {len(self.all_members)}")
        print("=" * 70)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Dallas City Council Data Extraction (Legistar + Socrata)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract Q4 2025 data
    python extract_dallas.py --year 2025 --quarter 4

    # Extract only voted items
    python extract_dallas.py --year 2025 --quarter 4 --votes-only

    # Include committee meetings
    python extract_dallas.py --year 2025 --quarter 3 --include-committees

    # Custom output directory
    python extract_dallas.py --year 2024 --quarter 1 --output-dir ./output

Data Sources:
    Legistar API: https://webapi.legistar.com/v1/cityofdallas/
    Socrata API:  https://www.dallasopendata.com/resource/ts5d-gdq6.json

Note: Per-member votes come from Socrata, NOT Legistar. The Legistar
vote endpoints are empty for Dallas. This script fetches from both
sources and correlates them by date + agenda item number.
        """
    )
    parser.add_argument(
        "--year", type=int, required=True,
        help="Year to extract (e.g., 2025)"
    )
    parser.add_argument(
        "--quarter", type=int, required=True, choices=[1, 2, 3, 4],
        help="Quarter to extract (1-4)"
    )
    parser.add_argument(
        "--votes-only", action="store_true",
        help="Only output items with Socrata vote data"
    )
    parser.add_argument(
        "--include-committees", action="store_true",
        help="Include committee meetings beyond City Council"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Override default output directory"
    )

    args = parser.parse_args()

    workflow = DallasExtractionWorkflow(
        year=args.year,
        quarter=args.quarter,
        votes_only=args.votes_only,
        include_committees=args.include_committees,
        output_dir=args.output_dir,
    )
    workflow.run()


if __name__ == "__main__":
    main()
