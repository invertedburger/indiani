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
| `tags` | ne | Štítky (kuchyně, halal, vegetariánské, momo...) |
| `price` | ne | Cenová hladina, např. `$`, `$$`, `$$$` |
| `note` | ne | Krátký popis na kartě |
| `geocode` | ne | Vlastní dotaz pro geokódování (přebije `address`) |
| `coords` | ne | `[lat, lng]` napevno, přeskočí geokódování |

Pokud restaurace nemá přesnou adresu, doplň `geocode` nebo `coords`, ať pin nesedí na středu Brna.

> Aktuální seznam je počáteční seed. Adresy a odkazy je potřeba ověřit a seznam doplnit o další podniky.

## Deploy

**GitHub Pages (primární).** `.github/workflows/build.yml` při každém pushi do `main` spustí `python run.py`, vygeneruje `results/` a nasadí na Pages. Soubor `CNAME` (`indiani.ivomartisek.cz`) se generuje automaticky. Cache souřadnic se mezi běhy uchovává podle hashe `restaurants.json`.

**FTP / WEDOS (volitelně).** Vyplň `secrets.json` podle `secrets.example.json` a `python run.py` po buildu nahraje obsah `results/` na FTP. Když je `ftp_host` prázdný, upload se přeskočí.

Podrobnosti k architektuře a provozu viz [PLAN.md](PLAN.md), instrukce pro Claude viz [CLAUDE.md](CLAUDE.md).
