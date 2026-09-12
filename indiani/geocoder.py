"""Geocode restaurants to map coordinates via Nominatim, with an on-disk cache.

The cache (results/coords.json) is keyed by restaurant name and stores the query
that produced the coordinates. That query is the invalidation key: fix a wrong
address and the stored query stops matching, so the pin is re-geocoded instead
of silently staying where it was. (Golden Nepal sat on the parent company's
headquarters for months precisely because a name-only key never noticed.)

Query precedence: explicit 'geocode' -> 'address' -> '<name> Brno Czech Republic'.
"""
import os
import json
import time
import requests
from indiani.config import RESULTS_DIR

NOMINATIM = 'https://nominatim.openstreetmap.org/search'

# Marker for entries whose coordinates came from restaurants.json, not Nominatim.
EXPLICIT = '<explicit coords>'


def build_query(r):
    """The Nominatim query for a restaurant, and its cache-invalidation key."""
    query = r.get('geocode') or r.get('address') or f"{r['name']} Brno Czech Republic"
    if 'brno' not in query.lower():
        query += ' Brno Czech Republic'
    return query


def load_cache(path):
    """Read the cache, upgrading the old flat ``{name: [lat, lng]}`` format.

    Legacy entries carry no query. They are adopted as-is rather than
    re-geocoded (the existing pins were verified), and get stamped with the
    current query on the way through, so the next address change is caught.
    """
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    cache = {}
    for name, value in raw.items():
        if isinstance(value, dict):
            cache[name] = {'coords': value.get('coords'), 'query': value.get('query')}
        else:
            cache[name] = {'coords': value, 'query': None}  # legacy [lat, lng]
    return cache


def _fetch(query):
    resp = requests.get(
        NOMINATIM,
        params={'q': query, 'format': 'json', 'limit': 1},
        headers={'User-Agent': 'Indiani/1.0 (indiani.ivomartisek.cz)'},
        timeout=10,
    )
    data = resp.json()
    if not data:
        return None
    return [float(data[0]['lat']), float(data[0]['lon'])]


def geocode(restaurants):
    coords_file = os.path.join(RESULTS_DIR, 'coords.json')
    cache = load_cache(coords_file)
    before = json.dumps(cache, sort_keys=True, ensure_ascii=False)

    for r in restaurants:
        name = r['name']

        if r.get('coords'):  # explicit override in restaurants.json wins
            cache[name] = {'coords': r['coords'], 'query': EXPLICIT}
            continue

        query = build_query(r)
        hit = cache.get(name)

        if hit and hit.get('coords'):
            stored = hit.get('query')
            if stored is None:  # legacy entry: adopt it and record the query
                cache[name] = {'coords': hit['coords'], 'query': query}
                r['coords'] = hit['coords']
                continue
            if stored == query:
                r['coords'] = hit['coords']
                continue
            print(f'Address changed for "{name}", re-geocoding')

        print(f'Geocoding: {query} ...')
        try:
            coords = _fetch(query)
            if coords:
                cache[name] = {'coords': coords, 'query': query}
                r['coords'] = coords
                print(f'  -> {coords}')
            else:
                print('  -> not found')
        except Exception as e:
            print(f'  -> error: {e}')
        time.sleep(1)  # Nominatim usage policy: max 1 req/s

    # Forget restaurants that are no longer in the data, so the cache doesn't
    # accumulate closed places forever.
    live = {r['name'] for r in restaurants}
    for gone in [k for k in cache if k not in live]:
        del cache[gone]
        print(f'Dropped stale cache entry: {gone}')

    # Write only when something actually changed, so a no-op build leaves the
    # file (and its mtime) alone.
    if json.dumps(cache, sort_keys=True, ensure_ascii=False) != before:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(coords_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    return restaurants
