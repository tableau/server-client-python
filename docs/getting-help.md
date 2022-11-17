---
title: Getting Help
layout: docs
---

This project is using [GitHub issues](https://github.com/tableau/server-client-python/issues) for tracking help requests, bugs, and feature requests.

## Filing an issue

As a first step, please search existing issues to see if your problem or bug is already reported.

If not, go ahead and create a new issue and include the following:

* Tableau Server version (or indicate if using Tableau Cloud)
* TSC library version
* Python version
* Environment (Mac, Win, Linux)
* Code snippet
* Expected vs actual results

If troubleshooting a problem could be helped by capturing the REST API requests and responses, see the [Troubleshooting](troubleshooting.md) page for more info.

<div class="alert alert-warning">
<span class="glyphicon glyphicon-warning-sign" aria-hidden="true"></span> Important: do not include in a GitHub issue anything private such as usernames, passwords, or access tokens. Also be careful when posting any API responses to sanitize and remove any sensitive content.
</div>

Some labels might be applied to help organize the open issues after some investigation:

* Bug: A bug in TSC itself (not working as expected)
* Docs: Documentation which is either missing or needs to be clarified
* Enhancement: An enhancement request (a new capability in TSC)
* Server-side enhancement: An enhancement which requires changes to the backend Tableau Server REST APIs
* Help wanted: A troubleshooting request asking for community help

## Contributing a pull request

Pull requests are also welcome! See the [Developer Guide](dev-guide) for more details on the process.

You can also start a conversation as an issue first and then create a pull request if the idea looks do-able.
