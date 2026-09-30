---
name: csk-eskymo
description: Startovní listiny a výsledky závodů ČSK ve vodním slalomu, sjezdu a sprintu v programu Eskymo (sešit .ods pro OpenOffice Calc) podle Pravidel ČSK DV a Směrnic pro závodění. Použij vždy, když jde o Eskymo, startovku/startovní listinu, nasazení nebo losování, startovní čísla, hlídky a závody družstev, přihlášky na závod (CSV z prihlasky.kanoe.cz, e-maily a formuláře oddílů), převod výsledků z Canoe123 XML nebo časů z časomíry do Eskyma, kontrolu sešitu závodu před tiskem či odesláním na ČSK, rozpis/propozice z kalendáře kanoe.cz, nebo dotaz na pravidla startovního pořadí a výsledků — i když uživatel Eskymo výslovně nezmíní. Also use for Czech canoe slalom / wildwater start lists and results (ČSK, Eskymo ODS workbooks).
license: MIT
compatibility: Python 3.10+ s lxml (odfpy pro Canoe123, openpyxl pro xlsx, python-docx pro Směrnice). LibreOffice (headless) jen pro kontrolní přepočet. Eskymo samo běží u pořadatele v Apache OpenOffice.
metadata:
  sezona-pravidel: "2026"
  repo: https://github.com/CzechCanoe/eskymo-skill
---

# Eskymo — startovky a výsledky ČSK

Eskymo je rozšíření OpenOffice Calc (results.cz), ve kterém pořadatelé závodů ČSK DV
zpracovávají startovky i výsledky a ve kterém se výsledky odevzdávají svazu. Tenhle skill
pomáhá pořadateli: z nesourodých podkladů (přihlášky, rozpis, loňské výsledky, Canoe123,
časomíra) připraví data, zapíše je do **vstupních buněk** sešitu, který si pořadatel
vytvořil v Eskymu, všechno zkontroluje a vede člověka u kroků, které patří do Eskyma.

Cesty ke skriptům jsou relativní k adresáři tohoto souboru (`scripts/…`, `references/…`).

## Zásady (proč takhle)

1. **Sešit vytváří Eskymo, ne skript.** Eskymo generuje listy, vzorce, zamčení a kapacitu
   podle dialogu Nový závod; některé volby (disciplína, kategorie, hlídky, #řádek, bodování)
   pak nejdou změnit. Skill pořadateli připraví hodnoty do dialogu (`kalendar.py`), člověk sešit
   založí, uloží a udělá **Import registru**. Skripty pak píšou jen do vstupních buněk.
2. **GUI kroky Eskyma dělá člověk podle návodu, neobcházej je.** Nový závod, Import registru,
   Losování (když ho chce dělat Eskymo), Body, Tisk, Export a nahrání na ČSK jsou pár kliknutí
   a obcházet je makry nebo ovládáním GUI je křehké. Napiš přesně, co kde kliknout
   (`references/eskymo-gui.md`).
3. **Nehádej, co rozhoduje pořadatel.** Nasazení, směr a rozsah čísel, pořadí kategorií,
   písmena hlídek, sporná jména, přestupy mezi oddíly, předžáci. Když zadání není jednoznačné
   („vynechat pár čísel“), nabídni 2–3 konkrétní varianty i s rozpisem důsledků
   (`cisla.popis`) a nech vybrat. Technickou vadu (překlep ve vzorci šablony) oprav na kopii
   a řekni o ní.
4. **Vstupy pořadatele nikdy nepřepisuj.** Každý zápis jde do nového souboru
   (`…_startovka.ods`, `…_vysledky.ods`). Registr `reg` jen čteš.
5. **Nikdy tiše nezahazuj.** Neznámá kategorie, závodník mimo registr, přihláška na jiný den
   → vždy vypiš. Tichá ztráta je v oficiálních výsledcích nejhorší chyba (Benátky 2026:
   skript tiše zahodil 100 závodnic, protože Canoe123 psal K1Z místo K1W).
6. **Nehlas hotovo bez kontroly.** Po zápisu jsou výsledky vzorců v souboru zastaralé; jestli
   se RGC chytla v registru, ukáže až přepočet. Vždy `verify_workbook.py` (přepočítá kopii
   v LibreOffice); bez LibreOffice ať člověk v Eskymu stiskne Ctrl+Shift+F9 a uloží,
   a pak spusť kontrolu s `--bez-prepoctu`.
7. **Vypisuj proč.** U nasazení ke každé lodi „nasazeno podle“ (VT los, žebříček 12., loni 3.
   přes osobu…). Díky tomu pořadatel odhalí přestup nebo přejmenovaný oddíl, který by
   v samotných číslech neviděl.
8. **Osobní údaje.** Sešit obsahuje celý registr ČSK (i nezletilé, zdravotní prohlídky).
   Nevyvěšuj ho, necommituj, nepřikládej víc, než je potřeba. Registr nestahuj skriptem
   (`exp.php`) — importuje ho Eskymo.

## Krok 0 — vždy na začátku

```bash
python -m pip install -r scripts/requirements.txt      # lxml, odfpy, openpyxl, python-docx
python scripts/check_rules.py --sesit zavod.ods         # platí výtah pravidel pro sezónu závodu?
python scripts/inspect_workbook.py zavod.ods            # co je to za sešit, co v něm chybí
```

- **`check_rules.py`** (potřebuje síť; u čistě technických úloh — převod časů, kontrola sešitu —
  ho lze přeskočit): skill má zadrátovaný výtah Pravidel 2022 a Směrnic 2026
  (`references/pravidla-2026.md`). Když verdikt není OK (nová sezóna, opravená příloha),
  stáhni aktuální dokumenty (`--stahnout DIR`), přečti relevantní části a řiď se jimi. Rozdíl
  proti výtahu řekni pořadateli. Offline → pracuj s výtahem a řekni, že platnost nebyla ověřena.
- **`inspect_workbook.py`**: verze Eskyma, parametry (`param`), kategorie a listy, stav
  registru, zaplnění startovek, varování (prázdný `reg` → nejdřív Import registru; překlep
  `uuper(` v hlídkové šabloně; duplicitní `id`; sešit bez `param` = kros šablona).

## Rozcestník úloh

| Úloha | Přečti | Skripty |
|---|---|---|
| Připravit závod z odkazu v kalendáři (hodnoty do Nový závod) | `references/zalozeni-zavodu.md` | `kalendar.py` |
| Zpracovat přihlášky (CSV export, e-maily, formuláře) | `references/prihlasky.md` | `prihlasky.py` |
| Individuální startovka (nasazení, los, čísla) | `references/startovka.md` | `startovka.py`, `cisla.py` |
| Startovka hlídek / družstev | `references/hlidky.md` | `hlidky.py` |
| Výsledky z Canoe123 XML (slalom, kros) | `references/vysledky.md` | `canoe123.py` |
| Výsledky z časomíry, CSV, ručních protokolů | `references/vysledky.md` | `casy.py` |
| Kontrola sešitu před tiskem / odesláním | `references/kontrola.md` | `verify_workbook.py`, `recalc.py` |
| Co přesně udělat v Eskymu (klikání) | `references/eskymo-gui.md` | — |
| Otázka na pravidla (nasazení, čísla, VK, body, lhůty) | `references/pravidla-2026.md` | `check_rules.py` |
| Něco v sešitu nesedí (sloupce, vzorce, verze) | `references/eskymo-sesit.md`, `references/uskali.md` | `inspect_workbook.py` |

## Typický průběh závodu

1. **Rozpis → Nový závod.** `kalendar.py <odkaz>` → tahák hodnot. Člověk v Eskymu: Nový závod,
   uložit, Import registru, `param` Prohlídka-zobrazit = ano (S26 §7b). Pak `inspect_workbook.py`.
2. **Přihlášky → lode.json.** CSV export: `prihlasky.py csv export.csv --sablona zavod.ods
   [--zavod <číslo>]`. Volné přihlášky přepiš do stejného JSON (schéma v `references/prihlasky.md`)
   a zkontroluj `prihlasky.py over`. PROBLÉMY vyřeší pořadatel, dřív se nezapisuje.
3. **Nasazení.** Najdi pravidlo pro typ soutěže (`references/startovka.md` → tabulka podle Směrnic).
   `startovka.py nasad` → přehled s důvody → pořadatel potvrdí (případně ruční úpravy v plan.json).
4. **Čísla a zápis.** `startovka.py zapis` (čísla lze měnit bez nového losu; dohlášky `startovka.py dohlas`).
   Hlídky: `hlidky.py`.
5. **Kontrola.** `verify_workbook.py vystup.ods --plan plan.json`. Pak předání (níže).
6. **Závod.** Časy: `canoe123.py` (Canoe123), nebo `casy.py` (CSV, protokoly), nebo ruční zadávání
   v Eskymu. `verify_workbook.py --vysledky`.
7. **Výsledky.** Člověk v Eskymu: Ctrl+Shift+F9, Setřídit, **Body**, Tisk VL, nahrát sešit na ČSK
   přes odkaz z e-mailu **do 24 h** (VPZ; závody ČSK DV do pondělí 8:00).

## Co se zeptat pořadatele (když to není v zadání ani v rozpisu)

- Typ soutěže a rozpis (BHZ, vypsané kategorie, pořadí kategorií/skupin, počet jízd).
- Nasazení: podle Směrnic pro daný typ soutěže; u VPZ zvyklost pořadatele (los podle VT,
  nejslabší/nejlepší první) — ukaž, co říká `P 2.17.01`, a co dělá Eskymo.
- Podklady, které má dodat počtářka (průběžný žebříček ČPŽ, NKZ, ČPJ, ČPw).
- Čísla: od kolika, směr, bloky po kategoriích vs. průběžně, rezervy, chybějící dresy, max. dresů.
- Hlídky: loňské výsledky, písmena oddílů (deklarovaná / přidělit / netisknout).
- Den a číslo závodu u vícedenních akcí; co s předžáky a s kategoriemi pod 3 lodě.

## Předání pořadateli

Stručně česky, v tomto pořadí:
1. **Soubory**: výstupní `.ods` (a přehled nasazení `.md`/tisk), cesta.
2. **Co je hotové a ověřené**: počty po kategoriích, rozsah čísel, výsledek kontroly.
3. **K rozhodnutí / k ověření**: krátký konkrétní seznam (sporné nasazení, jména mimo registr,
   předžáci, přestupy, cizinci, opravy šablony).
4. **Další kroky v Eskymu**: otevřít v OpenOffice s Eskymem, Ctrl+Shift+F9, zkontrolovat
   jména/oddíly, Setřídit list, tisk; u výsledků Body a nahrání na ČSK (lhůta).

## Prostředí

- Python 3.10+, `pip install -r scripts/requirements.txt`. Jen `lxml` je nutné pro zápis;
  `odfpy` potřebuje Canoe123 převod, `openpyxl` čtení xlsx, `python-docx` čtení Směrnic.
- LibreOffice pro kontrolní přepočet: `soffice` v PATH nebo proměnná `ESKYMO_SOFFICE`.
  Apache OpenOffice headless převod neumí. Bez LibreOffice přepočítá člověk v Eskymu.
- kanoe.cz odmítá požadavky bez prohlížečového User-Agentu (403); skripty ho posílají.
- Cowork / sandbox: soubory ukládej do výstupní složky uživatele, ne do `/tmp` (recykluje se).
