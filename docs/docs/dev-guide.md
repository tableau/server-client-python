---
title: Developer Guide
layout: docs
---

This topic describes how to contribute to the Tableau Server Client (Python) project.

* TOC
{:toc}

## Submitting your first patch

1. Make sure you have [signed the CLA](http://tableau.github.io/#contributor-license-agreement-cla)

1. Fork the repository.

   We follow the "Fork and Pull" model as described [here](https://help.github.com/articles/about-collaborative-development-models/).

1. Clone your fork:

   ```shell
   git clone git@github.com:tableau/server-client-python.git
   ```

1. Run the tests to make sure everything is peachy:

   ```shell
   python setup.py test
   ```

1. Set up the feature, fix, or documentation branch.

   It is recommended to use the format issue#-type-description (e.g. 13-fix-connection-bug) like so:

   ```shell
   git checkout -b 13-feature-new-stuff
   ```

1. Code and commit!

   Here's a quick checklist for ensuring a good pull request:

   - Only touch the minimal amount of files possible while still accomplishing the goal.
   - Ensure all indentation is done as 4-spaces and your editor is set to unix line endings.
   - The code matches PEP8 style guides. If you cloned the repo you can run `pycodestyle .`
   - Keep commit messages clean and descriptive.
     If the PR is accepted it will get 'Squashed' into a single commit before merging, the commit messages will be used to generate the Merge commit message.

1. Add tests.

   All of our tests live under the `test/` folder in the repository.
   We use `unittest` and the built-in test runner `python setup.py test`.
   If a test needs a static file, like a twb/twbx, it should live under `test/assets/`

1. Update the documentation.

   Our documentation is written in markdown and built with Jekyll on Github Pages. All of the documentation source files can be found in `docs/docs`.

   When adding a new feature or improving existing functionality we may ask that you update the documentation along with your code.

   If you are just making a PR for documentation updates (adding new docs, fixing typos, improving wording) the easiest method is to use the built in `Edit this file` in the Github UI

1. Submit to your fork.

1. Make a PR as described [here](https://help.github.com/articles/creating-a-pull-request-from-a-fork/) against the 'development' branch.

1. Wait for a review and address any feedback.
   While we try and stay on top of all issues and PRs it might take a few days for someone to respond. Politely pinging
   the PR after a few days with no response is OK, we'll try and respond with a timeline as soon as we are able.

1. That's it! When the PR has received :rocket:'s from members of the core team they will merge the PR


## Adding new features

1. Create an endpoint class for the new feature, following the structure of the other endpoints. Each endpoint usually
   has get, post, update, and delete operations that require making the url, creating the XML request if necesssary,
   sending the request, and creating the target item object based on the server response.

1. Create an item class for the new feature, following the structure of the other item classes. Each item has properties
   that correspond to what attributes are sent to/received from the server (refer to docs amd Postman for attributes).
   Some items also require constants for user input that are limited to specific strings. After making all the
   properties, make the parsing method that takes the server response and creates an instances of the target item. If
   the corresponding endpoint class has an update function, then parsing is broken into multiple parts (refer to another
   item like workbook or datasource for example).

1. Add testing by getting real xml responses from the server, and asserting that all properties are parsed and set
   correctly.

1. Add a sample to show users how to use the new feature.

<!--
### Updating Documentation

### Running Tests
-->
