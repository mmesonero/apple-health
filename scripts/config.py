from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    export_xml_path: str
    outdir: str

    google_sheet_id: str
    google_worksheet: str
    google_service_account_json: str

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

    return Settings(
        export_xml_path=req("APPLE_HEALTH_EXPORT_XML"),
        outdir=os.getenv("OUTDIR", "outputs").strip() or "outputs",
        google_sheet_id=req("GOOGLE_SHEET_ID"),
        google_worksheet=os.getenv("GOOGLE_WORKSHEET", "Daily").strip() or "Daily",
        google_service_account_json=req("GOOGLE_SERVICE_ACCOUNT_JSON"),
        telegram_bot_token=req("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=req("TELEGRAM_CHAT_ID"),
    )

