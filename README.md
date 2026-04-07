## apple_health

Extract **daily calories consumed** and **daily weight** from an Apple Health export (`export.xml`).

Also supports:
- Syncing **today's** calories + weight into **Google Sheets**
- Telegram alerts if today's weight didn't arrive
- Telegram reminders on **Mondays and Fridays**

### What you get

- `outputs/calories_daily.csv`: total calories consumed per day
- `outputs/weight_daily.csv`: weight per day (latest measurement that day)
- `outputs/daily_health.csv`: combined calories + weight per day

### How to export Apple Health data

On your iPhone: **Health** → profile icon → **Export All Health Data**.
Unzip the export and locate:

- `apple_health_export/export.xml`

### Run locally

Requires Python 3.11+.

```bash
python scripts/extract_apple_health.py --input "path/to/export.xml" --outdir outputs
```

### Google Sheets + Telegram automation

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the repo root (or pass `--env path/to/.env`):

```bash
# Required
APPLE_HEALTH_EXPORT_XML=C:\path\to\export.xml
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_WORKSHEET=Daily
GOOGLE_SERVICE_ACCOUNT_JSON=C:\path\to\service-account.json
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_CHAT_ID=123456789

# Optional
OUTDIR=outputs
```

Expected Google Sheet columns:
- Column A: `date` (YYYY-MM-DD)
- Column B: `calories_kcal`
- Column C: `weight_kg`

Run the daily job (sync + optional missing-weight alert):

```bash
python scripts/daily_job.py --alert-if-missing-weight
```

Run the reminder job (sends only on Mon/Fri):

```bash
python scripts/reminder_job.py
```

### Windows Task Scheduler setup (recommended)

Create two tasks.

**Task 1 (daily 23:55):**
- Trigger: Daily, 23:55
- Action: Start a program
  - Program/script: `python`
  - Add arguments:
    - `C:\apple-health\scripts\daily_job.py --alert-if-missing-weight --env C:\apple-health\.env`
  - Start in:
    - `C:\apple-health`

**Task 2 (Mon/Fri 08:00):**
- Trigger: Weekly → Monday + Friday, 08:00
- Action: Start a program
  - Program/script: `python`
  - Add arguments:
    - `C:\apple-health\scripts\reminder_job.py --env C:\apple-health\.env`
  - Start in:
    - `C:\apple-health`

### Run on GitHub (web)

1. Push this repo to GitHub.
2. In GitHub: **Actions** → **Apple Health Extract** → **Run workflow**
3. Upload your `export.xml` as the workflow input artifact (see workflow notes), or commit it privately (not recommended).
4. Download artifacts: `apple-health-outputs`.

### Notes

- Calories uses Apple Health type: `HKQuantityTypeIdentifierDietaryEnergyConsumed` (unit: `kcal`).
- Weight uses Apple Health type: `HKQuantityTypeIdentifierBodyMass` (unit: `kg`).
- If your export uses different identifiers, tell me and I’ll adjust the mappings.

