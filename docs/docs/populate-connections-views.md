---
title: Populate Connections and Views
layout: docs
---

When you get a workbook with the TSC library, the response from Tableau Server does not include information about the
views or connections that make up the workbook. Similarly, when you get a data source, the response does not include
information about the connections that make up the data source. This is a result of the design of the Tableau Server
REST API, which optimizes the size of responses by only returning what you ask for explicitly.

As a result, if you want to get views and connections, you need to run the `populate_views` and `populate_connections`
functions.

* TOC
{:toc}

## Populate views for workbooks

```py
workbook = server.workbooks.get_by_id('a1b2c3d4')
print(workbook.id)

server.workbooks.populate_views(workbook)
print([view.name for view in workbook.views])
```

## Populate connections for workbooks

```py
workbook = server.workbooks.get_by_id('a1b2c3d4')
print(workbook.id)

server.workbooks.populate_connections(workbook)
print([connection.datasource_name for connection in workbook.connections])
```

## Populate connections for data sources

```py
datasource = server.datasources.get_by_id('a1b2c3d4')
print(datasource.name)

server.datasources.populate_connections(datasource)
print([connection.datasource_name for connection in datasource.connections])
```
