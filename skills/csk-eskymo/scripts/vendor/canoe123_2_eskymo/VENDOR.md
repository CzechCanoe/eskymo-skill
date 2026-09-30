# Vendorovaná kopie canoe123-2-eskymo

Zdroj: <https://github.com/CzechCanoe/canoe123-2-eskymo> (MIT, viz `LICENSE`).

| | |
|---|---|
| commit | `704735a9d2fbd0ed7215c53a617e75594d5c4c8c` (2026-09-30) |
| stav | main po sloučení PR #1 (české kódy žen) a PR #2 (kapacita, nejednoznačná jména) |
| soubory | `canoe2eskymo.py` (slalom), `cross.py` (kajak kros), `LICENSE` |

Soubory se **needitují ručně**. Oprava patří do upstream repa (PR), pak se sem
přenese skriptem z kořene tohoto repa:

```bash
python tools/sync_vendor.py --ref <commit|větev> [--repo ../c1232eskymo]
```

Skript zkopíruje soubory z daného commitu a přepíše tabulku výše. Po synchronizaci
spusť `python tests/run_tests.py`.

Proč kopie, a ne submodul nebo stahování za běhu: skill musí fungovat offline a
v prostředích, kde git není (Claude Cowork, nahraný zip skillu), a chování se nesmí
měnit pod rukama během sezóny.
