# Contributing

We welcome contributions to this project!

Contribution can include, but are not limited to, any of the following:

* File an Issue
* Request a Feature
* Implement a Requested Feature
* Fix an Issue/Bug
* Add/Fix documentation

## Issues and Feature Requests

To submit an issue/bug report, or to request a feature, please submit a [GitHub issue](https://github.com/tableau/server-client-python/issues) to the repo.

If you are submitting a bug report, please provide as much information as you can, including clear and concise repro steps, attaching any necessary
files to assist in the repro.  **Be sure to scrub the files of any potentially sensitive information.  Issues are public.**

For a feature request, please try to describe the scenario you are trying to accomplish that requires the feature.  This will help us understand
the limitations that you are running into, and provide us with a use case to know if we've satisfied your request.

### Making Contributions

Refer to the [Developer Guide](https://tableau.github.io/server-client-python/docs/dev-guide) which explains how to make contributions to the TSC project.

## Running Tests

### Unit tests

```bash
pip install -e ".[test]"
pytest
```

### End-to-end tests

E2e tests run against a real Tableau server and are kept in `test_e2e/`. They are excluded from the default `pytest` run.

**Required environment variables:**

| Variable | Description |
|---|---|
| `TABLEAU_SERVER` | Server URL, e.g. `https://10ax.online.tableau.com/` |
| `TABLEAU_SITE` | Site content URL |
| `TABLEAU_TOKEN` | Personal access token value |
| `TABLEAU_TOKEN_NAME` | Personal access token name |
| `TABLEAU_PROJECT` | Project to publish test content into (defaults to `Default`) |

**Run:**

```bash
TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=mytoken TABLEAU_PROJECT="My Project" \
pytest test_e2e/
```
