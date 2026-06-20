# Customer Voice Semantic Layer — Code-Level Walkthrough (Feasibility V1)

*Distilled 6/10/2026 from the HTML walkthrough on Kanu's work laptop. This describes the CURRENT sequential architecture — it supersedes the parallel/reconciliation design in `customer-voice-semantic-layer.md`.*

## Mental model: deterministic → probabilistic → deterministic

Registry (deterministic) → prompt builder (deterministic) → **one LLM call** (probabilistic) → intent gate (deterministic) → typed intent → SQL compiler (deterministic).

The LLM is boxed into **semantic parsing only**. It does not write SQL, choose tables, or bypass validation. If its JSON names something illegal, the gate fails before SQL exists.

## Registry (source of truth)

- `registry/_tables.yml` — logical table IDs → fully-qualified BigQuery tables + grain keys.
- `registry/dimensions/demographics.yml` — legal demographic fields, physical columns, allowed values, synonyms (e.g., `male/man/men/m → "Male"`).
- `registry/feasibility.yml` — panelist-centric archetype: panelist hub table, demographic join key, transaction columns, task states, survey metadata wiring.
- `registry/_vocab/*.sqlite` — SQLite snapshots for large vocabularies: product hierarchy, brands, survey resolution. UPCs use a live BigQuery checker instead (too high-cardinality to snapshot into prompts).

Each dimension definition has two jobs: `build_feasibility_prompt()` exposes its name + allowed values to the LLM; `Dimension.normalize_value()` later canonicalizes values (`male` → `Male`).

## Entry point: `ask.py main()` (CLI `cv-ask`)

Order: `_load_dotenv()` → `load_registry()` → `validate_registry()` (fail fast) → `load_feasibility_model()` → `anthropic_llm()` (creates callable, no call yet) → `load_vocab()` → `load_survey_resolver()` → `make_upc_checker()` (only with `--run`/`--dry-run`) → `question_to_intent()` → `compile_feasibility()` → optional `run_bigquery()`.

## Prompt builder

`build_feasibility_prompt(reg, model)` is deterministic — generates the LLM contract straight from the registry. The prompt enumerates: 5 output types (`count`, `response_rate`, `completion_rate`, `panelist_list`, `dimension_ranking`), 16 demographic dimensions with exact allowed values, behavior block (entity_type: upc/category/brand/department/category_group/subcategory; window; channel; banner; direction purchased/not_purchased), survey block (survey_ref copied verbatim), cap/rank_by/ranking. Rules map phrasings → intents ("how many" → count; "top buyers of X" → panelist_list ranked by purchases; "which category had most purchases" → dimension_ranking). Output: JSON only, no prose.

*Known gotcha:* prompt example text says `"male" → "M"` but registry canonicalizes to `"Male"`. Gate uses the registry, so it's safe — just a stale example.

## LLM call (the only one)

`question_to_intent()`: `system = build_feasibility_prompt(...)`; `raw = llm(system, question)`; → `parse_feasibility_intent(...)`. `llm_anthropic.py` `anthropic_llm()._call()` wraps `client.messages.create(...)` behind a pluggable callable (tests use fake LLMs). LLM's role: infer that "mael panelists bought UPC..." means `field=gender, value=male, entity_type=upc`.

## Intent gate: `parse_feasibility_intent()`

Returns a typed `FeasibilityIntent` dataclass, not raw model text.

- `_parse_filter` — dimension exists + is panelist/demographic, op valid, value exists; `dim.normalize_value()` canonicalizes.
- `_parse_behavior` — entity type, non-empty values, positive window, valid direction; routes UPCs → `normalize_upc`, category/brand → vocab resolution.
- `_parse_survey` — `SurveyResolver` maps link/name/id → external survey id.
- `_parse_ranking` — group_by, metric, cap, window → `TxnRanking`.

Misspellings: fuzzy correction is the LLM's job; the gate does case-insensitive canonical matching + synonym lookup. Literal `mael` is rejected unless explicitly in `value_synonyms`.

## UPC lane

1. LLM extracts candidate strings + `entity_type: "upc"` (UPCs are never prompt vocabulary).
2. `normalize_upc()` strips non-digits, left-pads to 13-digit warehouse form (`078742012345` → `0078742012345`).
3. Optional live check (`make_upc_checker()`, only with `--run`/`--dry-run`): `SELECT DISTINCT upc FROM <transactions> WHERE upc IN UNNEST(@upcs)`.

Why: separates "real product nobody bought" (valid zero) from "fake/malformed UPC" (should fail before SQL so users don't trust a bogus zero).

## Compiler: `compile_feasibility()`

Deterministic. Dispatches by output type; most build a `cohort` CTE. `_cohort_cte` (panelist IDs + demographic join + active filter + predicates), `_demo_filter`, `_behavior_predicate` (transaction subquery: UPC/category/brand/window/channel/banner), `_survey_predicate` (task/task_metadata subquery), `_rate_select` (response/completion rate).

Note: `compiler.py` `compile_intent()` is the generic registry compiler (metric/group_by/filters) — same pattern, different archetype; the active LLM path uses `compile_feasibility()`.

## Worked example

"how many mael panelists bought UPC 078742012345 in the last 4 months?" → LLM JSON: count, gender = male, upc behavior, 4-month window → gate canonicalizes `male`→`Male`, `078742012345`→`0078742012345` → compiled SQL: cohort CTE joining panelist + demographics (`state = 'REGISTERED'`, `gender = 'Male'`) with transaction subquery on the flattened txn table, then `COUNT(DISTINCT panelist_id)`.

## Code map

| File | Key code | Intent |
|---|---|---|
| `ask.py` | `main()` | Orchestrates load → LLM → parse → compile → optional execute |
| `loader.py` | `load_registry()` | YAML → typed `Registry` |
| `validator.py` | `validate_registry()` | Static integrity check, fail fast |
| `feasibility.py` | `load_feasibility_model()` / `compile_feasibility()` | Physical wiring / SQL generation |
| `intent_layer.py` | `build_feasibility_prompt()` / `parse_feasibility_intent()` | Prompt contract / strict validation gate |
| `llm_anthropic.py` | `anthropic_llm()._call()` | Only model invocation |
| `vocab.py` | `normalize_upc()`, `SqliteVocab.resolve()` | UPC normalization, hierarchy/brand validation |
| `executor.py` | `make_upc_checker()` | Live UPC existence check |
| `survey_resolver.py` | `SurveyResolver.resolve()` | Survey link/name/id → canonical id |
| `compiler.py` | `compile_intent()` | Generic registry compiler (tests/generic path) |

## How to explain it to another engineer

- "The LLM is only a semantic parser. The registry and prompt builder constrain what it can name, and the gate refuses anything illegal."
- "UPCs are not prompt vocabulary. They're identifiers extracted by the model, normalized with regex, and optionally validated against BigQuery before SQL."
- "The compiler is boring on purpose. Boring compilers are good compilers."
