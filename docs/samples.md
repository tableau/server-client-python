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

```
python samples/publish_workbook.py -h
```

You might see that you need to enter a server address, a user name, and a file path for the workbook that you want to
publish.

## Samples list

The following list describes the samples available in the repository:

* `create_group.py` Create a user group.

* `create_project.py` Creates a project in a site.

* `create_schedules.py` Create schedules for extract refreshes and subscriptions.

* `download_view_image.py`	Downloads an image of a specified view.

* `explore_datasource.py` Queries datasources, selects a datasource, populates connections for the datasource, then updates the datasource.

* `explore_workbook.py` Queries workbooks, selects a workbook, populates the connections and views for a workbook, then updates the workbook.

* `export.py`	Exports a view as an image, pdf, or csv.

* `export_wb.py`	Exports a pdf containing all views in a workbook.

* `filter_sort_groups.py`	Demonstrates selecting user groups as filters.

* `initialize_server.py`	Sets up an existing server instance with site, workbooks and datasources.

* `kill_all_jobs.py`	Kills all running jobs.

* `list.py`	Lists all datasources or workbooks of a site.

* `move_workbook_projects.py` Updates the properties of a workbook to move the workbook from one project to another.

* `move_workbook_sites.py` Downloads a workbook, stores it in-memory, and uploads it to another site.

* `pagination_sample.py` Use the Pager generator to iterate over all the items on the server.

* `publish_workbook.py` Publishes a Tableau workbook.

* `refresh.py` Refreshes a datasource or workbook.

* `refresh_tasks.py` Lists and runs configured tasks on a server.

* `set_http_options.py` Sets HTTP options for the server and specifically for downloading workbooks.

* `set_refresh_schedule.py` Sets the schedule to refresh a datasource or workbook.

* `update_connection.py` Updates and embeds connection credentials of a datasource. 

**Note**: For all of the samples, ensure that your Tableau Server user account has permission to access the resources.

