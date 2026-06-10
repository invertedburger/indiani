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
├── assets/hero.jpg         # Hlavičkový obrázek
└── indiani/
    ├── config.py           # Načte config.json + secrets.json, exportuje konstanty
    ├── geocoder.py         # Nominatim geokódování s cache (results/coords.json)
    ├── ftp.py              # FTP upload (no-op, když ftp_host prázdný)
    ├── builder.py          # Pipeline: data -> geokód -> HTML -> assets -> FTP
    └── html/
        ├── assets.py       # DARK_INIT, TAILWIND, THEME_CSS, THEME_JS
        └── index_page.py   # generate(restaurants, timestamp) -> HTML string
```

## Datový tok

```text
restaurants.json
      │ config.load_restaurants()
      ▼
  geocoder.geocode()  ──► results/coords.json (cache podle názvu)
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
  "name": "Taj Mahal",        // povinné, klíč pro cache souřadnic
  "address": "Běhounská 4, Brno",
  "url": "https://...",
  "tags": ["severoindická", "halal"],
  "price": "$$",
  "note": "Krátký popis.",
  "geocode": "...",            // nepovinné, přebije address při geokódování
  "coords": [49.19, 16.60]     // nepovinné, přeskočí geokódování úplně
}
```

## Konvence kódu

- HTML se generuje jako f-string v `indiani/html/index_page.py`, žádný šablonovací
  engine. Pozor na zdvojené `{{ }}` ve vloženém JS uvnitř f-stringu.
- Veškerá klientská logika je inline JS (motiv, hledání, mapa). Žádný build step.
- Tailwind a Leaflet z CDN. Vlastní paleta (saffron/curry/masala/gold) je v
  `tailwind.config` v `assets.TAILWIND` plus `THEME_CSS`.
- Geokódování drží limit Nominatim 1 dotaz/s (`time.sleep(1)`); cache je
  v `results/coords.json` klíčovaná názvem restaurace.
- Secrets se nikdy nehardcodují, čtou se z `secrets.json` přes `indiani.config`.
- `restaurants.json` je jediný zdroj pravdy o restauracích, nepřidávej data do kódu.
- V uživatelské copy (texty na webu) se vyhýbej dlouhým pomlčkám (em/en dash),
  Ivo je nemá rád. Používej běžný spojovník nebo přeformuluj.

## Kontrola po změně

```bash
python run.py
```

Pak ověř `results/index.html`:

- Obsahuje `id="map"`, `id="search"` a `id="cards-grid"`.
- Každá restaurace má kartu s `data-search` (pro fulltext) a odkazem na Mapy.
- Restaurace se souřadnicemi mají pin v `markers_js` (Leaflet `L.marker`).
- Po změně `restaurants.json` zkontroluj, že nové podniky mají rozumné `coords`
  (ne střed Brna kvůli chybějící adrese).

Lokální náhled: `serve.bat` nebo `python -m http.server 8000 --directory results`.

## Časté úkoly

- **Přidat restauraci:** edituj `restaurants.json` (viz datový model). Žádná
  změna kódu. Když Nominatim adresu netrefí, doplň `geocode` nebo `coords`.
- **Změnit motiv/barvy:** `indiani/html/assets.py` (`THEME_CSS`, `TAILWIND`).
- **Změnit layout karty nebo mapy:** `indiani/html/index_page.py`.
- **Vyměnit hero obrázek:** nahraď `assets/hero.jpg` (nebo změň `hero_image`
  v `config.json`).
