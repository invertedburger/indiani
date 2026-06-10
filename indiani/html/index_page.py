"""Generates results/index.html — hero banner, searchable restaurant cards and a
Leaflet map of every Indian restaurant in Brno."""
import json
from urllib.parse import quote_plus
from indiani.html.assets import DARK_INIT, TAILWIND, THEME_CSS, THEME_JS
from indiani.config import SITE_TITLE, SITE_TAGLINE, HERO_IMAGE, MAP_CENTER, MAP_ZOOM


def _card(r, i):
    name = r['name']
    address = r.get('address', '')
    url = r.get('url', '')
    price = r.get('price', '')
    note = r.get('note', '')
    tags = r.get('tags', [])

    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    if tags_html:
        tags_html = f'<div class="flex flex-wrap gap-1.5 mt-2">{tags_html}</div>'

    maps_q = quote_plus(f'{name} {address}')
    links = (
        f'<a href="https://www.google.com/maps/search/?api=1&query={maps_q}" target="_blank" rel="noopener" '
        f'class="text-xs font-medium text-saffron hover:text-masala dark:text-gold dark:hover:text-orange-300">📍 Mapy</a>'
    )
    if url:
        links += (
            f'<a href="{url}" target="_blank" rel="noopener" '
            f'class="text-xs font-medium text-saffron hover:text-masala dark:text-gold dark:hover:text-orange-300">🌐 Web ↗</a>'
        )

    price_html = (
        f'<span class="shrink-0 text-sm font-semibold text-amber-600 dark:text-gold">{price}</span>'
        if price else ''
    )

    haystack = ' '.join([name, address, note] + tags).lower()

    return f"""
      <div data-search="{haystack}"
           class="anim-card card bg-white dark:bg-[#241a13] rounded-2xl shadow-sm border border-orange-100 dark:border-orange-900/40 flex flex-col"
           style="animation-delay:{i * 70}ms">
        <div class="px-5 pt-5 pb-4 flex flex-col gap-1 flex-1">
          <div class="flex items-start justify-between gap-3">
            <h3 class="font-bold text-gray-800 dark:text-orange-50 leading-tight">{name}</h3>
            {price_html}
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400">{address}</p>
          {f'<p class="text-sm text-gray-600 dark:text-gray-300 mt-1">{note}</p>' if note else ''}
          {tags_html}
        </div>
        <div class="px-5 py-3 border-t border-orange-50 dark:border-orange-900/30 flex items-center gap-4">
          {links}
        </div>
      </div>"""


def generate(restaurants, timestamp):
    cards_html = ''.join(_card(r, i) for i, r in enumerate(restaurants))

    with_coords = [r for r in restaurants if r.get('coords')]
    markers_js = json.dumps([
        {
            'n': r['name'],
            'a': r.get('address', ''),
            'u': r.get('url', ''),
            'lat': r['coords'][0],
            'lng': r['coords'][1],
        }
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

  <header class="hero h-56 sm:h-72" style="background-image:url('{HERO_IMAGE}')">
    <div class="hero-inner max-w-3xl mx-auto h-full px-4 flex items-start justify-end pt-4">
      <button id="themeBtn" title="Přepnout motiv"
              class="w-9 h-9 flex items-center justify-center rounded-full bg-black/30 text-white backdrop-blur hover:bg-black/50 transition-colors"></button>
    </div>
  </header>
  <div class="mandala-divider"></div>

  <main class="max-w-3xl mx-auto px-4 -mt-2">
    <div class="pt-6 pb-2">
      <h1 class="text-3xl font-extrabold text-masala dark:text-gold tracking-tight">{SITE_TITLE}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-1">{SITE_TAGLINE}</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{count} restaurací &middot; klikni na pin pro detail</p>
    </div>

    <section class="mb-6">
      <div id="map" class="rounded-2xl overflow-hidden border border-orange-100 dark:border-orange-900/40 shadow-sm" style="height:340px"></div>
    </section>

    <div class="mb-4">
      <input id="search" type="search" placeholder="🔍 Hledat restauraci, jídlo, čtvrť…"
             class="w-full px-4 py-2.5 rounded-xl border border-orange-200 dark:border-orange-900/50 bg-white dark:bg-[#241a13] text-gray-800 dark:text-orange-50 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-saffron"/>
    </div>

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

    (function() {{
      const lt = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{attribution:'&copy; OSM &copy; CARTO', maxZoom:19}});
      const dt = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',  {{attribution:'&copy; OSM &copy; CARTO', maxZoom:19}});
      const map = L.map('map').setView([{MAP_CENTER[0]}, {MAP_CENTER[1]}], {MAP_ZOOM});
      let tile = document.documentElement.classList.contains('dark') ? dt : lt;
      tile.addTo(map);
      new MutationObserver(() => {{
        const nd = document.documentElement.classList.contains('dark');
        map.removeLayer(tile); tile = nd ? dt : lt; tile.addTo(map);
      }}).observe(document.documentElement, {{attributes:true, attributeFilter:['class']}});

      const icon = L.divIcon({{
        className: '',
        html: '<div style="background:#ea580c;color:#fff;border-radius:50% 50% 50% 0;transform:rotate(-45deg);width:32px;height:32px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,.35);border:2px solid #fff"><span style="transform:rotate(45deg);font-size:15px">🍛</span></div>',
        iconSize:[32,32], iconAnchor:[16,32], popupAnchor:[0,-30]
      }});

      const rs = {markers_js};
      rs.forEach(r => {{
        const web = r.u ? '<br><a href="'+r.u+'" target="_blank" style="color:#ea580c;font-size:12px">🌐 Web ↗</a>' : '';
        L.marker([r.lat, r.lng], {{icon}}).addTo(map)
          .bindPopup('<b style="font-size:13px">'+r.n+'</b><br><span style="font-size:11px;color:#666">'+r.a+'</span>'+web);
      }});
      if (rs.length) map.fitBounds(rs.map(r => [r.lat, r.lng]), {{padding:[40,40], maxZoom:15}});
    }})();
  </script>
</body>
</html>"""
