"""
Bluesky profiles from the public AppView, which needs no account or API key.

People give their Bluesky account in many shapes (a profile URL, `@name`, a bare name, a
DID), so `normalize_handle` reduces each to the actor identifier the API accepts before
`fetch_profiles` looks them up in batches.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Any

from universe_kb.snapshot import Fetcher

GET_PROFILES_URL = "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfiles"
# The `app.bsky.actor.getProfiles` lexicon allows at most 25 actors per call.
MAX_ACTORS_PER_REQUEST = 25
DEFAULT_DOMAIN = ".bsky.social"

_PROFILE_URL = re.compile(r"(?:https?://)?(?:www\.)?bsky\.app/profile/([^/?#]+)", re.IGNORECASE)
# atproto handle syntax: a domain name whose last label starts with a letter.
_LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
_HANDLE = re.compile(rf"(?:{_LABEL}\.)+[a-z](?:[a-z0-9-]{{0,61}}[a-z0-9])?")
_DID = re.compile(r"did:[a-z]+:[A-Za-z0-9._:%-]+")
_PLACEHOLDERS = {"n/a", "na", "none", "null", "-"}


def normalize_handle(raw: str | None) -> tuple[str | None, bool]:
    """
    Reduce a Bluesky account reference to a lowercase handle or a DID, returned as
    `(handle_or_did, assumed_domain)`. A bare name such as `ada` becomes
    `ada.bsky.social` with `assumed_domain` True, because that guess can name someone
    else's account. Placeholders such as `N/A`, and text that is not a valid handle or
    DID, give `(None, False)`.
    """
    text = (raw or "").strip()
    if match := _PROFILE_URL.match(text):
        text = urllib.parse.unquote(match.group(1))
    text = text.removeprefix("@")
    if _DID.fullmatch(text):
        return text, False
    handle = text.lower().rstrip(".")
    if handle in _PLACEHOLDERS:
        return None, False
    assumed = bool(handle) and "." not in handle
    if assumed:
        handle += DEFAULT_DOMAIN
    if not _HANDLE.fullmatch(handle):
        return None, False
    return handle, assumed


def fetch_profiles(fetcher: Fetcher, actors: list[str]) -> dict[str, dict[str, Any] | None]:
    """
    Look up profiles by handle or DID, `MAX_ACTORS_PER_REQUEST` to a request. Each
    requested actor, lowercased, maps to its profile, or to None when the API returned
    nothing for it (no such account, or a handle that no longer resolves). An HTTP error
    propagates, since it does not say which actor in the batch caused it; pass actors
    through `normalize_handle` first so a malformed one cannot fail a batch.
    """
    requested = list(dict.fromkeys(actor.lower() for actor in actors))
    found: dict[str, dict[str, Any]] = {}
    for start in range(0, len(requested), MAX_ACTORS_PER_REQUEST):
        batch = requested[start : start + MAX_ACTORS_PER_REQUEST]
        query = urllib.parse.urlencode([("actors", actor) for actor in batch])
        data = fetcher.json("GET", f"{GET_PROFILES_URL}?{query}")
        for profile in data.get("profiles", []):
            record = _profile_record(profile)
            for key in (record["did"], record["handle"]):
                if key:
                    found[key.lower()] = record
    return {actor: found.get(actor) for actor in requested}


def _profile_record(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "did": profile.get("did"),
        "handle": profile.get("handle"),
        "display_name": profile.get("displayName") or None,
        "description": profile.get("description") or None,
        "followers": profile.get("followersCount"),
        "follows": profile.get("followsCount"),
        "posts": profile.get("postsCount"),
        "created_at": profile.get("createdAt"),
        "avatar": profile.get("avatar"),
    }
