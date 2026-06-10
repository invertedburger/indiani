"""Build pipeline: load data -> geocode -> render index.html -> copy assets -> FTP.

There is no scraping or AI here — the restaurant list is curated in
restaurants.json, so a build is fast and deterministic.
"""
import os
import shutil
from datetime import datetime

from indiani.config import (
    RESULTS_DIR, ASSETS_DIR, DOMAIN, load_restaurants,
)
from indiani.geocoder import geocode
from indiani.html import index_page
from indiani import ftp


def build():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    restaurants = load_restaurants()
    print(f'Loaded {len(restaurants)} restaurants')

    restaurants = geocode(restaurants)

    # Default order: best rated first; unrated (null) fall to the bottom.
    restaurants.sort(key=lambda r: r.get('rating') or 0, reverse=True)

    timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
    html = index_page.generate(restaurants, timestamp)
    index_path = os.path.join(RESULTS_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {index_path}')

    # Copy image assets (hero, stickers) next to index.html so Pages/FTP serve them.
    if os.path.isdir(ASSETS_DIR):
        for name in os.listdir(ASSETS_DIR):
            if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif')):
                shutil.copy(os.path.join(ASSETS_DIR, name), os.path.join(RESULTS_DIR, name))

    # CNAME for GitHub Pages custom subdomain.
    with open(os.path.join(RESULTS_DIR, 'CNAME'), 'w', encoding='utf-8') as f:
        f.write(DOMAIN + '\n')

    # Optional FTP upload (no-op when ftp_host is empty).
    ftp.upload_dir(RESULTS_DIR)

    print('Done.')
    return restaurants
