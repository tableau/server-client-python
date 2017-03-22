---
title: API reference
layout: docs
---

<div class="alert alert-info">
    <b>Important:</b> More coming soon! This section is under active construction and might not reflect all the available functionality of the TSC library.
    Until this reference is completed, we have noted the source files in the TSC library where you can get more information for individual endpoints.
</div>

* TOC
{:toc}
{:toc_levels(1,2,3)}

## Authentication

Source files: server/endpoint/auth_endpoint.py, models/tableau_auth.py

### Sign In

Signs you in to Tableau Server.

```py
Auth.sign_in(authentication_object)
```

### Sign Out

Signs you out of Tableau Server.

```py
Auth.sign_out()
```

## Connection

### ConnectionItem class

```py
class ConnectionItem(object)
```

**Attributes**

`datasource_id` : 

`datasource_name` :

`id`  : 

`connection_type`  : 

`embed_password`  : 

`password`  : 

`server_address`   :  

`server_port`   : 

`username`    : 


Source file: models/connection_item.py

<br>
<br>

## Sites

Source files: server/endpoint/sites_endpoint.py, models/site_item.py

### Create Site

Creates a new site for the given site item object.

```py
Sites.create(new_site_item)
```

Example:

```py
new_site = TSC.SiteItem(name='Tableau', content_url='tableau', admin_mode=TSC.SiteItem.AdminMode.ContentAndUsers, user_quota=15, storage_quota=1000, disable_subscriptions=True)
self.server.sites.create(new_site)
```

### Get Site by ID

Gets the site with the given ID.

```py
Sites.get_by_id(id)
```

### Get Sites

Gets the first 100 sites on the server. To get all the sites, use the Pager.

```py
Sites.get()
```

### Update Site

Modifies a site. The site item object must include the site ID and overrides all other settings.

```py
Sites.update(site_item_object)
```

### Delete Site

Deletes the site with the given ID.

```py
Sites.delete(id)
```

## Projects

Source files: server/endpoint/projects_endpoint.py

### Create Project

Creates a project for the given project item object.

```py
Projects.create(project_item_object)
```

Example:

```py
new_project = TSC.ProjectItem(name='Test Project', description='Project created for testing')
new_project.content_permissions = 'ManagedByOwner'
self.server.projects.create(new_project)
```

### Get Projects

```py
Projects.get()
```

Get the first 100 projects on the server. To get all projects, use the Pager.

### Update Project

```py
Projects.update(project_item)
```

Modify a project. 

You can use this method to update the project name, the project description, or the project permissions.

##### Parameters

`project_item`

  The project item object must include the project ID. The values in the project item override the current project settings. 

##### Returns

Returns the updated project information. 

See ProjectItem

### Delete Project

Deletes a project by ID.

```py
Projects.delete(id)
```

## Workbooks

Source files: server/endpoint/workbooks_endpoint.py, models/workbook_item.py

### Get Workbooks

Get the first 100 workbooks on the server. To get all workbooks, use the Pager.

```py
Workbooks.get()
```

### Get Workbook by ID

Gets a workbook with a given ID.

```py
Workbooks.get_by_id(id)
```

### Publish Workbook

Publish a local workbook to Tableau Server.

```py
Workbooks.publish(workbook_item, file_path, publish_mode)
```

Where the publish mode is one of the following:

* Append
* Overwrite
* CreateNew

Example:

```py
wb_item = TSC.WorkbookItem(name='Sample',
                           show_tabs=False,
                           project_id='ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')

server.workbooks.publish(wb_item,
                         os.path.join(YOUR_DIR, 'SampleWB.twbx'),
                         self.server.PublishMode.CreateNew)
```

### Update Workbook

Modifies a workbook. The workbook item object must include the workbook ID and overrides all other settings.

```py
Workbooks.update(wb_item_object)
```

### Delete Workbook

Deletes a workbook with the given ID.

```py
Workbooks.delete(id)
```

### Download Workbook

Downloads a workbook to the specified directory.

```py
Workbooks.download(id, file_path)
```

### Populate Views for a Workbook

Populates a list of views for a workbook object. You must populate views before you can iterate through the views.

```py
Workbooks.populate_views(workbook_obj)
```

### Populate Connections for a Workbook

Populates a list of connections for a given workbook. You must populate connections before you can iterate through the
connections.

```py
Workbooks.populate_connections(workbook_obj)
```

### Populate a Preview Image for a Workbook

Populates a preview image for a given workbook. You must populate the image before you can iterate through the
connections.

```py
Workbooks.populate_preview_image(workbook_obj)
```

### Get Views for a Workbook

Returns a list of views for a workbook. Before you get views, you must call populate_views.

```py
Workbooks.views
```

### Get Connections for a Workbook

Returns a list of connections for a workbook. Before you get connections, you must call populate_connections.

```py
workbook_obj.connections
```



## Views
Get all the views on a site, or get the views for a specific workbook, or populate the preview image for a view.
The methods are based upon the ViewItem class. 

### ViewItem class

```
class ViewItem(object)
 
```

The ViewItem class contains the members or attributes for the view resources on Tableau Server. The ViewItem class defines the information you can request or query from Tableau Server. The class members correspontd to the attributes of a server request or response payload. 

Source file: models/view_item.py

**Attributes**


`id` : The identifier of the view item.  
 
`name`  : The name of the view. 

`owner_id` :  The id for the owner of the view. 

`preview_image` : The thumbnail image for the view. 

`total_views`  :  The usage statistics for the view. Indicates the total number of times the view has been looked at. 

`workbook_id`  :  The id of the workbook associated with the view. 





### View methods

The Tableau Server Client provides two methods for interacting with view resources, or endpoints. These methods correspond to the [Query Views for Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Views_for_Site%3FTocPath%3DAPI%2520Reference%7C_____64) and [Query View Preview Image](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Workbook_Preview_Image%3FTocPath%3DAPI%2520Reference%7C_____69) endpoints in the Tableau Server REST API. 

Source file: server/endpoint/views_endpoint.py

#### get()
```
Views.get(req_option=None)
```

Returns the list of views items for a site. 

**Parameters**

`req_option`  :   (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific view, you could specify the name of the view or its id. 


**Returns**

Returns a list of all `ViewItem` objects and a `PaginationItem`. Use these values to iterate through the results. 

**Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password')
server = TSC.Server('http://servername')

with server.auth.sign_in(tableau_auth):
  all_views, pagination_item = server.views.get()
  print([view.name for view in all_views])

````

See [ViewItem class](#viewitem-class)

#### populate_preview_image(*view_item*)

```py
 Views.populate_preview_image(view_item)

```

Populates a preview image for a given view. 

This method gets the preview image (thumbnail) for the specified view item. The method uses the `view.id` and `workbook.id` to identify the preview image. The method populates the `view.preview_image` for the view. 


**Parameters** 

`view_item`  :  The view item specifies the the `view.id` and `workbook.id` that identifies the preview image.

**Exceptions** 

`View item missing ID or workbook ID` :  Raises an error if the id for the view item or workbook is missing.   

**Returns**

None. The preview image is added to the view. 

See [ViewItem class](#viewitem-class)

   
## Data sources

Using the TSC library, you can get all the data sources on a site, or get the data sources for a specific project. 
The data source resources for Tableau Server are defined in the DatasourceItem class. The class corresponds to the data source resources you can access using the Tableau Server REST API, for example, information about the name of the data source, its type, and connections, and the project it is associated with. The data source methods are based upon the endpoints for data sources in the REST API and operate on the DatasourceItem class.  

### DatasourceItem class

```py
class DatasourceItem(object)
```
The `DatasourceItem` represents the data source resources on Tableau Server. This is the information returned in the response to a REST API request for data sources. 

**Attributes**

`connections` :  The list of data connections (`ConnectionItem`) for the specified data source. You must first call the `populate_connections` method to access this data. See the [ConnectionItem class](#connectionitem-class).

`content_url` :  The name of the data source as it would appear in a URL. 

`created_at` :  The date and time when the data source was created.  

`datasource_type` : The type of data source, for example, `sqlserver` or `excel-direct`. 

`id` : The identifier for the data source. You need this value to query a specific data source or to delete a data source with the `get_by_id` and `delete` methods. 

`project_id` :  The identifer of the project associated with the data source. 

`project_name` :  The name of the project associated with the data source. 

`tags` :  The tags that have been added to the data source. 

`updated_at` :  The date and time when the data source was last updated. 

Source file:  models/datasource_item.py

<br> 
<br>

### Datasource methods

The Tableau Server Client provides several methods for interacting with data source resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API. 

<br> 
<br>

#### delete(*datasource_id*)

```py
datasources.delete(datasource_id)
```

Removes the specified data source from Tableau Server. 


**Parameters**

`datasource_id`  :  The identifier (`id`) for the the `DatasourceItem` that you want to delete from the server. 


**Exceptions**

`Datasource ID undefined`   :  Raises an exception if a valid `datasource_id` is not provided.


REST API: [Delete Datasource](http://onlinehelp.tableau.com/v0.0/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Delete_Datasource%3FTocPath%3DAPI%2520Reference%7C_____19){:target="_blank"}

<br> 
<br>


#### download(*datasource_id*, *filepath=None*)

```py
datasources.download(datasource_id, filepath=None)

```
Downloads the specified data source in `.tdsx` format. 


**Parameters**

`datasource_id` :  The identifier (`id`) for the the `DatasourceItem` that you want to download from the server. 

`filepath` :  (Optional) Downloads the file to the location you specify. If no location is specified (the default is `Filepath=None`), the file is downloaded to the current working directory. 


**Exceptions**

`Datasource ID undefined`   :  Raises an exception if a valid `datasource_id` is not provided.


**Returns**  

The data source in `.tdsx` format. 


REST API: [Download Datasource](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Download_Datasource%3FTocPath%3DAPI%2520Reference%7C_____34){:target="_blank"}  
  
<br> 
<br>

#### get()

```py
datasources.get(req_options=None)
```

Returns all the data sources for the site. 

To get the connection information for each data source, you must first populate the `DatasourceItem` with connection information using the [populate_connections(*datasource_item*)](#populate-connections-datasource) method. For more information, see [Populate Connections and Views](populate-connections-views#populate-connections-for-data-sources)

REST API: [Query Datasources](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasources%3FTocPath%3DAPI%2520Reference%7C_____49)

**Parameters**

`req_option` :  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific data source, you could specify the name of the project or its id. 


**Returns**

Returns a list of `DatasourceItem` objects and a `PaginationItem`  object.  Use these values to iterate through the results. 




**Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVERURL')

with server.auth.sign_in(tableau_auth):
    all_datasources, pagination_item = server.datasources.get()
    print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
    print([datasource.name for datasource in all_datasources])
````



<br>   
<br>  


#### get_by_id(*datasource_id*)

```py
datasources.get_by_id(datasource_id)
```

Returns the specified data source item. 

REST API: [Query Datasource](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasource%3FTocPath%3DAPI%2520Reference%7C_____46)


**Parameters**

`datasource_id`  :  The `datasource_id` specifies the data source to query. 


**Exceptions**

`Datasource ID undefined`   :  Raises an exception if a valid `datasource_id` is not provided.


**Returns**

The `DatasourceItem`.  See [DatasourceItem class](#datasourceitem-class)


**Example**

```py
datasource = server.datasources.get_by_id(server.datasources[1].id)
print(datasource.name)

```


<br>   
<br>  

<a name="populate-connections-datasource"></a>

#### populate_connections(*datasource_item*)

Populates the connections for the specified data source.




This method retrieves the connection information for the specified data source. The REST API is designed to return only the information you ask for explicitly. When you query for all the data sources, the connection information is not included. Use this method to retrieve the connections. The method adds the list of data connections to the data source item (`datasource_item.connections`) populates the data source with the list of `ConnectionItem`.  

REST API:  [Query Datasource Connections](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasource_Connections%3FTocPath%3DAPI%2520Reference%7C_____47)

**Parameters**

`datasource_item`  :  The `datasource_item` specifies the data source to populate with connection information.




**Exceptions**

`Datasource item missing ID. Datasource must be retrieved from server first.` :  Raises an errror if the datasource_item is unspecified.


**Returns**

None. A list of `ConnectionItem` objects are added to the data source (`datasource_item.connections`). 


**Example**

```py
datasource = server.datasources.get_by_id(server.datasources[1].id)
print(datasource.name)

server.datasources.populate_connections(datasource)
print([connection.datasource_name for connection in datasource.connections])
```


<br>   
<br>  

#### publish(*datasource_item*)


<br>   
<br>  

#### update(*datasource_item*)

Source files: server/endpoint/datasources_endpoint.py, models/datasource_item.py

<br>   
<br>  

## Users

Source files: server/endpoint/users_endpoint.py, models/user_item.py


<br>   
<br>  

## Groups

Source files: server/endpoint/groups_endpoint.py, models/group_item.py



<br>   
<br>  

