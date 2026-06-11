# Indiáni v Brně

Mapa a adresář všech indických (a indicko-nepálských) restaurací v Brně na jednom místě. Statická stránka generovaná z jednoho JSON souboru, publikovaná na [indiani.ivomartisek.cz](https://indiani.ivomartisek.cz).

Žádné denní scrapování ani AI: seznam restaurací je kurátorovaný v `restaurants.json`. Build je rychlý a deterministický.

## Funkce

- Leaflet mapa s pinem u každé restaurace (světlý i tmavý podklad CARTO)
- Karty restaurací s adresou, odkazem na web, tagy a cenovou hladinou
- Živé vyhledávání (název, čtvrť, druh kuchyně, poznámka)
- Tmavý režim, teplý indický motiv, hero banner
- Geokódování přes Nominatim s cache (přidání restaurace stojí jeden dotaz)
- Deploy na GitHub Pages (primárně) nebo přes FTP na WEDOS

## Struktura

```
indiani/
├── run.py                # Vstupní bod (python run.py)
├── config.json           # Nastavení webu (titulek, doména, střed mapy)
├── restaurants.json      # Data: seznam restaurací (commituje se)
├── secrets.json          # FTP přihlašovací údaje (NEcommitovat)
├── secrets.example.json  # Vzor pro secrets.json
├── requirements.txt
├── serve.bat             # Build + lokální server na :8000
├── assets/
│   └── hero.jpg          # Hlavičkový obrázek
├── results/              # Vygenerovaný web (gitignored)
└── indiani/
    ├── config.py         # Načítá config.json + secrets.json
    ├── geocoder.py       # Nominatim geokódování s cache
    ├── ftp.py            # FTP upload (no-op, když je ftp_host prázdný)
    ├── builder.py        # Pipeline: data -> geokód -> HTML -> assets -> FTP
    └── html/
        ├── assets.py     # Sdílené CSS a JS
        └── index_page.py # Generátor index.html
```

## Spuštění

```bash
pip install -r requirements.txt
python run.py            # vygeneruje results/index.html
```

Nebo `serve.bat` (Windows) pro build a lokální náhled na <http://localhost:8000>.

## Přidání restaurace

Stačí přidat objekt do `restaurants.json`, žádné změny kódu:

```json
{
  "name": "Taj Mahal",
  "address": "Běhounská 116/4, 602 00 Brno",
  "url": "https://www.tajmahalbrno.cz/",
  "tags": ["severoindická", "tandoori", "vegetariánské"],
  "price": "$$",
  "note": "Krátký popis."
}
```

| Pole | Povinné | Popis |
|------|---------|-------|
| `name` | ano | Název restaurace (klíč pro cache souřadnic) |
| `address` | doporučeno | Adresa, použije se pro geokódování |
| `url` | ne | Web restaurace |
| `tags` | ne | Popisné štítky (kuchyně, momo, thali, street food...) |
| `attrs` | ne | Filtrovatelné facety, viz níže (`ayce`, `lunch`, `delivery`) |
| `rating` | ne | Google hodnocení, např. `4.7` (zobrazí se jako ⭐ odznak) |
| `price` | ne | Cenová hladina, např. `$`, `$$`, `$$$` |
| `note` | ne | Krátký popis na kartě |
| `geocode` | ne | Vlastní dotaz pro geokódování (přebije `address`) |
| `coords` | ne | `[lat, lng]` napevno, přeskočí geokódování |

### Facety a filtrování

`attrs` je seznam klíčů z [indiani/facets.py](indiani/facets.py). Pro každý
klíč, který se vyskytne v datech, se nahoře automaticky objeví filtrační chip a
na kartě ikonka. Aktuální facety:

| Klíč | Ikonka | Význam |
|------|--------|--------|
| `ayce` | 🍽️ (sticker se smějícím Buddhou) | All you can eat / bufet |
| `lunch` | 🥢 | Polední menu (všední dny) |
| `delivery` | 🚚 | Rozvoz (foodora / Wolt / vlastní) |

Navíc: chip **⭐ 4.5+** filtruje podle `rating` a tlačítko **📍 Nejblíž u mě**
zjistí polohu z prohlížeče, dopočítá vzdálenost ke každé restauraci a seřadí je.
Nový facet přidáš do `FACETS` v `facets.py` a do `attrs` dané restaurace, nic
víc.

> Pozn.: `rating` je statické číslo (Google API hodnocení zdarma nedává), takže
> ho je potřeba občas ručně přepsat. Mírně zastaralá hodnota nevadí, hvězdička
> prokliká na Google.

Pokud restaurace nemá přesnou adresu, doplň `geocode` nebo `coords`, ať pin nesedí na středu Brna.

> Aktuální seznam je počáteční seed. Adresy a odkazy je potřeba ověřit a seznam doplnit o další podniky.

## Testy

```bash
pip install -r requirements-dev.txt
playwright install chromium   # jen pro e2e
pytest                        # data + build (rychlé), nepotřebují síť
```

- `tests/test_data.py` - validace `restaurants.json` (unikátní názvy, rating 1-5, známé `attrs`, formát URL).
- `tests/test_build.py` - build a kontrola HTML: počet karet, AYCE stickery, filtrační chipy a hlavně že **každý mapový odkaz míří na souřadnice** dané restaurace.
- `tests/test_e2e.py` - Playwright v prohlížeči: filtry, hledání a špendlík polohy (i fallback na střed Brna). Vyžaduje internet (CDN) a Chromium; bez nich se čistě přeskočí.

## Deploy

**GitHub Pages (primární).** `.github/workflows/build.yml` při každém pushi do `main` spustí `python run.py`, vygeneruje `results/` a nasadí na Pages. Soubor `CNAME` (`indiani.ivomartisek.cz`) se generuje automaticky. Cache souřadnic se mezi běhy uchovává podle hashe `restaurants.json`.

**FTP / WEDOS (volitelně).** Vyplň `secrets.json` podle `secrets.example.json` a `python run.py` po buildu nahraje obsah `results/` na FTP. Když je `ftp_host` prázdný, upload se přeskočí.

Podrobnosti k architektuře a provozu viz [PLAN.md](PLAN.md), instrukce pro Claude viz [CLAUDE.md](CLAUDE.md).
