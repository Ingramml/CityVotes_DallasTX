# Data Files Required

Place these JSON files in this folder to populate the website.

## File List

| File | Description |
|------|-------------|
| `stats.json` | Global KPI statistics |
| `council.json` | All council members summary |
| `council/{id}.json` | Individual member details + vote history |
| `meetings.json` | All meetings list |
| `meetings/{id}.json` | Individual meeting detail with full agenda |
| `votes.json` | All votes combined |
| `votes-{year}.json` | Votes split by year (for performance) |
| `votes-index.json` | Available years index |
| `votes/{id}.json` | Individual vote detail with member votes |
| `alignment.json` | Voting alignment between member pairs |
| `agenda-items.json` | Non-voted agenda items (first readings, etc.) |

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
    "total_agenda_items": 2500,
    "total_non_voted_items": 1256,
    "first_readings": 400,
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
        "outcome": "PASS|FAIL"
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
      "event_id": "6137",
      "meeting_date": "YYYY-MM-DD",
      "meeting_type": "regular|special",
      "legistar_url": "https://...|null",
      "agenda_url": "https://...|null",
      "minutes_url": "https://...|null",
      "video_url": "https://...|null",
      "agenda_item_count": 268,
      "vote_count": 195,
      "non_voted_count": 73,
      "first_reading_count": 18
    }
  ]
}
```

### meetings/{id}.json
```json
{
  "success": true,
  "meeting": {
    "id": 1,
    "event_id": "6137",
    "meeting_date": "YYYY-MM-DD",
    "meeting_type": "regular|special",
    "legistar_url": "https://...|null",
    "agenda_url": "https://...|null",
    "minutes_url": "https://...|null",
    "video_url": "https://...|null",
    "vote_count": 195,
    "non_voted_count": 73,
    "first_reading_count": 18,
    "agenda_item_count": 268,
    "agenda_items": [
      {
        "agenda_sequence": 0,
        "item_type": "non_voted",
        "category": "committee_header|first_reading|read_and_filed|adopted_no_vote|corrections|other",
        "importance": "high|medium|low",
        "display_type": "section_header|legislation|procedural",
        "title": "Item title text",
        "matter_file": "0001-2024|null",
        "matter_type": "Ordinance|Resolution|null",
        "action": "Read for the First Time|null",
        "description": "Full description text|null",
        "topics": ["Topic1"]
      },
      {
        "agenda_sequence": 4,
        "item_type": "voted",
        "item_number": "3",
        "title": "Vote title text",
        "section": "CONSENT|GENERAL|PUBLIC_HEARING",
        "matter_file": "0001-2024",
        "matter_type": "Ordinance",
        "topics": ["Budget & Finance"],
        "vote": {
          "id": 123,
          "outcome": "PASS|FAIL|CONTINUED|TABLED|WITHDRAWN",
          "ayes": 7,
          "noes": 0,
          "abstain": 0,
          "absent": 0
        }
      }
    ]
  }
}
```

### agenda-items.json
```json
{
  "success": true,
  "agenda_items": [
    {
      "event_item_id": "554873",
      "meeting_date": "YYYY-MM-DD",
      "meeting_id": 1,
      "agenda_sequence": 14,
      "title": "Item title text",
      "matter_file": "0002-2024",
      "matter_type": "Ordinance|Resolution",
      "action": "Read for the First Time|Read & Filed|Adopted (No Vote)",
      "category": "first_reading|read_and_filed|adopted_no_vote|other",
      "topics": ["Budget & Finance", "Infrastructure"],
      "description_preview": "First 200 chars of description..."
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
      "title": "Vote title text",
      "meeting_date": "YYYY-MM-DD",
      "meeting_type": "regular|special",
      "topics": ["Budget & Finance", "Housing"]
    }
  ]
}
```

### votes-index.json
```json
{
  "success": true,
  "available_years": [2024, 2023, 2022]
}
```

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

## Topic Categories

Topics are dynamically extracted from the data. Common categories include:

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

Additional topics may appear depending on your city's data (e.g., Grants, Education, etc.). The UI populates topic filters dynamically from the data.
