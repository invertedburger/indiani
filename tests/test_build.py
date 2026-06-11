"""Build the site and validate the generated HTML, especially that every map
link points at the restaurant's exact coordinates (the 'weird map link' guard)."""
import os
import re
import pytest
from indiani.builder import build

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'results', 'index.html')


@pytest.fixture(scope='module')
def built():
    restaurants = build()  # geocode uses results/coords.json cache (offline)
    with open(HTML, encoding='utf-8') as f:
        return restaurants, f.read()


def test_core_elements(built):
    _, html = built
    for token in ('id="map"', 'id="search"', 'id="cards-grid"', 'ayce.png', 'hero.jpg'):
        assert token in html, token


def test_card_count(built):
    restaurants, html = built
    assert html.count('data-attrs=') == len(restaurants)


def test_ayce_sticker_count(built):
    restaurants, html = built
    expected = sum(1 for r in restaurants if 'ayce' in r.get('attrs', []))
    assert html.count('class="ayce-sticker"') == expected


def test_filter_chips_only_known(built):
    _, html = built
    facets = set(re.findall(r'data-facet="([^"]*)"', html))
    assert facets == {'', '__top', 'ayce'}, facets


def test_map_links_point_to_coords(built):
    """Every geocoded restaurant must have a Google Maps link to its lat,lng."""
    restaurants, html = built
    for r in restaurants:
        if r.get('coords'):
            lat, lng = r['coords']
            assert f'query={lat}%2C{lng}' in html, f"map link not at coords: {r['name']}"


def test_map_links_wellformed(built):
    _, html = built
    queries = re.findall(r'https://www\.google\.com/maps/search/\?api=1&query=([^"]+)', html)
    assert queries, "no map links found"
    for q in queries:
        assert q.strip(), "empty map query"


def test_web_links_present(built):
    restaurants, html = built
    for r in restaurants:
        if r.get('url'):
            assert f'href="{r["url"]}"' in html, f"web link missing: {r['name']}"


def test_sorted_by_rating(built):
    restaurants, _ = built
    ratings = [r.get('rating') or 0 for r in restaurants]
    assert ratings == sorted(ratings, reverse=True), "not sorted by rating desc"
