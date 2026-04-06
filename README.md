## apple_health

Extract **daily calories consumed** and **daily weight** from an Apple Health export (`export.xml`).

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

### Run on GitHub (web)

1. Push this repo to GitHub.
2. In GitHub: **Actions** → **Apple Health Extract** → **Run workflow**
3. Upload your `export.xml` as the workflow input artifact (see workflow notes), or commit it privately (not recommended).
4. Download artifacts: `apple-health-outputs`.

### Notes

- Calories uses Apple Health type: `HKQuantityTypeIdentifierDietaryEnergyConsumed` (unit: `kcal`).
- Weight uses Apple Health type: `HKQuantityTypeIdentifierBodyMass` (unit: `kg`).
- If your export uses different identifiers, tell me and I’ll adjust the mappings.

