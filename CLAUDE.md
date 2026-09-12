# Indiáni v Brně, instrukce pro Claude

## Přehled

Statický web mapující všechny indické restaurace v Brně. Python generátor čte
kurátorovaná data z `restaurants.json`, geokóduje adresy přes Nominatim a
vyrenderuje jediný `results/index.html` (hero banner, hledání, karty, Leaflet
mapa). Deploy na GitHub Pages, volitelně FTP na WEDOS.

Sesterský projekt je `Tacek` (denní polední menu s AI). Tento projekt je
záměrně jednodušší: žádné scrapování, žádné AI, žádné API klíče.

- **Vstupní bod:** `run.py` -> `indiani.builder.build()`
- **Data:** `restaurants.json` (commituj), `secrets.json` (FTP, NEcommituj)
- **Výstup:** `results/index.html`, `hero.jpg`, `CNAME`, `coords.json`

## Struktura

```text
indiani/
├── run.py                  # Vstupní bod
├── config.json             # Nastavení webu
├── restaurants.json        # Data, jediný zdroj pravdy o restauracích
├── secrets.json            # FTP údaje, NIKDY necommitovat
├── assets/                 # hero.jpg, ayce.png (nálepka all you can eat)
├── tests/                  # pytest: data, build, Playwright e2e
├── plans/                  # rozfázované plány úprav
└── indiani/
    ├── config.py           # Načte config.json + secrets.json, exportuje konstanty
    ├── facets.py           # Filtrovatelné facety (ayce, lunch, delivery)
    ├── geocoder.py         # Nominatim geokódování s cache (results/coords.json)
    ├── ftp.py              # FTP upload (no-op, když ftp_host prázdný)
    ├── builder.py          # Pipeline: data -> geokód -> HTML -> assets -> FTP
    └── html/
        ├── assets.py       # DARK_INIT, TAILWIND, THEME_CSS, THEME_JS,
        │                   # FOLD_JS, EASTER_EGG_JS
        └── index_page.py   # generate(restaurants, timestamp) -> HTML string
```

## Datový tok

```text
restaurants.json
      │ config.load_restaurants()
      ▼
  geocoder.geocode()  ──► results/coords.json (cache: název -> coords + dotaz)
      │
      ▼
index_page.generate() ──► results/index.html
      │
      ├─ shutil.copy hero.jpg -> results/
      ├─ zapiš results/CNAME
      └─ ftp.upload_dir(results/)   (jen když je ftp_host)
```

## Datový model (restaurants.json)

```json
{
  "name": "Taj Mahal",         // povinné, klíč pro cache souřadnic
  "address": "Běhounská 4, 602 00 Brno",
  "url": "https://...",
  "tags": ["severoindická", "halal"],   // jen pro hledání, na kartě se nezobrazují
  "rating": 4.5,               // přibližné Google hodnocení, null = neověřeno
  "attrs": ["ayce", "lunch"],  // facety, viz indiani/facets.py
  "price": "Bufet 189 Kč",     // konkrétní cena, typicky jen u bufetů
  "note": "Krátký popis.",     // zobrazí se na kartě a je v hledání
  "geocode": "...",            // nepovinné, přebije address při geokódování
  "coords": [49.19, 16.60]     // nepovinné, přeskočí geokódování úplně
}
```

Řazení je podle `rating` sestupně, neohodnocené spadnou dolů.

## Konvence kódu

- HTML se generuje jako f-string v `indiani/html/index_page.py`, žádný šablonovací
  engine. Pozor na zdvojené `{{ }}` ve vloženém JS uvnitř f-stringu.
- Veškerá klientská logika je inline JS (motiv, hledání, mapa). Žádný build step.
- Tailwind, Leaflet a Leaflet.markercluster z CDN, všechno z cdnjs. Vlastní
  paleta (saffron/curry/masala/gold) je v `tailwind.config` v `assets.TAILWIND`
  plus `THEME_CSS`.
- Všechno, co jde z dat do markupu, projde `html.escape()`. Pět názvů nese
  holý ampersand, apostrof v datech by rozbil atribut kolem sebe.
- Geokódování drží limit Nominatim 1 dotaz/s (`time.sleep(1)`). Cache
  v `results/coords.json` je klíčovaná názvem a ukládá i dotaz, který
  souřadnice vyrobil. Dotaz je invalidační klíč: po opravě adresy se pin
  přegeokóduje sám, ručně se nic mazat nemusí. Klíče restaurací, co v datech
  už nejsou, se zahazují.
- Facety přidávej do `indiani/facets.py` (`FACETS` i `FACET_ORDER`) a do `attrs`
  v datech. Facet, který je v datech a chybí v kódu, se tiše nevykreslí, přesně
  takhle byly `lunch` a `delivery` dlouho mrtvé. Hlídá to test.
- Hledání skládá diakritiku na obou stranách (`index_page._fold` a
  `assets.FOLD_JS`) a kvůli českému skloňování zkouší i kmen dotazu, aby
  "Bohunice" našlo "v Bohunicích".
- Secrets se nikdy nehardcodují, čtou se z `secrets.json` přes `indiani.config`.
- `restaurants.json` je jediný zdroj pravdy o restauracích, nepřidávej data do kódu.
- V uživatelské copy (texty na webu) se vyhýbej dlouhým pomlčkám (em/en dash),
  Ivo je nemá rád. Používej běžný spojovník nebo přeformuluj.

## Kontrola po změně

```bash
python run.py
python -m pytest tests/ -q     # 30 testů, včetně Playwright e2e
```

Pak ověř `results/index.html`:

- Obsahuje `id="map"`, `id="search"` a `id="cards-grid"`.
- Počet karet odpovídá počtu restaurací v `restaurants.json`, každá má
  `data-search` a odkaz na Mapy mířící na své souřadnice.
- Restaurace se souřadnicemi mají pin v `markers_js`.
- Po změně `restaurants.json` zkontroluj, že nové podniky mají rozumné `coords`
  (ne střed Brna kvůli chybějící adrese). Změnu adresy si cache pohlídá sama.

Pozor, `pytest | tail` spolkne návratový kód. Pouštěj pytest bez roury, nebo
si ověř `$?`.

Lokální náhled: `serve.bat` nebo `python -m http.server 8000 --directory results`.

## Časté úkoly

- **Přidat restauraci:** edituj `restaurants.json` (viz datový model). Žádná
  změna kódu. Když Nominatim adresu netrefí, doplň `geocode` nebo `coords`.
- **Změnit motiv/barvy:** `indiani/html/assets.py` (`THEME_CSS`, `TAILWIND`).
- **Změnit layout karty nebo mapy:** `indiani/html/index_page.py`.
- **Vyměnit hero obrázek:** nahraď `assets/hero.jpg` (nebo změň `hero_image`
  v `config.json`) a srovnej `width`/`height` v `index_page.generate`.
- **Přidat facetu:** `indiani/facets.py` (`FACETS` + `FACET_ORDER`) a `attrs`
  v datech. Nic dalšího, chip i badge se vykreslí samy.
- **Easter egg:** napsat kdekoliv `iddqd`. Kód je v `assets.EASTER_EGG_JS`,
  nápověda schovaná v HTML komentáři nad patičkou.
