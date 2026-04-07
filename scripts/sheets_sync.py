from __future__ import annotations

from typing import Any

import gspread
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _client_from_service_account_json(service_account_json_path: str) -> gspread.Client:
    creds = Credentials.from_service_account_file(service_account_json_path, scopes=SCOPES)
    return gspread.authorize(creds)


def upsert_daily_row(
    *,
    service_account_json_path: str,
    sheet_id: str,
    worksheet_name: str,
    day: str,
    calories_kcal: float | None,
    weight_kg: float | None,
) -> None:
    """
    Ensure a row exists for `day` (YYYY-MM-DD) and set values.

    Sheet format expected:
    - Column A: date (YYYY-MM-DD)
    - Column B: calories_kcal
    - Column C: weight_kg

    Header row is optional; if present, it should be row 1.
    """
    gc = _client_from_service_account_json(service_account_json_path)
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(worksheet_name)

    # Read col A once to find existing row.
    col_a: list[str] = ws.col_values(1)
    existing_row_idx: int | None = None

    for idx, v in enumerate(col_a, start=1):
        if v.strip() == day:
            existing_row_idx = idx
            break

    values: list[list[Any]] = [
        [
            day,
            "" if calories_kcal is None else float(f"{calories_kcal:.2f}"),
            "" if weight_kg is None else float(f"{weight_kg:.3f}"),
        ]
    ]

    if existing_row_idx is None:
        ws.append_rows(values, value_input_option="USER_ENTERED")
        return

    # Update the full A:C range for that row.
    ws.update(f"A{existing_row_idx}:C{existing_row_idx}", values, value_input_option="USER_ENTERED")

