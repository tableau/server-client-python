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
API help](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_filtering_and_sorting.htm).

## Filtering

To filter on a field, you need to specify the field name, an operator criteria and a value criteria.

**Note**: Commas in filter values are not supported by the REST API, because it uses them to separate filter expressions. See [Special characters in filter values](#special-characters-in-filter-values) for a workaround.

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

Not every operator is supported on every field. See the per-endpoint field tables in the [REST
API help](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_filtering_and_sorting.htm).

### Value criteria

The value that you want to filter on. This can be any valid string.

### Special characters in filter values

The REST API does not accept a comma (`,`) in a filter value, because it uses commas to
separate expressions. A filter value that contains a comma fails with a `400065` error.
Percent-encoding the comma or putting a backslash in front of it does not help.

```py
# Fails: the workbook name contains a comma
workbooks = server.workbooks.filter(name="Sales, Q1 & Q2")
```

An ampersand (`&`) in a name is matched as typed.

To find an item whose name contains a comma, replace the comma with an asterisk (`*`). The
asterisk acts as a wildcard, so the following filter finds the workbook named
`Sales, Q1 & Q2`:

```py
for workbook in server.workbooks.filter(name="Sales* Q1 & Q2"):
    print(workbook.name, workbook.id)
```

Because `*` matches any run of characters, the filter can return more than one item. Check
the results on the client side if you need an exact match:

```py
wb_name = "Sales, Q1 & Q2"
pattern = wb_name.replace(",", "*")
matches = [wb for wb in server.workbooks.filter(name=pattern) if wb.name == wb_name]
```

This works because `Equals` treats `*` as a wildcard (see [Wildcard searches](#wildcard-searches)).

### Wildcard searches

In a filter value, `*` matches any run of characters, including none. For example,
`server.workbooks.filter(name="Sales*")` returns workbooks whose names start with `Sales`. This
was tested for workbook names on Tableau Cloud. Confirm the behavior on your Tableau Server
version before you rely on it for other fields.

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
