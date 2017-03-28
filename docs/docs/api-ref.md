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

<br>   
<br>

## Views

Using the TSC library, you can get all the views on a site, or get the views for a workbook, or populate a view with preview images. 
The view resources for Tableau Server are defined in the ViewItem class. The class corresponds to the view resources you can access using the Tableau Server REST API, for example, you can find the name of the view, its id, and the id of the workbook it is associated with. The view methods are based upon the endpoints for views in the REST API and operate on the `ViewItem` class. 


<br>

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


<br>   
<br>


### View methods

The Tableau Server Client provides two methods for interacting with view resources, or endpoints. These methods correspond to the endpoints for views in the Tableau Server REST API. 

Source file: server/endpoint/views_endpoint.py

<br>   
<br>

#### views.get()
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

#### views.populate_preview_image(*view_item*)

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

### Datasource methods

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

  all_datasources, pagination_item = server.datasources.get()
  datasource = server.datasources.get_by_id(all_datasources[1].id)
  print(datasource.name)

  server.datasources.populate_connections(datasource)
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


###  User Methods

The Tableau Server Client provides several methods for interacting with user resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API.

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
  newU = TSC.UserItem('Monty', 'Publisher')

# add the new user to the site
  newU = server.users.add(newU)
  print(newU.name, newU.site_role)

```

### users.get()

```py
users.get(req_options=None)
```

Returns information about the users on the specified site.

To get information about the workbooks a user owns or has view permission for, you must first populate the `UserItem` with workbook information using the [populate_workbooks(*user_item*)](#populate-workbooks-user) method. 


REST API: [Get Uers on Site](http://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm#REST/rest_api_ref.htm#Get_Users_on_Site%3FTocPath%3DAPI%2520Reference%7C_____41){:target="_blank"}

**Parameters**

``req_option` :  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific user, you could specify the name of the user or the user's id. 


**Returns**

Returns a list of UserItem` objects and a `PaginationItem`  object.  Use these values to iterate through the results. 


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
user1 = server.users.get_by_id('6de21c06-c936-47a1-8f92-ed2e9512e6ab')
print(user1.name)

```

<br>   
<br>  


#### users.populate_favorites_
  
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
  pagn = server.users.populate_workbooks(all_users[0])
  print("\nUser {0} owns or has READ permissions for {1} workbooks".format(all_users[0].name, pagn.total_available))
  print("\nThe workbooks are:")
  for workbook in all_users[0].workbooks :
       print(workbook.name)
```




<br>   
<br>

#### users.remove(*user_id*)

```py
users.remove(user_id):
        if not user_id:
            error = "User ID undefined."
```




<br>   
<br>


#### users.update  

```py
users.update(user_item, password=None)
```



Source file: server/endpoint/users_endpoint.py


<br>   
<br>  

## Groups

Source files: server/endpoint/groups_endpoint.py, models/group_item.py



<br>   
<br>  

