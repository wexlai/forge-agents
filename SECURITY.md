# Security policy

## Reporting a vulnerability

Please report security problems privately. Do not open a public issue.

- Use GitHub's private vulnerability reporting: **Security → Report a vulnerability** on this repository, or
- email **bharat@wexl.in**.

Include the agent folder, what you found, and how to reproduce it. We will acknowledge your report within five working days and keep you informed until it is fixed.

## Scope

Every `forge-*` folder in this repository is in scope. Model providers' own services are not; report those to the provider.

## Secrets

Agents read API keys from environment variables or a local `.env` file, which is git-ignored. If you find a committed key, report it as above; we will revoke it.
