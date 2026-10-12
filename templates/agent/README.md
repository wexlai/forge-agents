# __NAME__ (__FRAMEWORK__, __LANGUAGE__)

[![ci](https://github.com/wexlai/forge-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/wexlai/forge-agents/actions/workflows/ci.yml)

__DESCRIPTION__

## What it does

What goes in, what comes out, and who uses it. Two or three sentences.

## Quick start

```bash
cp .env.example .env    # add your API key
uv sync
uv run forge-__ID__ examples/example.input.txt
```

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `MODEL_PROVIDER` | `openai` | Which provider to call |
| `MODEL_ID` | `gpt-5` | Which model |
| `OPENAI_API_KEY` | | Key for the OpenAI provider |

## How it works

How the agent is put together in __FRAMEWORK__: the steps, the tools it calls, and how the output is checked.

## Examples

| Input | Output |
| --- | --- |
| [example.input.txt](examples/example.input.txt) | [example.output.md](examples/example.output.md) |

Say where the example input came from (illustrative, or cleared for publication).

## Limitations

What it does not do, and where a person still needs to check its work.
