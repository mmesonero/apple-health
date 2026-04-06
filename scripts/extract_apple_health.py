import argparse
import csv
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from xml.etree.ElementTree import iterparse


CALORIES_TYPE = "HKQuantityTypeIdentifierDietaryEnergyConsumed"
WEIGHT_TYPE = "HKQuantityTypeIdentifierBodyMass"


def _parse_dt(s: str) -> datetime:
    # Apple Health export dates look like: "2026-04-06 08:22:11 +0000"
    # Some exports may omit timezone; treat as UTC in that case.
    s = s.strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)


def _day_key(dt: datetime) -> str:
    # Normalize to local date as encoded in the timestamp; use YYYY-MM-DD.
    return dt.date().isoformat()


@dataclass(frozen=True)
class WeightPoint:
    day: str
    end_dt: datetime
    kg: float


def extract_daily(input_xml: str):
    calories_by_day = defaultdict(float)
    weight_candidates: list[WeightPoint] = []

    context = iterparse(input_xml, events=("end",))
    for event, elem in context:
        if elem.tag != "Record":
            continue

        r_type = elem.attrib.get("type")
        if r_type not in (CALORIES_TYPE, WEIGHT_TYPE):
            elem.clear()
            continue

        start_s = elem.attrib.get("startDate") or ""
        end_s = elem.attrib.get("endDate") or start_s
        val_s = elem.attrib.get("value")
        unit = elem.attrib.get("unit")

        if not val_s:
            elem.clear()
            continue

        try:
            value = float(val_s)
        except ValueError:
            elem.clear()
            continue

        start_dt = _parse_dt(start_s) if start_s else None
        end_dt = _parse_dt(end_s) if end_s else (start_dt or datetime.now(timezone.utc))

        if r_type == CALORIES_TYPE:
            # Expect kcal; if not, still sum numerically.
            day = _day_key(start_dt or end_dt)
            calories_by_day[day] += value

        elif r_type == WEIGHT_TYPE:
            # Expect kg; if lb, convert.
            if unit == "lb":
                value = value * 0.45359237
            day = _day_key(end_dt)
            weight_candidates.append(WeightPoint(day=day, end_dt=end_dt, kg=value))

        elem.clear()

    # Choose the latest weight measurement per day.
    weight_by_day: dict[str, float] = {}
    latest_dt_by_day: dict[str, datetime] = {}
    for p in weight_candidates:
        prev = latest_dt_by_day.get(p.day)
        if prev is None or p.end_dt > prev:
            latest_dt_by_day[p.day] = p.end_dt
            weight_by_day[p.day] = p.kg

    return calories_by_day, weight_by_day


def write_csvs(outdir: str, calories_by_day: dict[str, float], weight_by_day: dict[str, float]):
    os.makedirs(outdir, exist_ok=True)

    cal_path = os.path.join(outdir, "calories_daily.csv")
    w_path = os.path.join(outdir, "weight_daily.csv")
    combined_path = os.path.join(outdir, "daily_health.csv")

    days = sorted(set(calories_by_day.keys()) | set(weight_by_day.keys()))

    with open(cal_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "calories_kcal"])
        for d in sorted(calories_by_day.keys()):
            w.writerow([d, f"{calories_by_day[d]:.2f}"])

    with open(w_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "weight_kg"])
        for d in sorted(weight_by_day.keys()):
            w.writerow([d, f"{weight_by_day[d]:.3f}"])

    with open(combined_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "calories_kcal", "weight_kg"])
        for d in days:
            cal = calories_by_day.get(d)
            kg = weight_by_day.get(d)
            w.writerow(
                [
                    d,
                    "" if cal is None else f"{cal:.2f}",
                    "" if kg is None else f"{kg:.3f}",
                ]
            )

    return cal_path, w_path, combined_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to Apple Health export.xml")
    ap.add_argument("--outdir", default="outputs", help="Output directory (default: outputs)")
    args = ap.parse_args()

    calories_by_day, weight_by_day = extract_daily(args.input)
    cal_path, w_path, combined_path = write_csvs(args.outdir, calories_by_day, weight_by_day)

    print("Wrote:")
    print(f"- {cal_path}")
    print(f"- {w_path}")
    print(f"- {combined_path}")
    print()
    print(f"Days with calories: {len(calories_by_day)}")
    print(f"Days with weight:   {len(weight_by_day)}")


if __name__ == "__main__":
    main()

