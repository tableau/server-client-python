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

### Value criteria

The value that you want to filter on. This can be any valid string.

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

### Direction criteria - Django style

The field name cane be input as normal for ascending or prefixed with `-` for descending.

### Sorting example - Django style

The following code sorts the workbooks in ascending order:

```py
matching_workbooks = server.workbooks.sort('name')

for wb in matching_workbooks:
    print(wb.name)
```

Sort can take multiple args, with desc direction added as a (-) prefix 

```py
workbooks = workbooks.sort("project_name", "-created_at")
```

### More detailed examples

```py
# Return queryset with no filters
workbooks = server.workbooks.all() 

# filters can be appended in new lines
workbooks = workbooks.filter(project_name=project_name)

# sort can take multiple args, with desc direction added as a (-) prefix 
workbooks = workbooks.sort("project_name", "-created_at")

# pagination take these two keywords
workbooks = workbooks.paginate(page_size=10, page_number=2) 

# query is executed at time of access
for workbook in workbooks: 
    print(workbook)

# pagination item is still accessible  
print(workbooks.total_available, workbooks.page_size, workbooks.page_number) 

# methods can be chained
all_workbooks = server.workbooks.filter(project_name=project_name).sort("-project_name")

# operators are implemented using dunderscore
all_workbooks = server.workbooks.filter(project_name__in=["Project A", "Project B"])
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