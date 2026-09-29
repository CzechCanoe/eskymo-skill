# Evaly skillu

`evals.json` — realistická zadání (česky, jak je píší pořadatelé) nad anonymními daty z
`tests/fixtures`. Každé zadání se pouští dvakrát: agent **se skillem** a **bez skillu** (baseline).

Postup (podle skill-creator):

1. Pro iteraci N vytvoř `skills/csk-eskymo-workspace/iteration-N/eval-<id>-<name>/` s `inputs/`
   (kopie souborů z `files`) a `eval_metadata.json`; výstupy agentů jdou do
   `<config>/run-1/outputs/` (`with_skill`, `without_skill`), odpověď agenta do `response.md`.
2. `python evals/grade.py skills/csk-eskymo-workspace/iteration-N` — strojově ověřitelná tvrzení
   (počty lodí, čísla, pořadí, úplnost jízd, přepočet v LibreOffice, klíčové body odpovědi).
3. Agregace a prohlížeč z balíčku skill-creator (`aggregate_benchmark`, `eval-viewer/generate_review.py --static`).

Workspace je v `.gitignore`; do repa patří jen zadání, hodnoticí skript a shrnutí výsledků.
