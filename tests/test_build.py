"""Build the site and validate the generated HTML, especially that every map
link points at the restaurant's exact coordinates (the 'weird map link' guard)."""
import os
import re
import pytest
from indiani.builder import build
from indiani.facets import FACETS, FACET_ORDER

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


def _expected_facets(restaurants):
    """Chips the page should render: the reset chip, the rating chip, and one
    per known facet that actually occurs in the data."""
    present = {k for r in restaurants for k in r.get('attrs', [])}
    return {'', '__top'} | (present & set(FACET_ORDER))


def test_filter_chips_only_known(built):
    restaurants, html = built
    facets = set(re.findall(r'data-facet="([^"]*)"', html))
    assert facets == _expected_facets(restaurants), facets


def test_all_data_facets_are_rendered(built):
    """Every facet used in restaurants.json must exist in facets.py, otherwise
    the chip silently never appears (lunch and delivery were dead this way)."""
    restaurants, _ = built
    used = {k for r in restaurants for k in r.get('attrs', [])}
    assert used <= set(FACETS), f'facets in data but not in facets.py: {used - set(FACETS)}'


def test_notes_rendered_and_searchable(built):
    """The curated note must reach both the card and the search haystack."""
    restaurants, html = built
    assert html.count('class="note') == sum(1 for r in restaurants if r.get('note'))
    haystacks = ' '.join(re.findall(r'data-search="([^"]*)"', html))
    assert 'kralovo pole' in haystacks, 'district from note missing in haystack'
    assert 'krenova' in haystacks, 'haystack is not diacritics-folded'


def test_map_links_point_to_coords(built):
    """Every geocoded restaurant must have a Google Maps link to its lat,lng."""
    restaurants, html = built
    for r in restaurants:
        if r.get('coords'):
            lat, lng = r['coords']
            assert f'query={lat}%2C{lng}' in html, f"map link not at coords: {r['name']}"


def test_map_links_wellformed(built):
    _, html = built
    queries = re.findall(r'https://www\.google\.com/maps/search/\?api=1&amp;query=([^"]+)', html)
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


def test_easter_egg_present(built):
    """Kód iddqd a jeho styly musí být ve vygenerované stránce."""
    _, html = built
    for token in ('egg-drop', 'egg-toast', "CODE = 'iddqd'", '@keyframes eggFall'):
        assert token in html, token


def test_easter_egg_does_not_add_chips(built):
    """Easter egg nesmí do filtrů přidat vlastní facetu."""
    restaurants, html = built
    facets = set(re.findall(r'data-facet="([^"]*)"', html))
    assert facets == _expected_facets(restaurants), facets
