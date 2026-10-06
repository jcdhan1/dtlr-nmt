# Digital Techniques for Language Revival: Neural Machine Translation API

Neural Machine Translation API for the DTLR website. Built upon [argos-translate](https://github.com/argosopentech/argos-translate) using custom models involving languages ranging from safe to critically endangered.

![CI/CD Pipeline](https://github.com/jcdhan1/dtlr-nmt/actions/workflows/ci-cd.yml/badge.svg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Usage

Argos Translate Models in `models/` are installed automatically when none are already installed. To overwrite installed models that are identically named, run the application with `--reinstall-models`.

## Environment configuration

The API uses the following environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `APP_ENV` | Set to `production` to enable the configured CORS origin allowlist. The only accepted values are `development` and `production`. | `development` |
| `ALLOWED_ORIGINS` | A comma-separated list of browser origins permitted to access the API when `APP_ENV=production`. Each origin must include its scheme and host, and any required port, but must not include a path or trailing slash. Required in production. | Not set |

For example, configure production access for the hosted UI with:

```sh
export APP_ENV=production
export ALLOWED_ORIGINS=https://your-ui.example.com
```

Multiple origins can be listed, separated by commas:

```sh
export ALLOWED_ORIGINS=https://your-ui.example.com,https://staging-ui.example.com
```

In development, CORS allows requests from any browser origin. CORS only controls whether browsers can access API responses; it does not prevent direct requests from scripts or other non-browser clients. Use network or application-level access controls if the API must reject those clients.
