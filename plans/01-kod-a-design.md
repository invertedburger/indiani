# Plán: kód a design (září 2026)

Rozfázovaná oprava kódu a designu webu Indiáni v Brně. Data v `restaurants.json`
jsou už ověřená a opravená (30 podniků, září 2026), tenhle plán se jich netýká.

Každá fáze je samostatná, dá se udělat v novém chatu a po každé fázi musí web
fungovat. Po každé fázi: `python run.py` a `python -m pytest tests/ -q`.

## Pravidla pro každou fázi

- HTML se skládá jako f-string v `indiani/html/index_page.py`. Uvnitř vloženého
  JS se složené závorky zdvojují (`{{ }}`), jinak je f-string sní.
- Žádný build step na klientu. Tailwind a Leaflet z CDN, zbytek inline.
- V českých textech na webu nepoužívej dlouhé pomlčky, Ivo je nemá rád.
  Běžný spojovník nebo přeformuluj.
- `restaurants.json` je jediný zdroj pravdy o restauracích. Nepřidávej data do kódu.
- Nevymýšlej si API. Co není v sekci "Ověřená API" níž, si nejdřív ověř.

---

## Fáze 0: Ověřená API (hotovo, čti jako referenci)

Ověřeno 12. 9. 2026, nepřepisuj to z hlavy.

**Leaflet.markercluster 1.5.3** (cdnjs, MIT, vyžaduje Leaflet 1.0.0+)

```text
https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js
https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css
https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css
```

API, přesně tohle a nic jiného:

```javascript
var markers = L.markerClusterGroup({ maxClusterRadius: 50 });
markers.addLayer(L.marker([lat, lng], {icon: icon}).bindPopup(html));
map.addLayer(markers);
```

Ověřené volby: `maxClusterRadius` (default 80, jde i funkce podle zoomu),
`spiderfyOnMaxZoom`, `disableClusteringAtZoom`, `showCoverageOnHover`,
`zoomToBoundsOnClick` (default zapnuto). Obě CSS jsou povinné, pokud
nepoužiješ vlastní `iconCreateFunction`.

**Python:** `html.escape(s, quote=True)` ze standardní knihovny. `quote=True`
je default a escapuje i uvozovku, což je to, co potřebujeme v atributech.

**Odstranění diakritiky v JS** (pro hledání bez háčků): `String.prototype.normalize('NFD')`,
pak zahodit kombinující znaky rozsahu U+0300 až U+036F regulárním výrazem
a dát na malá písmena. `normalize` umí každý prohlížeč, co utáhne Leaflet 1.9.
V Pythonu totéž přes `unicodedata.normalize('NFD', s)`.

---

## Fáze 1: Korektnost buildu a geokódování

Neviditelné pro návštěvníka, nízké riziko, ale řeší chybu, která dnes reálně
schovala špatný pin. Dělej ji první.

### Co udělat

**1.1 HTML escapování v `indiani/html/index_page.py`**

Naimportuj `html` a prožeň `html.escape()` všechno, co jde z dat do markupu:
`name`, `address` (i výstup `_short_addr`), `url`, `price`, `tags` v haystacku.
Dnes pět karet vykresluje holý ampersand v `<h3>` (Buddha, Everest,
Nepal & Curry House, Siddhartha, Dr. Indy Pub & Indian Grill).

Pozor: `markers_js` jde přes `json.dumps`, což řeší JS string, ale ne HTML.
Popup se skládá v JS konkatenací, takže tam escapuj hodnoty ještě v Pythonu,
než se dostanou do JSON.

Nedělej: neescapuj výstup `quote_plus()` znovu, ten už je URL-safe.

**1.2 Invalidace cache podle adresy v `indiani/geocoder.py`**

Cache `results/coords.json` je dnes `{název: [lat, lng]}`. Změna `address`
pin neaktualizuje, protože klíč zůstal stejný. Takhle se schovalo, že Golden
Nepal seděl na sídle firmy na Lidické místo na Křenové 19.

Změň formát na `{název: {"coords": [lat, lng], "query": "<dotaz, co ho vyrobil>"}}`
a při čtení porovnej uložený `query` s aktuálním. Když nesedí, geokóduj znovu.
Dotaz skládej stejně jako dnes: `geocode` -> `address` -> `<název> Brno Czech Republic`.

Musí umět načíst i starý plochý formát (`[lat, lng]`), ať se cache nezahodí
celá. Chybějící `query` ber jako neznámý, tedy přegeokóduj.

**1.3 Úklid cache**

- Klíče, které už nejsou v `restaurants.json`, při zápisu zahoď. Dnes tam
  zůstávaly navždy, ručně jsem mazal `Flavours` a `Makalu`.
- `changed = True` nastavuj jen při skutečné změně. Větev s explicitním
  `coords` ho dnes nastaví vždy a přepíše soubor při každém buildu.

### Ověření

```bash
python run.py                      # projde bez geokódování (cache sedí)
python -m pytest tests/ -q         # 18 testů zelených
grep -c '<h3[^>]*>[^<]*&[^<]*</h3>' results/index.html   # musí být 0
grep -o '&amp;' results/index.html | head                # escapované jsou vidět
```

Ruční test invalidace: změň někomu v `restaurants.json` `address`, spusť
`python run.py` a ověř, že se ta jedna restaurace přegeokódovala a ostatní ne.
Pak změnu vrať.

### Čeho se vyvarovat

- Nezahazuj celý `coords.json` při upgradu formátu, migruj ho.
- Nesahej na `time.sleep(1)`, Nominatim má politiku 1 dotaz za sekundu.
- Nepřidávej do geokodéru žádnou novou síťovou závislost.

---

## Fáze 2: Oživit mrtvá data (facety, popisky, hledání)

Tady je největší užitek pro návštěvníka. Tři věci jsou v datech, ale kód je
nepoužívá.

### Co udělat

**2.1 Vrátit facety `lunch` a `delivery` do `indiani/facets.py`**

`FACETS` i `FACET_ORDER` obsahují dnes jen `ayce`, ale data mají `delivery`
u 10 podniků a `lunch` u 4, a `CLAUDE.md` dokumentuje všechny tři.
`_filter_bar()` klíč mimo `FACETS` přeskočí, takže chipy nikdy nevzniknou.

Doplň podle existujícího zápisu `ayce` ve stejném souboru:

- `lunch`: emoji pro polévku, label `Polední menu`
- `delivery`: emoji pro skútr, label `Rozvoz`

`FACET_ORDER = ['ayce', 'lunch', 'delivery']`. Barvy badge vezmi ve stejném
duchu jako `ayce` (Tailwind třídy pro světlý i tmavý motiv).

Poznámka: `ayce` je speciální, kreslí i nálepku se smějícím se Buddhou.
`lunch` a `delivery` nálepku nemají, jen chip ve filtru a případně badge.

**2.2 Vrátit `note` na kartu**

Všech 30 restaurací má ručně psaný popis a `_card()` ho nevykresluje.
`grep -rn note indiani/` vrátí nulu. Zmizel v commitu 09425b6 "Declutter cards".

Tohle je zároveň jediná věc, která odliší dvojice poboček: 2x Namaskar,
2x Sargam, 2x Satyam, 2x Royal Nepal, 2x Dr. Indy. Dnes vypadají skoro stejně.

Doporučení: vykresli `note` pod adresu, malým písmem, oříznuté na dva řádky
přes `-webkit-line-clamp: 2` (přidej pomocnou třídu do `THEME_CSS`). Karta
zůstane vzdušná a zároveň bude z čeho vybírat.

Tagy nech jen v hledání, na kartu je nevracej. Pak ale smaž nepoužívanou
třídu `.tag` z `THEME_CSS`, dnes se vykresluje nulakrát.

Alternativa, kdyby se `note` na kartě nelíbilo: vrátit místo něj tagy a `.tag`
nechat. Rozhodni s Ivem, ale neřeš obojí naráz, karta by zase zhoustla.

**2.3 Opravit hledání**

Placeholder slibuje "Hledat název nebo čtvrť…", ale `data-search` je jen
název, adresa a tagy. Čtvrti (Židenice, Bohunice, Královo Pole, Slatina)
jsou výhradně v `note`, takže hledání čtvrti dnes vrátí nulu výsledků.

- Přidej `note` do haystacku v `_card()`.
- Sjednoť diakritiku. Haystack ukládej už bez háčků a stejně ošetři dotaz
  v JS podle postupu z Fáze 0. Pak "Krenova" najde Křenovou a "Zidenice"
  Židenice.
- Původní text nech pro zobrazení, normalizuj jen `data-search`.

### Ověření

```bash
python run.py
python -m pytest tests/ -q
grep -o 'data-facet="[^"]*"' results/index.html | sort -u
#   musí obsahovat prázdný, ayce, lunch, delivery, __top
grep -c 'line-clamp' results/index.html     # note se vykresluje
grep -c 'class="tag"' results/index.html    # 0, pokud jsi tagy nevrátil
```

V prohlížeči (`serve.bat`): napiš do hledání `bohunice`, `zidenice`, `krenova`
bez diakritiky. Každé musí něco najít. Klikni chip Rozvoz, musí zůstat 10 karet,
chip Polední menu 4.

### Čeho se vyvarovat

- Nepřidávej facet, který není v datech. `_filter_bar()` schválně kreslí jen ty,
  co se v datech reálně vyskytují.
- Nedávej normalizovaný text do zobrazení, jen do `data-search`.
- Nepiš názvy facet do HTML natvrdo, ber je z `FACETS`.

---

## Fáze 3: Mapa při 30 pinech

Seznam vyrostl z 25 na 30 a v centru se piny překrývají. Sargam a Golden Nepal
jsou na Křenové zhruba 350 m od sebe, na Veveří jsou čtyři podniky.

### Co udělat

**3.1 Clustering**

Přidej Leaflet.markercluster podle Fáze 0. Do `<head>` obě CSS, skript až za
`leaflet.js`. Pak v `index_page.generate()` nahraď přímé
`L.marker(...).addTo(_map)` přidáním do skupiny: vyrob `L.markerClusterGroup`
s `maxClusterRadius: 50`, v `rs.forEach` volej `cluster.addLayer(...)` místo
`.addTo(_map)` a na konci `_map.addLayer(cluster)`.

Nezapomeň na zdvojené složené závorky, jsi uvnitř f-stringu.

`maxClusterRadius: 50` je menší než default 80, na hustém centru Brna se to
chová líp. Ověř vizuálně a případně dolaď.

**3.2 Výchozí výřez**

`fitBounds` s `maxZoom: 14` a odlehlíky (Modřice, Bohunice, Slatina) udělá
z centra při prvním pohledu jednu šmouhu. S clusteringem to bude přijatelné,
ale projdi to očima a zvaž `maxZoom: 13` nebo jiný `padding`.

### Ověření

```bash
python run.py
python -m pytest tests/ -q
grep -c 'markerClusterGroup' results/index.html   # 1
grep -c 'MarkerCluster.css' results/index.html    # 1
```

V prohlížeči: cluster bubliny se rozpadají při přiblížení, klik na cluster
přizoomuje, klik na jednotlivý pin otevře popup s názvem, adresou a odkazem.
Zkontroluj světlý i tmavý motiv, přepínání dlaždic nesmí clustery rozbít.

### Čeho se vyvarovat

- Nepřepisuj `MutationObserver`, co mění dlaždice při přepnutí motivu.
  Mění vrstvu dlaždic, ne markery.
- Nevymýšlej volby markerclusteru mimo seznam z Fáze 0.
- Netahej skripty z unpkg, používej cdnjs URL z Fáze 0.

---

## Fáze 4: Dolady designu, přístupnost, závislosti

Drobnosti, každá samostatně nasaditelná.

### Co udělat

**4.1 Hero bez poskočení layoutu**

`<img src="{HERO_IMAGE}">` nemá rozměry, takže stránka při načtení poskočí.
Zjisti reálné rozměry `assets/hero.jpg` a doplň `width` a `height`
plus `decoding="async"`. `loading="lazy"` sem nedávej, hero je nad ohybem.

**4.2 Favicon a OG image**

Dnes sdílený odkaz nemá náhled a v záložce je prázdná ikona.

- Favicon: stačí inline SVG s emoji přes data URI, nebo malý soubor
  v `assets/` (builder kopíruje `.png`, `.jpg`, `.svg` automaticky).
- OG: `og:title`, `og:description`, `og:image` (může ukazovat na `hero.jpg`
  absolutní URL na `indiani.ivomartisek.cz`), `og:type`, `twitter:card`.

Texty ber z `SITE_TITLE` a `SITE_TAGLINE` v `indiani/config.py`.

**4.3 Přístupnost**

- `themeBtn` má jen `title`, doplň `aria-label`.
- `#map` je prázdný div, doplň `role="region"` a `aria-label`.
- Filtrační chipy jsou `<button>` bez stavu, doplň `aria-pressed` a udržuj ho
  v `syncChips()` vedle přepínání tříd.
- `#noResults` se schovává inline stylem, použij atribut `hidden`.
  Pozor, `applyFilters()` na něj sahá přes `style.display`, sjednoť to.

**4.4 CDN**

Leaflet se tahá z `unpkg.com`. Přendej JS i CSS na `cdnjs.cloudflare.com`
(stejná verze 1.9.4), ať je to konzistentní s markerclusterem z Fáze 3.

Tailwind z play CDN píše do konzole varování, že není pro produkci. Řešit to
znamená build step, což je proti záměru projektu. Nech to být a jen si toho
buď vědom. Kdyby to vadilo, je to samostatné rozhodnutí, ne součást téhle fáze.

### Ověření

```bash
python run.py
python -m pytest tests/ -q
grep -c 'og:image' results/index.html      # 1
grep -c 'aria-pressed' results/index.html  # nenulové
grep -c 'unpkg.com' results/index.html     # 0
```

V prohlížeči: konzole bez chyb, DevTools na CLS u hera, procházení filtrů
klávesnicí (Tab, Enter) funguje.

### Čeho se vyvarovat

- Nepřidávej build step ani npm.
- Neměň paletu ani rozvržení, tahle fáze je hygiena, ne redesign.

---

## Fáze 5: Závěrečná verifikace

1. `python run.py` proběhne bez chyb a bez zbytečného geokódování.
2. `python -m pytest tests/ -q` zelené, včetně Playwright e2e.
3. `results/index.html` obsahuje `id="map"`, `id="search"`, `id="cards-grid"`.
4. Počet karet odpovídá počtu restaurací v `restaurants.json` (dnes 30)
   a každá má `data-search` a odkaz na mapu.
5. Restaurace se souřadnicemi mají marker, celkem 30 v `const rs`.
6. Grep na anti-vzory:

```bash
grep -c 'unpkg.com' results/index.html                  # 0
grep -c 'class="tag"' results/index.html                # 0 (pokud tagy nevráceny)
grep -o 'data-facet="[^"]*"' results/index.html | sort -u
grep -c '<h3[^>]*>[^<]*&[^<]*</h3>' results/index.html  # 0
```

7. Doplň testy pro to, co fáze přidaly. Minimálně: escapování ampersandu
   v názvu, invalidace cache při změně adresy, přítomnost všech tří facet
   chipů, hledání bez diakritiky.
8. Aktualizuj `CLAUDE.md` (sekce Struktura a Konvence kódu) a `PLAN.md`
   (přesuň hotové položky z Backlogu do Hotovo).

---

## Co tenhle plán vědomě neřeší

- **Otevírací doba a "otevřeno teď"**. Nejužitečnější chybějící údaj, ale
  znamená to nové pole v datech a jejich ruční údržbu u 30 podniků.
  Samostatné rozhodnutí, ne součást úklidu kódu.
- **Google ratingy u sedmi podniků** (Desi Dhaba, Light of India, obou
  Satyamů, Khaybaru, Royal Nepal Židenice a Dr. Indy Pub). Zůstávají `null`, protože se je nepodařilo ověřit z Googlu.
  Foodora a Firmy.cz mají jinou škálu, míchat je by pole rozbilo.
- **Klub cestovatelů** (Veleslavínova 183/14). Firmy.cz ho vede jako indickou
  restauraci, ale je to primárně libanonský podnik s cestovatelskými
  přednáškami. Ivo má rozhodnout, jestli do seznamu patří.
