---
title: Developer Guide
layout: docs
---

This topic describes how to contribute to the Tableau Server Client (Python)
project:

<!-- prettier-ignore -->
- TOC
{:toc}

---

## Submit your first patch

This section will get you started with the basic workflow, describing how to
create your own fork of the repository and how to open a pull request (PR) to
add your contributions to the **development** branch.

### Get the source code and set up your branch

1. Fork the repository. We follow the "Fork and Pull" model as described
   [here](https://help.github.com/articles/about-collaborative-development-models/).

1. Clone your fork:

   ```shell
   git clone git@github.com:<user-name>/server-client-python.git
   cd server-client-python
   ```

1. Install dependencies and run the tests to make sure everything is passing:

   ```shell
   python -m pip install --upgrade pip
   pip install -e .[test] build
   pytest test
   ```

1. Configure a remote that points to the source (upstream) repository:
   ```shell
   git remote add upstream https://github.com/tableau/server-client-python
   ```
   More information about configuring a remote for a fork can be found [here](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/configuring-a-remote-for-a-fork).
   
1. Sync your fork:
   ```shell
   git fetch upstream
   ```

1. Set up the feature/fix branch (based off the source `development` branch). It is
   recommended to use the format issue#-type-description, for example:

   ```shell
   git checkout -b 13-fix-connection-bug upstream/development
   ```

For documentation changes, see the documentation section below.

### Code and commit

Here's a quick checklist to follow when coding to ensure a good pull request
(PR) that will pass the PR checks:

- Only touch the fewest number of files possible while still accomplishing the
  goal.
- Ensure all indentation is done as 4-spaces and your editor is set to unix line
  endings.
- The code matches PEP8 style guides, enforced by the black formatter. Make sure to run
  `black --line-length 120 tableauserverclient samples test` to catch and fix any style
  issues before submitting your pull request. (Run black with the `--check` option if
  you want to check whether formatting is valid without changing any files.)
- Ensure the Mypy static type checker is still passing by running
  `mypy --show-error-codes --disable-error-code misc --disable-error-code import tableauserverclient test`.
- Keep commit messages clean and descriptive.

### Use git pre-commit hook

Setting up a git pre-commit hook can be helpful to ensure your code changes follow
the project style conventions before pushing and creating a pull request.

To configure the pre-commit hook, navigate to your local clone/fork of the
`server-client-python` project and change into the `.git/hooks` directory.
Create a file `pre-commit` with the contents below and mark it as executable
(`chmod +x pre-commit`).

To test that the hook is working correctly, make a style-inconsistent change (for
example, changing some indentation to not be a multiple of 4), then try to commit
locally. You should get a failure with an explanation from black with the
issue.

```shell
#!/bin/sh

# only check if on a code branch (i.e. skip if on a docs branch)
if [ -e tableauserverclient/__init__.py ];
then
   # check for style conventions in all code dirs
   echo Running black format check
   black --check --line-length 120 tableauserverclient samples test
   echo Running mypy type checking
   mypy --show-error-codes --disable-error-code misc --disable-error-code import tableauserverclient test
fi
```

Windows users: The first line of the sample script above will need to be adjusted
depending on how and where git is installed on your system, for example:

```shell
#!C:/Program\ Files/Git/usr/bin/sh.exe
```

### Adding features

1. Create an endpoint class for the new feature, following the structure of the
   other endpoints. Each endpoint usually has `get`, `post`, `update`, and
   `delete` operations that require making the url, creating the XML request if
   necessary, sending the request, and creating the target item object based on
   the server response.

1. Create an item class for the new feature, following the structure of the
   other item classes. Each item has properties that correspond to what
   attributes are sent to/received from the server (refer to docs and Postman
   for attributes). Some items also require constants for user input that are
   limited to specific strings. After making all the properties, make the
   parsing method that takes the server response and creates an instances of the
   target item. If the corresponding endpoint class has an update function, then
   parsing is broken into multiple parts (refer to another item like workbook or
   datasource for example).

1. Add testing by getting real xml responses from the server, and asserting that
   all properties are parsed and set correctly.

1. Add type hints to all new classes and functions added. Including type hinting
   on unit tests.

2. Add a sample to show users how to use the new feature. Try to keep the command
   line arguments of your sample consistent with the [Samples documentation page](samples)
   and with other samples.

3. Add documentation (most likely in api-ref.md) in a separate pull request
   (see more below).

### Add tests

All of our tests live under the `test/` folder in the repository. We use
`pytest` and the built-in test runner `python setup.py test`.

Follow the structure of existing tests, especially if new server responses
are going to be mocked.

If a test needs a
static file, like a .twb/.twbx/.xml, it should live under `test/assets/`

Make sure that all tests are passing before submitting your pull request.

### Update the documentation

When adding a new feature or improving existing functionality we ask that you
update the documentation along with your code. See the Updating documentation
section below for details.

### Commit changes to your fork and open a pull request

1. Make a PR as described
   [here](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork)
   against the **development** branch for code changes.

1. In your first pull request, the Salesforce Contributor License Agreement bot
   (`salesforce-cla`) will add a comment with instructions to follow.

1. Wait for a review and address any feedback. While we try and stay on top of
   all issues and PRs it might take a while for someone to respond. Politely
   pinging the PR after a few days with no response is OK; we'll try and respond
   with a timeline as soon as we are able.

1. That's it! When the PR has received
   ![](https://github.githubassets.com/images/icons/emoji/unicode/1f680.png){:height="5%"
   width="5%"} (:rocket:'s) from members of the core team they will merge the
   PR. **Maintainers:** Make sure to choose a Squash Merge when merging a PR into
   the `development` branch; that will keep the timeline clean with just the
   final result from each PR.

## Updating documentation

Our documentation is written in Markdown (specifically
[kramdown](https://kramdown.gettalong.org/quickref.html)) and built with Jekyll
on GitHub Pages.

All of the documentation source files can be found in `/docs` folder in the
**gh-pages** branch. The docs are hosted on the following URL:
<https://tableau.github.io/server-client-python>.

To make changes or additions to the documentation, please create a pull request
against the **gh-pages** branch. Because the docs are in a separate branch, you
would need to create a separate PR for your code versus docs changes. It's helpful
to link them to each other in comments so it's clear they go together.

### Running docs locally

To preview and run the documentation locally, these are the steps:

1. Install [Ruby](https://www.ruby-lang.org/en/documentation/installation/) (v2.5.0 or higher).

1. Install [Bundler](https://bundler.io/).

1. Install the project dependencies (which includes Jekyll) by running `bundle install`. (In the future you can run `bundle update` to catch any new dependencies.)

1. Run the Jekyll site locally with `bundle exec jekyll serve`.

1. In your browser, connect to <http://127.0.0.1:4000/server-client-python/> to preview the changes. As long as the Jekyll serve process is running, it will rebuild any new file changes automatically.

For more details, see the GitHub Pages topic on
[testing locally](https://docs.github.com/en/github/working-with-github-pages/testing-your-github-pages-site-locally-with-jekyll).

## Release process (maintainers)

To do a release and publish a new version to [PyPI](https://pypi.org/project/tableauserverclient/),
follow these steps:

1. Do a `development` to `master` branch merge. This should be a regular merge
   (not a squash) to ensure all individual commits are visible.

1. (Optional) Do a test publish to PyPI without creating the next version tag.
   This will create a pre-release package with a version like `0.30.post0.dev`.

1. On a local clone of the repo, create and push the tag for the *next* version
   (in this example it's "v0.31"):

   ```shell
   git fetch
   git fetch --tags
   git checkout master
   git pull
   git log  # confirm most recent commit on master is the new release commit
   git tag -a v0.31 -m 'Release v0.31'
   git push origin tag v0.31
   ```

1. Publish the updated release to PyPI by running the [Publish](https://github.com/tableau/server-client-python/actions/workflows/publish-pypi.yml)
   job and choosing the `master` branch.

1. The job should just take a few minutes to complete, then check the updated
   package exists on [PyPI](https://pypi.org/project/tableauserverclient/).

1. Create a release in GitHub with the title like "v0.31" and release notes
   with changes from the last release. You can try the automatic generation
   of notes, or just create a list of merged PR titles with reference PR numbers.
