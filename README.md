# server-api-python
Tableau Server API is a client library for the Tableau REST API. The Server API is delightful to use and easy to love because it requires writing much less code than working directly with the REST API.

This repository contains Python source and sample files.

This repository is currently NOT ready to be made public.  Please leave this as a private repo for now.


###Getting Started
You must have Python installed. You can use either 2.7.X or 3.3 and later.

#### Installing the latest stable version (preferred)

```text
pip install tableauserverapi
```

#### Installing From Source

Download the `.zip` file. Unzip the file and then run the following command:

```text
pip install -e <directory containing setup.py>
```


###Server API Samples
* Can be run using the command prompt or terminal

Demo | Source Code | Description
-------- |  -------- |  --------
Publish Workbook | [publish_workbook.py](./samples/publish_workbook.py) | Shows how to upload a Tableau workbook.
Move Workbook | [move_workbook_projects.py](./samples/move_workbook_projects.py)<br />[move_workbook_sites.py](./samples/move_workbook_sites.py) | Shows how to move a workbook from one project/site to another. Moving across different sites require downloading the workbook. 2 methods of downloading are demonstrated in the sites sample.<br /><br />Moving to another project uses an API call to update workbook.<br />Moving to another site uses in-memory download method.
Set HTTP Options | [set_http_options.py](./samples/set_http_options.py) | Sets HTTP options on server and downloads workbooks.
Explore Datasource | [explore_datasource.py](./samples/explore_datasource.py) | Demonstrates working with Tableau Datasource. Queries all datasources, picks one and populates its connections, then updates the datasource. Has additional flags for publish and download.
Explore Workbook | [explore_workbook.py](./samples/explore_workbook.py) | Demonstrates working with Tableau Workbook. Queries all workbooks, picks one and populates its connections/views, then updates the workbook. Has additional flags for publish, download, and getting the preview image.