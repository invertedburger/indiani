# Indiáni v Brně, Plán

Živý dokument pro architektonická rozhodnutí a provoz. Pro uživatelské
nastavení viz [README.md](README.md), pro konvence kódu viz [CLAUDE.md](CLAUDE.md).

## Cíl

Jedno místo, kde jsou zmapované všechny indické (a indicko-nepálské) restaurace
v Brně. Návštěvník otevře stránku, na mapě vidí, kde co je, a v kartách najde
adresu, web a druh kuchyně. Žádné přihlašování, žádný build na klientu.

## Proč bez scrapování a AI

Na rozdíl od sesterského projektu Tácek (denní polední menu) se adresář
restaurací mění zřídka. Data jsou proto ručně kurátorovaná v `restaurants.json`.
Build je tím pádem rychlý, deterministický a nepotřebuje žádné API klíče.
Jediná externí závislost je geokódování přes Nominatim, a to je cachované.

## Pipeline (run.py -> builder.build)

1. `load_restaurants` načte `restaurants.json`.
2. `geocode` doplní `coords` ke každé restauraci (cache `results/coords.json`,
   klíčem je název). Dotaz: `geocode` -> `address` -> `<název> Brno`.
3. `index_page.generate` vyrenderuje `results/index.html` (hero, hledání,
   karty, Leaflet mapa s piny).
4. Zkopíruje `assets/hero.jpg` do `results/` a zapíše `CNAME`.
5. `ftp.upload_dir` nahraje `results/` na FTP, pokud je nastavený `ftp_host`.

## Klíčová rozhodnutí

- **Data jako jediný zdroj pravdy.** Vše o restauraci žije v `restaurants.json`.
  Přidání podniku je editace JSON, ne kódu.
- **Geokódování s cache podle názvu.** Nominatim má limit 1 dotaz/s. Cache
  drží souřadnice mezi běhy, takže nová restaurace stojí jeden dotaz. V CI se
  cache obnovuje podle hashe `restaurants.json`.
- **Žádný build step na klientu.** HTML se generuje jako f-string, veškerá
  interaktivita (motiv, hledání, mapa) je inline JS. Tailwind a Leaflet z CDN.
- **Souřadnice lze přebít.** Pole `coords` nebo `geocode` v datech řeší případy,
  kdy Nominatim adresu netrefí nebo restaurace přesnou adresu nemá.

## Deploy topologie

```text
push do main
  └─ .github/workflows/build.yml
       ├─ python run.py  -> results/ (index.html, hero.jpg, CNAME, coords.json)
       └─ deploy na GitHub Pages -> indiani.ivomartisek.cz
```

Volitelně FTP na WEDOS přímo z `run.py` během běhu (když je vyplněný
`secrets.json`). GitHub Pages je primární cíl, FTP je záloha / alternativa.

## Provozní poznámky

### Pin sedí na špatném místě

- Zkontroluj `address` v `restaurants.json`, případně doplň přesnější `geocode`.
- Pro jistotu nastav `coords: [lat, lng]` napevno (zjistíš na openstreetmap.org).
- Po změně adresy smaž danou položku z `results/coords.json`, ať se přegeokóduje
  (nebo smaž celý soubor pro kompletní refresh).

### Tři piny na sobě na středu Brna

Restaurace bez adresy se geokódují na střed města. Doplň jim `address` nebo
`coords`.

## Backlog / nápady

- Naplnit kompletní a ověřený seznam brněnských indických restaurací (web search
  / Google Maps), současný seznam je jen seed.
- Filtrování podle tagů (vegetariánské, halal, rozvoz) nad rámec fulltextu.
- Odkaz na Zomato/Google hodnocení u každé karty.
- Otevírací doba a indikace "otevřeno teď".
- Volitelně napojení na denní menu jako v Tácku pro vybrané podniky.
