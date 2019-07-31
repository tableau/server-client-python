---
title: Get Started
layout: docs
---

Use the Tableau Server Client (TSC) library to increase your productivity as you interact with the Tableau Server REST API. With
the TSC library you can do almost everything that you can do with the REST API, including:

* Publish workbooks and data sources.
* Create users and groups.
* Query projects, sites, and more.

This section describes how to:

* TOC
{:toc}

## Confirm prerequisites

Before you install TSC, confirm that you have the following dependencies installed:

* Python. You can use TSC with Python 2.7.9 or later and with Python 3.3 or later. These versions include pip, which is
  the recommended means of installing TSC.
* Git. Optional, but recommended to download the samples or install from the source code.


## Install TSC

You can install TSC with pip or from the source code.

### Install with pip (recommended)

Run the following command to install the latest stable version of TSC:

```
pip install tableauserverclient
```

### Install from the development branch

You can install from the development branch for a preview of upcoming features. Run the following command
to install from the development branch:

```
pip install git+https://github.com/tableau/server-client-python.git@development
```

Note that the version from the development branch should not be used for production code. The methods and endpoints in the
development version are subject to change at any time before the next stable release.

## Get the samples

The TSC samples are included in the `samples` directory of the TSC repository on Github. You can run the following command to clone the
repository:

```
git clone git@github.com:tableau/server-client-python.git
```

For more information on the samples and how to run the samples, see [Samples]({{ site.baseurl }}/docs/samples).

## Write your first program

Run the following code to get a list of all the data sources on your installation of Tableau Server:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD','SITEID')
server = TSC.Server('http://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    all_datasources, pagination_item = server.datasources.get()
    print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
    print([datasource.name for datasource in all_datasources])
```
