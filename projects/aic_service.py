from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

import httpx
from config import settings

_cache: Dict[str, Tuple[Any, float]] = {}


def _cache_get(key: str) -> Optional[Any]:
    entry = _cache.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.monotonic() > expires_at:
        del _cache[key]
        return None
    return value


def _cache_set(key: str, value: Any, ttl: int) -> None:
    _cache[key] = (value, time.monotonic() + ttl)


async def fetch_artwork(external_id: int) -> Optional[Dict[str, Any]]:
    cache_key = f"artwork:{external_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.aic_base_url}/artworks/{external_id}"
    params = {"fields": "id,title,artist_display,image_id,api_link"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
        except httpx.RequestError:
            return None

    if response.status_code == 404:
        return None
    if response.status_code != 200:
        return None

    data = response.json().get("data")
    if data:
        _cache_set(cache_key, data, settings.aic_cache_ttl_seconds)
    return data


def build_image_url(image_id: Optional[str]) -> Optional[str]:
    if not image_id:
        return None
    return f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"


async def validate_and_enrich(external_id: int) -> Dict[str, Any]:
    data = await fetch_artwork(external_id)
    if data is None:
        raise ValueError(f"Artwork with id={external_id} not found in Art Institute of Chicago API.")
    return {
        "external_id": external_id,
        "title": data.get("title"),
        "artist": data.get("artist_display"),
        "image_url": build_image_url(data.get("image_id")),
    }
