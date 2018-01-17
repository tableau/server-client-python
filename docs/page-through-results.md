---
title: Page through Results
layout: docs
---

Many of the calls that you make with the TSC library query for resources (like workbooks or data sources) on Tableau
Server. Because the number of resources on Tableau Server can be very large, Tableau Server only returns the first 100
resources by default. To get all of the resources on Tableau Server, you need to page through the results.

* TOC
{:toc}

## The Pager generator

The simplest way to page through results is to use the `Pager` generator on any endpoint with a `get` function.

For example, to get all of the workbooks on Tableau Server, run the following code:

```py
for wb in TSC.Pager(server.workbooks):
    print(wb.name)
```

The `Pager` generator function returns one resource for each time that it is called. To get all the resources on the
server, you can make multiple calls to the `Pager` function. For example, you can use a `for ... in` loop to call the
`Pager` function until there are no resources remaining. Note that the `Pager` generator only makes calls to the Tableau
Server REST API when it runs out of resources--it does not make a call for each resource.

**Tip**: For more information on generators, see the [Python wiki](https://wiki.python.org/moin/Generators).

### Set pagination options

You can set pagination options in the request options and then pass the request options to the `Pager` function as a
second optional parameter.

For example, to set the page size to 1000 use the following code:

```py
request_options = TSC.RequestOptions(pagesize=1000)
all_workbooks = list(TSC.Pager(server.workbooks, request_options))
```

You can also set the page number where you want to start like so:

```py
request_options = TSC.RequestOptions(pagenumber=5)
all_workbooks = list(TSC.Pager(server.workbooks, request_options))
```

### Use list comprehensions and generator expressions

The `Pager` generator can also be used in list comprehensions or generator expressions for compactness and easy
filtering. Generator expressions will use less memory than list comprehensions. The following example shows how to use
the `Pager` generator with list comprehensions and generator expressions:

```py
# List comprehension
[wb for wb in TSC.Pager(server.workbooks) if wb.name.startswith('a')]

# Generator expression
(wb for wb in TSC.Pager(server.workbooks) if wb.name.startswith('a'))
```

If you want to load all the resources returned by the `Pager` generator in memory (rather than one at a time), then you
can insert the elements into a list:

```py
all_workbooks = list(TSC.Pager(server.workbooks))
```
