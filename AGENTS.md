# AGENTS.md — orientace pro AI agenty a přispěvatele

Repo obsahuje skill `csk-eskymo` (složka `skills/csk-eskymo`) a jeho vývojové zázemí.
Uživatelé skillu jsou pořadatelé závodů ČSK — převážně ne-programátoři; komunikace, dokumentace,
výpisy skriptů a identifikátory, kde to dává smysl, jsou **česky**.

## Mapa

| Cesta | Co |
|---|---|
| `skills/csk-eskymo/SKILL.md` | rozcestník, zásady, typický průběh (drž pod ~300 řádky) |
| `skills/csk-eskymo/references/*.md` | detailní znalosti — načítají se podle potřeby |
| `skills/csk-eskymo/references/pravidla-2026.md` + `pravidla-manifest.json` | výtah pravidel sezóny + zdroje s hashi |
| `skills/csk-eskymo/scripts/eskymo_ods.py` | jediná vrstva pro čtení/zápis ODS (lxml) |
| `scripts/domena.py`, `registr.py`, `cisla.py` | číselníky ČSK, registr, startovní čísla |
| `scripts/prihlasky.py`, `startovka.py`, `hlidky.py`, `casy.py`, `canoe123.py`, `kalendar.py` | úlohy |
| `scripts/inspect_workbook.py`, `recalc.py`, `verify_workbook.py`, `check_rules.py` | diagnostika a kontroly |
| `scripts/vendor/canoe123_2_eskymo/` | připnutá kopie upstream převodníku — **needitovat** |
| `tests/run_tests.py`, `tests/fixtures/` | testy nad anonymními daty |
| `tools/` | fixtures, sync vendoru, zip skillu |

## Invarianty (neporušit bez vědomého rozhodnutí)

1. Sešit vytváří Eskymo; skripty píšou jen do **vstupních buněk** (`Sheet.set_input` odmítne vzorec).
   Nikdy neměnit `id`, nepřidávat/nemazat řádky, sloupce ani listy.
2. Vstupní soubory pořadatele se nepřepisují (`Workbook.save` odmítne stejnou cestu).
3. Nic se tiše nezahazuje — neznámá kategorie, osoba mimo registr, kapacita → vždy výpis / chyba.
4. RGC Čecha jako číslo, C2 a cizinec jako text; stč číslo; `ano`/`ne` malými písmeny.
5. Každá jízda zařazeného závodníka má čas nebo stav (slalom stav + 999).
6. Po zápisu vždy kontrola přepočtem (`verify_workbook.py`).
7. Číslování je samostatný krok nad uloženým plánem (přečíslování bez nového losu).
8. U nasazení se vždy uvádí důvod („nasazeno podle“).
9. Žádná reálná osobní data v repu (viz níže). Registr se nestahuje skriptem.
10. GUI kroky Eskyma (Nový závod, Import registru, Body, Tisk, nahrání) dělá člověk podle návodu —
    neautomatizovat je makry ani ovládáním GUI.

## Testy

```bash
python tests/run_tests.py            # musí projít; bez LibreOffice se přepočtové testy přeskočí
python tests/run_tests.py --online   # i kontrola pravidel proti kanoe.cz
```

Nová funkce = nový test nad fixtures. Když chybí data, rozšiř `tools/make_fixtures.py`
(syntetický registr je deterministický — seed).

## Osobní údaje a fixtures

- `podklady/` (reálné exporty, šablony s registrem) je v `.gitignore` a zůstává lokálně.
- Fixtures se vyrábějí **jen** přes `tools/make_fixtures.py` z lokálních reálných šablon: nahradí
  `reg`/`cizi` syntetickými osobami, anonymizuje `param`, meta.xml, záhlaví, smaže náhled a na konci
  ověří, že v souborech není žádné původní příjmení ani klíč registru. Když kontrola selže, fixture
  se necommituje.
- V příkladech v dokumentaci používej smyšlená jména a RGC.

## Roční aktualizace pravidel (typicky leden–únor)

1. `python skills/csk-eskymo/scripts/check_rules.py --sezona <rok> --stahnout /tmp/smernice<rok>`
2. Přečti nové Směrnice a přílohy; porovnej se `references/pravidla-2026.md` po sekcích
   (§1 soutěže a kategorie, §2 čísla a přihlášky, §5–7 startovky a hlídky, §8 intervaly, §9 omluvy,
   §11 odeslání výsledků, §12 body, přílohy — hlavně P1 právo startu ČP a P3 zkratky oddílů).
3. Vytvoř `references/pravidla-<rok>.md` (starý smaž nebo nech jako archiv mimo skill), uprav
   odkazy v `SKILL.md` a ostatních referencích, `metadata.sezona-pravidel` v SKILL.md.
4. Aktualizuj `pravidla-manifest.json` (URL, velikosti, sha256, Last-Modified, `current`).
5. Zkontroluj tabulku nasazení v `references/startovka.md` a `hlidky.md`, věkové kategorie
   (`domena.VK_VEK` jsou věkové hranice — ročníky se dopočítají samy) a mapování druhů závodu
   na bodování v `kalendar.py`.
6. `python tests/run_tests.py --online`, zvyš verzi v `.claude-plugin/plugin.json`, vydej release se zipem.

## Upstream canoe123-2-eskymo

Vendor se needituje. Oprava → PR do `CzechCanoe/canoe123-2-eskymo` (s testem tam) → po sloučení
`python tools/sync_vendor.py --ref <commit> --popis "…"` → testy. Známé otevřené body upstream:
A-část ze slepeného ICFId se nedoplní do `cizi`; disambiguace ročníkem při neshodě vezme tiše
prvního kandidáta; při překročení kapacity se výsledky uříznou bez chyby (obal `canoe123.py prehled`
to hlídá předem); `cross.py` nechává sloupec „celk.“ prázdný.

## Konvence

- Python 3.10+, jen stdlib + lxml (odfpy jen ve vendoru, openpyxl/python-docx volitelně).
- Skripty mají CLI s českou nápovědou v docstringu, výstup pro člověka česky, návratové kódy
  0 = OK, 1 = problémy, 2 = nejde spustit/ověřit.
- ODS se zapisuje výhradně přes `eskymo_ods.Workbook` (ne odfpy, ne ElementTree).
