from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    export_xml_path: str | None
    outdir: str

    google_sheet_id: str | None
    google_worksheet: str | None
    google_service_account_json: str | None

    telegram_bot_token: str
    telegram_chat_id: str


def load_settings(env_path: str | None = None) -> Settings:
    # Load .env if present (local dev / Task Scheduler).
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    def req(name: str) -> str:
        v = os.getenv(name, "").strip()
        if not v:
            raise RuntimeError(f"Missing required env var: {name}")
        return v

    def opt(name: str) -> str | None:
        v = os.getenv(name, "").strip()
        return v or None

    return Settings(
        export_xml_path=opt("APPLE_HEALTH_EXPORT_XML"),
        outdir=os.getenv("OUTDIR", "outputs").strip() or "outputs",
        google_sheet_id=opt("GOOGLE_SHEET_ID"),
        google_worksheet=opt("GOOGLE_WORKSHEET"),
        google_service_account_json=opt("GOOGLE_SERVICE_ACCOUNT_JSON"),
        telegram_bot_token=req("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=req("TELEGRAM_CHAT_ID"),
    )

