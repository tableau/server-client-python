---
title: Versions
layout: docs
---

Because the TSC library is a client for the Tableau Server REST API, you need to confirm that the version of the TSC
library that you use is compatible with the version of the REST API used by your installation of Tableau Server.

* TOC
{:toc}

## Display the REST API version

To display the default version of the REST API used by TSC, run the following code:

```py
import tableauserverclient as TSC

server = TSC.Server('http://SERVER_URL')

print(server.version)
```

For example, the code might display version `2.3`.

## Use another version of the REST API

To use another version of the REST API, set the version like so:

```py
import tableauserverclient as TSC

server = TSC.Server('http://SERVER_URL')


server.version = '2.6'

```

## Supported versions

The current version of TSC only supports the following REST API and Tableau Server versions:

|REST API version|Tableau Server version|
|---|---|
|2.3|10.0|
|2.4|10.1|
|2.5|10.2|
|2.6|10.3|
