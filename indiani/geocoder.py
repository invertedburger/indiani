"""Geocode restaurants to map coordinates via Nominatim, with an on-disk cache.

Each restaurant is keyed by its name. The cache (results/coords.json) means we
only hit Nominatim for restaurants we haven't seen before, so adding one entry
to restaurants.json costs a single request. Geocoding query precedence:
explicit 'geocode' field -> 'address' -> '<name> Brno Czech Republic'.
"""
import os
import json
import time
import requests
from indiani.config import RESULTS_DIR

NOMINATIM = 'https://nominatim.openstreetmap.org/search'


def geocode(restaurants):
    coords_file = os.path.join(RESULTS_DIR, 'coords.json')
    cache = {}
    if os.path.exists(coords_file):
        with open(coords_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)

    changed = False
    for r in restaurants:
        name = r['name']

        if r.get('coords'):  # explicit override in restaurants.json
            cache[name] = r['coords']
            changed = True
            continue

        if name in cache:
            r['coords'] = cache[name]
            continue

        query = r.get('geocode') or r.get('address') or f'{name} Brno Czech Republic'
        if 'brno' not in query.lower():
            query += ' Brno Czech Republic'
        print(f'Geocoding: {query} ...')
        try:
            resp = requests.get(
                NOMINATIM,
                params={'q': query, 'format': 'json', 'limit': 1},
                headers={'User-Agent': 'Indiani/1.0 (indiani.ivomartisek.cz)'},
                timeout=10,
            )
            data = resp.json()
            if data:
                coords = [float(data[0]['lat']), float(data[0]['lon'])]
                cache[name] = coords
                r['coords'] = coords
                changed = True
                print(f'  -> {coords}')
            else:
                print('  -> not found')
        except Exception as e:
            print(f'  -> error: {e}')
        time.sleep(1)  # Nominatim usage policy: max 1 req/s

    if changed:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(coords_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    return restaurants
