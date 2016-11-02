---
title: Filter and Sort
layout: docs
---
Use the `RequestOptions` object to define filtering and sorting criteria for an endpoint,
then pass the object to your endpoint as a parameter.

* TOC
{:toc}


## Available endpoints and fields

You can use the TSC library to filter and sort the following endpoints:

* Users
* Datasources
* Workbooks
* Views

For the above endpoints, you can filter or sort on the following
fields:

* CreatedAt
* LastLogin
* Name
* OwnerName
* SiteRole
* Tags
* UpdatedAt

**Important**: Not all of the fields are available for all endpoints. For more information, see the [REST
API help](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_concepts_filtering_and_sorting.htm).

## Filtering

To filter on a field, you need to specify the following criteria:

### Operator criteria

The operator that you want to use for that field. For example, you can use the Equals operator to get everything from the endpoint that matches exactly.

The operator can be any of the following:

* Equals
* GreaterThan
* GreaterThanOrEqual
* LessThan
* In

### Value criteria

The value that you want to filter on. This can be any valid string.

### Filtering example

The following code displays only the workbooks where the name equals 'Superstore':

```py
req_option = TSC.RequestOptions()
req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, 'Superstore'))
matching_workbooks, pagination_item = server.workbooks.get(req_option)

print(matching_workbooks[0].owner_id)
```

## Sorting

To sort on a field, you need to specify the direction in which you want to sort.

### Direction criteria

This can be either `Asc` for ascending or `Desc` for descending.

### Sorting example

The following code sorts the workbooks in ascending order:

```py
req_option = TSC.RequestOptions()
req_option.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))
matching_workbooks, pagination_item = server.workbooks.get(req_option)

for wb in matching_workbooks:
	print wb.name
```

