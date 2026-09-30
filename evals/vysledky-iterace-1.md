# Evaly — iterace 1 (30. 9. 2026)

Čtyři zadání z `evals.json`, vždy jeden běh se skillem a jeden bez (Claude Opus 5.5), hodnoceno `evals/grade.py`.

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 87% ± 10% | +0.13 |
| Time | 390.7s ± 53.8s | 1039.9s ± 377.2s | -649.2s |
| Tokens | 156335 ± 9283 | 218566 ± 28800 | -62230 |
## Po zadáních

| eval | se skillem | bez skillu | co baseline nesplnil |
|---|---|---|---|
| 1 VPZ startovka | 11/11 | 10/11 | přepsal sloupec `id` ve startovkách a výsledcích |
| 2 MČR hlídky | 10/10 | 8/10 | neopravil překlep `uuper(` (u C2 hlídek `#NAME?`), nezmínil ho |
| 3 Canoe123 | 9/9 | 7/9 | jízdu bez času nechal prázdnou; DNS/DNF s penalizací 10000 místo 999 |
| 4 pravidla ČPw | 8/8 | 8/8 | (bez rozdílu; baseline dohledal Směrnice na webu) |

Se skillem byly běhy v průměru 2,7× rychlejší a spotřebovaly o ~28 % méně tokenů.
Nezávislá revize (Fable) a nálezy z evalů vedly k opravám v commitu po této iteraci.
