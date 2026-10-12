# Forge agents

[![validate](https://github.com/wexlai/forge-agents/actions/workflows/validate.yml/badge.svg)](https://github.com/wexlai/forge-agents/actions/workflows/validate.yml)
[![ci](https://github.com/wexlai/forge-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/wexlai/forge-agents/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Open-source agents for the software development lifecycle, built by [WeXL](https://wexlai.com) on different agent frameworks: Strands, CrewAI, Spring AI, Embabel and others. They are the runnable source behind the [Forge Catalog](https://wexlai.com/forge).

Each folder is one agent built on one framework. Folders share no code: copy one out of this repository and it still works.

## Agents

<!-- agents:start -->
| Agent | Framework | Language | Status | Description |
| --- | --- | --- | --- | --- |
| [Forge Spec](forge-spec-strands-python/) | strands | python | beta | Turns notes, transcripts and docs into epics, stories and acceptance criteria |
<!-- agents:end -->

## Run an agent

Every folder works the same way:

```bash
cd forge-spec-strands-python
cp .env.example .env        # then add your API key
```

Then run the `setup` and `example` commands from the folder's `agent.yaml`. The folder's README explains its options and which model providers it supports.

## Folder names

`forge-<agent>-<framework>[-<language>]`, for example `forge-spec-strands-python`. The same agent can appear more than once, built on different frameworks.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Report security problems privately, as described in [SECURITY.md](SECURITY.md).

## Licence

[Apache-2.0](LICENSE). Copyright 2026 WeXL.
