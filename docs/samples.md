---
title: Samples
layout: docs
---

The TSC samples are included in the `samples` directory of the TSC repository [on Github](https://github.com/tableau/server-client-python/tree/master/samples).

* TOC
{:toc}

## Prerequisites

Before running any of the sample scripts, install the TSC library in your Python environment following the [Get Started](https://tableau.github.io/server-client-python/docs/) instructions.

## Run the samples

Each of the samples accepts the following arguments:

* `--server` (required): The URL for the Tableau Server that you want to connect to.
* `--site` (optional): The site on the Server that you want to connect to.
* `--token-name` (required): The name of the personal access token used to sign into the server.
* `--token-value` (required): The value of the personal access token used to sign into the server.
* `--logging-level` (optional; `debug`, `info` or `error`): The desired log level.

To get a `token-name` and `token-value`, you will have to create personal access token first.
You can follow [Tableau's documentation](https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm#create-tokens) to do so.

Some of the samples also require additional arguments. For more information about the arguments
required by a particular sample, run the sample with the `-h` flag.

For example, if you run the following command:

```shell
python samples/publish_workbook.py -h
```

You will see that you need to enter a file path for the workbook that you want to publish.

## Samples list

The following list describes the samples available in the repository:

* `add_default_permission.py` Adds workbook default permissions for a given project.
* `create_extract_task.py` Creates extract tasks.
* `create_group.py` Creates a user group.
* `create_project.py` Creates a project in a site.
* `create_schedules.py` Creates schedules for extract refreshes and subscriptions.
* `explore_datasource.py` Queries datasources, selects a datasource, populates connections for the datasource, then updates the datasource.
* `explore_favorites.py` Queries favorites and optionally add or delete favorites.
* `explore_site.py` Interacts with sites (create, delete, and so on).
* `explore_webhooks.py` Explores webhook functions supported by the Server API.
* `explore_workbook.py` Queries workbooks, selects a workbook, populates the connections and views for a workbook, then updates the workbook.
* `export.py` Exports a view as an image, PDF, or CSV.
* `extracts.py` Interacts with extracts, including querying, deleting or creating.
* `filter_sort_groups.py` Demonstrates filtering and sorting user groups.
* `filter_sort_projects.py` Demonstrates filtering and sorting projects.
* `initialize_server.py` Sets up an existing server instance with site, workbooks and datasources.
* `kill_all_jobs.py` Kills all running jobs.
* `list.py` Lists all datasources or workbooks of a site.
* `login.py` Demonstrates logging in to the server with either username/password or personal access token.
* `metadata_query.py` Uses the metadata API to query information on a published data source.
* `move_workbook_projects.py` Moves a workbook from one project to another.
* `move_workbook_sites.py` Downloads a workbook, stores it in-memory, and uploads it to another site.
* `pagination_sample.py` Uses the Pager generator to iterate over all the items on the server.
* `publish_datasource.py` Publishes a datasource to a server.
* `publish_workbook.py` Publishes a workbook to a server.
* `query_permissions.py` Queries permissions of a given resource.
* `refresh.py` Refreshes a datasource or workbook.
* `refresh_tasks.py` Lists and runs configured tasks on a server.
* `set_refresh_schedule.py` Sets the schedule to refresh a workbook or datasource.
* `smoke_test.py` Verifies that TSC is installed correctly and is able to run.
* `update_connection.py` Updates and embeds connection credentials of a datasource.
* `update_datasource_data.py` Updates the data within a published live-to-Hyper datasource.
* `update_workbook_data_freshness_policy.py` Updates workbook data freshness policy settings.

**Note**: For all of the samples, ensure that your Tableau Server user account has permission to access the resources. Also keep in mind that some example operations (like create group) are not allowed on Tableau Cloud.
