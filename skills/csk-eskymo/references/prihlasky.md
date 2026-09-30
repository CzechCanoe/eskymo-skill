# Přihlášky → seznam lodí (lode.json)

Přihlášky chodí ve dvou světech: **strukturovaný export** z přihlašovacího systému ČSK a **volné
přihlášky** (e-maily, docx/xlsx formuláře, SMS, papír). Oba se převádějí na stejný `lode.json`
a kontrolují stejně proti registru v sešitu (`prihlasky.py over`). Co nejde určit jednoznačně,
se **nehádá** — jde do seznamu pro pořadatele i s kandidáty z registru.

## 1. Export z přihlašovacího systému

Oddíly se přihlašují na `prihlasky.kanoe.cz` (od 2025 napojené na Registr ČSK). Pořadatel po
přihlášení exportuje CSV „pro Eskymo“ (cp1250 nebo UTF-8, oddělovač `;`, **jedna loď na řádek**).
Veřejné API není; export dodá pořadatel. Fallback bez přihlášení: veřejný seznam
`prihlasky.kanoe.cz/pr.php?k=…` (odkaz „přihlášeno N“ v kalendáři; HTML, bez `kod`/`poradi`).

| Sloupec | Význam | Pozor |
|---|---|---|
| `kategorie` | K1M, **K1W**, C1M, **C1W**, C2M, C2W, mix | ženy jako W → Eskymo `k1z`/`c1z`; kód mixu ověřit (`C2X`/`C2miX`) |
| `rgc` | RGC; **C2 dvě čísla oddělená mezerou**; cizinci `A…` | bez vodicích nul |
| `jmeno` | „Příjmení Jméno“, u C2 obě jména za sebou | u C2 nejde bezpečně rozdělit — páruj přes RGC |
| `nar` | ročník (u C2 dva) | |
| `oddil` | **plný název** oddílu | zkratku bere Eskymo z `reg` (sloupec M) |
| `vt`, `vk` | VT a VK v době exportu | autoritativní je `reg` (VT pro disciplínu S/W) |
| `zavody` | čísla závodů akce, na které loď jede | prázdné = všechny; → `--zavod` |
| `poradi` | pořadí podle řazení zvoleného před exportem | |
| `kod` | kód oddílové přihlášky (32 hex) | součty startovného po oddílech |
| `startovne`, `zeme`, `vedouci`, `poznamky`, `disciplina` | | `vedouci` = osobní údaj |

```bash
python scripts/prihlasky.py csv export.csv --sablona zavod.ods [--zavod 135] -o lode.json
```

## 2. Volné přihlášky (e-maily, formuláře)

Reálné vzorky (MČR družstev 2026): čistý xlsx formulář s RGC a písmeny, docx tabulka s RGČ, a hlavně
e-maily: „3x K1M: Novák Jan 012345, …“, jen příjmení („Novák Svoboda Dvořák“), jména s ročníky,
RGC s vodicími nulami (`049999`), deklarovaná písmena („K1Ž ´´A´´“), překlepy, „Novák Novák Petr“
(= dva sourozenci Novákovi a Petr? nebo Petr Novák?), odhlášky, které patří k jinému závodu.

Postup:
1. Strukturované formuláře (xlsx/docx tabulka) čti cíleně (openpyxl, python-docx), text přečti sám.
2. Každou loď zapiš do `lode.json` (schéma níže). RGC normalizuj bez vodicích nul. Když je jen
   jméno, najdi osobu v registru — `Registr.hledej(prijmeni, jmeno, rok, oddil)` (bez diakritiky,
   zúžení ročníkem a oddílem; vrací **seznam** kandidátů). Víc kandidátů = nerozhodnuto.
3. `python scripts/prihlasky.py over lode.json --sablona zavod.ods -o lode.json`
4. Pořadateli předlož jen nejednoznačnosti — krátce a konkrétně: „Oddíl X, K1M 2. hlídka: `12345`
   není v registru, podle jména Novák je to nejspíš `112345` — potvrdit?“

## 3. Schéma lode.json

```json
{"lode": [
  {"kat": "k1m", "rgc": ["9162"], "jmena": ["NOVÁK Jan"], "rocniky": [2008],
   "oddil": "USK Praha", "vt": "2", "vk": "DS", "zavody": ["135"], "poznamka": "",
   "poradi": 12, "kod": "…", "zdroj": "e-mail USK 12.9."},
  {"kat": "c2m", "rgc": ["57036", "57054"], "zdroj": "csv:ř.40"},
  {"kat": "k1z", "rgc": ["A90001"], "jmena": ["MÜLLER Anna"], "zdroj": "e-mail GER"}
]}
```

Povinné jen `kat` (kód Eskyma nebo K1W/C1Ž…) a `rgc`. `zdroj` vždy vyplň — podle něj se hledá
původ problému. Volitelně `poradi_start` (pevné pořadí) a `stc` (pevné číslo, např. ČP).

Hlídky mají vlastní tvar (`hlidky.json`, viz `hlidky.md`); z CSV exportu je vyrobí
`hlidky.py z-prihlasek lode.json`.

## 4. Co kontrola hlídá

| Problém (brání zápisu) | Varování / info (ověřit) |
|---|---|
| neznámá kategorie, chybí RGC | RGC patří jinému jménu (překlep v RGC nebo jménu) |
| RGC není v `reg`/`cizi` (+ kandidáti podle jména) | jiný ročník než v registru |
| sešit nemá list kategorie | jiná VT v přihlášce než v registru (platí registr) |
| loď přihlášená 2× v kategorii | žena v mužské kategorii (P 2.39.04: jen když se ženská nekoná) |
| C2: počet RGC ≠ 2, jeden závodník ve 2 posádkách (P 2.39.05) | předžák → přesunut do `pzk`/`pzc` (nebo chybí list) |
| muž v ženské kategorii | bez platné prohlídky (Eskymo tiskne `#`) · víc než 3 starty (MČR/ČP/NKZ) |

## 5. Zvláštní případy

- **Předžáci** (VK PZ, ročníky sezóna−10 až sezóna−6) bývají přihlášení v běžné K1/C1. Patří do
  listů `pzk`/`pzc` (jen BHZ 4 slalom, bez bodů; S26 §1). `prihlasky.py` je přesune, když sešit
  listy má; jinak rozhodne pořadatel.
- **Cizinci**: RGC `A…` musí být v listu `cizi` (jinak prázdné jméno). Přihlašovací systém
  A-kódy generuje; při ručním doplnění: `A` + 5 číslic navazující na maximum v `cizi`,
  sloupce jako `reg` (A RGC, B příjmení, C jméno, D ročník, E pohlaví, M oddíl/stát).
- **Odhlášky**: omluvené do pátku 18:00 do startovky nepatří; omluvené na poradě / neomluvené
  ve startovce zůstávají (S26 §1). Eskymo má stavy DNS-A / DNS-B („omluven“) a DNS — jak je přiřadit
  k lhůtám S26, není nikde definováno; návrh (omluven do porady = DNS-B, neomluven = DNS) ověř s VR.
  Při pozdní odhlášce stačí smazat rgc a stč řádku (nemazat řádek) — nebo nechat a ve výsledcích zadat stav.
- **Dohlášky na místě**: `startovka.py dohlas` + `zapis --prepsat` s čísly `pevne` (recept v
  `startovka.md` §2), nebo ručně v Eskymu.
- **Závodní společenství / C2 ze dvou oddílů**: v pořádku; Eskymo tiskne oba oddíly.
