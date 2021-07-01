---
title: Versions
layout: docs
---

Because the TSC library is a client for the Tableau Server REST API, you need to confirm that the version of the TSC
library that you use is compatible with the version of the REST API used by your installation of Tableau Server.

For reference, the [REST API and Resource Versions](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm) page has more details about versions.

* TOC
{:toc}

## Display the REST API version

To display the default version of the REST API used by TSC, run the following code:

```py
import tableauserverclient as TSC

server = TSC.Server('http://SERVER_URL')

print(server.version)
```

For example, the code might display version `3.10`.

## Use the REST API version supported by the server

It's recommended to always use the latest REST API version supported by the server. This helps ensure you'll get the latest behaviors as documented here and in the Tableau REST API documentation.

There are two options for always using the the latest version supported by the instance of Tableau Server you are connecting to:

The first method is to specify `use_server_version=True` as one of the arguments, for example:

```py
import tableauserverclient as TSC

server = TSC.Server('http://SERVER_URL', use_server_version=True)
```

The second method is to create the server object first, then call the `use_server_version()` method on it. There are some situations where this method is needed. For instance, if you want to disable certificate checking, you have to do that after you create the server object, but before you make calls to the server (use_server_version makes a call to the server).

```py
import tableauserverclient as TSC

server = TSC.Server('http://SERVER_URL')
server.use_server_version()
```

## Use a specific version of the REST API

To use a specific version of the REST API, set the version like so:

```py
import tableauserverclient as TSC

server = TSC.Server('http://SERVER_URL')
server.version = '3.6'

```

## Supported versions

The current version of TSC only supports the following REST API and Tableau Server versions:

|REST API version|Tableau Server version|
|---|---|
|3.11|2021.1|
|3.10|2020.4|
|3.9|2020.3|
|3.8|2020.2|
|3.7|2020.1|
|3.6|2019.4|
|3.5|2019.3|
|3.4|2019.2|
|3.3|2019.1|
|3.2|2018.3|
|3.1|2018.2|
|3.0|2018.1|
|2.8|10.5|
|2.7|10.4|
|2.6|10.3|
|2.5|10.2|
|2.4|10.1|
|2.3|10.0|

Note that Tableau provides support and security updates for each version of the product for thirty (30) months after release. Review the Supported Versions table on the [Technical Support Programs page](https://www.tableau.com/support/services) for details.
