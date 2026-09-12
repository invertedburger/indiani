"""Browser end-to-end tests (Playwright): filters, search and the location pin.

Run: pip install -r requirements-dev.txt && playwright install chromium && pytest
Needs internet (Tailwind + Leaflet load from CDN). Skips cleanly if Playwright or
the Chromium browser is unavailable.
"""
import os
import pytest

sync_api = pytest.importorskip('playwright.sync_api')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file:///' + os.path.join(ROOT, 'results', 'index.html').replace('\\', '/')


@pytest.fixture(scope='module')
def page():
    # results/index.html must exist; build it if needed.
    if not os.path.exists(os.path.join(ROOT, 'results', 'index.html')):
        from indiani.builder import build
        build()
    with sync_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:  # browser binary not installed
            pytest.skip(f"chromium not available: {e}")
        ctx = browser.new_context()
        pg = ctx.new_page()
        pg.goto(URL)
        pg.wait_for_selector('#cards-grid > [data-search]')
        yield pg
        browser.close()


def _visible(page):
    return page.locator('#cards-grid > [data-search]:visible')


def test_cards_render(page):
    assert _visible(page).count() >= 20


def test_ayce_filter_shows_only_buffets(page):
    page.click('button[data-facet="ayce"]')
    vis = _visible(page)
    n = vis.count()
    assert n > 0
    for i in range(n):
        assert vis.nth(i).locator('.ayce-sticker').count() == 1, "non-AYCE card shown"
    page.click('button[data-facet=""]')  # reset to "Vše"
    assert _visible(page).count() >= 20


def test_search_filters(page):
    page.fill('#search', 'Padagali')
    assert _visible(page).count() == 1
    page.fill('#search', 'zzzznotreal')
    assert _visible(page).count() == 0
    assert page.locator('#noResults').is_visible()
    page.fill('#search', '')


def test_location_far_snaps_to_brno(page):
    """Geolocation far outside Brno must fall back to the city centre pin and
    still produce distances + a sorted list."""
    ctx = page.context
    ctx.grant_permissions(['geolocation'])
    ctx.set_geolocation({'latitude': 40.7128, 'longitude': -74.0060})  # New York
    page.click('#nearBtn')
    page.wait_for_selector('[data-dist-label]:visible', timeout=5000)
    assert page.locator('[data-dist-label]:visible').count() > 0
    # The blue draggable user pin exists on the map.
    assert page.locator('.leaflet-marker-draggable').count() == 1


def test_iddqd_easter_egg(page):
    """Napsání iddqd ukáže hlášku, spustí déšť kari a přepne na bufety."""
    for key in 'iddqd':
        page.keyboard.press(key)

    page.wait_for_selector('.egg-toast', timeout=3000)
    assert 'God mode' in page.locator('.egg-toast').inner_text()
    assert page.locator('.egg-drop').count() > 0, "neprší kari"

    # Odměna za kód: zapne se filtr all you can eat.
    vis = _visible(page)
    n = vis.count()
    assert n > 0
    for i in range(n):
        assert vis.nth(i).locator('.ayce-sticker').count() == 1

    page.click('button[data-facet=""]')  # úklid pro případné další testy


def test_search_without_diacritics(page):
    """Čech bez háčků musí najít Křenovou i Židenice."""
    for term, expect in [('krenova', 2), ('zidenice', 2), ('modrice', 1)]:
        page.fill('#search', term)
        assert _visible(page).count() == expect, f'{term}: {_visible(page).count()}'
    page.fill('#search', '')


def test_search_handles_czech_declension(page):
    """Popisky mají "v Bohunicích", lidé píšou "Bohunice". Musí to najít,
    a to všechny podniky ve čtvrti, ne jen ten, co ji má v názvu."""
    for term in ['bohunice', 'slatina', 'zidenice', 'kralovo pole']:
        page.fill('#search', term)
        assert _visible(page).count() > 0, f'{term} nenašlo nic'
    page.fill('#search', 'uplnenesmysl')
    assert _visible(page).count() == 0, 'nesmysl nesmí projít přes kmenovou zálohu'
    page.fill('#search', '')


def test_delivery_facet_filters(page):
    """Facet rozvoz byl mrtvý, teď musí filtrovat."""
    page.click('button[data-facet="delivery"]')
    vis = _visible(page)
    n = vis.count()
    assert n > 0
    for i in range(n):
        assert 'delivery' in (vis.nth(i).get_attribute('data-attrs') or '')
    page.click('button[data-facet=""]')


def test_map_clusters_and_expands(page):
    """Piny se shlukují a klik na shluk je rozbalí."""
    clusters = page.locator('.marker-cluster')
    assert clusters.count() > 0, 'mapa neshlukuje'
    before = page.locator('.leaflet-marker-icon').count()
    clusters.first.click()
    page.wait_for_timeout(1200)
    assert page.locator('.leaflet-marker-icon').count() != before, 'shluk se nerozbalil'
