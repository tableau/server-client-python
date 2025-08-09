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

For example, the code might display version `3.20`.

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
server.version = '3.20'

```

## Supported versions

The TSC library uses the same REST API versions as used in Tableau Server and Tableau Cloud. Refer to the [Tableau Server versions and REST API versions](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm#version_and_rest) table for an up-to-date mapping.

Note that Tableau provides support and security updates for each version of the product for a specific period of time. Review the Supported Versions table on the [Technical Support Programs page](https://www.tableau.com/support/services) for details.
