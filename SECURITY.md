# Security policy

## Reporting a vulnerability

Report security issues privately through [GitHub Security Advisories](https://github.com/cameronenochs/second-language-llm-tprs/security/advisories/new).

Do not open a public issue for a suspected vulnerability.

## Supported versions

Only the `main` branch is supported.

## Secrets

`ELEVENLABS_API_KEY` is read from the environment at call time. Do not commit it, a filled-in `tprs.config.json`, or files under `output/`.
