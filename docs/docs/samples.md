---
title: Samples
layout: docs
---

The TSC samples are included in the `samples` directory of the TSC repository [on Github](https://github.com/tableau/server-client-python).

* TOC
{:toc}

## Run the samples

Each of the samples requires the following arguments:

* `--server`. The URL for the Tableau Server that you want to connect to.
* `--username`. The user name of the Tableau Server account that you want to use. When you run the samples, you are
  prompted for a password for the user account that you enter.

Additionally, some of the samples require that you enter other arguments when you run them. For more information about
the arguments required by a particular sample, run the argument without arguments to see the help output.

For example, if you run the following command:

```
python samples/publish_workbook.py
```

You might see that you need to enter a server address, a user name, and a file path for the workbook that you want to
publish.

## List of samples

The following list describes the samples available in the repository:

* `create_group.py`. Create a user group.

* `create_schedules.py`. Create scheduled extract refresh tasks and subscription tasks.

* `explore_datasource.py`. Queries all datasources, selects a datasource, populates connections for the datasource, then updates the datasource.

* `explore_workbook.py`. Queries all workbooks, selects a workbook, populates the connections and views for a workbook, then updates the workbook.

* `move_workbook_projects.py`. Updates the properties of a workbook to move the workbook from one project to another.

* `move_workbook_sites.py`. Downloads a workbook, stores it in-memory, and uploads it to another site.

* `pagination_sample.py`. Use the pagination item that is returned by many TSC calls to iterate over all the items on
  the server.

* `publish_workbook.py`. Publishes a Tableau workbook.

* `set_http_options.py`. Sets HTTP options for the server and specifically for downloading workbooks.

**Note**: For all of the samples, ensure that your Tableau Server user account has permission to access the resources
requested by the samples.

