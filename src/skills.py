from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compile_skill_patterns(skills: dict[str, str | re.Pattern[str]]) -> dict[str, re.Pattern[str]]:
    compiled: dict[str, re.Pattern[str]] = {}
    for name, pat in skills.items():
        if isinstance(pat, re.Pattern):
            compiled[name] = pat
        else:
            compiled[name] = re.compile(pat, flags=re.IGNORECASE)
    return compiled


def extract_skills_from_text(
    text: str, *, skill_patterns: dict[str, re.Pattern[str]]
) -> set[str]:
    found: set[str] = set()
    if not text:
        return found
    for skill, pat in skill_patterns.items():
        if pat.search(text):
            found.add(skill)
    return found


def skill_counts(
    df: pd.DataFrame,
    *,
    text_columns: Iterable[str] = ("headline", "description_text"),
    skill_patterns: dict[str, re.Pattern[str]],
) -> pd.DataFrame:
    """
    Returns a DataFrame with columns: skill, mentions, share_of_postings.

    Counts each skill at most once per posting (deduplicated by row).
    """
    if df.empty:
        return pd.DataFrame(columns=["skill", "mentions", "share_of_postings"])

    cols = [c for c in text_columns if c in df.columns]
    if not cols:
        raise ValueError(f"No text columns found. Expected one of: {list(text_columns)}")

    combined = (
        df[cols]
        .astype("string")
        .fillna("")
        .agg(" ".join, axis=1)
        .map(normalize_text)
    )

    mentions: dict[str, int] = {k: 0 for k in skill_patterns.keys()}
    for text in combined.tolist():
        found = extract_skills_from_text(text, skill_patterns=skill_patterns)
        for skill in found:
            mentions[skill] += 1

    out = (
        pd.DataFrame({"skill": list(mentions.keys()), "mentions": list(mentions.values())})
        .query("mentions > 0")
        .sort_values(["mentions", "skill"], ascending=[False, True])
        .reset_index(drop=True)
    )
    out["share_of_postings"] = out["mentions"] / len(df)
    return out

