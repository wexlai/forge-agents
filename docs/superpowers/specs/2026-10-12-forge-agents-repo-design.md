# forge-agents repository — design

Date: 12 Oct 2026
Status: draft, awaiting review
Repo: `git@github.com:wexlai/forge-agents.git` (public, Apache-2.0)

## 1. Purpose

WeXL builds agents for the AI SDLC (the Forge Catalog on wexlai.com). This repo shows that we can build them in many agent frameworks (Strands, CrewAI, Spring AI, Embabel, and others) and in several languages, and it is the public, runnable source the Forge Catalog pages link to.

It will grow to roughly 100 agents. Success means:

- An engineer doing diligence can open any agent folder, follow the README, and run its example in minutes with whichever model provider key they have.
- Every folder meets the same visible bar (README, configuration, examples, tests, green CI), whatever its framework or language.
- The repo looks alive: dependencies current, CI green, stale agents surfaced before a visitor notices them.

### Decisions already made

| # | Decision |
|---|---|
| D1 | One monorepo is the single source. It replaces the per-agent `wexl-forge-<agent>` repos in §11.1 of the catalog spec, because separate repos go stale. |
| D2 | Everything is open source, including orchestration. |
| D3 | Each agent folder is self-contained. There is no rule that an agent is built in every framework; which agent gets which framework is chosen case by case. No shared contract or shared code between folders. |
| D4 | Model provider is pluggable per agent. Every folder ships a `.env.example` with working defaults. |
| D5 | Licence: Apache-2.0. Security contact: bharat@wexl.in. |
| D6 | Skills are out of scope. They go in a separate `forge-skills` repo, laid out like `anthropics/skills`, designed in its own session. |
| D7 | Consistency is enforced by a per-folder manifest (`agent.yaml`) plus thin repo tooling, not by a monorepo build system. |

## 2. Repository layout

```
forge-agents/
├── README.md                  # intro, how to run an agent, generated agent table
├── LICENSE                    # Apache-2.0
├── NOTICE                     # Copyright 2026 WeXL
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md         # Contributor Covenant 2.1
├── .gitignore
├── renovate.json
├── .github/
│   ├── workflows/
│   │   ├── validate.yml
│   │   ├── ci.yml
│   │   ├── live-examples.yml
│   │   └── staleness.yml
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/        # bug report, new agent proposal
├── tools/
│   ├── forge_repo.py          # validate + index
│   └── tests/                 # pytest for forge_repo.py
├── templates/
│   └── agent/                 # skeleton for a new agent folder
├── docs/
│   └── superpowers/specs/     # design docs (this file)
└── forge-<agent>-<framework>[-<language>]/   # one folder per agent implementation
```

## 3. Agent folder standard

### 3.1 Naming

`forge-<id>-<framework>` or `forge-<id>-<framework>-<language>`, all lowercase, words joined by hyphens. The language part is optional. When present it must equal `language` in `agent.yaml`. `<id>` matches the Forge Catalog id (the website page is `/forge/forge-<id>`).

### 3.2 Required contents

| Item | Rule |
|---|---|
| `agent.yaml` | Manifest, §4. |
| `README.md` | Must contain these six level-2 headings, in this order: `What it does`, `Quick start`, `Configuration`, `How it works`, `Examples`, `Limitations`. Starts with the `ci.yml` badge (see §6.3 for what it reflects). |
| `.env.example` | Every variable the agent reads, each with a working default. Must set `MODEL_PROVIDER` (equal to the first entry of `providers` in `agent.yaml`) and `MODEL_ID`. At least one alternative provider is shown commented out. |
| `examples/` | At least one pair `<name>.input.<ext>` and `<name>.output.<ext>`, committed. The output is a real run of the agent, not hand-written. |
| Tests | In the language's normal place. They must pass with no API key and no network; the LLM is replaced by a stub (§6.2). |
| Build file | The language's standard one: `pyproject.toml` (uv) for Python, `package.json` for TypeScript, `pom.xml` or `build.gradle(.kts)` for JVM. Dependencies are pinned through the lockfile (`uv.lock`, `package-lock.json`, Maven/Gradle versions). |

### 3.3 Rules

- No code or packages shared between folders, and no imports across folders. A folder copied out of the repo works on its own.
- Never commit `.env`, secrets, or real customer data. The root `.gitignore` excludes `.env`, and gitleaks runs in CI.
- Example inputs are illustrative or cleared for publication, and say which in the README's Examples section.

## 4. `agent.yaml` manifest

```yaml
id: spec
name: Forge Spec
framework: strands
language: python
status: beta
description: "Turns notes, transcripts and docs into epics, stories and acceptance criteria"
catalog: https://wexlai.com/forge/forge-spec
providers: [openai, anthropic, bedrock]
commands:
  setup: uv sync
  test: uv run pytest
  example: uv run forge-spec examples/refinement-call.input.txt
runtime:
  python: "3.12"
maintainers: ["@wexlai/forge"]
```

| Key | Required | Rule |
|---|---|---|
| `id` | yes | Lowercase slug `[a-z0-9-]+`. |
| `name` | yes | Display name. |
| `framework` | yes | One of the allowed frameworks list in `tools/forge_repo.py`. Initial list: `strands`, `crewai`, `spring-ai`, `embabel`, `langgraph`, `autogen`, `pydantic-ai`, `openai-agents`, `claude-agent-sdk`, `mastra`, `semantic-kernel`, `adk`. Adding one is a one-line PR. |
| `language` | yes | One of `python`, `typescript`, `java`, `kotlin`, `go`, `csharp`. |
| `status` | yes | `experimental`, `beta`, `live`, or `deprecated`. |
| `description` | yes | One line, at most 120 characters. |
| `catalog` | no | URL of the website page, if one exists. |
| `providers` | yes | Non-empty list from `anthropic`, `bedrock`, `openai`, `azure-openai`, `vertex`, `gemini`, `ollama`. The first is the `.env.example` default. |
| `commands.setup`, `commands.test`, `commands.example` | yes | Run from the folder root. |
| `runtime` | yes | Exactly one key (`python`, `node`, `java`, `go`, `dotnet`) giving the toolchain version. CI uses it to set up the runner. |
| `maintainers` | yes | GitHub users or teams. |

## 5. Repo tooling: `tools/forge_repo.py`

A single Python 3.12 script. Its only dependency is PyYAML, run with `uv run --with pyyaml`.

- `validate [folder…]` checks every `forge-*` folder (or the ones named):
  - the manifest exists and is valid against §4;
  - the folder name matches §3.1;
  - the required files from §3.2 exist;
  - the README headings are present and in order;
  - `MODEL_PROVIDER` in `.env.example` equals `providers[0]`;
  - `examples/` has at least one input/output pair.
  It prints every failure as `folder: message` and exits non-zero if there are any.
- `index` rewrites the table between `<!-- agents:start -->` and `<!-- agents:end -->` in the root README. Columns: Agent (name, linked to the folder), Framework, Language, Status, Description, CI (badge). Rows are sorted by `id`, then by folder name, so implementations of one agent sit together. `deprecated` rows keep their place and show the status `deprecated`.
- `index --check` exits non-zero if the committed table differs from what `index` would write.
- `matrix [--changed-from <ref>]` prints JSON for the CI matrix: one entry per folder, with its folder name, `runtime`, `commands.setup` and `commands.test`. With `--changed-from`, it lists only folders with changed files, unless `tools/`, `templates/` or `.github/` changed, in which case it lists all of them.
- `stale --days 120` prints non-deprecated folders whose last commit (`git log -1 -- <folder>`) is older than the threshold.

`tools/tests/` covers each command with fixture folders (valid, and each kind of invalid).

`templates/agent/` is not a `forge-*` folder, so `validate` ignores it. CI copies it into a temporary `forge-example-strands-python` and checks that it passes `validate`, with its placeholders filled in by the test.

## 6. CI and freshness

### 6.1 Workflows

| Workflow | Trigger | Does |
|---|---|---|
| `validate.yml` | PR, push to main | `forge_repo.py validate`, `index --check`, `pytest tools/tests`, template check, gitleaks. |
| `ci.yml` | PR, push to main, nightly schedule, `workflow_dispatch` with optional `agent` input | Detect job runs `matrix` (changed-only on PR and push; all on schedule; one folder on dispatch with `agent`). Matrix job per folder sets up the toolchain from `runtime` (setup-python + setup-uv, setup-node, setup-java with Temurin, setup-go, setup-dotnet), then runs `setup` and `test` in that folder. |
| `live-examples.yml` | `workflow_dispatch`, weekly schedule | For each non-deprecated folder: copy `.env.example` to `.env`, inject provider secrets (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, AWS credentials for Bedrock), run `setup` and `example`. Upload outputs as artifacts. Open or update a GitHub issue labelled `live-example-failure` and `agent:<folder>` on failure. Never blocks PRs. |
| `staleness.yml` | Monthly schedule | Runs `stale --days 120`; opens or updates one issue per stale folder titled "Refresh or deprecate <folder>". |

### 6.2 Tests without keys

Each agent's tests replace the model with a stub that returns canned responses, using whatever the framework offers (a custom model class or a mocked client). The tests exercise the agent's own code: prompt assembly, tool wiring, parsing and validating the structured output, rendering. They do not test the model's quality. Model quality is checked by the live run and by reading the committed example output.

### 6.3 Per-agent badge

Each folder's README badge shows the status of `ci.yml` for that folder. Because GitHub badges are per workflow, not per matrix entry, the nightly scheduled run is the source of truth. The badge links to `ci.yml` runs and the README row in the index shows the same badge. If per-folder precision turns out to matter, a later change can publish per-folder status JSON to a shields.io endpoint. That is out of scope here.

### 6.4 Renovate

`renovate.json` at the root:

- enables the pip/uv, npm, Maven and Gradle managers;
- groups updates per folder (`additionalBranchPrefix` from the parent directory);
- automerges minor and patch updates when CI passes;
- leaves majors for a person to review;
- runs on a weekly schedule.

## 7. Governance

- `LICENSE` (Apache-2.0) and `NOTICE`. No per-file licence headers.
- `CONTRIBUTING.md`: how to add an agent (copy `templates/agent/`, rename, fill `agent.yaml`, follow §3, run `validate` and the folder's tests, run `index`, open a PR). DCO sign-off (`git commit -s`) is required; a DCO GitHub App or check enforces it.
- `SECURITY.md`: report privately through GitHub Security Advisories or to bharat@wexl.in. Do not open public issues for vulnerabilities.
- `CODE_OF_CONDUCT.md`: Contributor Covenant 2.1, contact bharat@wexl.in.
- `CODEOWNERS`: `* @wexlai/forge`.
- Branch protection on `main` (set by a maintainer in GitHub; documented in CONTRIBUTING): PRs required; `validate` and `ci` must pass.

## 8. Website tie-in

- An agent's catalog page sets `proof.repo` to its folder URL, e.g. `https://github.com/wexlai/forge-agents/tree/main/forge-spec-strands-python`. When an agent has several implementations, the page links to the `live` one, or else the most complete one.
- §11.1 of `wexlai-site/docs/forge-catalog-requirements.md` is rewritten to match this design: one monorepo, folder naming, everything open, freshness enforced by Renovate and the staleness job. That edit is part of this work.
- Agent pages' `proof.repo` values are not changed in this work. Each one changes only when its folder exists and passes CI.

## 9. Reference agent: `forge-spec-strands-python`

The first agent, built from the template, proves the whole path: template → validate → CI with stubbed tests → live example → index row.

- **Does:** reads a meeting transcript or notes file and writes epics and user stories with Given/When/Then acceptance criteria. Every criterion cites the line or timestamp it came from, and open questions and assumptions are listed separately. This matches the existing Forge Spec catalog page.
- **Framework:** Strands Agents SDK (Python), using the SDK's structured-output support to return a typed result (Pydantic models: `SpecResult` → `Epic` → `Story` → `AcceptanceCriterion` with `source_ref`; plus `open_questions` and `assumptions`).
- **Output:** Markdown (the format on the website page) by default; `--format jira-csv` writes a Jira-importable CSV from the same typed result.
- **Providers:** `openai` (default, `MODEL_ID=gpt-5`), `anthropic`, `bedrock`, selected by `MODEL_PROVIDER`.
- **Interface:** CLI `forge-spec <input-file> [--format markdown|jira-csv] [--out <file>]`. Reads `.txt`, `.md`, `.vtt`.
- **Example:** `examples/refinement-call.input.txt` is the website's `forge-spec-input.txt`; `examples/refinement-call.output.md` is regenerated by a real run of this agent and committed. If it differs from the website's `forge-spec-output.md`, the website's copy gets updated later, in the site repo.
- **Tests (no key):** the stub model returns a fixed `SpecResult`; tests cover input loading per format, prompt assembly, Markdown and CSV rendering, provider selection from env, and a clear error when the selected provider's key is missing.
- **Out of scope:** `.docx` and `.pdf` input, Jira API sync, and a web UI.

## 10. Initial state changes

- `git init` in this folder, remote `origin` = `git@github.com:wexlai/forge-agents.git`, default branch `main`. Pushing is done by a person, or by me when asked.
- Remove the empty `forge-spec-strands-typescript/` folder. It would fail `validate`; it comes back when that agent is designed and built.
- The empty `forge-spec-strands-python/` folder is filled by §9.

## 11. Out of scope

- Skills and steering content (they go in `forge-skills`).
- Any agent other than `forge-spec-strands-python`. Each later agent gets its own short spec and plan.
- A shared cross-framework contract or eval harness (D3).
- Per-matrix-entry badge endpoints (§6.3).
- Publishing packages to PyPI, npm or Maven Central.
- Changing agent pages on the website.
