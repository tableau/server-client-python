# Contributing

We welcome contributions to this project!

Contribution can include, but are not limited to, any of the following:

* File an Issue
* Request a Feature
* Implement a Requested Feature
* Fix an Issue/Bug
* Add/Fix documentation

Contributions must follow the guidelines outlined on the [Tableau Organization](http://tableau.github.io/) page, though filing an issue or requesting
a feature do not require the CLA.

## Issues and Feature Requests

To submit an issue/bug report, or to request a feature, please submit a [GitHub issue](https://github.com/tableau/server-client-python/issues) to the repo.

If you are submitting a bug report, please provide as much information as you can, including clear and concise repro steps, attaching any necessary
files to assist in the repro.  **Be sure to scrub the files of any potentially sensitive information.  Issues are public.**

For a feature request, please try to describe the scenario you are trying to accomplish that requires the feature.  This will help us understand
the limitations that you are running into, and provide us with a use case to know if we've satisfied your request.

### Label usage on Issues

The core team is responsible for assigning most labels to the issue.  Labels
are used for prioritizing the core team's work, and use the following
definitions for labels.

The following labels are only to be set or changed by the core team:

* **bug** - A bug is an unintended behavior for existing functionality. It only relates to existing functionality and the behavior that is expected with that functionality.  We do not use **bug** to indicate priority.
* **enhancement** - An enhancement is a new piece of functionality and is related to the fact that new code will need to be written in order to close this issue.  We do not use **enhancement** to indicate priority.
* **CLARequired** - This label is used to indicate that the contribution will require that the CLA is signed before we can accept a PR.  This label should not be used on Issues
* **CLANotRequired** - This label is used to indicate that the contribution does not require a CLA to be signed.  This is used for minor fixes and usually around doc fixes or correcting strings.
* **help wanted** - This label on an issue indicates it's a good choice for external contributors to take on. It usually means it's an issue that can be tackled by first time contributors.

The following labels can be used by the issue creator or anyone in the
community to help us prioritize enhancement and bug fixes that are
causing pain from our users.  The short of it is, purple tags are ones that
anyone can add to an issue:

* **Critical** - This means that you won't be able to use the library until the issues have been resolved.  If an issue is already labeled as critical, but you want to show your support for it, add a +1 comment to the issue.  This helps us know what issues are really impacting our users.
* **Nice To Have** - This means that the issue doesn't block your usage of the library, but would make your life easier.  Like with critical, if the issue is already tagged with this, but you want to show your support, add a +1 comment to the issue.

## Fixes, Implementations, and Documentation

For all other things, please submit a PR that includes the fix, documentation, or new code that you are trying to contribute.  More information on
creating a PR can be found in the [Development Guide](https://tableau.github.io/server-client-python/docs/dev-guide).

If the feature is complex or has multiple solutions that could be equally appropriate approaches, it would be helpful to file an issue to discuss the
design trade-offs of each solution before implementing, to allow us to collectively arrive at the best solution, which most likely exists in the middle
somewhere.

## Getting Started

```shell
pip install versioneer
python setup.py build
python setup.py test
```

### Before Committing

Our CI runs include a Python lint run, so you should run this locally and fix complaints before committing as this will fail your checkin.

```shell
pycodestyle tableauserverclient test samples
```
