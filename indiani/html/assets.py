"""Shared inline CSS and JS. No build step — Tailwind via CDN plus a small block
of custom CSS for the warm "Indian spice" palette and the hero banner."""

# Apply theme before paint to avoid a flash. Dark is the default; light only when
# the user has explicitly chosen it.
DARK_INIT = (
    "<script>if(localStorage.getItem('theme')!=='light')"
    "document.documentElement.classList.add('dark');</script>"
)

TAILWIND = (
    "<script src=\"https://cdn.tailwindcss.com\"></script>\n"
    "  <script>tailwind.config={darkMode:'class',theme:{extend:{colors:{"
    "saffron:'#ea580c',curry:'#b45309',masala:'#9a3412',gold:'#f59e0b'}}}}</script>"
)

# Custom CSS: hero banner, mandala divider, card hover, tag chips, marker pulse.
THEME_CSS = """<style>
    body { font-family: ui-sans-serif, system-ui, 'Segoe UI', sans-serif; }
    .tag {
      display: inline-block; padding: 2px 9px; border-radius: 9999px;
      font-size: 11px; font-weight: 600;
      background: #fed7aa; color: #9a3412;
    }
    .dark .tag { background: rgba(154,52,18,.35); color: #fdba74; }
    .card {
      transition: box-shadow .2s ease, transform .2s ease, border-color .2s ease;
    }
    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(154,52,18,.18);
      border-color: #fdba74;
    }
    .dark .card:hover { border-color: #9a3412; box-shadow: 0 8px 24px rgba(0,0,0,.5); }
    @keyframes fadeUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
    .anim-card { animation: fadeUp .4s ease both; }
    .mandala-divider {
      height: 6px;
      background: repeating-linear-gradient(90deg,#ea580c 0,#ea580c 10px,#f59e0b 10px,#f59e0b 20px,#b45309 20px,#b45309 30px);
      opacity: .85;
    }
    .leaflet-popup-content-wrapper { border-radius: 12px; }

    /* Filter chips */
    .chip {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 6px 12px; border-radius: 9999px; font-size: 13px; font-weight: 600;
      cursor: pointer; user-select: none; white-space: nowrap;
      border: 1px solid transparent; transition: all .15s ease;
    }
    .chip-off { background: #fff; color: #9a3412; border-color: #fed7aa; }
    .dark .chip-off { background: #241a13; color: #fdba74; border-color: #7c2d12; }
    .chip-off:hover { background: #fff7ed; }
    .dark .chip-off:hover { background: #2e2018; }
    .chip-on { background: #ea580c; color: #fff; border-color: #ea580c; box-shadow: 0 2px 8px rgba(234,88,12,.4); }
    .chip:active { transform: scale(.95); }

    /* Facet badge pill on a card */
    .fbadge {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;
    }
    /* Rating badge */
    .rating {
      display: inline-flex; align-items: center; gap: 3px;
      font-size: 12px; font-weight: 700; color: #b45309;
    }
    .dark .rating { color: #fbbf24; }
    /* Distance label (filled in by geolocation) */
    .dist { font-size: 11px; font-weight: 600; color: #ea580c; }
    .dark .dist { color: #fdba74; }

    /* All-you-can-eat laughing-Buddha sticker, top-right corner of a card */
    .ayce-sticker {
      position: absolute; top: -16px; right: -12px; width: 92px; height: 92px;
      background-size: contain; background-repeat: no-repeat; background-position: center;
      filter: drop-shadow(0 3px 7px rgba(0,0,0,.5));
      transform: rotate(8deg); pointer-events: none;
    }
    .price-badge { background: #fde68a; color: #92400e; }
    .dark .price-badge { background: rgba(180,83,9,.45); color: #fde68a; }
  </style>"""

THEME_JS = """
    const themeBtn = document.getElementById('themeBtn');
    function _updateThemeBtn() {
      themeBtn.textContent = document.documentElement.classList.contains('dark') ? '☀' : '☾';
    }
    themeBtn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.contains('dark');
      localStorage.setItem('theme', isDark ? 'light' : 'dark');
      document.documentElement.classList.toggle('dark', !isDark);
      _updateThemeBtn();
    });
    _updateThemeBtn();
"""
