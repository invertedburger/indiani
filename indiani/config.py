"""Loads config.json + secrets.json and exports settings as module constants.

secrets.json holds FTP credentials and is never committed. All FTP fields may be
left empty to skip the upload (GitHub Pages is the primary deploy target).
"""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, default=None):
    path = os.path.join(_ROOT, name)
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


_config = _load('config.json')
_secrets = _load('secrets.json')

SITE_TITLE   = _config.get('site_title', 'Indiáni v Brně')
SITE_TAGLINE = _config.get('site_tagline', 'Indické restaurace v Brně na jednom místě')
DOMAIN       = _config.get('domain', 'indiani.ivomartisek.cz')
DATA_FILE    = _config.get('data_file', 'restaurants.json')
RESULTS_DIR  = os.path.join(_ROOT, _config.get('results_dir', 'results'))
ASSETS_DIR   = os.path.join(_ROOT, _config.get('assets_dir', 'assets'))
HERO_IMAGE   = _config.get('hero_image', 'hero.jpg')
MAP_CENTER   = _config.get('map_center', [49.1951, 16.6068])
MAP_ZOOM     = _config.get('map_zoom', 13)

ROOT = _ROOT

# FTP (optional)
FTP_HOST = _secrets.get('ftp_host', '')
FTP_USER = _secrets.get('ftp_user', '')
FTP_PASS = _secrets.get('ftp_pass', '')
FTP_DIR  = _secrets.get('ftp_dir', '')


def load_restaurants():
    data = _load(DATA_FILE, {'restaurants': []})
    return data.get('restaurants', [])
