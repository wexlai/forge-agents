# Contributing

Each `forge-*` folder is one agent built on one framework. Folders do not share code, so a change usually touches one folder.

## Add an agent

1. Pick a folder name: `forge-<id>-<framework>` or `forge-<id>-<framework>-<language>`, lowercase with hyphens. `<id>` is the agent's catalog id (`spec`, `review`, `test`, …). The language part is optional.
2. Copy the template and fill in its placeholders:

   ```bash
   cp -R templates/agent forge-<id>-<framework>-<language>
   grep -rl "__[A-Z]*__" forge-<id>-<framework>-<language>   # every file listed needs editing
   ```

3. Fill in `agent.yaml` (see "The manifest" below), build the agent, and write tests that run without an API key: replace the model with a stub.
4. Commit at least one real example pair in `examples/`: `<name>.input.<ext>` and the `<name>.output.<ext>` the agent actually produced.
5. Check the folder and regenerate the agent table in the root README:

   ```bash
   uv run tools/forge_repo.py validate
   uv run tools/forge_repo.py index
   ```

6. Run the folder's own `commands.test`, then open a pull request.

If your framework or language is new to the repo, add it to `FRAMEWORKS` or `LANGUAGES` in `tools/forge_repo.py` in the same pull request.

## Folder standard

Every agent folder contains:

| Item | Rule |
| --- | --- |
| `agent.yaml` | The manifest. |
| `README.md` | These `##` headings, in order: What it does, Quick start, Configuration, How it works, Examples, Limitations. |
| `.env.example` | Every variable the agent reads, with working defaults. `MODEL_PROVIDER` must equal the first entry of `providers`. Show at least one alternative provider, commented out. |
| `examples/` | At least one input/output pair, produced by a real run. |
| Tests | Wherever the language normally puts them. They must pass with no API key and no network. |
| Build file | `pyproject.toml` (uv), `package.json`, `pom.xml` or `build.gradle(.kts)`, with a lockfile. |

Never commit `.env`, secrets or real customer data.

## The manifest

```yaml
id: spec
name: Forge Spec
framework: strands
language: python
status: beta            # experimental | beta | live | deprecated
description: "One line, at most 120 characters"
catalog: https://wexlai.com/forge/forge-spec   # optional
providers: [openai, anthropic, bedrock]       # first one is the .env.example default
commands:
  setup: uv sync
  test: uv run pytest
  example: uv run forge-spec examples/refinement-call.input.txt
runtime:
  python: "3.12"        # exactly one of python, node, java, go, dotnet; quote the version
maintainers: ["@wexlai/forge"]
```

## Sign your commits (DCO)

We use the [Developer Certificate of Origin](https://developercertificate.org/). Sign off every commit:

```bash
git commit -s -m "your message"
```

## For maintainers

- Branch protection on `main`: require a pull request, and require the `validate` and `ci` checks to pass. `ci` is the summary job in `ci.yml`; do not require the per-folder jobs, which only run when their folder changes.
- Install the [DCO GitHub App](https://github.com/apps/dco) on the repository.
- Install the [Renovate GitHub App](https://github.com/apps/renovate) on the repository.
- Repository secrets for the weekly live run: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and optionally `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (with repository variable `AWS_REGION`).
- `CODEOWNERS` names the `@wexlai/forge` team; create it in the organisation if it does not exist.
