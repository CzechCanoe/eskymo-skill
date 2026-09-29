# Vendorovaná kopie canoe123-2-eskymo

Zdroj: <https://github.com/CzechCanoe/canoe123-2-eskymo> (MIT, viz `LICENSE`).

| | |
|---|---|
| commit | `c4f04f3e706ff9ef2a19cae6c8f36314a8082735` (2026-09-29) |
| stav | hlava [PR #1](https://github.com/CzechCanoe/canoe123-2-eskymo/pull/1) — české kódy žen K1Z/C1Z/C2Z, hlasité varování na neznámé třídy |
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
