#!/usr/bin/env python3
"""Shared Spotify helper utilities."""
from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

CONFIG_DIR = Path.home() / ".config" / "spotify-resolver"
CONFIG_FILE = CONFIG_DIR / "config.json"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"


def load_config(config_file: Optional[Path] = None) -> Dict[str, Any]:
    default = {
        "timeout": 10,
        "max_retries": 3,
        "retry_delay": 1,
        "default_market": "US",
        "log_level": "INFO",
        "client_id": None,
        "client_secret": None,
        "user_agent": "Spotify Resolver"
    }
    path = config_file or CONFIG_FILE
    if path.exists():
        try:
            with path.open() as fh:
                default.update(json.load(fh))
        except (IOError, json.JSONDecodeError) as exc:
            logging.warning("Could not read config: %s", exc)
    return default


def create_session(config: Dict[str, Any]) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=config.get("max_retries", 3),
        backoff_factor=config.get("retry_delay", 1),
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": config.get("user_agent"),
        "Accept": "application/json"
    })
    return session


def get_spotify_token(session: requests.Session, client_id: str, client_secret: str) -> Optional[str]:
    creds = f"{client_id}:{client_secret}"
    b64 = base64.b64encode(creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    resp = None
    try:
        resp = session.post(SPOTIFY_TOKEN_URL, headers=headers, data={"grant_type": "client_credentials"}, timeout=10)
        resp.raise_for_status()
        return resp.json().get("access_token")
    except requests.RequestException as exc:
        logging.error("Token error: %s", exc)
        if resp is not None:
            logging.error("Token response: %s", resp.text[:400])
        return None
