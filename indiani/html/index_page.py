"""Generates results/index.html: hero banner, filter bar, searchable restaurant
cards (with facet badges, rating and the all-you-can-eat sticker) and a Leaflet
map. Geolocation lets the visitor sort restaurants by distance from where they
are."""
import json
from urllib.parse import quote_plus
from indiani.html.assets import DARK_INIT, TAILWIND, THEME_CSS, THEME_JS
from indiani.facets import FACETS, FACET_ORDER, TOP_RATING
from indiani.config import SITE_TITLE, SITE_TAGLINE, HERO_IMAGE, MAP_CENTER, MAP_ZOOM

AYCE_IMG = 'ayce.png'


def _card(r, i):
    name = r['name']
    address = r.get('address', '')
    url = r.get('url', '')
    price = r.get('price', '')
    note = r.get('note', '')
    tags = r.get('tags', [])
    attrs = r.get('attrs', [])
    rating = r.get('rating')

    has_ayce = 'ayce' in attrs
    sticker = (f'<div class="ayce-sticker" style="background-image:url(\'{AYCE_IMG}\')" '
               f'title="All you can eat"></div>') if has_ayce else ''

    # Facet badges (ayce is shown as the corner sticker, not a pill).
    fbadges = ''
    for k in FACET_ORDER:
        if k in attrs and k != 'ayce' and k in FACETS:
            f = FACETS[k]
            fbadges += f'<span class="fbadge {f["cls"]}">{f["emoji"]} {f["label"]}</span>'
    if has_ayce:
        f = FACETS['ayce']
        fbadges = f'<span class="fbadge {f["cls"]}">{f["emoji"]} {f["label"]}</span>' + fbadges
    # Concrete price (e.g. buffet price) shown as a badge instead of $ symbols.
    price_badge = (
        f'<span class="fbadge price-badge">💰 {price}</span>' if price else ''
    )
    badges = price_badge + fbadges
    fbadges_html = f'<div class="flex flex-wrap gap-1.5 mt-2">{badges}</div>' if badges else ''

    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    if tags_html:
        tags_html = f'<div class="flex flex-wrap gap-1.5 mt-2">{tags_html}</div>'

    rating_html = ''
    if rating:
        reviews_q = quote_plus(f'{name} {address}')
        rating_html = (
            f'<a href="https://www.google.com/maps/search/?api=1&query={reviews_q}" target="_blank" '
            f'rel="noopener" class="rating" title="Hodnocení na Google">⭐ {str(rating).replace(".", ",")}</a>'
        )

    maps_q = quote_plus(f'{name} {address}')
    btn = ('flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 '
           'rounded-xl text-sm font-semibold transition-colors')
    links = (
        f'<a href="https://www.google.com/maps/search/?api=1&query={maps_q}" target="_blank" rel="noopener" '
        f'class="{btn} bg-saffron text-white hover:bg-masala shadow-sm">📍 Mapa</a>'
    )
    if url:
        links += (
            f'<a href="{url}" target="_blank" rel="noopener" '
            f'class="{btn} border border-saffron text-saffron hover:bg-orange-50 dark:hover:bg-orange-900/20">🌐 Web</a>'
        )

    haystack = ' '.join([name, address, note] + tags).lower()
    lat = r['coords'][0] if r.get('coords') else ''
    lng = r['coords'][1] if r.get('coords') else ''

    return f"""
      <div data-search="{haystack}" data-attrs="{' '.join(attrs)}" data-rating="{rating or 0}"
           data-lat="{lat}" data-lng="{lng}"
           class="anim-card card relative bg-white dark:bg-[#241a13] rounded-2xl shadow-sm border border-orange-100 dark:border-orange-900/40 flex flex-col"
           style="animation-delay:{i * 60}ms">
        {sticker}
        <div class="px-5 pt-5 pb-4 flex flex-col gap-1 flex-1">
          <h3 class="font-bold text-gray-800 dark:text-orange-50 leading-tight pr-16">{name}</h3>
          <div class="flex items-center gap-2">
            <p class="text-xs text-gray-500 dark:text-gray-400 flex-1 min-w-0 truncate">{address}</p>
            <span class="dist" data-dist-label style="display:none"></span>
            {rating_html}
          </div>
          {f'<p class="text-sm text-gray-600 dark:text-gray-300 mt-1">{note}</p>' if note else ''}
          {fbadges_html}
          {tags_html}
        </div>
        <div class="px-5 py-3 border-t border-orange-50 dark:border-orange-900/30 flex items-center gap-2">
          {links}
        </div>
      </div>"""


def _filter_bar(restaurants):
    present = {k for r in restaurants for k in r.get('attrs', [])}
    has_rating = any(r.get('rating') for r in restaurants)
    chips = ['<button class="chip chip-on" data-facet="">Vše</button>']
    for k in FACET_ORDER:
        if k in present and k in FACETS:
            f = FACETS[k]
            chips.append(f'<button class="chip chip-off" data-facet="{k}">{f["emoji"]} {f["label"]}</button>')
    if has_rating:
        chips.append(f'<button class="chip chip-off" data-facet="__top">⭐ {str(TOP_RATING).replace(".", ",")}+</button>')
    chips.append('<button id="nearBtn" class="chip chip-off" type="button">📍 Nejblíž u mě</button>')
    return '<div class="flex flex-wrap gap-2 mb-4">' + ''.join(chips) + '</div>'


def generate(restaurants, timestamp):
    cards_html = ''.join(_card(r, i) for i, r in enumerate(restaurants))
    filter_bar = _filter_bar(restaurants)

    with_coords = [r for r in restaurants if r.get('coords')]
    markers_js = json.dumps([
        {'n': r['name'], 'a': r.get('address', ''), 'u': r.get('url', ''),
         'lat': r['coords'][0], 'lng': r['coords'][1]}
        for r in with_coords
    ], ensure_ascii=False)

    count = len(restaurants)

    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{SITE_TITLE}</title>
  <meta name="description" content="{SITE_TAGLINE}">
  {DARK_INIT}
  {TAILWIND}
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  {THEME_CSS}
</head>
<body class="bg-orange-50 dark:bg-[#1c1410] min-h-screen text-gray-800 dark:text-orange-50">

  <header class="max-w-3xl mx-auto px-4 pt-4">
    <div class="relative rounded-2xl overflow-hidden shadow-md">
      <img src="{HERO_IMAGE}" alt="{SITE_TITLE}" class="w-full block">
      <button id="themeBtn" title="Přepnout motiv"
              class="absolute top-3 right-3 w-9 h-9 flex items-center justify-center rounded-full bg-black/35 text-white backdrop-blur hover:bg-black/55 transition-colors"></button>
    </div>
  </header>
  <div class="mandala-divider max-w-3xl mx-auto mt-3 rounded-full"></div>

  <main class="max-w-3xl mx-auto px-4">
    <div class="pt-5 pb-2">
      <h1 class="sr-only">{SITE_TITLE}</h1>
      <p class="text-lg font-semibold text-masala dark:text-gold">{SITE_TAGLINE}</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{count} restaurací &middot; klikni na pin pro detail</p>
    </div>

    <section class="mb-6">
      <div id="map" class="rounded-2xl overflow-hidden border border-orange-100 dark:border-orange-900/40 shadow-sm" style="height:340px"></div>
    </section>

    <div class="mb-3">
      <input id="search" type="search" placeholder="🔍 Hledat restauraci, jídlo, čtvrť…"
             class="w-full px-4 py-2.5 rounded-xl border border-orange-200 dark:border-orange-900/50 bg-white dark:bg-[#241a13] text-gray-800 dark:text-orange-50 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-saffron"/>
    </div>
    {filter_bar}

    <div id="cards-grid" class="grid sm:grid-cols-2 gap-3">
      {cards_html}
    </div>
    <p id="noResults" style="display:none" class="text-center text-gray-400 dark:text-gray-500 py-10">Nic nenalezeno 🥲</p>
  </main>

  <footer class="text-center text-gray-400 dark:text-gray-600 text-xs py-8 mt-6">
    Aktualizováno {timestamp} &middot; indiani.ivomartisek.cz
  </footer>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    {THEME_JS}

    /* ---- Map ---- */
    let _map, _userMarker;
    (function() {{
      const lt = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{attribution:'&copy; OSM &copy; CARTO', maxZoom:19}});
      const _esri = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/';
      const dt = L.layerGroup([
        L.tileLayer(_esri + 'World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{attribution:'&copy; Esri', maxZoom:16}}),
        L.tileLayer(_esri + 'World_Dark_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{maxZoom:16}})
      ]);
      _map = L.map('map').setView([{MAP_CENTER[0]}, {MAP_CENTER[1]}], {MAP_ZOOM});
      let tile = document.documentElement.classList.contains('dark') ? dt : lt;
      tile.addTo(_map);
      new MutationObserver(() => {{
        const nd = document.documentElement.classList.contains('dark');
        _map.removeLayer(tile); tile = nd ? dt : lt; tile.addTo(_map);
      }}).observe(document.documentElement, {{attributes:true, attributeFilter:['class']}});

      const icon = L.divIcon({{
        className: '',
        html: '<div style="background:#ea580c;color:#fff;border-radius:50% 50% 50% 0;transform:rotate(-45deg);width:32px;height:32px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,.35);border:2px solid #fff"><span style="transform:rotate(45deg);font-size:15px">🍛</span></div>',
        iconSize:[32,32], iconAnchor:[16,32], popupAnchor:[0,-30]
      }});
      const rs = {markers_js};
      rs.forEach(r => {{
        const web = r.u ? '<br><a href="'+r.u+'" target="_blank" style="color:#ea580c;font-size:12px">🌐 Web ↗</a>' : '';
        L.marker([r.lat, r.lng], {{icon}}).addTo(_map)
          .bindPopup('<b style="font-size:13px">'+r.n+'</b><br><span style="font-size:11px;color:#666">'+r.a+'</span>'+web);
      }});
      // Fit every pin in view (pins span the centre plus Modřice, Slatina, Královo Pole).
      if (rs.length) _map.fitBounds(rs.map(r => [r.lat, r.lng]), {{padding:[55,55], maxZoom:14}});
    }})();

    /* ---- Filtering: search + facet chips + rating ---- */
    const active = new Set();
    const search = document.getElementById('search');
    const chips = [...document.querySelectorAll('[data-facet]')];

    function applyFilters() {{
      const q = (search.value || '').trim().toLowerCase();
      let shown = 0;
      document.querySelectorAll('[data-search]').forEach(el => {{
        const attrs = (el.dataset.attrs || '').split(' ');
        const rating = parseFloat(el.dataset.rating || '0');
        let ok = el.dataset.search.includes(q);
        active.forEach(f => {{
          if (f === '__top') {{ if (rating < {TOP_RATING}) ok = false; }}
          else if (!attrs.includes(f)) ok = false;
        }});
        el.style.display = ok ? '' : 'none';
        if (ok) shown++;
      }});
      document.getElementById('noResults').style.display = shown ? 'none' : '';
    }}

    function syncChips() {{
      chips.forEach(c => {{
        const f = c.dataset.facet;
        const on = (f === '') ? active.size === 0 : active.has(f);
        c.classList.toggle('chip-on', on);
        c.classList.toggle('chip-off', !on);
      }});
    }}

    chips.forEach(c => c.addEventListener('click', () => {{
      const f = c.dataset.facet;
      if (f === '') active.clear();
      else active.has(f) ? active.delete(f) : active.add(f);
      syncChips();
      applyFilters();
    }}));
    search.addEventListener('input', applyFilters);
    applyFilters();

    /* ---- Distance from the visitor ---- */
    function _haversine(la1, lo1, la2, lo2) {{
      const R = 6371, toRad = x => x * Math.PI / 180;
      const dLa = toRad(la2 - la1), dLo = toRad(lo2 - lo1);
      const a = Math.sin(dLa/2)**2 + Math.cos(toRad(la1)) * Math.cos(toRad(la2)) * Math.sin(dLo/2)**2;
      return 2 * R * Math.asin(Math.sqrt(a));
    }}
    function _fmt(km) {{
      return km < 1 ? Math.round(km * 1000) + ' m' : km.toFixed(1).replace('.', ',') + ' km';
    }}
    const nearBtn = document.getElementById('nearBtn');
    nearBtn.addEventListener('click', () => {{
      if (!navigator.geolocation) {{ alert('Tvůj prohlížeč neumí zjistit polohu.'); return; }}
      nearBtn.textContent = '📍 Zjišťuji…';
      navigator.geolocation.getCurrentPosition(pos => {{
        const ula = pos.coords.latitude, ulo = pos.coords.longitude;
        const cards = [...document.querySelectorAll('#cards-grid > [data-search]')];
        cards.forEach(el => {{
          const la = parseFloat(el.dataset.lat), lo = parseFloat(el.dataset.lng);
          const lbl = el.querySelector('[data-dist-label]');
          if (!isNaN(la) && !isNaN(lo)) {{
            const km = _haversine(ula, ulo, la, lo);
            el.dataset.dist = km;
            lbl.textContent = _fmt(km); lbl.style.display = '';
          }}
        }});
        // Sort cards by distance, nearest first.
        cards.sort((a, b) => (parseFloat(a.dataset.dist) || 1e9) - (parseFloat(b.dataset.dist) || 1e9));
        const grid = document.getElementById('cards-grid');
        cards.forEach(c => grid.appendChild(c));
        // Drop a "you are here" marker and zoom there.
        if (_userMarker) _map.removeLayer(_userMarker);
        _userMarker = L.circleMarker([ula, ulo], {{radius:8, color:'#2563eb', fillColor:'#3b82f6', fillOpacity:1, weight:2}})
          .addTo(_map).bindPopup('Tady jsi');
        _map.setView([ula, ulo], 14);
        nearBtn.textContent = '📍 Seřazeno podle vzdálenosti';
      }}, () => {{
        nearBtn.textContent = '📍 Nejblíž u mě';
        alert('Polohu se nepodařilo zjistit.');
      }});
    }});
  </script>
</body>
</html>"""
