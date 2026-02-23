# CityVotes Year Filter Implementation Plan

**Purpose**: This document tells an LLM how to limit any CityVotes static site to display only 2 years of data (2022-2023). It applies to all CityVotes city sites that follow the same architecture as the Dallas implementation.

---

## Architecture Overview

Every CityVotes site follows this structure:

```
project-root/
  build_site.py              # Python build script (CSV -> JSON)
  {City}-{ST}/               # Source CSV data folder
    {City}-{ST}-{YEAR}-Q{N}-Votes.csv
    {City}-{ST}-{YEAR}-Q{N}-Persons.csv
    {City}-{ST}-{YEAR}-Q{N}-Voted-Items.csv
  frontend/
    data/                    # Generated JSON files (output of build_site.py)
      stats.json
      council.json
      council/{id}.json
      meetings.json
      meetings/{id}.json
      votes.json
      votes-{year}.json
      votes-index.json
      votes/{id}.json
      alignment.json
      agenda-items.json
    js/api.js                # Frontend data fetching (reads from data/)
    *.html                   # Static HTML pages
```

**Data flow**: `CSV files -> build_site.py -> frontend/data/*.json -> frontend HTML/JS`

The only file you need to edit is `build_site.py`. No frontend code changes are needed.

---

## Step-by-Step Implementation

### Step 1: Identify the Build Script

Open `build_site.py` in the project root. Find the **Configuration** section near the top of the file. It will look like this:

```python
# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "{City}-{ST}"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = FRONTEND_DIR / "data"
```

### Step 2: Add the YEAR_RANGE Configuration

Add these lines immediately after the `DATA_DIR` line:

```python
# Year filter: only process CSVs within this range (inclusive).
# Set to None to process all years.
YEAR_RANGE = (2022, 2023)
```

### Step 3: Add the Filter Function

Add this function immediately after the `YEAR_RANGE` line (before any class or other function definitions, but after all the configuration variables):

```python
def _filter_csv_files(files):
    """Filter CSV file list to only include years within YEAR_RANGE."""
    if YEAR_RANGE is None:
        return files
    filtered = []
    for f in files:
        # Extract year from filename pattern: {City}-{ST}-{YEAR}-Q{N}-{Type}.csv
        match = re.search(r"-(\d{4})-Q\d", f.name)
        if match:
            year = int(match.group(1))
            if YEAR_RANGE[0] <= year <= YEAR_RANGE[1]:
                filtered.append(f)
        else:
            filtered.append(f)  # Keep files that don't match the pattern
    return filtered
```

**Important**: This function requires `import re` at the top of the file. Check that `re` is already imported. If not, add it to the imports section.

### Step 4: Apply the Filter to All CSV Loading Points

Search `build_site.py` for every place where CSV files are loaded using `.glob()`. There are exactly **3 locations** to modify in the standard CityVotes build script:

#### Location 1: `_load_members()` method
Find this pattern:
```python
persons_files = sorted(CSV_DIR.glob("*-Persons.csv"))
```
Change to:
```python
persons_files = _filter_csv_files(sorted(CSV_DIR.glob("*-Persons.csv")))
```

#### Location 2: `_load_current_members()` method
Find this pattern:
```python
persons_files = sorted(CSV_DIR.glob("*-Persons.csv"))
```
Change to:
```python
persons_files = _filter_csv_files(sorted(CSV_DIR.glob("*-Persons.csv")))
```

**Note**: There are two methods that load `*-Persons.csv`. Make sure you change BOTH of them. `_load_members()` builds the full member roster. `_load_current_members()` determines who is "current" (appears in the most recent CSV within the range).

#### Location 3: `_load_all_csv_data()` method
Find this pattern:
```python
votes_files = sorted(CSV_DIR.glob("*-Votes.csv"))
```
Change to:
```python
votes_files = _filter_csv_files(sorted(CSV_DIR.glob("*-Votes.csv")))
```

### Step 5: Add a Status Message (Optional but Recommended)

In the `run()` method, add a print statement so the build output confirms the filter is active. Find:

```python
print("=" * 60)
print("{City} City Council - Building Website Data")
print("=" * 60)
```

Add after the last print:
```python
if YEAR_RANGE:
    print(f"  Year filter active: {YEAR_RANGE[0]}-{YEAR_RANGE[1]}")
```

### Step 6: Clean Old Generated Data

Before re-running the build, delete all previously generated JSON files to prevent stale data from remaining. Run these commands from the project root:

```bash
# Delete individual detail files
rm -rf frontend/data/votes/
rm -rf frontend/data/meetings/
rm -rf frontend/data/council/

# Delete top-level generated JSON files
rm -f frontend/data/votes.json
rm -f frontend/data/votes-*.json
rm -f frontend/data/meetings.json
rm -f frontend/data/stats.json
rm -f frontend/data/council.json
rm -f frontend/data/alignment.json
rm -f frontend/data/agenda-items.json
```

**Why this matters**: The build script generates `votes/{id}.json` files with sequential IDs starting from 1. Old data may have files like `votes/5000.json` that won't be overwritten by the new build (which might only go up to `votes/2386.json`). These orphaned files would be served by the frontend and show stale data.

### Step 7: Re-run the Build Script

```bash
python3 build_site.py
```

Expected output will show:
- Year filter active message
- Only the filtered quarters being processed (e.g., "Processing 2022-Q1...", "Processing 2022-Q2...", etc.)
- Reduced counts for members, meetings, and votes

### Step 8: Verify the Build

Run these verification checks:

```bash
# Check stats.json for correct date range and counts
cat frontend/data/stats.json | python3 -m json.tool

# Check votes-index.json shows only [2023, 2022]
cat frontend/data/votes-index.json | python3 -m json.tool

# Count generated files
echo "Votes:" && ls frontend/data/votes/*.json | wc -l
echo "Meetings:" && ls frontend/data/meetings/*.json | wc -l
echo "Council:" && ls frontend/data/council/*.json | wc -l

# Check no stale year files exist
ls frontend/data/votes-20*.json
# Should only show votes-2022.json and votes-2023.json
```

**Expected results for 2022-2023 Dallas data**:
| Metric           | Value |
|-----------------|-------|
| Meetings         | 75    |
| Votes            | 2,386 |
| Council members  | 17    |
| Date range start | 2022-01-05 |
| Date range end   | 2023-12-13 |

---

## How It Works (Technical Explanation)

The filter works at the CSV file selection level, not at the row level. The filename convention `{City}-{ST}-{YEAR}-Q{N}-{Type}.csv` embeds the year, so the regex `-(\d{4})-Q\d` extracts it from each filename.

When `YEAR_RANGE = (2022, 2023)`:
- `Dallas-TX-2020-Q1-Votes.csv` -> year 2020 -> **excluded** (2020 < 2022)
- `Dallas-TX-2022-Q1-Votes.csv` -> year 2022 -> **included** (2022 >= 2022 and 2022 <= 2023)
- `Dallas-TX-2025-Q4-Votes.csv` -> year 2025 -> **excluded** (2025 > 2023)

**No CSV files are deleted**. All source data remains on disk. Only the JSON output changes.

The build script handles all downstream effects automatically:
- **Member IDs** are renumbered starting from 1 based on filtered data
- **Meeting IDs** are renumbered starting from 1
- **Vote IDs** are renumbered starting from 1
- **Council member stats** (aye %, participation, dissent) are recomputed from filtered votes only
- **Alignment pairs** are recomputed for members who appear in the filtered data
- **`is_current`** is determined by the most recent Persons CSV within the filtered range
- **`votes-index.json`** lists only years present in the filtered data
- **`votes-{year}.json`** files are only generated for years in the filtered data

---

## Changing the Year Range

To use different years, just change the `YEAR_RANGE` tuple:

```python
# Examples:
YEAR_RANGE = (2022, 2023)   # Two years: 2022 and 2023
YEAR_RANGE = (2023, 2024)   # Two years: 2023 and 2024
YEAR_RANGE = (2020, 2025)   # All six years
YEAR_RANGE = None            # No filter: process ALL available CSVs
```

After changing, repeat Steps 6-8 (clean, rebuild, verify).

---

## Do NOT Modify These Files

The following files require **no changes** for the year filter:
- `frontend/js/api.js` - Dynamically loads whatever JSON exists in data/
- `frontend/*.html` - All HTML pages are data-driven
- `frontend/css/*` - No data dependencies
- `Dallas-TX/*.csv` - Keep all source CSVs (do NOT delete any)
- `frontend/vercel.json` - Deployment config, unaffected
- `frontend/package.json` - No dependencies affected

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `command not found: python` | macOS uses `python3` | Use `python3 build_site.py` |
| Old vote/meeting pages still showing | Stale JSON files in data/ | Re-run Step 6 cleanup, then rebuild |
| `votes-index.json` shows old years | Old `votes-{year}.json` files not deleted | Delete `frontend/data/votes-20*.json` before rebuild |
| `re` not imported | Missing import | Add `import re` to the imports at the top of `build_site.py` |
| Regex doesn't match filenames | Different city naming convention | Adjust regex in `_filter_csv_files()` to match your filename pattern |
| Members appear with 0 votes | Name aliases not covering all variants | Check `NAME_ALIASES` dict covers all name spelling variants in the filtered quarters |

---

## Summary of All Changes

**Files edited**: 1 (`build_site.py`)

**Changes made**:
1. Added `YEAR_RANGE = (2022, 2023)` config constant
2. Added `_filter_csv_files()` function (~10 lines)
3. Wrapped 3 `.glob()` calls with `_filter_csv_files()`
4. Added optional status print in `run()` method

**Total lines changed**: ~15 lines added, 3 lines modified

**Files regenerated**: All JSON files in `frontend/data/` (deleted and rebuilt)

**Files NOT changed**: All CSV source files, all frontend HTML/JS/CSS
