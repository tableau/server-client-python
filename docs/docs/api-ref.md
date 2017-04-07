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

You can use the TSC library to manage authentication, so you can sign in and sign out of Tableau Server and Tableau Online. The authentication resources for Tableau Server are defined in the `TableauAuth` class and they correspond to the authentication attributes you can access using the Tableau Server REST API. 

<br>
<br>  

### TableauAuth class

```py
TableauAuth(username, password, site=None, site_id='', user_id_to_impersonate=None)
```
The `TableauAuth` class contains the attributes for the authentication resources. The `TableauAuth` class defines the information you can set in a  request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload. To use this class, create a new instance, supplying user name, password, and site information if necessary, and pass the request object to the [Auth.sign_in](#auth.sign-in) method.

**Attributes**  
`username` : The name of the user whose credentials will be used to sign in.   
`password` : The password of the user.   
`site`  : (Deprecated) Use `site_id` instead.   
`site_id` : This corresponds to the `contentUrl` attribute in the Tableau REST API. The `site_id` is the portion of the URL that follows the `/site/` in the URL. For example, "MarketingTeam" is the `site_id` in the following URL *MyServer*/#/site/**MarketingTeam**/projects. To specify the default site on Tableau Server, you can use an empty string **""**.  For Tableau Online, you must provide a value for the `site_id`.  
`user_id_to_impersonate` :  Specifies the id (not the name) of the user to sign in as. 

Source file: models/tableau_auth.py

**Example**

```py
import tableauserverclient as TSC
# create a new instance of a TableauAuth object for authentication

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')

# create a server instance
# pass the "tableau_auth" request object to server.auth.sign_in()
```

<br>
<br>  

### Auth methods
The Tableau Server Client provides two methods for interacting with authentication resources. These methods correspond to the sign in and sign out endpoints in the Tableau Server REST API.


Source file: server/endpoint/auth_endpoint.py

<br>
<br> 

#### auth.sign in

```py
auth.sign_in(auth_req)
```

Signs you in to Tableau Server.


The method signs into Tableau Server or Tableau Online and manages the authentication token. You call this method from the server object you create. For information about the server object, see [Server](#server). The authentication token keeps you signed in for 240 minutes, or until you call the `auth.sign_out` method. Before you use this method, you first need to create the sign-in request (`auth_req`) by creating an instance of the `TableauAuth`. To call this method, create a server object for your server. For more information, see [Sign in and Out](sign-in-out).

REST API: [Sign In](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Sign_In%3FTocPath%3DAPI%2520Reference%7C_____77){:target="_blank"}

**Parameters**

`auth_req` : The `TableauAuth` object that holds the sign-in credentials for the site. 


**Example**

```py
import tableauserverclient as TSC

# create a auth request
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')

# create an instance for your server
server = TSC.Server('http://SERVER_URL')

# call the sign-in method with the request
server.auth.sign_in(tableau_auth)

```


**See Also**  
[Sign in and Out](sign-in-out)  
[Server](#server)

<br>
<br>


#### auth.sign out

```py
auth.sign_out()
```
Signs you out of the current session.

The method takes care of invalidating the authentiction token. For more information, see [Sign in and Out](sign-in-out).

REST API: [Sign Out](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Sign_Out%3FTocPath%3DAPI%2520Reference%7C_____78){:target="_blank"}

**Example**

```py

server.auth.sign_out()


```




**See Also**  
[Sign in and Out](sign-in-out)  
[Server](#server)

<br>
<br>




## Connections

The connections for Tableau Server data sources and workbooks are represented by a `ConnectionItem` class.  You can call data source and view methods to query or update the connection information.  The `ConnectionCredentials` class represents the connection information you can update. 

### ConnectionItem class

```py
ConnectionItem(object)
```

**Attributes**

`datasource_id` :  The identifier of the data source. 

`datasource_name` :  The name of the data source.

`id`  :  The identifer of the connection.

`connection_type`  :  The type of connection. 


Source file: models/connection_item.py  

<br>
<br>



### ConnectionCredentials class

```py
ConnectionCredentials(name, password, embed=True, oauth=False)
```


The `ConnectionCredentials` class corresponds to workbook and data source connections. 

In the Tableau Server REST API, there are separate endopoints to query and update workbook and data source connections. 

**Attributes**

Attribute | Description
:--- | :---
`name`     | The username for the connection.
`embed_password`  |  (Boolean) Determines whether to embed the passowrd (`True`) for the workbook or data source connection or not (`False`). 
`password`  |  The password used for the connection.   
`server_address`   |  The server address for the connection.   
`server_port`   |  The port used by the server.  
`ouath`  |  (Boolean) Specifies whether OAuth is used for the data source of workbook connection. For more information, see [OAuth Connections](https://onlinehelp.tableau.com/current/server/en-us/protected_auth.htm?Highlight=oauth%20connections){:target="_blank"}.  


Source file: models/connection_credentials.py

<br>
<br>

## Server

In the Tableau REST API, the server (`http://MY-SERVER/`) is the base or core of the URI that makes up the various endpoints or methods for accessing resources on the server (views, workbooks, sites, users, data sources, etc.) 
The TSC library provides a `Server` class that represents the server. You create a server instance to sign in to the server and to call the various methods for accessing resources.  


<br>
<br>  


### Server class

```py
Server(server_address)
```
The `Server` class contains the attributes that represent the server on Tableau Server. After you create an instance of the `Server` class, you can sign in to the server and call methods to access all of the resources on the server.   

**Attributes**

`server_address`  :  Specifies the address of the Tableau Server or Tableau Online (for example, `http://MY-SERVER/`).  

`version`   :  Specifies the version of the REST API to use (for example, `2.5`). When you use the TSC library to call methods that access Tableau Server, the `version` is passed to the endpoint as part of the URI (`https://MY-SERVER/api/2.5/`). Each release of Tableau Server supports specific versions of the REST API. New versions of the REST API are released with Tableau Server. By default, the value of `version` is set to 2.3, which corresponds to Tableau Server 10.0.  You can view or set this value. You might need to set this to a different value, for example, if you want to access features that are supported by the server and a later version of the REST API.  For more information, see [REST API Versions](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_concepts_versions.htm){:target="_blank"}  



**Example**

```py
import tableauserverclient as TSC

# create a instance of server 
server = TSC.Server('http://MY-SERVER')


# change the REST API version to 2.5
server.version = 2.5  


```

#### Server.*Resources* (Objects)  

When you create an instance of the `Server` class, you have access to the resources on the server after you sign in. You can select these resources and their methods as members of the class, for example: `server.views.get()`  



Resource   |  Description  |   
 --- | ---|  
*server*.auth   |   Sets authentication for sign in and sign out. See [Auth](#auththentication)  |
*server*.views  |   Access the server views and methods.  See [Views](#views)  
*server*.users  |   Access the user resources and methods.  See [Users](#users)  
*server*.sites  |   Access the sites.  See [Sites](#sites)  
*server*.groups   | Access the groups resources and methods. See [Groups](#groups)  
*server*.workbooks  |  Access the resources and methods for workbooks. See [Workbooks](#workbooks)
*server*.datasources  |  Access the resources and methods for data sources. See [Data Sources](#data-sources)
*server*.projects  |   Access the resources and methods for projects. See [Projects](#projets)
*server*.schedules  |  Access the resources and methods for schedules. See [Schedules](#Schedules)
*server*.server_info  |  Access the resources and methods for server information. See [ServerInfo class](#serverinfo-class) 

<br>
<br>

#### Server.PublishMode

The `Server` class has `PublishMode` class that enumerates the options that specify what happens when you publish a workbook or data source. The options are `Overwrite`,  `Append`, or `CreateNew`. 


**Properties**

`PublishMode.Overwrite`  : The `Server` class has `PublishMode` class that you can set to specify what happens when you publish a workbook or data source. The options are `Overwrite`,  `Append`, or `CreateNew`. 

**Example**

```py
 
 print(TSC.Server.PublishMode.Overwrite)
 # prints 'Overwrite'
 
 overwrite_true = TSC.Server.PublishMode.Overwrite

 ...

 # pass the PublishMode to the publish workbooks method
 new_workbook = server.workbooks.publish(new_workbook, args.filepath, overwrite_true)


```


<br>
<br>


### ServerInfoItem class

```py
ServerInfoItem(product_version, build_number, rest_api_version)
```
The `ServerInfoItem` class contains the builid and version information for Tableau Server. The server information is accessed with the `server_info.get()` method, which returns an instance of the `ServerInfo` class. 

**Attributes**

`product_version`  :  Shows the version of the Tableau Server or Tableau Online (for example, 10.2.0).   
`build_number`   :  Shows the specific build number (for example, 10200.17.0329.1446).
`rest_api_version`  :  Shows the supported REST API version number. Note that this might be different from the default value specified for the server, with the `Server.version` attribute. To take advantage of new features, you should query the server and set the `Server.version` to match the supported REST API version number. 


<br>
<br>


### ServerInfo methods

The TSC library provides a method to access the build and version information from Tableau Server.   

<br>   

#### server_info.get

```py
server_info.get()
 
```
Retrieve the build and version information for the server.  

This method makes an unauthenticated call, so no sign in or authentication token is required.  

REST API: [Server Info](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Server_Info%3FTocPath%3DAPI%2520Reference%7C_____76){:target="_blank"}   
  
**Parameters**  
 None 
 
**Exceptions**

`404003	UNKNOWN_RESOURCE`  :  Raises an exception if the server info endpoint is not found. 

**Example**

```py
import tableauserverclient as TSC

# create a instance of server 
server = TSC.Server('http://MY-SERVER')

# set the version number > 2.3 
# the server_info.get() method works in 2.4 and later
server.version = '2.5'

s_info = server.server_info.get()
print("\nServer info:")
print("\tProduct version: {0}".format(s_info.product_version))
print("\tREST API version: {0}".format(s_info.rest_api_version))
print("\tBuild number: {0}".format(s_info.build_number))

``` 


<br>
<br>


## Sites

Using the TSC library, you can query a site or sites on a server, or create or delete a site on the server.

The site resources for Tableau Server and Tableau Online are defined in the `SiteItem` class. The class corresponds to the site resources you can access using the Tableau Server REST API. The site methods are based upon the endpoints for sites in the REST API and operate on the `SiteItem` class.

<br>   
<br> 

### SiteItem class

```py
SiteItem(name, content_url, admin_mode=None, user_quota=None, storage_quota=None,
                 disable_subscriptions=False, subscribe_others_enabled=True, revision_history_enabled=False)
```

The `SiteItem` class contains the members or attributes for the site resources on Tableau Server or Tableau Online. The `SiteItem` class defines the information you can request or query from Tableau Server or Tableau Online. The class members correspond to the attributes of a server request or response payload.

**Attributes**

Attribute | Description
:--- | :---
`name` | The name of the site. The name of the default site is "".  
`content_url` | The path to the site.  
`admin_mode` | (Optional) For Tableau Server only. Specify `ContentAndUsers` to allow site administrators to use the server interface and **tabcmd** commands to add and remove users. (Specifying this option does not give site administrators permissions to manage users using the REST API.) Specify `ContentOnly` to prevent site administrators from adding or removing users. (Server administrators can always add or remove users.)
`user_quota`| (Optional) Specifies the maximum number of users for the site. If you do not specify this value, the limit depends on the type of licensing configured for the server. For user-based license, the maximum number of users is set by the license. For core-based licensing, there is no limit to the number of users. If you specify a maximum value, only licensed users are counted and server administrators are excluded.
`storage_quota` | (Optional) 	Specifes the maximum amount of space for the new site, in megabytes. If you set a quota and the site exceeds it, publishers will be prevented from uploading new content until the site is under the limit again.
`disable_subscriptions` | (Optional) Specify `true` to prevent users from being able to subscribe to workbooks on the specified site. The default is `false`.  
`subscribe_others_enabled` | (Optional) Specify `false` to prevent server administrators, site administrators, and project or content owners from being able to subscribe other users to workbooks on the specified site. The default is `true`. 
`revision_history_enabled` |  (Optional) Specify `true` to enable revision history for content resources (workbooks and datasources). The default is `false`.   
`revision_limit` | (Optional) Specifies the number of revisions of a content source (workbook or data source) to allow. On Tableau Server, the default is 25.   
`state` | Shows the current state of the site (`Active` or `Suspended`). 


**Example**

```py

# create a new instance of a SiteItem

new_site = TSC.SiteItem(name='Tableau', content_url='tableau', admin_mode='ContentAndUsers', user_quota=15, storage_quota=1000, disable_subscriptions=True)

```

Source files: server/endpoint/sites_endpoint.py, models/site_item.py

### sites.create

```py
sites.create(site_item)
```

Creates a new site on the server for the specified site item object. 

Tableau Server only. 


REST API: [Create Site](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Create_Site%3FTocPath%3DAPI%2520Reference%7C_____17){:target="_blank"}  



**Parameters**  
  
`site_item` : The settings for the site that you want to create. You need to create an instance of `SiteItem` and pass the the `create` method.


**Returns**  

Returns a new instance of `SiteItem`.


**Example**

```py
import tableauserverclient as TSC

# create an instance of server 
server = TSC.Server('http://MY-SERVER')

# create shortcut for admin mode
content_users=TSC.SiteItem.AdminMode.ContentAndUsers

# create a new SiteItem
new_site = TSC.SiteItem(name='Tableau', content_url='tableau', admin_mode=content_users, user_quota=15, storage_quota=1000, disable_subscriptions=True)

# call the sites create method with the SiteItem
new_site = server.sites.create(new_site)
```
<br>
<br>  


### sites.get_by_id

```py
sites.get_by_id(site_id)
```

Queries the site with the given ID.


REST API: [Query  Site](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Site){:target="_blank"}    

**Parameters**  

`site_id`  | The id for the site you want to query. 


**Exceptions**  

`Site ID undefined.` | Raises an error if an id is not specified. 


**Returns**  

Returns the `SiteItem`.  
  

**Example**   

```py

# import tableauserverclient as TSC
# server = TSC.Server('http://MY-SERVER')
# sign in, etc.

 a_site = server.sites.get_by_id('9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d')
 print("\nThe site with id '9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d' is: {0}".format(a_site.name)) 

```

<br>
<br>

### sites.get

```py
sites.get()
```

Queries all the sites on the server. 


REST API: [Query Sites](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Sites%3FTocPath%3DAPI%2520Reference%7C_____58){:target="_blank"}  


**Parameters**

 None.

**Returns**  
 
Returns a list of all `SiteItem` objects and a `PaginationItem`. Use these values to iterate through the results. 


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('http://MY-SERVER')
# sign in, etc.

  # query the sites
  all_sites, pagination_item = server.sites.get()

  # print all the site names and ids
  for site in TSC.Pager(server.sites):
       print(site.id, site.name, site.content_url, site.state)


```

<br>
<br>


### sites.update

```py
sites.update(site_item)
```

Modifies the settings for site. 


The site item object must include the site ID and overrides all other settings.


REST API: [Update Site](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Update_Site%3FTocPath%3DAPI%2520Reference%7C_____84){:target="_blank"}  


**Parameters**

`site_item` |  The site item that you want to update. The settings specified in the site item override the current site settings.  


**Exceptions**

Error | Description
:--- | :---  
`Site item missing ID.` |    The site id must be present and must match the id of the site you are updating.   
`You cannot set admin_mode to ContentOnly and also set a user quota`  |  To set the `user_quota`, the `AdminMode` must be set to `ContentAndUsers`


**Returns**  

Returns the updated `site_item`.  


**Example**  

```py
...

# make some updates to an existing site_item
site_item.name ="New name"

# call update
site_item = server.sites.update(site_item)

...
```

<br>
<br>




### sites.delete


```py
Sites.delete(site_id)
```

Deletes the specified site.


REST API: [Delete Site](https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Delete_Site%3FTocPath%3DAPI%2520Reference%7C_____27){:target="_name"}  


**Parameters**
  

`site_id`    |       The id of the site that you want to delete.   



**Exceptions**

Error  |  Description  
:---  | :---   
`Site ID Undefined.`   |    The site id must be present and must match the id of the site you are deleting.   

**Example**
```py

# import tableauserverclient as TSC
# server = TSC.Server('http://MY-SERVER')
# sign in, etc.

server.sites.delete('9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d')

```

<br>
<br>


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

<br>   
<br>

## Views

Using the TSC library, you can get all the views on a site, or get the views for a workbook, or populate a view with preview images. 
The view resources for Tableau Server are defined in the `ViewItem` class. The class corresponds to the view resources you can access using the Tableau Server REST API, for example, you can find the name of the view, its id, and the id of the workbook it is associated with. The view methods are based upon the endpoints for views in the REST API and operate on the `ViewItem` class. 


<br>

### ViewItem class

```
class ViewItem(object)
 
```

The `ViewItem` class contains the members or attributes for the view resources on Tableau Server. The `ViewItem` class defines the information you can request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload. 

Source file: models/view_item.py

**Attributes**


`id` : The identifier of the view item.  
 
`name`  : The name of the view. 

`owner_id` :  The id for the owner of the view. 

`preview_image` : The thumbnail image for the view. 

`total_views`  :  The usage statistics for the view. Indicates the total number of times the view has been looked at. 

`workbook_id`  :  The id of the workbook associated with the view. 


<br>   
<br>


### Views methods

The Tableau Server Client provides two methods for interacting with view resources, or endpoints. These methods correspond to the endpoints for views in the Tableau Server REST API. 

Source file: server/endpoint/views_endpoint.py

<br>   
<br>

#### views.get
```
views.get(req_option=None)
```

Returns the list of views items for a site. 


REST API: [Query Views for Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Views_for_Site%3FTocPath%3DAPI%2520Reference%7C_____64){:target="_blank"}

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


<br>   
<br>

#### views.populate_preview_image

```py
 views.populate_preview_image(view_item)

```

Populates a preview image for a given view. 

This method gets the preview image (thumbnail) for the specified view item. The method uses the `view.id` and `workbook.id` to identify the preview image. The method populates the `view.preview_image` for the view. 

REST API: [Query View Preview Image](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Workbook_Preview_Image%3FTocPath%3DAPI%2520Reference%7C_____69){:target="_blank"}

**Parameters** 

`view_item`  :  The view item specifies the the `view.id` and `workbook.id` that identifies the preview image.

**Exceptions** 

`View item missing ID or workbook ID` :  Raises an error if the id for the view item or workbook is missing.   

**Returns**

None. The preview image is added to the view. 

See [ViewItem class](#viewitem-class)

<br>   
<br>

## Data sources

Using the TSC library, you can get all the data sources on a site, or get the data sources for a specific project. 
The data source resources for Tableau Server are defined in the `DatasourceItem` class. The class corresponds to the data source resources you can access using the Tableau Server REST API. For example, you can gather information about the name of the data source, its type, and connections, and the project it is associated with. The data source methods are based upon the endpoints for data sources in the REST API and operate on the `DatasourceItem` class.  

<br>

### DatasourceItem class

```py
DatasourceItem(project_id, name=None)
```

The `DatasourceItem` represents the data source resources on Tableau Server. This is the information that can be sent or returned in the response to an REST API request for data sources.  When you create a new `DatasourceItem` instance, you must specify the `project_id` that the data source is associated with.

**Attributes**

`connections` :  The list of data connections (`ConnectionItem`) for the specified data source. You must first call the `populate_connections` method to access this data. See the [ConnectionItem class](#connectionitem-class).

`content_url` :  The name of the data source as it would appear in a URL. 

`created_at` :  The date and time when the data source was created.  

`datasource_type` : The type of data source, for example, `sqlserver` or `excel-direct`. 

`id` : The identifier for the data source. You need this value to query a specific data source or to delete a data source with the `get_by_id` and `delete` methods. 

`name`  : The name of the data source. If not specified, the name of the published data source file is used. 

`project_id` :  The identifer of the project associated with the data source. When you must provide this identifier when create an instance of a `DatasourceItem`

`project_name` :  The name of the project associated with the data source. 

`tags` :  The tags that have been added to the data source. 

`updated_at` :  The date and time when the data source was last updated. 


**Example**

```py
    import tableauserverclient as TSC

    # Create new datasource_item with project id '3a8b6148-493c-11e6-a621-6f3499394a39'

    new_datasource = TSC.DatasourceItem('3a8b6148-493c-11e6-a621-6f3499394a39')
```


Source file:  models/datasource_item.py

<br> 
<br>

### Datasources methods

The Tableau Server Client provides several methods for interacting with data source resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API. 

Source file: server/endpoint/datasources_endpoint.py

<br> 
<br>

#### ds.delete(*datasource_id*)

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


#### ds.download(*datasource_id*, *filepath=None*)

```py
datasources.download(datasource_id, filepath=None)

```
Downloads the specified data source in `.tdsx` format. 

REST API: [Download Datasource](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Download_Datasource%3FTocPath%3DAPI%2520Reference%7C_____34){:target="_blank"}  

**Parameters**

`datasource_id` :  The identifier (`id`) for the the `DatasourceItem` that you want to download from the server. 

`filepath` :  (Optional) Downloads the file to the location you specify. If no location is specified (the default is `Filepath=None`), the file is downloaded to the current working directory. 


**Exceptions**

`Datasource ID undefined`   :  Raises an exception if a valid `datasource_id` is not provided.


**Returns**  

The data source in `.tdsx` format. 



  
<br> 
<br>

#### ds.get()

```py
datasources.get(req_options=None)
```

Returns all the data sources for the site. 

To get the connection information for each data source, you must first populate the `DatasourceItem` with connection information using the [populate_connections(*datasource_item*)](#populate-connections-datasource) method. For more information, see [Populate Connections and Views](populate-connections-views#populate-connections-for-data-sources)

REST API: [Query Datasources](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasources%3FTocPath%3DAPI%2520Reference%7C_____49){:target="_blank"}

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


#### ds.get_by_id(*datasource_id*)

```py
datasources.get_by_id(datasource_id)
```

Returns the specified data source item. 

REST API: [Query Datasource](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasource%3FTocPath%3DAPI%2520Reference%7C_____46){:target="_blank"}


**Parameters**

`datasource_id`  :  The `datasource_id` specifies the data source to query. 


**Exceptions**

`Datasource ID undefined`   :  Raises an exception if a valid `datasource_id` is not provided.


**Returns**

The `DatasourceItem`.  See [DatasourceItem class](#datasourceitem-class)


**Example**

```py

datasource = server.datasources.get_by_id('59a57c0f-3905-4022-9e87-424fb05e9c0e')
print(datasource.name)

```


<br>   
<br>  

<a name="populate-connections-datasource"></a>

#### ds.populate_connections(*datasource_item*)

```py
datasources.populate_connections(datasource_item)
```

Populates the connections for the specified data source.




This method retrieves the connection information for the specified data source. The REST API is designed to return only the information you ask for explicitly. When you query for all the data sources, the connection information is not included. Use this method to retrieve the connections. The method adds the list of data connections to the data source item (`datasource_item.connections`) populates the data source with the list of `ConnectionItem`.  

REST API:  [Query Datasource Connections](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasource_Connections%3FTocPath%3DAPI%2520Reference%7C_____47){:target="_blank"}

**Parameters**

`datasource_item`  :  The `datasource_item` specifies the data source to populate with connection information.




**Exceptions**

`Datasource item missing ID. Datasource must be retrieved from server first.` :  Raises an errror if the datasource_item is unspecified.


**Returns**

None. A list of `ConnectionItem` objects are added to the data source (`datasource_item.connections`). 


**Example**

```py
# import tableauserverclient as TSC

# server = TSC.Server('http://SERVERURL')
# 
   ... 

# get the data source
  datasource = server.datasources.get_by_id('1a2a3b4b-5c6c-7d8d-9e0e-1f2f3a4a5b6b')


# get the connection information 
  server.datasources.populate_connections(datasource)

# print the information about the first connection item
  print(datasource.connections[0].connection_type)
  print(datasource.connections[0].id)
  print(datasource.connections[0].server_address)

  ...

```


<br>   
<br>  

#### ds.publish(*datasource_item*, *file_path*, *mode*, *connection_credentials=None*)

```py
datasources.publish(datasource_item, file_path, mode, connection_credentials=None)
```

Publishes a data source to a server, or appends data to an existing data source. 

This method checks the size of the data source and automatically determines whether the publish the data source in multiple parts or in one opeation.  

REST API: [Publish Datasource](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Publish_Datasource%3FTocPath%3DAPI%2520Reference%7C_____44){:target="_blank"}

**Parameters**

`datasource_item`  :  The `datasource_item` specifies the new data source you are adding, or the data source you are appending to. If you are adding a new data source, you need to create a new `datasource_item` with a `project_id` of an existing project. The name of the data source will be the name of the file, unless you also specify a name for the new data source when you create the instance. See [DatasourceItem](#datasourceitem-class).

`file_path`  :  The path and name of the data source to publish. 

`mode`     :  Specifies whether you are publishing a new data source (`CreateNew`), overwriting an existing data source (`Overwrite`), or appending data to a data source (`Append`). If you are appending to a data source, the data source on the server and the data source you are publishing must be be extracts (.tde files) and they must share the same schema. You can also use the publish mode attributes, for example: `TSC.Server.PublishMode.Overwrite`.

`connection_credentials` : (Optional)  The credentials required to connect to the data source. The `ConnectionCredentials` object contains the authentication information for the data source (user name and password, and whether the credentials are embeded or OAuth is used). 
 


**Exceptions**

`File path does not lead to an existing file.`  :  Raises an error of the file path is incorrect or if the file is missing.

`Invalid mode defined.`  :  Raises an error if the publish mode is not one of the defined options. 

`Only .tds, tdsx, or .tde files can be published as datasources.`  :  Raises an error if the type of file specified is not supported.  


**Returns**

The `DatasourceItem` for the data source that was added or appened to. 


**Example**

```py

  import tableauserverclient as TSC
  server = TSC.Server('http://SERVERURL')
    
  ...

  project_id = '3a8b6148-493c-11e6-a621-6f3499394a39'
  file_path = 'C:\\temp\\WorldIndicators.tde'

  # Use the project id to create new datsource_item
  new_datasource = TSC.DatasourceItem(project_id)

  # publish data source (specifed in file_path)
  new_datasource = server.datasources.publish(
                    new_datasource, file_path, 'CreateNew')

    ...
```

<br>   
<br>  

#### ds.update(*datasource_item*)

```py
datasource.update(datasource_item)
```

Updates the owner, or project of the specified data source. 

REST API: [Update Datasource](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Update_Datasource%3FTocPath%3DAPI%2520Reference%7C_____79){:target="_blank"}

**Parameters**

`datasource_item`  :  The `datasource_item` specifies the data source to update.



**Exceptions**

`Datasource item missing ID. Datasource must be retrieved from server first.` :  Raises an errror if the datasource_item is unspecified. Use the `Datasources.get()` method to retrieve that identifies for the data sources on the server.


**Returns**

An updated `DatasourceItem`.


**Example**

```py
# from server-client-python/test/test_datasource.py

    ...

    single_datasource = TSC.DatasourceItem('test', '1d0304cd-3796-429f-b815-7258370b9b74')
    single_datasource._id = '9dbd2263-16b5-46e1-9c43-a76bb8ab65fb'
    single_datasource._tags = ['a', 'b', 'c']
    single_datasource._project_name = 'Tester'
    updated_datasource = self.server.datasources.update(single_datasource)

     ...

```

Source files: server/endpoint/datasources_endpoint.py, models/datasource_item.py








<br>   
<br>  

## Users

Using the TSC library, you can get information about all the users on a site, and you can add or remove users, or update user information.

The user resources for Tableau Server are defined in the `UserItem` class. The class corresponds to the user resources you can access using the Tableau Server REST API. The user methods are based upon the endpoints for users in the REST API and operate on the `UserItem` class.  


### UserItem class

```py
UserItem(name, site_role, auth_setting=None)
```

The `UserItem` class contains the members or attributes for the view resources on Tableau Server. The `UserItem` class defines the information you can request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload. 

**Attributes**

`auth_setting` : (Optional) This attribute is only  for Tableau Online. The new authentication type for the user. You can assign the following values for this attribute: `SAML` (the user signs in using SAML) or `ServerDefault` (the user signs in using the authentication method that's set for the server). These values appear in the **Authentication** tab on the **Settings** page in Tableau Online -- the `SAML` attribute value corresponds to **Single sign-on**, and the `ServerDefault` value corresponds to **TableauID**.

`domain_name`  :    The name of the site.   
`external_auth_user_id` :   Represents ID stored in Tableau's single sign-on (SSO) system. The `externalAuthUserId` value is returned for Tableau Online. For other server configurations, this field contains null.    
`id` :   The id of the user on the site.  
`last_login` : The date and time the user last logged in.         
`workbooks` :  The workbooks the user owns. You must run the populate_workbooks method to add the workbooks to the `UserItem`.  

`email` :  The email address of the user.    
`fullname` : The full name of the user.    
`name` :   The name of the user. This attribute is required when you are creating a `UserItem` instance.  
`site_role` :  The role the user has on the site. This attribute is required with you are creating a `UserItem` instance. The `site_role` can be one of the following: `Interactor`, `Publisher`, `ServerAdministrator`, `SiteAdministrator`, `Unlicensed`, `UnlicensedWithPublish`, `Viewer`, `ViewerWithPublish`, `Guest`


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('server')

# create a new UserItem object.
  newU = TSC.UserItem('Monty', 'Publisher')
 
  print(newU.name, newU.site_role)

```

Source file: models/user_item.py

<br> 
<br>


###  Users Methods

The Tableau Server Client provides several methods for interacting with user resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API.

Source file: server/endpoint/users_endpoint.py
<br> 
<br>

#### users.add(*user_item*)

```py
users.add(user_item)
```

Adds the user to the site. 

To add a new user to the site you need to first create a new `user_item` (from `UserItem` class). When you create a new user, you specify the name of the user and their site role. For Tableau Online, you also specify the `auth_setting` attribute in your request.  When you add user to Tableau Online, the name of the user must be the email address that is used to sign in to Tableau Online. After you add a user, Tableau Online sends the user an email invitation. The user can click the link in the invitation to sign in and update their full name and password.

REST API: [Add User to Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Add_User_to_Site%3FTocPath%3DAPI%2520Reference%7C_____9){:target="_blank"}

**Parameters**

`user_item` :  You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific user, you could specify the name of the user or the user's id. 


**Returns**

Returns the new `UserItem` object.  




**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('server')
# login, etc.

# create a new UserItem object.
  newU = TSC.UserItem('Heather', 'Publisher')

# add the new user to the site
  newU = server.users.add(newU)
  print(newU.name, newU.site_role)

```

### users.get

```py
users.get(req_options=None)
```

Returns information about the users on the specified site.

To get information about the workbooks a user owns or has view permission for, you must first populate the `UserItem` with workbook information using the [populate_workbooks(*user_item*)](#populate-workbooks-user) method. 


REST API: [Get Uers on Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Get_Users_on_Site%3FTocPath%3DAPI%2520Reference%7C_____41){:target="_blank"}

**Parameters**

``req_option` :  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific user, you could specify the name of the user or the user's id. 


**Returns**

Returns a list of `UserItem` objects and a `PaginationItem`  object.  Use these values to iterate through the results. 


**Example**


```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVERURL')

with server.auth.sign_in(tableau_auth):
    all_users, pagination_item = server.users.get()
    print("\nThere are {} user on site: ".format(pagination_item.total_available))
    print([user.name for user in all_users])
````

<br>
<br>

#### users.get_by_id(*user_id*)


```py
users.get_by_id(user_id)
```

Returns information about the specified user.   

REST API: [Query User On Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_User_On_Site%3FTocPath%3DAPI%2520Reference%7C_____61){:target="_blank"}


**Parameters**

`user_id`  :  The `user_id` specifies the user to query. 


**Exceptions**

`User ID undefined.`   :  Raises an exception if a valid `user_id` is not provided.


**Returns**

The `UserItem`.  See [UserItem class](#useritem-class)


**Example**

```py
  user1 = server.users.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
  print(user1.name)

```

<br>   
<br>  


#### users.populate_favorites
  
```py
users.populate_favorites(user_item)
```

Returns the list of favorites (views, workbooks, and data sources) for a user.

*Not currently implemented*

<br>   
<br> 


#### users.populate_workbooks(*user_item*, *req_options=None*)

```py
users.populate_workbooks(user_item, req_options=None):
```

Returns information about the workbooks that the specified user owns and has Read (view) permissions for. 


This method retrieves the workbook information for the specified user. The REST API is designed to return only the information you ask for explicitly. When you query for all the users, the workbook information for each user is not included. Use this method to retrieve information about the workbooks that the user owns or has Read (view) permissions. The method adds the list of workbooks to the user item object (`user_item.workbooks`).  

REST API:  [Query Datasource Connections](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Query_Datasource_Connections%3FTocPath%3DAPI%2520Reference%7C_____47){:target="_blank"}

**Parameters**

`user_item`  :  The `user_item` specifies the user to populate with workbook information.




**Exceptions**

`User item missing ID.` :  Raises an errror if the `user_item` is unspecified.


**Returns**

A list of `WorkbookItem` 

A `PaginationItem` that points (`user_item.workbooks`). See [UserItem class](#useritem-class) 


**Example**

```py
# first get all users, call server.users.get()
# get workbooks for user[0]
    ...

  page_n = server.users.populate_workbooks(all_users[0])
  print("\nUser {0} owns or has READ permissions for {1} workbooks".format(all_users[0].name, page_n.total_available))
  print("\nThe workbooks are:")
  for workbook in all_users[0].workbooks :
      print(workbook.name)

    ...
```




<br>   
<br>

#### users.remove(*user_id*)

```py
users.remove(user_id)    
```



Removes the specified user from the site. 

REST API: [Remove User from Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Remove_User_from_Site%3FTocPath%3DAPI%2520Reference%7C_____74){:target="_blank"}


**Parameters**

`user_id`  :  The identifier (`id`) for the the user that you want to remove from the server. 


**Exceptions**

`User ID undefined`   :  Raises an exception if a valid `user_id` is not provided.


**Example**

```py
#  Remove a user from the site

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('http://SERVERURL')

   with server.auth.sign_in(tableau_auth):
     server.users.remove('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')

```
<br> 
<br>




#### users.update(*user_item*, *password=None*)  

```py
users.update(user_item, password=None)
```

Updates information about the specified user. 

The information you can modify depends upon whether you are using Tableau Server or Tableau Online, and whether you have configured Tableau Server to use local authentication or Active Directory. For more information, see [Update User](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Update_User%3FTocPath%3DAPI%2520Reference%7C_____86){:target="_blank"}.



REST API: [Update User](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Update_User%3FTocPath%3DAPI%2520Reference%7C_____86){:target="_blank"}

**Parameters**

`user_item`  :  The `user_item` specifies the user to update.

`password`  : (Optional) The new password for the user. 



**Exceptions**

`User item missing ID.` :  Raises an errror if the `user_item` is unspecified. 


**Returns**

An updated `UserItem`.    See [UserItem class](#useritem-class)


**Example**

```py

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('http://SERVERURL')

 with server.auth.sign_in(tableau_auth):
    
  # create a new user_item
    user1 = TSC.UserItem('temp', 'Viewer')
     
  # add new user
    user1 = server.users.add(user1)
    print(user1.name, user1.site_role, user1.id)

  # modify user info
    user1.name = 'Laura'
    user1.fullname = 'Laura Rodriguez'
    user1.email = 'laura@example.com'
 
  # update user
    user1 = server.users.update(user1)
    print("\Updated user info:")
    print(user1.name, user1.fullname, user1.email, user1.id)


```



<br>   
<br>  

## Groups

Using the TSC library, you can get information about all the groups on a site, you can add or remove groups, or add or remove users in a group.

The group resources for Tableau Server are defined in the `GroupItem` class. The class corresponds to the group resources you can access using the Tableau Server REST API. The group methods are based upon the endpoints for groups in the REST API and operate on the `GroupItem` class.

<br>   
<br> 

### GroupItem class

```py
GroupItem(name)
```

The `GroupItem` class contains the members or attributes for the view resources on Tableau Server. The `GroupItem` class defines the information you can request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload.

Source file: models/group_item.py

**Attributes**

`domain_name` :  The name of the Active Directory domain (`local` if local authentication is used).  
`id` :  The id of the group.  
`users`  :   The list of users (`UserItem`).  
`name` :  The name of the group.  The `name` is required when you create an instance of a group.



**Example**

```py
 newgroup = TSC.GroupItem('My Group')
```




<br>   
<br> 

### Groups methods

The Tableau Server Client provides several methods for interacting with group resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API.



Source file: server/endpoint/groups_endpoint.py

<br>   
<br> 

#### groups.add_user

```py
groups.add_user(group_item, user_id):
```

Adds a user to the specified group. 


REST API [Add User to Group](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Add_User_to_Group%3FTocPath%3DAPI%2520Reference%7C_____8){:target="_blank"}

**Parameters**

`group_item`  :  The `group_item` specifies the group to update.

`user_id`  : The id of the user. 




**Returns**

None.    


**Example**

```py
# Adding a user to a group
# Using the second group on the site, aleady have all_groups
# The id for Ian is '59a8a7b6-be3a-4d2d-1e9e-08a7b6b5b4ba'

# add Ian to the second group
  server.groups.add_user(all_groups[1], '59a8a7b6-be3a-4d2d-1e9e-08a7b6b5b4ba')

# populate the GroupItem with the users 
  pagination_item = server.groups.populate_users(all_groups[1])

  for user in all_groups[1].users :
      print(user.name)

```

<br>   
<br>

#### groups.create

```py
create(group_item)
```

Creates a new group in Tableau Server. 


REST API: [Create Group](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Create_Group%3FTocPath%3DAPI%2520Reference%7C_____14){:target="_blank"}


**Parameters**

`group_item`  :  The `group_item` specifies the group to add. You first create a new instance of a `GroupItem` and pass that to this method.




**Returns**
Adds new `GroupItem`.    


**Example**

```py

# Create a new group

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('http://SERVERURL')


# create a new instance with the group name
  newgroup = TSC.GroupItem('My Group')

# call the create method
  newgroup = server.groups.create(newgroup)

# print the names of the groups on the server
  all_groups, pagination_item = server.groups.get()
  for group in all_groups :
      print(group.name, group.id)
```

<br>   
<br> 

#### groups.delete

```py
groups.delete(group_id)
```

Deletes the group on the site. 

REST API: [Delete Group](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Remove_User_from_Site%3FTocPath%3DAPI%2520Reference%7C_____74){:target="_blank"}


**Parameters**

`group_id`  :  The identifier (`id`) for the the group that you want to remove from the server. 


**Exceptions**

`Group ID undefined`   :  Raises an exception if a valid `group_id` is not provided.


**Example**

```py
#  Delete a group from the site

# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('http://SERVERURL')

  with server.auth.sign_in(tableau_auth):
     server.groups.delete('1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d')

```
<br> 
<br>

#### groups.get

```py
groups.get(req_options=None)
```

Returns information about the groups on the site. 


To get information about the users in a group, you must first populate the `GroupItem` with user information using the [groups.populate_users](api-ref#groupspopulateusers) method. 


REST API: [Get Uers on Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Get_Users_on_Site%3FTocPath%3DAPI%2520Reference%7C_____41){:target="_blank"}

**Parameters**

`req_option` :  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific groups, you could specify the name of the group or the group id. 


**Returns**

Returns a list of `GroupItem` objects and a `PaginationItem`  object.  Use these values to iterate through the results. 


**Example**


```py
# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('http://SERVERURL')

  with server.auth.sign_in(tableau_auth):

       # get the groups on the server
       all_groups, pagination_item = server.groups.get()

       # print the names of the groups
       for group in all_groups :
           print(group.name, group.id)
````


<br>   
<br>  

#### groups.populate_users

```py
groups.populate_users(group_item, req_options=None)
```

Populates the `group_item` with the list of users. 


REST API:  [Get Users in Group](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Get_Users_in_Group){:target="_blank"}

**Parameters**

`group_item`  :  The `group_item` specifies the group to populate with user information.

`req_options` : (Optional) Additional request options to send to the endpoint. 



**Exceptions**

`Group item missing ID. Group must be retrieved from server first.` :  Raises an errror if the `group_item` is unspecified.


**Returns**

None. A list of `UserItem` objects are added to the group (`group_item.users`). 


**Example**

```py
# import tableauserverclient as TSC

# server = TSC.Server('http://SERVERURL')
# 
   ... 

# get the group
  mygroup = server.groups.get_by_id('1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d')


# get the user information 
  pagination_item = server.groups.populate_users(mygroup)


# print the information about the first connection item
  for user in mygroup.users :
        print(user.name) 
  



```

<br>   
<br> 

#### groups.remove_user

```py
groups.remove_user(group_item, user_id)
```

Removes a user from a group.




REST API: [Remove User from Group](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Remove_User_from_Group%3FTocPath%3DAPI%2520Reference%7C_____73){:target="_blank"}


**Parameters**

`group_item`  :  The `group_item` specifies the group to remove the user from.

`user_id` :  The id for the user. 



**Exceptions**

`Group must be populated with users first.` :  Raises an errror if the `group_item` is unpopulated.


**Returns**

None. The user is removed from the group. 


**Example**

```py
#  Remove a user from the group

# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('http://SERVERURL')

  with server.auth.sign_in(tableau_auth):

     # get the group
     mygroup = server.groups.get_by_id('1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d')

     # remove user '9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d'
     server.groups.remove_user(mygroup, '9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')

```

<br>   
<br>
