# Eskymo v GUI — co dělá člověk (a jak se Eskymo chová)

Tyto kroky dělá pořadatel v Apache OpenOffice Calc s rozšířením Eskymo. Skill je nemá obcházet,
ale přesně navést: napiš, co kliknout, co vyplnit a co pak zkontrolovat. U každého kroku je
i to, co Eskymo dělá uvnitř — kvůli rozhodování, co udělá skript a co Eskymo.

**Obsah:** 1 Instalace · 2 Nový závod · 3 Import registru · 4 Startovka v Eskymu (losování, řazení,
startovní časy) · 5 Tisk a Prezentace · 6 Výsledky (formulář, soubor časů, přepočet) · 7 Body ·
8 Exporty · 9 Odeslání výsledků ČSK · 10 Vícedenní závod

## 1. Instalace (jednou)

1. Apache OpenOffice (úplná instalace) + Java; v Nástroje → Volby → Obecné zapnout
   „Použít dialogy OpenOffice“ (jinak padá Import registru).
2. Stáhnout `https://www.results.cz/eskymo/Eskymo.oxt` (1.7.11), Nástroje → Správce rozšíření →
   Přidat (pro všechny uživatele), restart Calcu. Přibude menu **Eskymo** a nástrojová lišta.
3. LibreOffice Eskymo oficiálně nepodporuje (od 1.6.1).

## 2. Nový závod (Eskymo → Nový závod)

Dialog „Parametry závodu“. Hodnoty připraví `scripts/kalendar.py` z rozpisu. **Pole s * nejdou později
změnit** (vzorce se generují podle nich) — při chybě je nutné sešit založit znovu.

| Pole | Hodnoty | Pozn. |
|---|---|---|
| název, místo, pořadatel, ředitel, vrchní rozhodčí, číslo, datum, bhz | text / čísla | jdou kdykoli opravit v listu `param` |
| disciplína * | `slalom`, `sjezd`, `sprint` | kros Eskymo nemá |
| st. časy | `ne` / `ano` | `ano` = na `param` časový rozpis a startovky počítají časy startu |
| počet jízd | `2` / `1` | hlídky 1 jízda (P 2.09.03) |
| bodování * body1/2/3 | `nic čp čpž nkz bhz-č bhz-m oč om` | viz `pravidla-2026.md` §12.4 |
| kategorie * | předj., C1M, K1Z, C1Z, C2X, PŽK, PŽC, K1M, C2M, C2Z | předžáci = PŽK/PŽC |
| #řádek * | 150 | kapacita každé kategorie — dej rezervu nad max. počet lodí |
| hlídky * | `ne` / `ano` | závody družstev |
| branek | číslo | počet branek (do výsledků) |

Po OK Eskymo vygeneruje nový sešit. **Uložit** (Ctrl+S), název podle příručky `rrccc_nazev.ods`
(rok + číslo závodu), zkrátit interval automatického ukládání.

## 3. Import registru (Eskymo → Import registru)

- Stáhne registr ČSK z adresy v `param` (Adresa registru) do `CSK-registr.csv` a přepíše list `reg`.
  Bez registru se nedotáhnou jména (VLOOKUP) → `#N/A` / prázdná jména.
- Opakovat kdykoli (např. den před závodem kvůli novým registracím a prohlídkám).
- Po importu zkontrolovat `param`: Prohlídka-zobrazit = `ano`, Prohlídka-znak = `#` (S26 §7b).
- Skill registr **nestahuje** sám (klíč v adrese je globální a interní) — jen čte list `reg`.

## 4. Startovka v Eskymu

**Ruční zadání:** na listu `<kat>_sl` psát do sloupce stč a rgc; zbytek dopočítají vzorce.
Cizinci do listu `cizi` (RGC `A…`).

**Losování (ikona na liště, na aktivním listu `_sl`):**
- Seřadí podle VT a v každé skupině VT náhodně, skupiny od **nejhorší**: bez VT/0, 3, 3+, 2, 2+, 1, MT
  (MT startují poslední). Pak přečísluje **1…N v každé kategorii** — bez rezerv a bez návaznosti
  mezi kategoriemi.
- Cizinci (VT „9“) do žádné skupiny nepatří a číslo dostat nemusí → zkontrolovat ručně.
- Na hlídkové listy losování nepoužívat.
- Opačný směr (nejlepší první, P 2.17.01) nebo čísla navazující přes kategorie Eskymo neumí →
  udělá je `startovka.py` (nebo ruční přečíslování + Setřídit).

**Setřídit list (ikona):** `_sl` podle stč / vt / oddílu / poznámky, vzestupně/sestupně.
Po zápisu skriptem není nutné; při sestupném číslování netřídit vzestupně (převrátí pořadí startu).

**Startovní časy (jen když st. časy = ano):** na `param` tabulka od sloupce G: pořadí kategorií (#),
začátek 1. jízdy (J3), interval (K3), pauza v intervalech mezi kategoriemi (M3); pro 2. jízdu P3/Q3/S3.
Časy se počítají **v pořadí řádků** startovky. Nestartující v dané jízdě: `-` do sloupce R (1. jízda)
nebo S (2. jízda) — jeho interval se nepřidělí. Setřídit na `param` přeřadí rozpis podle #.

## 5. Tisk a Prezentace

- Ikona tiskárny = aktivní list; Eskymo → Tisk všech SL / Tisk všech VL (tiskne hned na výchozí
  tiskárnu — pro PDF zvolit PDF tiskárnu). Komplet SL = všechny startovky v jednom novém sešitu.
- Prezentace = nový sešit pro výdej čísel a startovné po oddílech (sazby přepsat, výchozí 40 Kč).
- Exporty → Formuláře hlídky = formuláře pro oddíly na doplnění sestav hlídek.

## 6. Výsledky

**Formulář Výsledek (ikona):** kategorie, jízda, stč → Najdi; slalom: sekundy + setiny + trestné body,
sjezd/sprint: MM:SS,DS; nebo start a cíl (`MM:SS,cc`) a „=“ spočítá čistý čas. Pole *výsledek*
(DNS/DNF/DSQ-R/DSQ-C/DNS-A/DNS-B) má přednost a u slalomu zapíše 999.

**Natažení časů ze souboru (ikona):** textový soubor, řádek `kat;stc;jizda;start;cil`, např.
`k1m;12;1;10:02:15,320;10:04:01,050`. Kategorie malými písmeny, jízda 1/2, desetinná **čárka**,
hodiny se ignorují (jízda < 60 min, cíl < start = přes hodinu). Trestné body a stavy se nenatáhnou —
zadat formulářem. Soubor vyrobí `scripts/casy.py eskymo`. Cesta k souboru bez mezer a diakritiky.

**Přepočet časů (menu):** přepočítá čisté časy ze sloupců start/cíl (V–Y) — po ruční opravě startu/cíle.

**Smazat výsledky (menu):** smaže časy, body, pořadí; startovka zůstane (vícedenní závod).

Po zadání výsledků vždy Ctrl+Shift+F9 a Setřídit (výsledek) — dopočte pořadí ve VK.

## 7. Body (ikona „Spočítat žebříčkové body“, na aktivním výsledkovém listu)

- Podle `param` Body1–3 do sloupců S–U. `čp`/`čpž`/`nkz` = tabulka T-4 (75, 68, 62 … 1; 35 míst,
  shoda se nedělí), `čpž` jen žáci, `nkz` jen VT 2/3; `bhz-č`/`bhz-m`/`oč`/`om` = banka BHZ
  (MT a 1 = 2×BHZ, 2 = BHZ, 3 = 1, bez VT = 0,5), `oč`/`om` jen závodníci dané oblasti.
- Cizinci (RGC `A…`) a předžáci body nedostávají.
- Body počítá **Eskymo**, ne skript. BHZ lze na `param` změnit a body přepočítat.

## 8. Exporty (Eskymo → Exporty)

- Export XLS: nový sešit jen s hodnotami (výsledky po kategoriích) — uložit ručně (např. `25045W.xlsx`).
- Export XML: `<rr><ččč><S|W>.xml` (S = slalom, W = sjezd/sprint) — hlavička závodu, výsledky, body.
- Export diplomy: tabulka pro hromadnou korespondenci (první 3 v kategoriích a VK).
- Startovní listina AB, Export CSV/SQL/KOMENT, Import CSV, Rafty: v ČSK buildu nedostupné (šedé).

## 9. Odeslání výsledků ČSK

- 2 dny před závodem přijde pořadateli e-mail s **unikátním odkazem** pro nahrání.
- Nahrává se **celý sešit Eskyma (.ods)** tak, jak je (bez exportů); znovu nahrát = oprava.
- Lhůta (S26 §6): VPZ do **24 h** po skončení závodu; závody v péči ČSK DV do pondělí 8:00.
  Po nahrání jsou výsledky neoficiální, počtářka je zkontroluje a schválí.
- Ztracený odkaz pošle znovu počtářka. Předtím: Body spočítané, Ctrl+Shift+F9, žádné `#N/A`,
  `verify_workbook.py --vysledky`.

## 10. Vícedenní závod

Každý den = samostatný sešit (jiné číslo závodu a datum). Se stejnou startovkou: Soubor → Uložit
jako (nový název) → Eskymo → Smazat výsledky → opravit `param` (datum, číslo, BHZ).
U Canoe123 převodu generuj každý den z čisté šablony (viz `vysledky.md`).
