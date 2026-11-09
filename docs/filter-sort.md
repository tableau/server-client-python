---
title: Filter and Sort
layout: docs
---
Use the `RequestOptions` object to define filtering and sorting criteria for an endpoint,
then pass the object to your endpoint as a parameter.

* TOC
{:toc}

## Available endpoints and fields

You can use the TSC library to filter and sort the results of any endpoint whose `get`
method accepts a `RequestOptions` object, and the endpoints that support the `.filter()` and
`.order_by()` shorthand: custom views, data sources, flow runs, flows, groups, group sets,
jobs, linked tasks, metrics, projects, users, views, virtual connections, and workbooks.

The fields you can filter or sort on are the members of `RequestOptions.Field`, for example
`CreatedAt`, `LastLogin`, `Name`, `OwnerName`, `SiteRole`, `Tags`, and `UpdatedAt`.

**Important**: Not all of the fields are available for all endpoints. For more information, see the [REST
API help](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_filtering_and_sorting.htm).

## Filtering

To filter on a field, you need to specify the field name, an operator criteria and a value criteria.

**Note**: Ampersands and commas in filter values are not supported by the REST API as they are used as delimiters. See [Special characters in filter values](#special-characters-in-filter-values) for a workaround.

### Operator criteria

The operator that you want to use for that field. For example, you can use the Equals operator to get everything from the endpoint that matches exactly.

The operator can be any of the following:

* Equals
* GreaterThan
* GreaterThanOrEqual
* LessThan
* LessThanOrEqual
* In
* Has
* CaseInsensitiveEquals

Not every operator is supported on every field. In particular, the REST API supports
`Has` (substring search) only for jobs, and `CaseInsensitiveEquals` only on user name,
group name, and group set name. See the per-endpoint field tables in the [REST
API help](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_filtering_and_sorting.htm).

### Value criteria

The value that you want to filter on. This can be any valid string. Field names, operator
names, and values are case-sensitive; use `CaseInsensitiveEquals` where the field supports it.

Pass values as plain strings. For REST API version 3.7 and later, TSC URL-encodes the
query string for you, so do not percent-encode values yourself.

### Special characters in filter values

The REST API does not accept ampersand (`&`) or comma (`,`) characters in a filter
expression, because it uses them to separate expressions. This is true even if the
characters are URL-encoded, and putting a backslash in front of a comma does not escape it.
A filter value that contains either character fails with a `400065: Bad Request` error:

```py
# Fails: the workbook name contains a comma and an ampersand
workbooks = server.workbooks.filter(name="T(L-F,SZ&V-MY) - PC")
```

To find an item whose name contains these characters, replace each one with an asterisk
(`*`). The asterisk acts as a wildcard, so the following filter finds the workbook named
`T(L-F,SZ&V-MY) - PC`:

```py
for workbook in server.workbooks.filter(name="T(L-F*SZ*V-MY) - PC"):
    print(workbook.name, workbook.id)
```

Because a wildcard matches any character, the filter can return more than one item. In the
example above, the same filter also returns a workbook named `T(L-F^SZ|V-MY) - PC`. Check
the results on the client side if you need an exact match:

```py
wb_name = "T(L-F,SZ&V-MY) - PC"
pattern = wb_name.replace(",", "*").replace("&", "*")
matches = [wb for wb in server.workbooks.filter(name=pattern) if wb.name == wb_name]
```

Wildcard matching with `Equals` is not described in the REST API documentation (see
[Wildcard searches](#wildcard-searches)), so test it against your server before you rely on it.

### Wildcard searches

The REST API supports wildcard searches (starts with, ends with, and contains) starting in
Tableau Cloud May 2023 and Tableau Server 2022.1.14. The REST API documents these searches
through its `like` operator, and only on selected name fields: user name, user
friendlyName, group name, and group set name. Other fields support exact matches only.

For example, to search for the string `marketing-example`, the REST API documentation
gives the following filter expressions:

| Search | REST API filter expression |
| --- | --- |
| Starts with | `name:like:mark*` |
| Ends with | `name:like:*-ample` |
| Contains | `name:like:mark*ex*` |

TSC does not define a `RequestOptions.Operator` value for `like`, and there are no
`contains`, `startswith`, or `endswith` operators. A Django style filter such as
`name__like="mark*"` raises a `ValueError`.

### Filtering example - RequestOptions

The following code displays only the workbooks where the name equals Superstore:

```py
req_option = TSC.RequestOptions()
req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                 TSC.RequestOptions.Operator.Equals,
                                 'Superstore'))
matching_workbooks, pagination_item = server.workbooks.get(req_option)

print(matching_workbooks[0].owner_id)
```

## Sorting

To sort on a field, you need to specify the field name and the direction criteria for the sort order.

### Direction criteria - RequestOptions

This can be either `Asc` for ascending or `Desc` for descending.

### Sorting example - RequestOptions

The following code sorts the workbooks in ascending order:

```py
req_option = TSC.RequestOptions()
req_option.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name,
                             TSC.RequestOptions.Direction.Asc))
matching_workbooks, pagination_item = server.workbooks.get(req_option)

for wb in matching_workbooks:
    print(wb.name)
```


## Django style filters and sorts

### Filtering examples - Django style

The following code displays only workbooks where the name equals Superstore:

```py
all_workbooks = server.workbooks.filter(name='Superstore')
for workbook in all_workbooks:
    print(workbook.owner_id)
```

### Setting page size

Starting with version 0.32, you can set the page size for the request by using
the `page_size` keyword argument. The default page size is 100 if not provided.

```py
superstore_workbooks = server.workbooks.filter(name='Superstore', page_size=10)
# or
all_workbooks = server.workbooks.all(page_size=1000)
```



### Direction criteria - Django style

The field name can be input as normal for ascending or prefixed with `-` for descending.

### Sorting example - Django style

The following code sorts the workbooks in ascending order:

```py
matching_workbooks = server.workbooks.order_by('name')

for wb in matching_workbooks:
    print(wb.name)
```

Sort can take multiple args, with desc direction added as a (-) prefix 

```py
workbooks = workbooks.order_by("project_name", "-created_at")
```

### Indexing and slicing

Querysets can be indexed and sliced like a list. The query is executed at when
the queryset is indexed or sliced.
```py
# Get the first item in the queryset
flow = server.flows.filter(owner_name="admin")[0]

# Get the last item in the queryset
flow = server.flows.filter(owner_name="admin")[-1]

# Get the most recent 10 runs from a flow
runs = server.flow_runs.filter(flow_id=flow.id, page_size=10).order_by("-created_at")[:10]
```

### Supported endpoints

The following endpoints support the Django style filters and sorts:

* Datasources
* Flow Runs
* Flows
* Groups
* Groupsets
* Jobs
* Projects
* Users
* Views
* Workbooks

### More detailed examples

```py
# Return queryset with no filters
workbooks = server.workbooks.all() 

# filters can be appended in new lines
workbooks = workbooks.filter(project_name=project_name)

# multiple filters can be added in a single line
workbooks = workbooks.filter(project_name=project_name, owner_name=owner_name, size__gte=1000)

# Multiple filters can be added through chaining.
workbooks = workbooks.filter(project_name=project_name).filter(owner_name=owner_name).filter(size__gte=1000)

# Find all views in a project, with a specific tag
views = server.views.filter(project_name=project_name, tags="stale")

# sort can take multiple args, with desc direction added as a (-) prefix 
workbooks = workbooks.order_by("project_name", "-created_at")

# query is executed at time of iteration
for workbook in workbooks: 
    print(workbook)

# pagination item is still accessible  
print(workbooks.total_available, workbooks.page_size, workbooks.page_number) 

# methods can be chained
all_workbooks = server.workbooks.filter(project_name=project_name).order_by("-project_name")

# operators are implemented using dunderscore
all_workbooks = server.workbooks.filter(project_name__in=["Project A", "Project B"])

# How many items are in the queryset?
flows = server.flows.filter(owner_name="admin")
print(len(flows))

```

### Operators available

| Operator | Implementation |
| --- | --- |
| Equals | eq |
| GreaterThan | gt |
| GreaterThanOrEqual | gte |
| LessThan | lt |
| LessThanOrEqual | lte |
| In | in |
| Has | has |
| CaseInsensitiveEquals | cieq |

For example, `server.users.filter(name__cieq="jsmith")` matches a user named `JSmith`.
See [Special characters in filter values](#special-characters-in-filter-values) and
[Wildcard searches](#wildcard-searches) for limits on filter values.
