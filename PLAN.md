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
3. Seřadí restaurace podle `rating` sestupně (neohodnocené `null` spadnou dolů).
4. `index_page.generate` vyrenderuje `results/index.html` (hero, hledání,
   filtrační facety, karty s ratingem/cenou/AYCE stickerem, Leaflet mapa).
5. Zkopíruje obrázky z `assets/` (`hero.jpg`, `ayce.png`) do `results/`
   a zapíše `CNAME`.
6. `ftp.upload_dir` nahraje `results/` na FTP, pokud je nastavený `ftp_host`.

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

## Hotovo

- Ověřený seznam 25 indických/nepálských podniků v Brně (+ Modřice).
- Filtrační facety: all you can eat (sticker), polední menu, rozvoz, rating 4,5+.
- Google rating u karet (odkaz na recenze), řazení podle hodnocení.
- Poloha: přetažitelný špendlík (GPS nebo ručně), vzdálenost + řazení.
- Tmavý motiv, Esri Dark Gray mapa, teplý indický vzhled.
- Nasazeno na GitHub Pages (auto-deploy z `main`).

## Backlog / nápady

- **DNS pro indiani.ivomartisek.cz**: ve WEDOSu CNAME `indiani` ->
  `invertedburger.github.io`, pak custom doména v Pages.
- Doplnit rating Desi Dhaba a Satyam (zatím `null`, neověřeno).
- Ověřit, jestli Flavours ještě funguje (Foursquare ho měl jako zavřený).
- Otevírací doba a indikace "otevřeno teď".
- Shlukování (cluster) hustých pinů v centru.
- Náhledový obrázek pro sdílení (OG image) a favicon.
- Lunch ceny u nebufetových podniků (volitelné, mění se často).
