from __future__ import annotations

import argparse
from datetime import date

from extract_apple_health import extract_daily, write_csvs

from config import load_settings
from sheets_sync import upsert_daily_row
from telegram import send_telegram_message


def _today_key() -> str:
    # Use local date for "did I log weight today" alerts.
    return date.today().isoformat()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=None, help="Optional path to .env file")
    ap.add_argument(
        "--alert-if-missing-weight",
        action="store_true",
        help="Send Telegram alert if today's weight is missing",
    )
    args = ap.parse_args()

    s = load_settings(args.env)

    calories_by_day, weight_by_day = extract_daily(s.export_xml_path)
    write_csvs(s.outdir, calories_by_day, weight_by_day)

    day = _today_key()
    calories = calories_by_day.get(day)
    weight = weight_by_day.get(day)

    upsert_daily_row(
        service_account_json_path=s.google_service_account_json,
        sheet_id=s.google_sheet_id,
        worksheet_name=s.google_worksheet,
        day=day,
        calories_kcal=calories,
        weight_kg=weight,
    )

    if args.alert_if_missing_weight and weight is None:
        send_telegram_message(
            s.telegram_bot_token,
            s.telegram_chat_id,
            f"ALERTA: No veo tu peso de hoy ({day}) en Apple Health. Revisa que la báscula haya sincronizado y que el export esté actualizado.",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
