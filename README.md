# Tableau Server Client (Python)

[![Tableau Supported](https://img.shields.io/badge/Support%20Level-Tableau%20Supported-53bd92.svg)](https://www.tableau.com/support-levels-it-and-developer-tools) [![Build Status](https://github.com/tableau/server-client-python/actions/workflows/run-tests.yml/badge.svg)](https://github.com/tableau/server-client-python/actions)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ftableau%2Fserver-client-python.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ftableau%2Fserver-client-python?ref=badge_shield)

Use the Tableau Server Client (TSC) library to increase your productivity as you interact with the Tableau Server REST API. With the TSC library you can do almost everything that you can do with the REST API, including:

* Publish workbooks and data sources.
* Create users and groups.
* Query projects, sites, and more.

This repository contains Python source code for the library and sample files showing how to use it. As of September 2024, support for Python 3.7 and 3.8 will be dropped - support for older versions of Python aims to match https://devguide.python.org/versions/

To see sample code that works directly with the REST API (in Java, Python, or Postman), visit the [REST API Samples](https://github.com/tableau/rest-api-samples) repo.

For more information on installing and using TSC, see the documentation:
<https://tableau.github.io/server-client-python/docs/>

### Authenticating from environment variables

The [`samples/login.py`](samples/login.py) sample shows three ways to
supply Tableau credentials, in precedence order:

1. Command-line arguments (`--server`, `--username`, `--password`,
   `--token-name`, `--token-value`, `--site`, `--api-version`)
2. `TABLEAU_*` environment variables — one way to keep credentials out
   of your source code:
   * `TABLEAU_SERVER` (required) — server URL
   * `TABLEAU_SITE` (optional) — site content URL; `""` for the default site
   * `TABLEAU_TOKEN_NAME` + `TABLEAU_TOKEN` — personal access token (preferred)
   * `TABLEAU_USERNAME` + `TABLEAU_PASSWORD` — basic auth (fallback)
   * `TABLEAU_API_VERSION` (optional) — pin REST API version; otherwise
     the sample negotiates with the server
3. Pass `--interactive` to prompt for a missing password on a terminal
   via `getpass` instead of exporting it. PATs are never prompted for.

Names are `TABLEAU_`-prefixed to avoid collision with generic shell
variables like `USERNAME` (which Windows sets automatically).

To contribute, see our [Developer Guide](https://tableau.github.io/server-client-python/docs/dev-guide). A list of all our contributors to date is in [CONTRIBUTORS.md].

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ftableau%2Fserver-client-python.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Ftableau%2Fserver-client-python?ref=badge_large)
