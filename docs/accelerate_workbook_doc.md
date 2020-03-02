---
title: Getting Started with Data Acceleration
layout: docs
---

* TOC
{:toc}

## Introduction

Starting in Tableau Server version 2020.2 and later, administrators can enable data acceleration for specific workbooks. An accelerated workbook loads faster because Tableau Server pre-computes the workbook's data in a background process.

The easiest way to configure data acceleration is to use the `accelerate_workbook.py` sample in the Tableau Server Client library. It is also possible to configure data acceleration using the [Tableau Server REST API](https://help.tableau.com/v2020.2/api/rest_api/en-us/REST/rest_api.htm).

Workbooks with published and live data sources (both with embedded credentials), and workbooks with embedded extracts are supported. Workbooks with embedded extracts do not need to be scheduled. Workbooks with published and live data sources need to have a data acceleration task added to a schedule.

## Limitations

* Site and Server Administrator permission are required to control data acceleration.
* Only those workbooks with embedded credentials can be accelerated.
* The pre-computed data is saved into the Tableau Cache.  The cache is subject to the cache size limit and the cache expiration limit. We recommend that you review your configuration and recommend 2GB or larger.
* When you attach an acceleration schedule to a workbook, if that acceleration schedule interval exceeds the Tableau Server cache expiration time, the workbook will not be accelerated during the period between the cache expiration time and the next run of the acceleration schedule.  The workbook will revert to using the databases. By default, the Tableau Server cache expiration time is 12 hours (720 minutes).
* Workbooks using encrypted extracts or that include user-based, now(), today() functions are not supported.
* Federated data sources are not supported. When there is a workbook containing both federated data sources and other data sources, the data queried against federated data sources will not be accelerated.
* Data Blending is partially supported for acceleration. Data queried against the secondary data sources is not accelerated.
* Data acceleration schedules are not currently supported to be created in the Tableau Server schedules view.  

## Prerequisites

When using this feature, it is recommended to increase the size of the Tableau Server external cache to 2 GB or larger.

View your current Tableau Server external cache size setting:
`tsm configuration get -k redis.max_memory_in_mb`

Set the Tableau Server external cache size to 2 GB:
`tsm configuration set -k redis.max_memory_in_mb -v 2048`
`tsm pending-changes apply`

## Quick Start Tutorial

This tutorial shows you how to enable and schedule workbooks for data acceleration using the `accelerate_workbook.py` command line tool.

Note: You must be signed in as a server administrator to create schedules or use site-level commands. For other commands, you can use the server administrator role or the site administrator role.

### Sign Into Tableau Server

`python accelerate_workbook.py --server <server-url> --username <username> --password <password> --site <site>`

For information about how to identify the site value, see [Sign In and Out](https://tableau.github.io/server-client-python/docs/sign-in-out). If you don’t specify a site, you will be signed into the Default site.  

### Enable Workbooks That Only Use Embedded Extracts

When data acceleration is enabled, a workbook that only has data sources that are embedded extracts does not require an acceleration schedule. Tableau Server automatically identifies the changes to its content and data whenever the workbook is republished or its extracts are refreshed (manually or on a schedule) and it submits a background task for the data pre-computation.  Thus, this type of workbook can be accelerated by just enabling it with the command:

`python accelerate_workbook.py --enable "My Project/Embedded Extract Workbook"`

Note: If a workbook is in a nested project, its path may be like "Project 1/Project 2/Workbook Name". Workbook paths are case sensitive.

The server will enable the workbook and you will see the following output:

Workbooks enabled
Project/Workbook
My Project/Embedded Extract Workbook

After the background task for pre-computation of the workbook's data is completed, subsequent loads of the workbooks will use those pre-computed results. The background task may take a few minutes to finish.

### Schedule Workbooks With Published or Live Data Sources

Workbooks with published or live data sources need to be scheduled for acceleration, which keeps their data fresh.

This command will create an acceleration schedule called "My Schedule" that runs every 4 hours throughout the day.

`python accelerate_workbook.py --create-schedule "My Schedule" --hourly-interval 4 --start-hour 0 --end-hour 23 --end-minute 45`

Next, we'll associate this acceleration schedule with your workbooks:

`python accelerate_workbook.py --add-to-schedule "My Schedule" "My Project/My Workbook"`

You will see the following output:

Workbooks added to schedule
Project/Workbook             |  Schedules
My Project/My Workbook       |  My Schedule

Users can also attach multiple workbooks to "My Schedule" by using a path list.

`python accelerate_workbook.py --add-to-schedule "My Schedule" --path-list pathfile.txt`

In the 'pathfile.txt' file, each line defines a workbook path.

My project/My Workbook
Finance Project/Expenses
Sales Project/Leads Per Region

Note: If a workbook uses only embedded extracts then an acceleration schedule will not be attached even when the user issues the `--add-to-schedule command`.

### Monitor Your Accelerated Workbooks

To see which workbooks have been enabled, use the `--status`, and `--show-schedules` commands.

Display all the workbooks that are enabled, and which acceleration schedules are associated.
`python accelerate_workbook.py --status`

Display the accelerated schedules associated with workbooks.
`python accelerate_workbook.py --show-schedules`

### Load Your Accelerated Workbooks and Check the Performance

#### Tableau Server Administrator Views  

Tableau Server provides an administrator view to review the load times for workbooks. See [Stats for Load Times](https://help.tableau.com/current/server/en-us/adminview_stats_load_time.htm).

### Sign Out of Tableau Server

Log out of Tableau Server and end your session.
`python accelerate_workbook.py --logout`

## Command Reference

Note: Optional arguments are indicated with [].

### Get Help

Get a list of the available commands.

`python accelerate_workbook.py --help`

### Sign Into Tableau Server

In Tableau Server, creating schedules and site level commands require the user to be signed in with an account with the Server Administrator role.  For other commands the Server Administrator role or the Site Administrator role is required.

`python accelerate_workbook.py [--server] [SERVER_URL] [--site] [SITE_NAME] [--username] [Username] [--password] [password]`

SITE_NAME is the sub-path of your full site URL (also called contentURL in the REST API).  Given the site URL 'https://my.tableauserver.com/MYSITE', 'MYSITE' is the site name.  See [Sign In and Out](https://tableau.github.io/server-client-python/docs/sign-in-out) for identifying the [SITE_NAME]. When `--site` is not specified or is specified with "" the Default site will be used.

After a successful sign in, a session token file (".token_profile") will be created and saved in the same directory as `accelerate_workbook.py`. The token file will be deleted when you log out.  

Example: Sign into Tableau Server and the Default site

`python accelerate_workbook.py --server https://server --site "" --username user1 --password password1`

You can ignore the SSL Certificate by pressing the ENTER key when prompted.

Example: Sign into Tableau Server with an SSL certificate

`python accelerate_workbook.py --server https://server --site "" --username user1 --password password1 --ssl-cert-pem cert.pem`

Example: Switch the site that you are logged into

`python accelerate_workbook.py --server https://server --username user1 --password password1 --site different_site`

Example: For some usernames and passwords it may be necessary to use double quotes.

`python accelerate_workbook.py --server https://server --site "" --username "user space name" --password "password with spaces"`

Example:  Double quotes "" should not be used when prompted for input:

`python accelerate_workbook.py --server https://server`

site (hit enter for the Default site):
username: user space name
password: password with spaces
path to ssl certificate (hit enter to ignore): cert.pem

### Sign Out of Tableau Server

The session token file (".token_profile") created on login will be deleted when you log out.

Example:  Sign out of Tableau Server

`python accelerate_workbook.py --logout`

When successfully signed out of Tableau Server, you will see the following message, "Signed out from current connection to https://server successfully". If you are not connected to an existing server, you will see the following message, "No existing connection to any server."

### Create Data Acceleration Schedules

The following command is used to create a data acceleration schedule.

`python accelerate_workbook.py --create-schedule SCHEDULE_NAME INTERVAL_TYPE [INTERVAL] [START_TIME] [END_TIME]`

In Tableau Server, creating schedules requires the Server Administrator role. For other commands the Server Administrator role or the Site Administrator role is sufficient.

INTERVAL_TYPE can be one of the four options below:
--hourly-interval with INTERVAL in {0.25,0.5,1,2,4,6,8,12}, the unit is hour.
--daily-interval, INTERVAL is not needed
--weekly-interval with INTERVAL as a non-empty subset of:
{Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday}
--monthly-interval, INTERVAL is the starting day in a month.

[START_TIME] is optional. If no starting time is specified, the default time 00:00:00 is used. To specify the starting time, --start-hour and --start-minute can be used to specify the time.

[END_TIME] is optional. If no end time is specified, the end of the day will be used. To specify the ending time, --end-hour and --end-minute can be used to specify the time. END_TIME option is only useful for hourly interval.

The warning, "Warning: The recurrence interval of the given schedule is larger than Vizql server data refresh interval of 720 minutes." will be displayed if the users try to create a schedule that exceeds the configured VizQL server data refresh interval. By default, this is set to 12 hours (720 minutes).

Example 1: Create a scheduled pre-computation every 4 hours.
  
In this example, a pre-computation background task will be submitted every 4 hours throughout the day.

`python  accelerate_workbook.py --create-schedule "My Schedule"  --hourly-interval 4 --start-hour 0 --end-hour 23 --end-minute 45`

After the acceleration schedule is created using the command line client, it can be viewed in the Tableau Server Schedules view. The scheduled task type will not currently be displayed.  

### Associate Workbooks to a Schedule

You can associate a workbook to single or multiple data acceleration schedules. If your workbook has not been enabled for acceleration, the --add-schedule command will automatically enable the workbook.  

`python accelerate_workbook.py --add-to-schedule [SCHEDULE_NAME] --workbook-path WORKBOOK_PATH`

`python accelerate_workbook.py --add-to-schedule [SCHEDULE_NAME] --path-list PATH_LIST`

Example 1: Associate a workbook to a schedule

`python accelerate_workbook.py --add-to-schedule "My Schedule" --workbook-path project/workbook1`

```iecst
Workbooks added to schedule
Project/Workbook     | Schedules
Default/my workbook1 | My Schedule
```

Example 2:  Associate an acceleration schedule using a text file with a path list containing one or more workbooks.

`python accelerate_workbook.py --add-to-schedule "My Schedule" --path-list path.txt`

```iecst
Workbooks added to schedule
Project/Workbook	Schedules
Default/my workbook1	My Schedule
Default/my workbook2	My Schedule
```

Example 3:  Associate acceleration schedules with a workbook that is only extract data source based.

Any workbook that uses only embedded extracts as its data source does not require an explicit acceleration schedule and thus it will only be enabled for acceleration without using an acceleration schedule.  For these workbooks, the Tableau Server will automatically identify changes to the workbook content and data.  Whenever the workbook is republished or its extract refreshes (manually or scheduled) a background task is submitted to pre-compute the data.  

In the example below, an attempt was made to add "My Schedule" to a workbook with only embedded extracts. The workbook is enabled for acceleration and it is not added to the "My Schedule" acceleration schedule.

`python accelerate_workbook.py --add-to-schedule "My schedule" Default/WorkbookwithOnlyExtracts`

```iecst
Workbooks added to schedule: None
Warning: Unable to add workbook "Default/WorkbookwithOnlyExtracts" to schedule due to Workbook with id 10000 uses only embedded extract(s) and does not need explicit scheduling for acceleration. It was enabled for acceleration but not attached to the given schedule.
```

`python accelerate_workbook.py --show-schedule`

```iecst
Workbooks added to schedule
Project/Workbook	Schedules
Default/my workbook1	My Schedule
Default/my workbook2	My Schedule
```

For workbooks that are not supported you will see the following warnings:

Workbooks with encrypted embedded extracts:
`Unable to enable Default/Sales. Workbook 'Sales' is not supported for data acceleration because it only uses encrypted embedded extracts as data sources.`

Workbooks where credentials are not embedded:
`Unable to enable Default/Finance. Workbook 'Finance' is not supported for data acceleration because it uses data sources without embedding credentials.`

The following warning will be displayed if the users try to create a schedule that exceeds the configured VizQL server data refresh interval.  By default, this is set to 12 hours (720 minutes).
`Warning: The recurrence interval of the given schedule is larger than Vizql server data refresh interval of 720 minutes.`

### Enable Workbooks

Enabling a workbook will opt in the workbook for acceleration. data acceleration will monitor the relevant Tableau events that could potentially change the data of the workbooks such as workbook publishing, extract refreshing (if the workbook has any) and web authoring.  Pre-computation will be triggered after these events. However, the data source changes which are not managed by Tableau will not be monitored and the acceleration schedule is used for keeping the pre-computed data up to date in those scenarios.  

To enable one workbook:

`python accelerate_workbook.py --enable [--workbook-path] WORKBOOK_PATH`

To enable one or more workbooks in batches, you can provide a file specifying a list of workbooks.

`python accelerate_workbook.py --enable [--path-list] PATH_LIST`

Example 1:  Enable a single workbook

`python accelerate_workbook.py --enable Default/Workbook1`

Example 2:  Enable multiple workbooks

Create a path file for example `paths.txt` using the format below project/workbook:
Default/Workbook1
Default/Workbook2
The following command will enable the workbooks defined in the paths.txt file.

`python accelerate_workbook.py --enable --path-list paths.txt`

```iecst
Workbooks enabled
Project/Workbook
Default/my workbook1
Default/my workbook2
```

For workbooks that are not currently supported, you will see the following warnings:

Workbooks with encrypted embedded extracts:
`Unable to enable Default/Sales. Workbook 'Sales' is not supported for data acceleration because it only uses encrypted embedded extracts as data sources.`

Workbooks where credentials are not embedded:
`Unable to enable Default/Finance. Workbook 'Finance' is not supported for data acceleration because it uses data sources without embedding credentials.`

### Detach a Workbook from a Schedule

Use the --remove-from-schedule command to detach a workbook from a schedule.

`python accelerate_workbook.py --remove-from-schedule SCHEDULE_NAME [--workbook-path] WORKBOOK_PATH`

`python accelerate_workbook.py --remove-from-schedule SCHEDULE_NAME [---path-list] PATH_LIST`

`python accelerate_workbook.py --remove-from-schedule SCHEDULE_NAME project/workbook`

Example 1:  Removing multiple workbooks from a schedule using --path-list.  
In the example below "workbook1" and "workbook2" was detached from the acceleration schedule "My Schedule".  Any workbooks included in the path list are not associated with "My Schedule".

`python accelerate_workbook.py --remove-from-schedule "My Schedule" --path-list "paths.txt"`

```iecst
Workbooks removed from schedule
Project/Workbook	Schedules
Default/workbook1	My Schedule
Default/workbook2	My Schedule

Workbooks not on schedule "My Schedule"
Project/Workbook
Default/extractworkbook
```

Example 2:  Remove a workbook from a schedule

`python accelerate_workbook.py --remove-from-schedule "My Schedule" Default/workbook1`

```iecst
Workbooks removed to schedule
Project/Workbook	Removed From Schedule
Default/my workbook1	My Schedule
```

Example 3:

`python accelerate_workbook.py --remove-from-schedule "My Schedule" --workbook-path Default/workbook1`

```iecst
Workbooks removed from schedule
Project/Workbook	Schedules
Default/workbook1	My Schedule
```

### Accelerate On-Demand

You can use --enable combined with --acceleration-now to submit a backgrounder pre-computation job on demand.  This can be useful to trigger a pre-computation ahead of the next scheduled run.

`python accelerate_workbook.py --enable --accelerate-now --path-list PATH_LIST`

`python accelerate_workbook.py --enable WORKBOOK_PATH --accelerate-now`

Example 1:

`python accelerate_workbook.py --enable Default/workbook1 --accelerate-now`

### Disable Workbooks

Disabling a workbook stops accelerating the workbook. It detaches the workbook from the workbook's associated schedules and cleans up all of the acceleration artifacts related to the workbook. It will not remove entries from the Tableau query cache.

`python accelerate_workbook.py --disable [--workbook-path] WORKBOOK_PATH`

`python accelerate_workbook.py --disable --path-list PATH_LIST`

`python accelerate_workbook.py --disable --workbook-path Default/workbook1`

```iecst
Workbooks Disabled
Project/Workbook
Default/workbook1
```

### Enable or Disable a Site for Data Acceleration

The following commands are used to enable or disable a site for acceleration.

`python accelerate_workbook.py --enable --site SITE_NAME --type site`

`python accelerate_workbook.py --disable --site SITE_NAME --type site`

Workbooks can only be enabled for acceleration if their site is enabled. Enabling a site will not enable any workbooks automatically. All sites are enabled for acceleration by default. Enabling a site is only needed when a site is explicitly disabled, or a site is imported from another Tableau Server.

Disabling a site for acceleration will disable all workbooks that were currently enabled for acceleration.  Once a site is disabled, no workbooks can be enabled on this site until this site is enabled again. All workbooks under that site will be disabled and detached from any accelerated schedules they are associated with.

In Tableau Server, to enable or disable acceleration requires the user to be signed in with an account with the Server Administrator role.

Example 1:  Disable the Default site for acceleration

`python accelerate_workbook.py --disable --site SITE_NAME --type site`

Example 2:  Enable the Default site for acceleration

`python accelerate_workbook.py --enable --site SITE_NAME --type site`

### Display Acceleration Schedules

The --show-schedules command displays the schedule information for enabled workbooks associated with their accelerated schedules. The schedule information includes the schedule name associated with the workbooks and their next run time.

`python accelerate_workbook.py --show-schedules`

`python accelerate_workbook.py --show-schedules SCHEDULE_NAME [--workbook-path] [WORKBOOK_PATH]`

`python accelerate_workbook.py --show-schedules SCHEDULE_NAME [---path-list] [PATH_LIST]`

Note: If --workbook-path or –path-list are omitted, the command will show all the enabled workbooks with their schedule information.

Example 1:  When there are no data acceleration schedules associated with enabled workbooks

`python accelerate_workbook.py --show-schedules`

Scheduled Tasks for Data Acceleration: None

Example 2:  When there are enabled workbooks with data acceleration schedules

```iecst
Scheduled Tasks for Data Acceleration

Project/Workbook	Schedule	Next Run
Default/extractworkbook	*	
Default/liveworkbook	My Schedule	2020-01-22 16:00:00-08:00
Default/liveandextractworkbook	My Schedule	2020-01-22 16:00:00-08:00
```

### Show Acceleration Status

The --status command shows the list of workbooks enabled for acceleration and their associated schedules.  When a workbook is enabled but not associated with any schedule, an asterisk '*' will be shown in the Schedule column. In that case, the pre-computed data for workbooks will be updated when the workbooks are re-published, or their extracts (if they have any) get refreshed.  Workbooks that only contain embedded extracts will not be associated with schedules.

`python accelerate_workbook.py --status`

Example 1: Display the status of all enabled and scheduled accelerated workbooks.

`python accelerate_workbook.py --status`

```iecst
Data Acceleration is enabled for the following workbooks
Site	Project/Workbook
Default	Default/extractworkbook
Default	Default/liveworkbook
Default	Default/liveandextractworkbook

Scheduled Tasks for Data Acceleration
Project/Workbook	Schedule	Next Run
Default/extractworkbook	*	
Default/liveworkbook	My Schedule	2020-01-22 16:00:00-08:00
Default/liveandextractworkbook	My Schedule	2020-01-22 16:00:00-08:00

*The Data Acceleration views for these workbooks will be updated when they are published, or when their extract is refreshed.
```

### Specify workbook paths

This section describes how to specify the workbook path argument and the path list argument in the commands --add-to-schedule, --enable, --remove-from-schedule.

--workbook-path
[WORKBOOK_PATH] is the path concatenating the project path and the workbook name by "/" where the project path is the path of the project directly containing the workbook to the root project.  The path is in the form of "Project Name/Workbook Name". If a workbook is in a nested project, its path may be like "Project 1/Project 2/Workbook Name". Workbook paths are case sensitive.

Double quotes are required for specifying the workbook path if it contains whitespace.

`python accelerate_workbook.py --enable [--workbook-path] PATH_LIST`

Example 1: Specifying --workbook-path

`python accelerate_workbook.py --enable --workbook-path "project/workbook with spaces"`

Example 2:  --workbook-path is optional

`python accelerate_workbook.py --enable project/workbook`

Example 3:  --workbook-path is optional

`python accelerate_workbook.py --add-to-schedule "My Schedule" project/workbook`

--path-list
PATH_LIST is a text file where each line is a workbook path. In the PATH_LIST, there is no need to use double quotes for workbook paths that contain whitespace.

Here is an example paths text file:
projectLevel1/projectLevel2/workbook1
project1/workbook2

Example 1:  Enable multiple workbooks

`python accelerate_workbook.py --enable --path-list paths.txt`

Example 2:  Add multiple workbooks to a schedule.

`python accelerate_workbook.py --add-to-schedule "My Schedule" --path-list paths.txt`

Example 3:  Remove multiple workbooks from a schedule.

`python accelerate_workbook.py –-remove-from-schedule "My Schedule" --path-list paths.txt`
