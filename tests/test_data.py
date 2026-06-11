"""Validate restaurants.json (no build, no network)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWN_ATTRS = {'ayce', 'lunch', 'delivery'}


def load():
    with open(os.path.join(ROOT, 'restaurants.json'), encoding='utf-8') as f:
        return json.load(f)['restaurants']


def test_nonempty():
    assert len(load()) > 0


def test_unique_names():
    names = [r['name'] for r in load()]
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"duplicate names: {dupes}"


def test_required_fields():
    for r in load():
        assert r.get('name'), r
        assert r.get('address'), f"missing address: {r.get('name')}"


def test_rating_range():
    for r in load():
        rt = r.get('rating')
        assert rt is None or (isinstance(rt, (int, float)) and 1.0 <= rt <= 5.0), r['name']


def test_attrs_known():
    for r in load():
        for a in r.get('attrs', []):
            assert a in KNOWN_ATTRS, f"{r['name']}: unknown attr {a}"


def test_url_format():
    for r in load():
        u = r.get('url', '')
        assert u == '' or u.startswith('http'), f"{r['name']}: bad url {u}"
