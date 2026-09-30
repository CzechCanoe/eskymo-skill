# Individuální startovka: nasazení, čísla, zápis

**Obsah:** 1 Pravidlo podle soutěže · 2 Postup · 3 nastaveni.json a typické konfigurace ·
4 Startovní čísla · 5 Startovní časy · 6 Jak předložit pořadateli

## 1. Kdo startuje kdy — podle soutěže (Směrnice 2026)

Ověř sezónu (`check_rules.py`) — tabulka je ze Směrnic 2026, citace v `pravidla-2026.md` §5–6.

| Soutěž | Startovní pořadí | Nezařazení | Čísla |
|---|---|---|---|
| **VPZ / VPZw / ČPV** (OČ, OM) | Směrnice neupravují → `P 2.17.01`: skupiny VT (MT+1, 2+, 2, 3+, 3, bez VT), uvnitř **los**; startovka „může být i v obráceném pořadí“ | — | P 2.18.03: vzestupně, kategorie od čísla končícího 1 |
| **ČP slalom** | startovku pro celý seriál posílá **předseda ZK** (od nejhorších, pevné časy); pořadatel jen vyřadí omluvené do pátku 18:00 | — | = umístění v ČP loni (na celý seriál) |
| ČP finále A / B | A: obrácené pořadí kvalifikace (10. první); B: podle čísel vzestupně | | |
| **NKZ** | MT+1 VT první, pak ostatní dle průběžného pořadí NKZ (1.–2. NKZ loňský žebříček; dál dodá počtářka), pak nezařazení 2. VT | na konec | P 2.18.03 |
| **ČPŽ slalom** | obrácený průběžný absolutní žebříček ČPŽ (1. a 2. závod loňský); dodá počtářka | **na začátek, losem podle VT „od nejlepší VT po nejhorší“** | P 2.18.03 |
| **MČR dorostu slalom** | obrácený průběžný žebříček ČPJ (dodá počtářka) | na začátek dle VT (jako ČPŽ) | P 2.18.03 |
| **MČR žáků slalom** | obrácený průběžný ČPŽ | na začátek dle VT | P 2.18.03 |
| **ČPw (klasik i sprint)** | od nejhorších k nejlepším v průběžném pořadí (jen z klasiků); 1.–2. ČPw loňský žebříček; dodá počtářka | neuvedeno → zeptat se | **sestupně, poslední v kategorii = 1** |
| ČPw sprint finále B / A | B: čísla vzestupně; A: postupující z FB (obráceně), pak z kvalifikace (obráceně) | | |
| **KC individuál** | podle ČP 2025, od nejvyššího čísla k nejnižšímu, pevné časy | rozlosováni na začátek | z ČP 2025 |
| **Družstva (MČR)** | obrácené pořadí loňských výsledků → `hlidky.md` | | |

Poznámky:
- „Obrácené pořadí žebříčku / loňska“ = **vítěz startuje poslední**.
- Nezařazení „na začátek … od nejlepší VT po nejhorší“ je doslovné znění S26, ale jde proti logice
  obráceného žebříčku i proti losování Eskyma (od nejhorší). Použij doslovné znění
  (`nezarazeni: zacatek-vt-nejlepsi-prvni`) a pořadateli to výslovně ukaž k potvrzení.
- Podklady žebříčků **dodává počtářka** — vyžádej je, nevymýšlej. slalom-world.com je jen neoficiální dopočet.
- ČP slalom: startovku od nuly nesestavuj; zpracuj dodanou (`metoda: pevne`, `cisla.rezim: pevne`).

## 2. Postup

```bash
python scripts/prihlasky.py csv export.csv --sablona zavod.ods -o lode.json      # nebo `over` pro ruční JSON
python scripts/startovka.py nasad lode.json zavod.ods -c nastaveni.json -o plan.json --prehled nasazeni.md
#   → pořadatel zkontroluje nasazeni.md (sloupec „nasazeno podle“); úpravy přímo v plan.json
python scripts/startovka.py zapis plan.json zavod.ods zavod_startovka.ods -c nastaveni.json --prehled nasazeni.md
python scripts/verify_workbook.py zavod_startovka.ods --plan plan.json
```

- `nasad` uloží do plánu **seed** losu → los je reprodukovatelný a doložitelný.
- Ruční úpravy (pestrost, výjimky, přestupy) dělej v `plan.json` přesunem lodí v seznamu
  a do `duvod` napiš proč. Pak znovu `zapis`.
- Přečíslování (chybějící dres, jiný rozsah) = jen `zapis` s jiným `cisla` — nasazení zůstane.
- `zapis` odmítne list, kde už jsou data (`--prepsat` smaže stč/rgc/poznámku celého listu).
- `metoda: eskymo-los` zapíše jen rgc (seřazené podle VT) — čísla pak vylosuje člověk tlačítkem
  v Eskymu (od 1 v každé kategorii, nejslabší první; `eskymo-gui.md` §4). Jen pro všechny kategorie
  najednou — kombinace s jinými metodami by dala kolidující čísla (skript ji odmítne).
- Lodě s nevyřešenými PROBLÉMY z `prihlasky.py` se nenasazují; jsou v přehledu v sekci „Nezapsáno“
  (`--i-s-problemy` je nasadí i tak — jen když to pořadatel chce).
- `zebricek`: řádky s neznámou kategorií a počty zařazených/nezařazených jsou v přehledu („Poznámky
  k nasazení“); když není v žebříčku ani jedna přihlášená loď kategorie, skript skončí chybou.

**Dohláška po zápisu** (čísla ostatních se nemění):

```bash
python scripts/startovka.py dohlas plan.json zavod.ods --kat k1m --rgc 12345 --stc 20 --pozice zacatek
python scripts/startovka.py zapis plan.json zavod.ods zavod_startovka_v2.ods --prepsat -c pevne.json
#   pevne.json: {"cisla": {"rezim": "pevne"}}
python scripts/verify_workbook.py zavod_startovka_v2.ods --plan plan.json
```

Číslo dohlášky vezmi z rezervy nebo za posledním číslem kategorie. `--pozice`: `zacatek`
(nezařazení podle Směrnic), `konec`, nebo pořadí (1 = první startující). Poznámky ve sloupci K
zůstávají na svých řádcích — po přeřazení je zkontroluj. Odhláška = smazat loď z `plan.json` a totéž
`zapis --prepsat` s `pevne` (nebo v Eskymu smazat rgc a stč na řádku).

## 3. nastaveni.json a typické konfigurace

```json
{"poradi_kategorii": ["k1m", "c1z", "c2m", "pzk", "c1m", "pzc", "k1z", "c2x"],
 "nasazeni": {"metoda": "vt-los", "smer": "nejslabsi-prvni", "skupiny": "pravidla", "seed": null,
              "zebricek": null, "nezarazeni": "zacatek-vt-nejlepsi-prvni"},
 "kategorie": {"c2x": {"nasazeni": {"metoda": "prihlaska"}}},
 "cisla": {"rezim": "desitky", "start": 1, "mezera": 0, "vynechat": [], "max": null}}
```

| Závod | Nastavení |
|---|---|
| VPZ, zvyklost „jako Eskymo“ | `vt-los`, `smer: nejslabsi-prvni`, `skupiny: eskymo` (MT a 1 zvlášť), čísla `desitky` |
| VPZ podle P 2.17.01 | `vt-los`, `smer: nejlepsi-prvni`, `skupiny: pravidla` (6 skupin; `pravidla-4` = MT+1, 2+/2, 3+/3, bez — viz Nejasnosti v pravidlech) |
| ČPŽ / MČR žáků / MČR dorostu | `zebricek` (CSV od počtářky `kat;rgc;poradi`), `smer: nejslabsi-prvni`, `nezarazeni: zacatek-vt-nejlepsi-prvni` |
| NKZ | S26: MT a 1. VT startují **první**, pak ostatní podle průběžného pořadí NKZ, nezařazení 2. VT na konec. Technicky `zebricek` (CSV, kde MT+1 dostanou nejlepší pořadí), `smer: nejlepsi-prvni`, `nezarazeni: konec`; směr uvnitř průběžného pořadí ověř s pořadatelem/počtářkou |
| ČPw | `zebricek`, `smer: nejslabsi-prvni`, čísla `sestupne-kat` |
| ČP slalom | `pevne` (pořadí z dodané startovky), čísla `pevne` (stc v lode.json) |
| Malý závod bez VT | `prihlaska` nebo `vt-los` |

`smer` znamená, kdo startuje **první** v kategorii. Žebříček v CSV má pořadí 1 = nejlepší.

## 4. Startovní čísla (`cisla`)

| Režim | Chování | Kdy |
|---|---|---|
| `desitky` (výchozí) | vzestupně; každá kategorie od dalšího čísla končícího 1 (1, 21, 31 …); `zarovnani: 100` → 101, 201 | P 2.18.03 |
| `prubezne` | vzestupně napříč závodem, `mezera` rezervních čísel mezi kategoriemi | zvyklost pořadatele |
| `sestupne` | od `start` dolů napříč závodem, rezervy mezi kategoriemi | hlídky MČR 2026 |
| `sestupne-kat` | v každé kategorii poslední startující = 1 | ČPw, KC individuál |
| `pevne` | čísla z dat (`stc`); unikátní jen v kategorii | ČP slalom (číslo = loňské umístění v kategorii), dohlášky |

Vždy: `vynechat` (dresy, které pořadatel nemá — přeskočí se i v rezervách), `max` (počet dresů).
Kontroly (unikátnost, vynechaná, rozsah) dělá `cisla.py` sám. Když zadání není přesné („pár čísel
mezi kategoriemi“), spočítej 2–3 varianty (`cisla.prirad` + `cisla.popis`) a ukaž rozpis bloků.
Pozor na logiku zadání: když má chybět číslo 66, musí rozsah sahat nad 66.

## 5. Startovní časy

Jen když sešit má st. časy = ano: časy počítá Eskymo z rozpisu na `param` (začátek, interval, pauza,
pořadí kategorií) v pořadí řádků startovky. Skript časy nepíše — připrav hodnoty rozpisu a návod
(`eskymo-gui.md` §4). Minima (P 2.29.02, MČR/ČP/NKZ): slalom 40 s, sjezd 30 s, družstva 90/60 s,
mezi kategoriemi 3 min (družstva 5 min). ČP a MČR mají intervaly ve Směrnicích (`pravidla-2026.md` §8).

## 6. Jak předložit pořadateli

- Přehled `nasazeni.md` po kategoriích: pořadí, stč, jméno, ročník, oddíl, VT, **nasazeno podle**.
- Nahoře 3–6 bodů k rozhodnutí (nezařazení, výjimky, předžáci, kategorie pod 3 lodě — S26:
  hodnotí se až od 3 odstartovaných lodí, jinak slučování podle příkladů A/B/C).
- Rozpis čísel (`cisla.popis`), seed losu.
- Připomenout: v Eskymu otevřít, Ctrl+Shift+F9, zkontrolovat jména, tisk (Tisk všech SL / Komplet SL).
