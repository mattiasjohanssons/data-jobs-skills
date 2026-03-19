from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from src.constants import CACHE_DIR, JOBSEARCH_BASE_URL


@dataclass(frozen=True)
class JobSearchRequest:
    query: str
    limit: int = 200
    offset: int = 0

    def to_params(self) -> dict[str, Any]:
        # JobSearch API uses `q`, `limit`, `offset` for search pagination.
        return {
            "q": self.query,
            "limit": int(self.limit),
            "offset": int(self.offset),
        }


def _stable_cache_key(url: str, params: dict[str, Any]) -> str:
    payload = {"url": url, "params": params}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _cache_path(cache_dir: str, cache_key: str) -> Path:
    return Path(cache_dir) / f"{cache_key}.json"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def search_jobs(
    req: JobSearchRequest,
    *,
    base_url: str = JOBSEARCH_BASE_URL,
    cache_dir: str = CACHE_DIR,
    use_cache: bool = True,
    timeout_s: int = 25,
) -> dict[str, Any]:
    """
    Fetch a single page of job postings from JobSearch API.

    Returns the parsed JSON response (dict).
    """
    params = req.to_params()
    cache_key = _stable_cache_key(base_url, params)
    cache_file = _cache_path(cache_dir, cache_key)

    if use_cache and cache_file.exists():
        payload = _read_json(cache_file)
        payload["_cache"] = {"hit": True, "path": str(cache_file)}
        return payload

    resp = requests.get(
        base_url,
        params=params,
        headers={"Accept": "application/json"},
        timeout=timeout_s,
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # Provide a helpful error message with a small response snippet.
        snippet = resp.text[:400]
        raise RuntimeError(f"JobSearch API request failed: {e}. Response: {snippet}") from e

    payload = resp.json()
    payload["_cache"] = {"hit": False, "path": str(cache_file)}
    _write_json(cache_file, payload)
    return payload

