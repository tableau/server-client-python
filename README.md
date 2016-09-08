# server-client-python
Tableau Server Client is a client library for the Tableau REST API. The Server Client is delightful to use and easy to love because it requires writing much less code than working directly with the REST API.

This repository contains Python source and sample files.

###Getting Started
You must have Python installed. You can use either 2.7.X or 3.3 and later.

#### Installing the latest stable version (preferred)

```text
pip install tableauserverclient
```

#### Installing From Source

Download the `.zip` file. Unzip the file and then run the following command:

```text
pip install -e <directory containing setup.py>
```

#### Installing the Development Version from Git

*Only do this if you know you want the development version, no guarantee that we won't break APIs during development*

```text
pip install git+https://github.com/tableau/server-client-python.git@development
```

If you go this route, but want to switch back to the non-development version, you need to run the following command before installing the stable version:

```text
pip uninstall tableauserverclient
```

###Basics
The following example shows the basic syntax for using the Server Client to query a list of all workbooks and the associated pagination information on the default site:

```python
import tableauserverclient

tableau_auth = tableauserverclient.TableauAuth('USERNAME', 'PASSWORD')
server = tableauserverclient.Server('SERVER')

with server.auth.sign_in(tableau_auth):
    pagination_info, all_workbooks = server.workbooks.get()
```

###Server Client Samples
* Can be run using the command prompt or terminal

Demo | Source Code | Description
-------- |  -------- |  --------
Publish Workbook | [publish_workbook.py](./samples/publish_workbook.py) | Shows how to upload a Tableau workbook.
Move Workbook | [move_workbook_projects.py](./samples/move_workbook_projects.py)<br />[move_workbook_sites.py](./samples/move_workbook_sites.py) | Shows how to move a workbook from one project/site to another. Moving across different sites require downloading the workbook. 2 methods of downloading are demonstrated in the sites sample.<br /><br />Moving to another project uses an API call to update workbook.<br />Moving to another site uses in-memory download method.
Set HTTP Options | [set_http_options.py](./samples/set_http_options.py) | Sets HTTP options on server and downloads workbooks.
Explore Datasource | [explore_datasource.py](./samples/explore_datasource.py) | Demonstrates working with Tableau Datasource. Queries all datasources, picks one and populates its connections, then updates the datasource. Has additional flags for publish and download.
Explore Workbook | [explore_workbook.py](./samples/explore_workbook.py) | Demonstrates working with Tableau Workbook. Queries all workbooks, picks one and populates its connections/views, then updates the workbook. Has additional flags for publish, download, and getting the preview image. Note: if you don't have permissions on the workbook the script retrieves from the server, the script will result in a 403033 error. This is expected.
