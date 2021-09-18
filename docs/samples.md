---
title: Samples
layout: docs
---

The TSC samples are included in the `samples` directory of the TSC repository [on Github](https://github.com/tableau/server-client-python/tree/master/samples).

* TOC
{:toc}

## Run the samples

Each of the samples requires the following arguments:

* `--server`. The URL for the Tableau Server that you want to connect to.
* `--username`. The user name of the Tableau Server account that you want to use. When you run the samples, you are
  prompted for a password for the user account that you enter.

Additionally, some of the samples require that you enter other arguments when you run them. For more information about
the arguments required by a particular sample, run the sample with the `-h` flag to see the help output.

For example, if you run the following command:

```shell
python samples/publish_workbook.py -h
```

You might see that you need to enter a server address, a user name, and a file path for the workbook that you want to
publish.

## Samples list

The following list describes the samples available in the repository:

* `add_default_permission.py` Adds workbook default permissions for a given project.
* `create_group.py` Creates a user group.
* `create_project.py` Creates a project in a site.
* `create_schedules.py` Creates schedules for extract refreshes and subscriptions.
* `download_view_image.py` Downloads an image of a specified view.
* `explore_datasource.py` Queries datasources, selects a datasource, populates connections for the datasource, then updates the datasource.
* `explore_webhooks.py` Explores webhook functions supported by the Server API.
* `explore_workbook.py` Queries workbooks, selects a workbook, populates the connections and views for a workbook, then updates the workbook.
* `export.py` Exports a view as an image, PDF, or CSV.
* `export_wb.py` Exports a PDF containing all views in a workbook.
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
* `set_http_options.py` Demonstrates HTTP options for the server and specifically for downloading workbooks.
* `set_refresh_schedule.py` Sets the schedule to refresh a workbook or datasource.
* `update_connection.py` Updates and embeds connection credentials of a datasource.

**Note**: For all of the samples, ensure that your Tableau Server user account has permission to access the resources. Also keep in mind that some example operations (like create group) are not allowed on Tableau Online.
