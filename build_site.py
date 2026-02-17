#!/usr/bin/env python3
"""
Dallas City Council - CSV to JSON Site Builder
===============================================
Reads all quarterly CSV files from Dallas-TX/ and generates the JSON data
files expected by the CityVotes template in frontend/data/.

Usage:
    python build_site.py
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "Dallas-TX"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = FRONTEND_DIR / "data"

# ---------------------------------------------------------------------------
# Name normalization: merge variant spellings into canonical names
# ---------------------------------------------------------------------------

NAME_ALIASES = {
    "Adam  Bazaldua": "Adam Bazaldua",
    "Adam  Medrano": "Adam Medrano",
    "B. Adam McGough": "Adam McGough",
    "Carolyn Arnold": "Carolyn King Arnold",
    "Carolyn King  Arnold": "Carolyn King Arnold",
    "Gay Donnel Willis": "Gay Donnell Willis",
    "Jaynie Schultz": "Jaynie Shultz",
    "Jennifer S.  Gates": "Jennifer S. Gates",
    "Jesse  Moreno": "Jesse Moreno",
    "Tennel Atkins": "Tennell Atkins",
    "Tennell  Atkins": "Tennell Atkins",
    "Zarin D. Gracey": "Zarin Gracey",
}

# Short name overrides for names where split()[-1] doesn't work
SHORT_NAME_OVERRIDES = {
    "Casey Thomas II": "Thomas",
}


def normalize_name(name):
    """Normalize a council member name to canonical form."""
    name = name.strip()
    # Collapse multiple spaces
    name = " ".join(name.split())
    return NAME_ALIASES.get(name, name)


# ---------------------------------------------------------------------------
# Vote value mapping
# ---------------------------------------------------------------------------

VOTE_MAP = {
    "YES": "AYE",
    "NO": "NAY",
    "AWVT": "ABSENT",
    "ABSNT": "ABSENT",
    "ABSNT_CB": "ABSENT",
    "ABST": "ABSTAIN",
}

# N/A means the person was not on the council - skip these


def map_vote(raw_vote):
    """Map a raw CSV vote value to the template's vote choices."""
    v = raw_vote.strip().upper()
    if not v or v == "N/A":
        return None  # Not on council for this vote
    return VOTE_MAP.get(v, None)


# ---------------------------------------------------------------------------
# Outcome derivation
# ---------------------------------------------------------------------------

def derive_outcome(passed_val, final_action, matter_status):
    """Derive vote outcome from CSV fields."""
    p = str(passed_val).strip()
    fa = (final_action or "").strip().upper()
    ms = (matter_status or "").strip().upper()

    # Check passed field first
    if p == "1":
        return "PASS"
    if p == "0":
        # Check if it's really a failure or a deferral/special action
        if "DENIED" in fa:
            return "FAIL"
        if "DEFERRED" in fa:
            return "CONTINUED"
        if "DELETED" in fa:
            return "WITHDRAWN"
        if "DID NOT PASS" in fa:
            return "FAIL"
        return "FAIL"

    # Derive from final_action
    if any(kw in fa for kw in ["APPROVED", "ADOPTED", "PASSED", "CONFIRMED", "ACCEPTED", "GRANTED", "SUSTAINED", "RATIFIED"]):
        return "PASS"
    if "AMENDED" in fa:
        return "PASS"
    if any(kw in fa for kw in ["DENIED", "REJECTED", "DEFEATED", "FAILED"]):
        return "FAIL"
    if "DEFERRED" in fa or "HELD" in fa:
        return "CONTINUED"
    if "DELETED" in fa or "WITHDRAWN" in fa:
        return "WITHDRAWN"
    if "REMANDED" in fa:
        return "CONTINUED"
    if "TABLED" in fa:
        return "TABLED"

    # Derive from matter_status
    if "APPROVED" in ms:
        return "PASS"
    if "DEFERRED" in ms:
        return "CONTINUED"

    return "PASS"  # Default for voted items


# ---------------------------------------------------------------------------
# Section classification
# ---------------------------------------------------------------------------

def classify_section(matter_status, title, agenda_info):
    """Classify agenda section: CONSENT, GENERAL, or PUBLIC_HEARING."""
    ms = (matter_status or "").upper()
    t = (title or "").upper()
    ai = (agenda_info or "").upper()

    if "HEARING" in ms or "HEARING" in t or "PUBLIC HEARING" in t:
        return "PUBLIC_HEARING"
    if "CONSENT" in ms or "CONSENT AGENDA" in ms:
        return "CONSENT"
    if "INDIVIDUAL" in ms:
        return "GENERAL"
    if "ZONING" in t:
        return "PUBLIC_HEARING"

    return "CONSENT"  # Dallas does a lot by consent


# ---------------------------------------------------------------------------
# Topic classification (keyword-based)
# ---------------------------------------------------------------------------

TOPIC_KEYWORDS = {
    "Appointments": [
        "appointment", "board", "commission", "nominate", "nominee",
    ],
    "Budget & Finance": [
        "budget", "appropriation", "revenue", "fiscal", "tax increment",
        "financing", "financial", "fund", "bond", "revenue",
    ],
    "Community Services": [
        "library", "libraries", "social service", "community",
        "nonprofit", "non-profit", "youth", "senior",
    ],
    "Contracts & Agreements": [
        "contract", "agreement", "memorandum of understanding", "mou",
        "vendor", "procurement", "rfp", "supplemental agreement",
        "interlocal", "professional services",
    ],
    "Economic Development": [
        "economic development", "incentive", "redevelopment", "tif",
        "tax increment", "business", "commercial",
    ],
    "Emergency Services": [
        "police", "fire", "ems", "emergency", "disaster", "dpd",
        "fire-rescue", "public safety", "law enforcement",
    ],
    "Health & Safety": [
        "health", "safety", "code enforcement", "sanitation",
        "environmental", "hazardous", "pollution",
    ],
    "Housing": [
        "housing", "affordable", "residential", "tenant", "homeless",
        "shelter",
    ],
    "Infrastructure": [
        "infrastructure", "water", "sewer", "drainage", "storm",
        "utility", "utilities", "pipeline", "watershed", "dwu",
    ],
    "Ordinances & Resolutions": [
        "ordinance", "resolution", "municipal code", "amend",
        "chapter", "code amendment",
    ],
    "Parks & Recreation": [
        "park", "recreation", "trail", "playground", "open space",
    ],
    "Planning & Development": [
        "zoning", "land use", "planning", "permit", "plat",
        "specific use", "comprehensive plan", "variance",
        "planned development", "cpc",
    ],
    "Property & Real Estate": [
        "property", "real estate", "easement", "lease", "deed",
        "right-of-way", "right of way", "conveyance",
    ],
    "Public Works": [
        "street", "road", "maintenance", "waste", "sanitary",
        "facilities", "construction", "repair", "renovation",
        "design-build",
    ],
    "Transportation": [
        "transportation", "transit", "traffic", "signal", "dart",
        "pedestrian", "bicycle", "bike", "parking", "txdot",
        "highway", "freeway",
    ],
}


def classify_topics(title):
    """Assign up to 3 topic categories based on title keywords."""
    if not title:
        return ["General"]
    title_lower = title.lower()
    matches = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                matches.append(topic)
                break
    if not matches:
        return ["General"]
    return matches[:3]


# ---------------------------------------------------------------------------
# Non-voted item classification
# ---------------------------------------------------------------------------

SECTION_HEADERS = [
    "AGENDA", "ORDER OF BUSINESS", "INVOCATION", "PLEDGE OF ALLEGIANCE",
    "OPEN MICROPHONE", "MINUTES", "CONSENT AGENDA",
    "ITEMS FOR INDIVIDUAL CONSIDERATION", "ADDITIONS", "ZONING",
    "PUBLIC HEARINGS AND RELATED ACTIONS", "ADJOURNMENT",
    "BRIEFINGS", "PRESENTATIONS",
]


def classify_non_voted_item(title, matter_type, matter_status, final_action):
    """Classify non-voted agenda items."""
    t_upper = (title or "").strip().upper()
    mt = (matter_type or "").strip().upper()
    ms = (matter_status or "").strip().upper()
    fa = (final_action or "").strip().upper()

    # Section headers
    for sh in SECTION_HEADERS:
        if t_upper == sh or t_upper.startswith(sh + "\n"):
            return "committee_header", "medium", "section_header"

    # First readings
    if "FIRST" in fa and "READ" in fa:
        return "first_reading", "high", "legislation"
    if "FIRST READING" in t_upper:
        return "first_reading", "high", "legislation"

    # Read and filed
    if "READ" in fa and "FILED" in fa:
        return "read_and_filed", "low", "procedural"

    # Adopted without formal vote
    if "ADOPTED" in fa or "APPROVED" in ms:
        return "adopted_no_vote", "medium", "legislation"

    # Corrections
    if "CORRECT" in fa or "CORRECT" in ms:
        return "corrections", "low", "procedural"

    # Hearings
    if "HEARING" in t_upper:
        return "other", "medium", "legislation"

    return "other", "low", "procedural"


# ---------------------------------------------------------------------------
# Main Builder
# ---------------------------------------------------------------------------

class DallasSiteBuilder:
    def __init__(self):
        self.members = {}        # canonical_name -> member data
        self.member_id_map = {}  # canonical_name -> int ID
        self.meetings = []       # list of meeting dicts
        self.meeting_id_map = {} # (event_id, date) -> int ID
        self.votes = []          # list of vote dicts (voted items only)
        self.all_items = []      # list of all agenda items
        self.vote_id_counter = 0
        self.meeting_id_counter = 0

    def run(self):
        print("=" * 60)
        print("Dallas City Council - Building Website Data")
        print("=" * 60)

        self._load_members()
        self._load_current_members()
        self._load_all_csv_data()
        self._assign_member_ids()

        print(f"\nData loaded:")
        print(f"  Members: {len(self.members)}")
        print(f"  Meetings: {len(self.meetings)}")
        print(f"  Voted items: {len(self.votes)}")
        print(f"  All agenda items: {len(self.all_items)}")

        self._ensure_output_dirs()
        self._generate_stats_json()
        self._generate_council_json()
        self._generate_council_member_jsons()
        self._generate_meetings_json()
        self._generate_meeting_detail_jsons()
        self._generate_votes_json()
        self._generate_votes_by_year()
        self._generate_votes_index()
        self._generate_vote_detail_jsons()
        self._generate_alignment_json()
        self._generate_agenda_items_json()

        print("\n" + "=" * 60)
        print("All JSON files generated successfully!")
        print(f"Output directory: {DATA_DIR}")
        print("=" * 60)

    # ---------------------------------------------------------------
    # Phase 1: Load member roster from Persons CSVs
    # ---------------------------------------------------------------

    def _load_members(self):
        """Build master member list from all Persons CSVs."""
        print("\nLoading council member roster...")
        persons_files = sorted(CSV_DIR.glob("*-Persons.csv"))

        for f in persons_files:
            with open(f, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    name = normalize_name(row["voter_name"])
                    if name not in self.members:
                        self.members[name] = {
                            "full_name": name,
                            "short_name": SHORT_NAME_OVERRIDES.get(name, name.split()[-1]),
                            "district": row.get("district", ""),
                            "titles": set(),
                            "first_seen": row["first_seen"],
                            "last_seen": row["last_seen"],
                            "raw_names": set(),
                        }
                    m = self.members[name]
                    m["raw_names"].add(row["voter_name"].strip())
                    # Also add collapsed version
                    m["raw_names"].add(" ".join(row["voter_name"].split()))
                    title = row.get("title", "").strip()
                    if title:
                        m["titles"].add(title)
                    if row["first_seen"] and row["first_seen"] < m["first_seen"]:
                        m["first_seen"] = row["first_seen"]
                    if row["last_seen"] and row["last_seen"] > m["last_seen"]:
                        m["last_seen"] = row["last_seen"]

        print(f"  Found {len(self.members)} unique council members")

    def _assign_member_ids(self):
        """Assign stable integer IDs to members, sorted by first_seen then name."""
        sorted_members = sorted(
            self.members.keys(),
            key=lambda n: (self.members[n]["first_seen"], n),
        )
        for i, name in enumerate(sorted_members, 1):
            self.member_id_map[name] = i

        # Build short_name disambiguation (e.g., two "Johnson" members)
        short_counts = defaultdict(list)
        for name in self.members:
            short = self.members[name]["short_name"]
            short_counts[short].append(name)
        for short, names in short_counts.items():
            if len(names) > 1:
                for name in names:
                    first_initial = name.split()[0][0]
                    self.members[name]["short_name"] = f"{first_initial}. {short}"

    def _get_position(self, name):
        """Determine the most prominent position for a member."""
        m = self.members.get(name, {})
        titles = m.get("titles", set())
        if "Mayor" in titles:
            return "Mayor"
        if "Mayor Pro Tem" in titles:
            return "Mayor Pro Tem"
        if "Deputy Mayor Pro Tem" in titles:
            return "Deputy Mayor Pro Tem"
        return "Council Member"

    def _is_current(self, name):
        """Check if member appears in the most recent quarter's Persons file."""
        return name in self._current_members

    def _load_current_members(self):
        """Load the most recent Persons CSV to determine current members."""
        persons_files = sorted(CSV_DIR.glob("*-Persons.csv"))
        if not persons_files:
            self._current_members = set()
            return
        latest = persons_files[-1]
        self._current_members = set()
        with open(latest, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name = normalize_name(row["voter_name"])
                self._current_members.add(name)

    # ---------------------------------------------------------------
    # Phase 2: Load all CSV data
    # ---------------------------------------------------------------

    def _load_all_csv_data(self):
        """Load all Votes CSVs and process into meetings, votes, and items."""
        print("\nLoading vote data from all quarterly CSVs...")
        votes_files = sorted(CSV_DIR.glob("*-Votes.csv"))

        # Track meetings by (event_id, date) to deduplicate
        meetings_by_key = {}
        # Track all items by (date, agenda_sequence or agenda_number)
        seen_items = set()

        for f in votes_files:
            quarter_label = f.stem.replace("Dallas-TX-", "").replace("-Votes", "")
            print(f"  Processing {quarter_label}...")

            with open(f, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                fieldnames = reader.fieldnames

                # Identify member columns (everything after attachment_links)
                fixed_cols = [
                    "event_id", "event_date", "event_time", "event_body",
                    "event_location", "event_item_id", "agenda_number",
                    "agenda_sequence", "title", "matter_file", "matter_type",
                    "matter_status", "matter_id", "matter_title",
                    "matter_intro_date", "matter_enactment_number",
                    "matter_requester", "matter_body_name", "passed",
                    "vote_type", "consent", "tally", "mover", "seconder",
                    "roll_call_flag", "socrata_item_number",
                    "socrata_agenda_info", "socrata_final_action",
                    "agenda_link", "minutes_link", "video_link",
                    "attachment_links",
                ]
                member_cols = [c for c in fieldnames if c not in fixed_cols]

                for row in reader:
                    date = (row.get("event_date") or "").strip()
                    if not date:
                        continue

                    event_id = (row.get("event_id") or "").strip()
                    seq = (row.get("agenda_sequence") or "").strip()
                    item_num = (row.get("agenda_number") or "").strip()
                    title = (row.get("title") or "").strip()
                    eid = (row.get("event_item_id") or "").strip()

                    if not title:
                        continue

                    # Deduplicate items
                    item_key = (date, eid or f"{seq}_{item_num}_{title[:50]}")
                    if item_key in seen_items:
                        continue
                    seen_items.add(item_key)

                    # Process meeting
                    meeting_key = (event_id, date)
                    if meeting_key not in meetings_by_key:
                        self.meeting_id_counter += 1
                        meetings_by_key[meeting_key] = {
                            "id": self.meeting_id_counter,
                            "event_id": event_id,
                            "meeting_date": date,
                            "meeting_type": "regular",
                            "legistar_url": None,
                            "agenda_url": row.get("agenda_link") or None,
                            "minutes_url": row.get("minutes_link") or None,
                            "video_url": row.get("video_link") or None,
                            "vote_count": 0,
                            "non_voted_count": 0,
                            "first_reading_count": 0,
                            "agenda_item_count": 0,
                            "agenda_items": [],
                        }

                    meeting = meetings_by_key[meeting_key]
                    meeting_id = meeting["id"]

                    # Update meeting links (prefer non-empty)
                    for link_field, json_field in [
                        ("agenda_link", "agenda_url"),
                        ("minutes_link", "minutes_url"),
                        ("video_link", "video_url"),
                    ]:
                        val = (row.get(link_field) or "").strip()
                        if val and not meeting[json_field]:
                            meeting[json_field] = val

                    # Collect member votes for this item
                    member_votes = {}
                    for col in member_cols:
                        raw_name = col
                        canonical = normalize_name(raw_name)
                        raw_vote = (row.get(col) or "").strip()
                        mapped = map_vote(raw_vote)
                        if mapped is not None and canonical in self.members:
                            member_votes[canonical] = mapped

                    has_votes = len(member_votes) > 0
                    meeting["agenda_item_count"] += 1

                    if has_votes:
                        # This is a voted item
                        self.vote_id_counter += 1
                        vote_id = self.vote_id_counter

                        outcome = derive_outcome(
                            row.get("passed", ""),
                            row.get("socrata_final_action", ""),
                            row.get("matter_status", ""),
                        )
                        section = classify_section(
                            row.get("matter_status", ""),
                            title,
                            row.get("socrata_agenda_info", ""),
                        )
                        topics = classify_topics(title)

                        # Count tallies
                        ayes = sum(1 for v in member_votes.values() if v == "AYE")
                        noes = sum(1 for v in member_votes.values() if v == "NAY")
                        abstain = sum(1 for v in member_votes.values() if v == "ABSTAIN")
                        absent = sum(1 for v in member_votes.values() if v == "ABSENT")
                        recusal = sum(1 for v in member_votes.values() if v == "RECUSAL")

                        vote_record = {
                            "id": vote_id,
                            "outcome": outcome,
                            "ayes": ayes,
                            "noes": noes,
                            "abstain": abstain,
                            "absent": absent,
                            "item_number": item_num.rstrip(".") or str(seq),
                            "section": section,
                            "title": title,
                            "description": (row.get("matter_title") or "").strip(),
                            "meeting_date": date,
                            "meeting_id": meeting_id,
                            "meeting_type": "regular",
                            "topics": topics,
                            "matter_file": (row.get("matter_file") or "").strip() or None,
                            "matter_type": (row.get("matter_type") or "").strip() or None,
                            "member_votes": member_votes,
                        }
                        self.votes.append(vote_record)
                        meeting["vote_count"] += 1

                        # Add to meeting agenda
                        meeting["agenda_items"].append({
                            "agenda_sequence": int(seq) if seq.isdigit() else meeting["agenda_item_count"] - 1,
                            "item_type": "voted",
                            "item_number": vote_record["item_number"],
                            "title": title,
                            "section": section,
                            "matter_file": vote_record["matter_file"],
                            "matter_type": vote_record["matter_type"],
                            "topics": topics,
                            "vote": {
                                "id": vote_id,
                                "outcome": outcome,
                                "ayes": ayes,
                                "noes": noes,
                                "abstain": abstain,
                                "absent": absent,
                            },
                        })

                    else:
                        # Non-voted item
                        fa = (row.get("socrata_final_action") or "").strip()
                        category, importance, display_type = classify_non_voted_item(
                            title,
                            row.get("matter_type", ""),
                            row.get("matter_status", ""),
                            fa,
                        )
                        meeting["non_voted_count"] += 1
                        if category == "first_reading":
                            meeting["first_reading_count"] += 1

                        agenda_item = {
                            "agenda_sequence": int(seq) if seq.isdigit() else meeting["agenda_item_count"] - 1,
                            "item_type": "non_voted",
                            "category": category,
                            "importance": importance,
                            "display_type": display_type,
                            "title": title,
                            "matter_file": (row.get("matter_file") or "").strip() or None,
                            "matter_type": (row.get("matter_type") or "").strip() or None,
                            "action": fa or None,
                            "description": (row.get("matter_title") or "").strip() or None,
                            "topics": classify_topics(title) if importance == "high" else None,
                            "vote": None,
                        }
                        meeting["agenda_items"].append(agenda_item)

                        # Track non-voted items for agenda-items.json
                        if category != "committee_header":
                            self.all_items.append({
                                "event_item_id": eid,
                                "meeting_date": date,
                                "meeting_id": meeting_id,
                                "agenda_sequence": agenda_item["agenda_sequence"],
                                "title": title,
                                "matter_file": agenda_item["matter_file"],
                                "matter_type": agenda_item["matter_type"],
                                "action": fa or None,
                                "category": category,
                                "topics": classify_topics(title),
                                "description_preview": title[:200],
                            })

        # Sort agenda items within each meeting
        for m in meetings_by_key.values():
            m["agenda_items"].sort(key=lambda x: x["agenda_sequence"])

        # Build final meetings list (sorted by date descending)
        self.meetings = sorted(
            meetings_by_key.values(),
            key=lambda m: m["meeting_date"],
            reverse=True,
        )

        # Sort votes by date descending, then item number
        self.votes.sort(key=lambda v: (v["meeting_date"], v["item_number"]), reverse=True)

    # ---------------------------------------------------------------
    # Phase 3: Generate JSON files
    # ---------------------------------------------------------------

    def _ensure_output_dirs(self):
        """Create output directories."""
        (DATA_DIR / "council").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "meetings").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "votes").mkdir(parents=True, exist_ok=True)

    def _write_json(self, path, data):
        """Write JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  Written: {path.relative_to(BASE_DIR)}")

    # --- stats.json ---

    def _generate_stats_json(self):
        print("\nGenerating stats.json...")
        total_votes = len(self.votes)
        total_meetings = len(self.meetings)

        pass_count = sum(1 for v in self.votes if v["outcome"] == "PASS")
        unanimous = sum(
            1 for v in self.votes
            if v["noes"] == 0 and v["abstain"] == 0
            and v["outcome"] in ("PASS", "FAIL")
        )

        dates = [v["meeting_date"] for v in self.votes if v["meeting_date"]]
        all_meeting_dates = [m["meeting_date"] for m in self.meetings]
        all_dates = sorted(set(dates + all_meeting_dates))

        total_agenda = sum(m["agenda_item_count"] for m in self.meetings)
        total_non_voted = sum(m["non_voted_count"] for m in self.meetings)
        total_first_readings = sum(m["first_reading_count"] for m in self.meetings)

        data = {
            "success": True,
            "stats": {
                "total_meetings": total_meetings,
                "total_votes": total_votes,
                "total_council_members": len(self.members),
                "total_agenda_items": total_agenda,
                "total_non_voted_items": total_non_voted,
                "first_readings": total_first_readings,
                "pass_rate": round(pass_count / total_votes * 100, 1) if total_votes else 0,
                "unanimous_rate": round(unanimous / total_votes * 100, 1) if total_votes else 0,
                "date_range": {
                    "start": all_dates[0] if all_dates else "",
                    "end": all_dates[-1] if all_dates else "",
                },
            },
        }
        self._write_json(DATA_DIR / "stats.json", data)

    # --- council.json ---

    def _compute_member_stats(self, name):
        """Compute voting stats for a single member."""
        total = 0
        aye_count = 0
        nay_count = 0
        abstain_count = 0
        absent_count = 0
        recusal_count = 0
        votes_on_losing_side = 0
        close_vote_dissents = 0

        for vote in self.votes:
            mv = vote["member_votes"].get(name)
            if mv is None:
                continue  # Not on council for this vote
            total += 1

            if mv == "AYE":
                aye_count += 1
            elif mv == "NAY":
                nay_count += 1
            elif mv == "ABSTAIN":
                abstain_count += 1
            elif mv == "ABSENT":
                absent_count += 1
            elif mv == "RECUSAL":
                recusal_count += 1

            # Dissent calculation
            outcome = vote["outcome"]
            if outcome in ("PASS", "FAIL"):
                on_losing = (
                    (outcome == "PASS" and mv == "NAY")
                    or (outcome == "FAIL" and mv == "AYE")
                )
                if on_losing:
                    votes_on_losing_side += 1
                    # Close vote: decided by 1-2 vote margin
                    margin = abs(vote["ayes"] - vote["noes"])
                    if margin <= 2:
                        close_vote_dissents += 1

        valid_votes = total - absent_count - abstain_count
        # Exclude special outcomes from dissent denominator
        special_outcomes = sum(
            1 for v in self.votes
            if v["member_votes"].get(name) is not None
            and v["outcome"] not in ("PASS", "FAIL")
        )
        dissent_denom = valid_votes - special_outcomes if valid_votes > special_outcomes else 1

        return {
            "total_votes": total,
            "aye_count": aye_count,
            "nay_count": nay_count,
            "abstain_count": abstain_count,
            "absent_count": absent_count,
            "recusal_count": recusal_count,
            "aye_percentage": round(aye_count / total * 100, 1) if total else 0,
            "participation_rate": round(
                (total - absent_count - abstain_count) / total * 100, 1
            ) if total else 0,
            "dissent_rate": round(
                votes_on_losing_side / dissent_denom * 100, 1
            ) if dissent_denom else 0,
            "votes_on_losing_side": votes_on_losing_side,
            "votes_on_winning_side": total - votes_on_losing_side - absent_count - abstain_count - recusal_count,
            "close_vote_dissents": close_vote_dissents,
        }

    def _generate_council_json(self):
        print("\nGenerating council.json...")
        members_list = []
        for name in sorted(self.members.keys(), key=lambda n: self.member_id_map[n]):
            mid = self.member_id_map[name]
            m = self.members[name]
            stats = self._compute_member_stats(name)
            members_list.append({
                "id": mid,
                "full_name": name,
                "short_name": m["short_name"],
                "position": self._get_position(name),
                "start_date": m["first_seen"],
                "end_date": None if self._is_current(name) else m["last_seen"],
                "is_current": self._is_current(name),
                "stats": {
                    "total_votes": stats["total_votes"],
                    "aye_count": stats["aye_count"],
                    "nay_count": stats["nay_count"],
                    "abstain_count": stats["abstain_count"],
                    "absent_count": stats["absent_count"],
                    "recusal_count": stats["recusal_count"],
                    "aye_percentage": stats["aye_percentage"],
                    "participation_rate": stats["participation_rate"],
                    "dissent_rate": stats["dissent_rate"],
                    "votes_on_losing_side": stats["votes_on_losing_side"],
                    "close_vote_dissents": stats["close_vote_dissents"],
                },
            })
        self._write_json(DATA_DIR / "council.json", {
            "success": True,
            "members": members_list,
        })

    # --- council/{id}.json ---

    def _generate_council_member_jsons(self):
        print("\nGenerating council/{id}.json files...")
        for name in self.members:
            mid = self.member_id_map[name]
            m = self.members[name]
            stats = self._compute_member_stats(name)

            # Build vote history
            recent_votes = []
            for vote in self.votes:
                mv = vote["member_votes"].get(name)
                if mv is None:
                    continue
                recent_votes.append({
                    "vote_id": vote["id"],
                    "meeting_date": vote["meeting_date"],
                    "item_number": vote["item_number"],
                    "title": vote["title"],
                    "vote_choice": mv,
                    "outcome": vote["outcome"],
                    "topics": vote["topics"],
                    "meeting_type": vote["meeting_type"],
                })

            data = {
                "success": True,
                "member": {
                    "id": mid,
                    "full_name": name,
                    "short_name": m["short_name"],
                    "position": self._get_position(name),
                    "start_date": m["first_seen"],
                    "end_date": None if self._is_current(name) else m["last_seen"],
                    "is_current": self._is_current(name),
                    "stats": stats,
                    "recent_votes": recent_votes,
                },
            }
            self._write_json(DATA_DIR / "council" / f"{mid}.json", data)

    # --- meetings.json ---

    def _generate_meetings_json(self):
        print("\nGenerating meetings.json...")
        meetings_list = []
        for m in self.meetings:
            meetings_list.append({
                "id": m["id"],
                "event_id": m["event_id"],
                "meeting_date": m["meeting_date"],
                "meeting_type": m["meeting_type"],
                "legistar_url": m["legistar_url"],
                "agenda_url": m["agenda_url"],
                "minutes_url": m["minutes_url"],
                "video_url": m["video_url"],
                "agenda_item_count": m["agenda_item_count"],
                "vote_count": m["vote_count"],
                "non_voted_count": m["non_voted_count"],
                "first_reading_count": m["first_reading_count"],
            })
        available_years = sorted(
            set(m["meeting_date"][:4] for m in self.meetings),
            reverse=True,
        )
        self._write_json(DATA_DIR / "meetings.json", {
            "success": True,
            "meetings": meetings_list,
            "available_years": [int(y) for y in available_years],
        })

    # --- meetings/{id}.json ---

    def _generate_meeting_detail_jsons(self):
        print("\nGenerating meetings/{id}.json files...")
        for m in self.meetings:
            data = {
                "success": True,
                "meeting": {
                    "id": m["id"],
                    "event_id": m["event_id"],
                    "meeting_date": m["meeting_date"],
                    "meeting_type": m["meeting_type"],
                    "legistar_url": m["legistar_url"],
                    "agenda_url": m["agenda_url"],
                    "minutes_url": m["minutes_url"],
                    "video_url": m["video_url"],
                    "vote_count": m["vote_count"],
                    "non_voted_count": m["non_voted_count"],
                    "first_reading_count": m["first_reading_count"],
                    "agenda_item_count": m["agenda_item_count"],
                    "agenda_items": m["agenda_items"],
                },
            }
            self._write_json(DATA_DIR / "meetings" / f"{m['id']}.json", data)

    # --- votes.json ---

    def _generate_votes_json(self):
        print("\nGenerating votes.json...")
        votes_list = []
        for v in self.votes:
            votes_list.append({
                "id": v["id"],
                "outcome": v["outcome"],
                "ayes": v["ayes"],
                "noes": v["noes"],
                "abstain": v["abstain"],
                "absent": v["absent"],
                "item_number": v["item_number"],
                "section": v["section"],
                "title": v["title"],
                "meeting_date": v["meeting_date"],
                "meeting_type": v["meeting_type"],
                "topics": v["topics"],
            })
        self._write_json(DATA_DIR / "votes.json", {
            "success": True,
            "votes": votes_list,
        })

    # --- votes-{year}.json ---

    def _generate_votes_by_year(self):
        print("\nGenerating votes-{year}.json files...")
        by_year = defaultdict(list)
        for v in self.votes:
            year = v["meeting_date"][:4]
            by_year[year].append({
                "id": v["id"],
                "outcome": v["outcome"],
                "ayes": v["ayes"],
                "noes": v["noes"],
                "abstain": v["abstain"],
                "absent": v["absent"],
                "item_number": v["item_number"],
                "section": v["section"],
                "title": v["title"],
                "meeting_date": v["meeting_date"],
                "meeting_type": v["meeting_type"],
                "topics": v["topics"],
            })
        for year, votes in sorted(by_year.items()):
            self._write_json(
                DATA_DIR / f"votes-{year}.json",
                {"success": True, "votes": votes},
            )

    # --- votes-index.json ---

    def _generate_votes_index(self):
        print("\nGenerating votes-index.json...")
        years = sorted(
            set(v["meeting_date"][:4] for v in self.votes),
            reverse=True,
        )
        self._write_json(DATA_DIR / "votes-index.json", {
            "success": True,
            "available_years": [int(y) for y in years],
        })

    # --- votes/{id}.json ---

    def _generate_vote_detail_jsons(self):
        print("\nGenerating votes/{id}.json files...")
        for v in self.votes:
            member_votes_list = []
            for name, choice in sorted(v["member_votes"].items()):
                mid = self.member_id_map.get(name)
                if mid:
                    member_votes_list.append({
                        "member_id": mid,
                        "full_name": name,
                        "vote_choice": choice,
                    })

            data = {
                "success": True,
                "vote": {
                    "id": v["id"],
                    "item_number": v["item_number"],
                    "title": v["title"],
                    "description": v.get("description", ""),
                    "outcome": v["outcome"],
                    "ayes": v["ayes"],
                    "noes": v["noes"],
                    "abstain": v["abstain"],
                    "absent": v["absent"],
                    "meeting_id": v["meeting_id"],
                    "meeting_date": v["meeting_date"],
                    "meeting_type": v["meeting_type"],
                    "member_votes": member_votes_list,
                    "topics": v["topics"],
                },
            }
            self._write_json(DATA_DIR / "votes" / f"{v['id']}.json", data)

    # --- alignment.json ---

    def _generate_alignment_json(self):
        print("\nGenerating alignment.json...")
        # Only compute for current members
        current_members = [
            name for name in self.members if self._is_current(name)
        ]

        pairs = []
        for m1, m2 in combinations(sorted(current_members), 2):
            shared = 0
            agreements = 0
            for vote in self.votes:
                v1 = vote["member_votes"].get(m1)
                v2 = vote["member_votes"].get(m2)
                # Both must have participated (not ABSENT/ABSTAIN/RECUSAL)
                if v1 in ("AYE", "NAY") and v2 in ("AYE", "NAY"):
                    shared += 1
                    if v1 == v2:
                        agreements += 1

            if shared > 0:
                pairs.append({
                    "member1": self.members[m1]["short_name"],
                    "member2": self.members[m2]["short_name"],
                    "shared_votes": shared,
                    "agreements": agreements,
                    "agreement_rate": round(agreements / shared * 100, 1),
                })

        pairs.sort(key=lambda p: p["agreement_rate"])
        least_aligned = pairs[:3] if len(pairs) >= 3 else pairs
        most_aligned = pairs[-3:][::-1] if len(pairs) >= 3 else pairs[::-1]

        self._write_json(DATA_DIR / "alignment.json", {
            "success": True,
            "members": [self.members[n]["short_name"] for n in sorted(current_members)],
            "alignment_pairs": pairs,
            "most_aligned": most_aligned,
            "least_aligned": least_aligned,
        })

    # --- agenda-items.json ---

    def _generate_agenda_items_json(self):
        print("\nGenerating agenda-items.json...")
        self._write_json(DATA_DIR / "agenda-items.json", {
            "success": True,
            "agenda_items": self.all_items[:5000],  # Cap for performance
        })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    builder = DallasSiteBuilder()
    builder.run()
