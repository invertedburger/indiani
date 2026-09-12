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

# Custom CSS: mandala divider, card hover, popisky, filtrační chipy,
# shluky pinů na mapě a easter egg.
THEME_CSS = """<style>
    body { font-family: ui-sans-serif, system-ui, 'Segoe UI', sans-serif; }
    /* Popisek na kartě: dva řádky, zbytek se ořízne. Odliší pobočky,
       které mají skoro stejný název (2x Namaskar, 2x Sargam, 5x Satyam). */
    .note {
      font-size: 12px; line-height: 1.45; color: #78716c;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .dark .note { color: #a8a29e; }
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

    /* Shluky pinů. Výchozí styl markerclusteru je modrozelený, tohle ho
       přebarvuje do stejné palety jako špendlíky. */
    .marker-cluster {
      background: rgba(234, 88, 12, .28);
      border-radius: 50%;
      /* Leaflet řadí markery podle zeměpisné šířky, takže samostatný pin může
         skončit nad shlukem a sebrat mu klik. Shluk zastupuje víc podniků,
         patří tedy nahoru. */
      z-index: 650 !important;
    }
    .marker-cluster div {
      background: #ea580c; color: #fff;
      width: 32px; height: 32px; margin-left: 4px; margin-top: 4px;
      border-radius: 50%; border: 2px solid #fff;
      display: flex; align-items: center; justify-content: center;
      font: 700 13px/1 ui-sans-serif, system-ui, 'Segoe UI', sans-serif;
      box-shadow: 0 2px 8px rgba(0,0,0,.35);
    }
    .marker-cluster-medium div { background: #c2410c; }
    .marker-cluster-large div  { background: #9a3412; }

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
    .chip-on { background: #d97746; color: #fff; border-color: #d97746; box-shadow: 0 1px 5px rgba(217,119,70,.35); }
    .chip:active { transform: scale(.95); }

    /* Card action buttons (softer orange than the accent) */
    .btn-act {
      display: inline-flex; align-items: center; justify-content: center; gap: 6px;
      padding: 8px 16px; border-radius: 12px; font-size: 14px; font-weight: 600;
      transition: background .15s ease, border-color .15s ease;
    }
    .btn-map { background: #d97746; color: #fff; }
    .btn-map:hover { background: #c2683b; }
    .btn-web { background: transparent; border: 1px solid #e6b58c; color: #b45309; }
    .dark .btn-web { border-color: #7c4a2d; color: #fdba74; }
    .btn-web:hover { background: rgba(217,119,70,.12); }

    /* Facet badge pill on a card */
    .fbadge {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;
    }
    /* Rating: gold pill so every card has a consistent rating chip. */
    .rating {
      display: inline-flex; align-items: center; gap: 3px;
      padding: 1px 8px; border-radius: 9999px;
      font-size: 12px; font-weight: 700;
      background: #fde68a; color: #92400e;
    }
    .dark .rating { background: rgba(245,158,11,.18); color: #fcd34d; }
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
    .price-badge { background: transparent; border: 1px solid #fbbf24; color: #b45309; }
    .dark .price-badge { border-color: #a16207; color: #fcd34d; }

    /* Easter egg: déšť kari a hláška po napsání iddqd */
    .egg-drop {
      position: fixed; top: -48px; z-index: 9998;
      pointer-events: none; user-select: none;
      animation: eggFall linear forwards;
    }
    @keyframes eggFall {
      to { transform: translateY(106vh) rotate(var(--spin, 360deg)); opacity: .1; }
    }
    .egg-toast {
      position: fixed; left: 50%; bottom: 28px; z-index: 9999;
      padding: 10px 18px; border-radius: 9999px;
      background: #9a3412; color: #fff; font-size: 14px; font-weight: 700;
      box-shadow: 0 6px 24px rgba(0,0,0,.35);
      pointer-events: none; white-space: nowrap;
      animation: eggToast 3.6s ease forwards;
    }
    @keyframes eggToast {
      0%        { opacity: 0; transform: translate(-50%, 14px); }
      12%, 78%  { opacity: 1; transform: translate(-50%, 0); }
      100%      { opacity: 0; transform: translate(-50%, -10px); }
    }
    /* Kdo nechce animace, dostane jen hlášku. */
    @media (prefers-reduced-motion: reduce) {
      .egg-drop { display: none; }
      .egg-toast { animation-duration: 3.6s; }
    }
  </style>"""

# Hledání bez ohledu na diakritiku: "Krenova" najde "Křenovou". Stejná
# normalizace se dělá i v Pythonu nad data-search (index_page._fold).
FOLD_JS = r"""
    const _fold = s => (s || '').normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '').toLowerCase();
"""

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

# Easter egg. Napsání "iddqd" (god mode z Doomu) odemkne "režim all you can
# eat": prší kari a stránka se přepne na bufety. Nesmrtelnost se hodí, když
# chceš jíst donekonečna.
# Žije tady, a ne v index_page.py, protože tohle není f-string a nemusí se
# tedy zdvojovat složené závorky. Spoléhá na Set `active` z filtrování.
EASTER_EGG_JS = """
    (function() {
      const CODE = 'iddqd';
      const FOOD = ['\\u{1F35B}', '\\u{1F958}', '\\u{1FAD3}', '\\u{1F336}',
                    '\\u{1F35A}', '\\u{1F95F}', '\\u{1F9C4}', '\\u{1F362}'];
      let typed = '', busy = false;

      function rain() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        for (let n = 0; n < 60; n++) {
          const d = document.createElement('div');
          d.className = 'egg-drop';
          d.textContent = FOOD[Math.floor(Math.random() * FOOD.length)];
          d.style.left = (Math.random() * 98) + 'vw';
          d.style.fontSize = (18 + Math.random() * 20) + 'px';
          d.style.setProperty('--spin', (Math.random() * 720 - 360) + 'deg');
          d.style.animationDuration = (2.6 + Math.random() * 2.4) + 's';
          d.style.animationDelay = (Math.random() * 1.6) + 's';
          d.addEventListener('animationend', () => d.remove());
          document.body.appendChild(d);
        }
      }

      function unlock() {
        if (busy) return;
        busy = true;
        rain();
        const t = document.createElement('div');
        t.className = 'egg-toast';
        t.textContent = '\\u{1F64F} God mode: all you can eat';
        t.addEventListener('animationend', () => t.remove());
        document.body.appendChild(t);
        // Odměna za kód: rovnou ukážeme, kde se dá najíst do sytosti.
        const chip = document.querySelector('[data-facet="ayce"]');
        if (chip && !active.has('ayce')) chip.click();
        setTimeout(() => { busy = false; }, 6000);
      }

      // Posuvné okno posledních znaků, takže kód jde napsat kdekoliv,
      // i do vyhledávacího políčka.
      document.addEventListener('keydown', e => {
        if (!e.key || e.key.length !== 1) return;
        typed = (typed + e.key.toLowerCase()).slice(-CODE.length);
        if (typed === CODE) { typed = ''; unlock(); }
      });
    })();
"""
