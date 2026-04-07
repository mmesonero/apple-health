from __future__ import annotations

import argparse
from datetime import date

from config import load_settings
from telegram import send_telegram_message


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=None, help="Optional path to .env file")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Send reminder regardless of weekday",
    )
    args = ap.parse_args()

    today = date.today()
    is_mon_or_fri = today.weekday() in (0, 4)  # Mon=0 ... Sun=6

    if not args.force and not is_mon_or_fri:
        return 0

    # Only Telegram variables are required for this job.
    s = load_settings(args.env)
    send_telegram_message(
        s.telegram_bot_token,
        s.telegram_chat_id,
        "Recuerda pesarte hoy.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

