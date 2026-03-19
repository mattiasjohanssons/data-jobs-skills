from __future__ import annotations

from typing import Any

import pandas as pd


def _get(obj: Any, path: str, default: Any = None) -> Any:
    """
    Safe getter for nested dict paths like "description.text" or "employer.name".
    """
    cur: Any = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def hits_to_dataframe(hits: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Convert JobSearch API `hits` into a tidy DataFrame with a stable core schema.
    """
    rows: list[dict[str, Any]] = []
    for h in hits:
        rows.append(
            {
                "id": h.get("id"),
                "headline": h.get("headline"),
                "description_text": _get(h, "description.text"),
                "webpage_url": h.get("webpage_url"),
                "publication_date": h.get("publication_date"),
                "application_deadline": h.get("application_deadline"),
                "employer_name": _get(h, "employer.name"),
                "workplace": _get(h, "employer.workplace"),
                "occupation_label": _get(h, "occupation.label"),
                "occupation_group_label": _get(h, "occupation_group.label"),
                "municipality": _get(h, "workplace_address.municipality"),
                "region": _get(h, "workplace_address.region"),
                "country": _get(h, "workplace_address.country"),
            }
        )

    df = pd.DataFrame(rows)

    # Basic cleaning
    if "publication_date" in df.columns:
        df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
    if "application_deadline" in df.columns:
        df["application_deadline"] = pd.to_datetime(df["application_deadline"], errors="coerce")

    for col in ["headline", "description_text", "employer_name"]:
        if col in df.columns:
            df[col] = df[col].astype("string")

    return df

