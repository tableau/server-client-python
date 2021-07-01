---
title: API reference
layout: docs
---

<div class="alert alert-info">
    <b>Important:</b> More coming soon! This section is under active construction and might not reflect all the available functionality of the TSC library.

</div>



The Tableau Server Client (TSC) is a Python library for the Tableau Server REST API. Using the TSC library, you can manage and change many of the Tableau Server and Tableau Online resources programmatically. You can use this library to create your own custom applications.

The TSC API reference is organized by resource. The TSC library is modeled after the REST API. The methods, for example, `workbooks.get()`, correspond to the endpoints for resources, such as [workbooks](#workbooks), [users](#users), [views](#views), and [data sources](#data-sources). The model classes (for example, the [WorkbookItem class](#workbookitem-class) have attributes that represent the fields (`name`, `id`, `owner_id`) that are in the REST API request and response packages, or payloads.

|:---  |
| **Note:**  Some methods and features provided in the REST API might not be currently available in the TSC library (and in some cases, the opposite is true).  In addition, the same limitations apply to the TSC library that apply to the REST API with respect to resources on Tableau Server and Tableau Online. For more information, see the [Tableau Server REST API Reference](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm).|



* TOC
{:toc }

<br>
<br>

---

## Authentication

You can use the TSC library to sign in and sign out of Tableau Server and Tableau Online. The credentials for signing in are defined in the `TableauAuth` class and they correspond to the attributes you specify when you sign in using the Tableau Server REST API.

<br>
<br>

### TableauAuth class

```py
TableauAuth(username, password, site_id='', user_id_to_impersonate=None)
```
The `TableauAuth` class defines the information you can set in a sign-in request. The class members correspond to the attributes of a server request or response payload. To use this class, create a new instance, supplying user name, password, and site information if necessary, and pass the request object to the [Auth.sign_in](#auth.sign-in) method.


 **Note:** In the future, there might be support for additional forms of authorization and authentication (for example, OAuth).

**Attributes**

Name | Description
:--- | :---
`username` | The name of the user whose credentials will be used to sign in.
`password` | The password of the user.
`site_id` | This corresponds to the `contentUrl` attribute in the Tableau REST API. The `site_id` is the portion of the URL that follows the `/site/` in the URL. For example, "MarketingTeam" is the `site_id` in the following URL *MyServer*/#/site/**MarketingTeam**/projects. To specify the default site on Tableau Server, you can use an empty string `''`  (single quotes, no space).  For Tableau Online, you must provide a value for the `site_id`.
`user_id_to_impersonate` |  Specifies the id (not the name) of the user to sign in as.

Source file: models/tableau_auth.py

**Example**

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', site_id='CONTENTURL')
server = TSC.Server('https://SERVER_URL', use_server_version=True)
server.auth.sign_in(tableau_auth)
```

<br>
<br>

### PersonalAccessTokenAuth class

```py
PersonalAccessTokenAuth(token_name, personal_access_token, site_id='')
```
The `PersonalAccessTokenAuth` class serves the same purpose and is used in the same way as `TableauAuth`, but using Personal Access Tokens](https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm) instead of username and password.

**Attributes**

Name | Description
:--- | :---
`token_name` | The personal access token name.
`personal_access_token` | The personal access token value.
`site_id` | This corresponds to the `contentUrl` attribute in the Tableau REST API. The `site_id` is the portion of the URL that follows the `/site/` in the URL. For example, "MarketingTeam" is the `site_id` in the following URL *MyServer*/#/site/**MarketingTeam**/projects. To specify the default site on Tableau Server, you can use an empty string `''` (single quotes, no space). For Tableau Online, you must provide a value for the `site_id`.

Source file: models/personal_access_token_auth.py

**Example**

```py
import tableauserverclient as TSC

tableau_auth = TSC.PersonalAccessTokenAuth('TOKEN-NAME', 'TOKEN-VALUE', site_id='CONTENTURL')
server = TSC.Server('https://SERVER_URL', use_server_version=True)
server.auth.sign_in(tableau_auth)
```

<br>
<br>
### Auth methods
The Tableau Server Client provides two methods for interacting with authentication resources. These methods correspond to the sign in and sign out endpoints in the Tableau Server REST API.

Source file: server/endpoint/auth_endpoint.py

**See Also**
[Sign in and Out](sign-in-out)
[Server](#server)

<br>
<br>

#### auth.sign_in

```py
auth.sign_in(auth_req)
```

Signs you in to Tableau Server.


The method signs into Tableau Server or Tableau Online and manages the authentication token. You call this method from the server object you create. For information about the server object, see [Server](#server). The authentication token keeps you signed in for 240 minutes, or until you call the `auth.sign_out` method. Before you use this method, you first need to create the sign-in request (`auth_req`) object by creating an instance of the `TableauAuth`. To call this method, create a server object for your server. For more information, see [Sign in and Out](sign-in-out).

REST API: [Sign In](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#sign_in)

**Parameters**

`auth_req` : The `TableauAuth` object that holds the sign-in credentials for the site.


**Example**

```py
import tableauserverclient as TSC

# create an auth object
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')

# create an instance for your server
server = TSC.Server('https://SERVER_URL')

# call the sign-in method with the auth object
server.auth.sign_in(tableau_auth)
```

<br>
<br>


#### auth.sign_out

```py
auth.sign_out()
```
Signs you out of the current session.

The `sign_out()` method takes care of invalidating the authentication token. For more information, see [Sign in and Out](sign-in-out).

REST API: [Sign Out](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#sign_out)

**Example**

```py
server.auth.sign_out()
```

<br>
<br>

#### auth.switch_site

```py
auth.switch_site(site_id)
```

Switch to a different site on the current Tableau Server.

Switching avoids the need for reauthenticating to the same server. (Note: This method is not available in Tableau Online.)

REST API: [Switch Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_authentication.htm#switch_site)

**Parameters**

`site_item` | The site that you want to switch to. This should be a `SiteItem` retrieved from `sites.get()`, `sites.get_by_id()` or `sites.get_by_name{}`.


**Example**

```py
# find and then switch auth to another site on the same server
site = server.sites.get_by_id('9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d')
server.auth.switch_site(site)
```

<br>
<br>


**See Also**  
[Sign in and Out](sign-in-out)  
[Server](#server)

<br>
<br>

---


## Connections

The connections for Tableau Server data sources and workbooks are represented by a `ConnectionItem` class.  You can call data source and workbook methods to query or update the connection information.  The `ConnectionCredentials` class represents the connection information you can update.

### ConnectionItem class

```py
ConnectionItem()
```

The `ConnectionItem` class corresponds to workbook and data source connections.

In the Tableau Server REST API, there are separate endpoints to query and update workbook and data source connections.

**Attributes**

Name   |  Description
 :--- | : ---
`datasource_id` |  The identifier of the data source.
`datasource_name` |  The name of the data source.
`id`  |  The identifier of the connection.
`connection_type`  |  The type of connection.
`username`     | The username for the connection.
`password`  |  The password used for the connection.
`embed_password`  |  (Boolean) Determines whether to embed the password (`True`) for the workbook or data source connection or not (`False`).
`server_address`   |  The server address for the connection.
`server_port`   |  The port used for the connection.

Source file: models/connection_item.py

<br>
<br>



### ConnectionCredentials class

```py
ConnectionCredentials(name, password, embed=True, oauth=False)
```


The `ConnectionCredentials` class is used for workbook and data source publish requests.



**Attributes**

Attribute | Description
:--- | :---
`name`     | The username for the connection.
`embed_password`  |  (Boolean) Determines whether to embed the password (`True`) for the workbook or data source connection or not (`False`).
`password`  |  The password used for the connection.
`server_address`   |  The server address for the connection.
`server_port`   |  The port used by the server.
`ouath`  |  (Boolean) Specifies whether OAuth is used for the data source of workbook connection. For more information, see [OAuth Connections](https://help.tableau.com/current/server/en-us/protected_auth.htm).


Source file: models/connection_credentials.py

<br>
<br>

---

## Data sources

Using the TSC library, you can get all the data sources on a site, or get the data sources for a specific project.
The data source resources for Tableau Server are defined in the `DatasourceItem` class. The class corresponds to the data source resources you can access using the Tableau Server REST API. For example, you can gather information about the name of the data source, its type, its connections, and the project it is associated with. The data source methods are based upon the endpoints for data sources in the REST API and operate on the `DatasourceItem` class.

<br>

### DatasourceItem class

```py
DatasourceItem(project_id, name=None)
```

The `DatasourceItem` represents the data source resources on Tableau Server. This is the information that can be sent or returned in the response to an REST API request for data sources.  When you create a new `DatasourceItem` instance, you must specify the `project_id` that the data source is associated with.

**Attributes**

Name | Description
:--- | :---
`ask_data_enablement` | Determines if a data source allows use of Ask Data. The value can be `TSC.DatasourceItem.AskDataEnablement.Enabled`, `TSC.DatasourceItem.AskDataEnablement.Disabled`, or `TSC.DatasourceItem.AskDataEnablement.SiteDefault`. If no setting is specified, it will default to SiteDefault. See [REST API Publish Datasource](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_datasources.htm#publish_data_source) for more information about ask_data_enablement.
`connections` |  The list of data connections (`ConnectionItem`) for the specified data source. You must first call the `populate_connections` method to access this data. See the [ConnectionItem class](#connectionitem-class).
`content_url` |  The name of the data source as it would appear in a URL.
`created_at` |  The date and time when the data source was created.
`certified` | A Boolean value that indicates whether the data source is certified.
`certification_note` |  The optional note that describes the certified data source.
`datasource_type` | The type of data source, for example, `sqlserver` or `excel-direct`.
`description` | The description for the data source.
`encrypt_extracts` | A Boolean value to determine if a datasource should be encrypted or not. See [Extract and Encryption Methods](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_extract_encryption.htm) for more information.
`has_extracts` | A Boolean value that indicates whether the datasource has extracts.
`id` |  The identifier for the data source. You need this value to query a specific data source or to delete a data source with the `get_by_id` and `delete` methods.
`name`  |  The name of the data source. If not specified, the name of the published data source file is used.
`owner_id` |  The identifier of the owner of the data source.
`project_id` |  The identifier of the project associated with the data source. You must provide this identifier when you create an instance of a `DatasourceItem`.
`project_name` |  The name of the project associated with the data source.
`tags` |  The tags (list of strings) that have been added to the data source.
`updated_at` |  The date and time when the data source was last updated.
`use_remote_query_agent` | A Boolean value that indicates whether to allow or disallow your Tableau Online site to use Tableau Bridge clients. Bridge allows you to maintain data sources with live connections to supported on-premises data sources. See [Configure and Manage the Bridge Client Pool](https://help.tableau.com/current/online/en-us/to_enable_bridge_live_connections.htm) for more information.
`webpage_url` | The url of the datasource as displayed in browsers.


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

#### datasources.delete

```py
datasources.delete(datasource_id)
```

Removes the specified data source from Tableau Server.


**Parameters**

Name | Description
:--- | :---
`datasource_id`  |  The identifier (`id`) for the `DatasourceItem` that you want to delete from the server.


**Exceptions**

Error   |  Description
 :--- | : ---
`Datasource ID undefined`   | Raises an exception if a valid `datasource_id` is not provided.


REST API: [Delete Datasource](https://help.tableau.com/v0.0/api/rest_api/en-us/REST/rest_api_ref.htm#delete_data_source)

<br>
<br>


#### datasources.download

```py
datasources.download(datasource_id, filepath=None, include_extract=True, no_extract=None)

```
Downloads the specified data source in `.tdsx` or `.hyper` format.

REST API: [Download Datasource](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#download_data_source)

**Parameters**

Name | Description
:--- | :---
`datasource_id` |  The identifier (`id`) for the `DatasourceItem` that you want to download from the server.
`filepath` |  (Optional) Downloads the file to the location you specify. If no location is specified (the default is `Filepath=None`), the file is downloaded to the current working directory.
`include_extract` | (Optional) Specifies whether to download the file with the extract. The default is to include the extract, if present (`include_extract=True`). When the data source has an extract, if you set the parameter `include_extract=False`, the extract is not included. You can use this parameter to improve performance if you are downloading data sources that have large extracts. Available starting with Tableau Server REST API version 2.5.
`no_extract` | (**Deprecated**) Use `include_extract` instead. The default value is to ignore this parameter (`no_extract=None`). If you set the parameter to `no_extract=True`, the download will not include an extract (if there is one). If set to `no_extract=False`, the download will include the extract (if there is one). Available starting with Tableau Server REST API version 2.5.

**Exceptions**

Error | Description
:--- | :---
`Datasource ID undefined`   |  Raises an exception if a valid `datasource_id` is not provided.


**Returns**

The file path to the downloaded data source. The data source is downloaded in `.tdsx` or `.hyper` format.

**Example**

```py

  file_path = server.datasources.download('1a2a3b4b-5c6c-7d8d-9e0e-1f2f3a4a5b6b')
  print("\nDownloaded the file to {0}.".format(file_path))

```


<br>
<br>

#### datasources.get

```py
datasources.get(req_options=None)
```

Returns all the data sources for the site.

To get the connection information for each data source, you must first populate the `DatasourceItem` with connection information using the [populate_connections(*datasource_item*)](#populate-connections-datasource) method. For more information, see [Populate Connections and Views](populate-connections-views#populate-connections-for-data-sources)

REST API: [Query Datasources](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_data_sources)

**Parameters**

Name | Description
:--- | :---
`req_options` |  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific data source, you could specify the name of the project or its id.


**Returns**

Returns a list of `DatasourceItem` objects and a `PaginationItem`  object.  Use these values to iterate through the results.




**Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('https://SERVERURL')

with server.auth.sign_in(tableau_auth):
    all_datasources, pagination_item = server.datasources.get()
    print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
    print([datasource.name for datasource in all_datasources])
```



<br>
<br>


#### datasources.get_by_id

```py
datasources.get_by_id(datasource_id)
```

Returns the specified data source item.

REST API: [Query Datasource](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_data_source)


**Parameters**

Name | Description
:--- | :---
`datasource_id`  |  The `datasource_id` specifies the data source to query.


**Exceptions**

Error | Description
:--- | :---
`Datasource ID undefined`   |  Raises an exception if a valid `datasource_id` is not provided.


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

#### datasources.populate_connections

```py
datasources.populate_connections(datasource_item)
```

Populates the connections for the specified data source.

This method retrieves the connection information for the specified data source. The REST API is designed to return only the information you ask for explicitly. When you query for all the data sources, the connection information is not included. Use this method to retrieve the connections. The method adds the list of data connections to the data source item (`datasource_item.connections`). This is a list of `ConnectionItem` objects.

REST API:  [Query Datasource Connections](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_data_source_connections)

**Parameters**

Name | Description
:--- | :---
`datasource_item`  |  The `datasource_item` specifies the data source to populate with connection information.




**Exceptions**

Error | Description
:--- | :---
`Datasource item missing ID. Datasource must be retrieved from server first.` |  Raises an error if the datasource_item is unspecified.


**Returns**

None. A list of `ConnectionItem` objects are added to the data source (`datasource_item.connections`).


**Example**

```py
# import tableauserverclient as TSC

# server = TSC.Server('https://SERVERURL')
#
   ...

# get the data source
  datasource = server.datasources.get_by_id('1a2a3b4b-5c6c-7d8d-9e0e-1f2f3a4a5b6b')


# get the connection information
  server.datasources.populate_connections(datasource)

# print the information about the first connection item
  connection = datasource.connections[0]
  print(connection.connection_type)
  print(connection.id)
  print(connection.server_address)

  ...

```

<br>
<br>

#### datasources.publish

```py
datasources.publish(datasource_item, file_path, mode, connection_credentials=None)
```

Publishes a data source to a server, or appends data to an existing data source.

This method checks the size of the data source and automatically determines whether the publish the data source in multiple parts or in one operation.

REST API: [Publish Datasource](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#publish_data_source)

**Parameters**

Name | Description
:--- | :---
`datasource_item`  |  The `datasource_item` specifies the new data source you are adding, or the data source you are appending to. If you are adding a new data source, you need to create a new `datasource_item` with a `project_id` of an existing project. The name of the data source will be the name of the file, unless you also specify a name for the new data source when you create the instance. See [DatasourceItem](#datasourceitem-class).
`file_path`  |  The path and name of the data source to publish.
`mode`     |  Specifies whether you are publishing a new data source (`CreateNew`), overwriting an existing data source (`Overwrite`), or appending data to a data source (`Append`). If you are appending to a data source, the data source on the server and the data source you are publishing must be be extracts (.tde files) and they must share the same schema. You can also use the publish mode attributes, for example: `TSC.Server.PublishMode.Overwrite`.
`connection_credentials` | (Optional)  The credentials required to connect to the data source. The `ConnectionCredentials` object contains the authentication information for the data source (user name and password, and whether the credentials are embedded or OAuth is used).



**Exceptions**

Error | Description
:--- | :---
`File path does not lead to an existing file.`  |  Raises an error of the file path is incorrect or if the file is missing.
`Invalid mode defined.`  |  Raises an error if the publish mode is not one of the defined options.
`Only .tds, tdsx, .tde, or .hyper files can be published as datasources.`  |  Raises an error if the type of file specified is not supported.


**Returns**

The `DatasourceItem` for the data source that was added or appended to.


**Example**

```py

  import tableauserverclient as TSC
  server = TSC.Server('https://SERVERURL')

  ...

  project_id = '3a8b6148-493c-11e6-a621-6f3499394a39'
  file_path = r'C:\temp\WorldIndicators.tde'


  # Use the project id to create new datsource_item
  new_datasource = TSC.DatasourceItem(project_id)

  # publish data source (specified in file_path)
  new_datasource = server.datasources.publish(
                    new_datasource, file_path, 'CreateNew')

    ...
```

<br>
<br>

#### datasources.refresh

```py
datasource.refresh(datasource_item)
```

Refreshes the data of the specified extract.

REST API: [Update Data Source Now](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_datasources.htm#update_data_source_now)

**Parameters**

Name   |  Description
 :--- | : ---
`datasource_item`  |  The `datasource_item` specifies the data source to update.


**Exceptions**

Error   |  Description
 :--- | : ---
`Datasource item missing ID. Datasource must be retrieved from server first.` |  Raises an error if the datasource_item is unspecified. Use the `Datasources.get()` method to retrieve that identifies for the data sources on the server.


**Returns**

A refreshed `DatasourceItem`.


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://SERVERURL')
# sign in ...

# get the data source item to update
  datasource = server.datasources.get_by_id('1a2a3b4b-5c6c-7d8d-9e0e-1f2f3a4a5b6b')

# call the refresh method with the data source item
  refreshed_datasource = server.datasources.refresh(datasource)

```
<br>
<br>

#### datasources.update

```py
datasource.update(datasource_item)
```

Updates the specified data source. 

REST API: [Update Data Source](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_data_source)

**Parameters**

Name   |  Description
 :--- | : ---
`datasource_item`  |  The `datasource_item` specifies the data source to update.



**Exceptions**

Error   |  Description
 :--- | : ---
`Datasource item missing ID. Datasource must be retrieved from server first.` |  Raises an error if the datasource_item is unspecified. Use the `Datasources.get()` method to retrieve that identifies for the data sources on the server.


**Returns**

An updated `DatasourceItem`.


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://SERVERURL')
# sign in ...

# get the data source item to update
  datasource = server.datasources.get_by_id('1a2a3b4b-5c6c-7d8d-9e0e-1f2f3a4a5b6b')

# do some updating
  datasource.owner_id = 'New Owner ID'

# call the update method with the data source item
  updated_datasource = server.datasources.update(datasource)



```
<br>
<br>

#### datasource.update_connection

```py
datasource.update_connection(datasource_item, connection_item)
```

Updates the server address, port, username, or password for the specified data source connection.

REST API: [Update Datasource Connection](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_data_source_connection)


**Parameters**

Name   |  Description
 :--- | : ---
`datasource_item`  |  The `datasource_item` specifies the data source to update.
`connection_item` | The `connection_item` that has the information you want to update.


**Returns**

An updated `ConnectionItem` for the data source.

**Example**

See the `update_connection.py` sample in the Samples directory.


<br>
<br>

## Filters

The TSC library provides a `Filter` class that you can use to filter results returned from the server.

You can use the `Filter` and `RequestOptions` classes to filter and sort the following endpoints:

- Users
- Datasources
- Workbooks
- Views

For more information, see [Filter and Sort](filter-sort).


### Filter class

```py
Filter(field, operator, value)
```

The `Filter` class corresponds to the *filter expressions* in the Tableau REST API.



**Attributes**

Name | Description
:--- | :---
`Field` | Defined in the `RequestOptions.Field` class.
`Operator` | Defined in the `RequestOptions.Operator` class
`Value` | The value to compare with the specified field and operator.





<br>
<br>

---

## Groups

Using the TSC library, you can get information about all the groups on a site, you can add or remove groups, or add or remove users in a group.

The group resources for Tableau Server are defined in the `GroupItem` class. The class corresponds to the group resources you can access using the Tableau Server REST API. The group methods are based upon the endpoints for groups in the REST API and operate on the `GroupItem` class.

<br>
<br>

### GroupItem class

```py
GroupItem(name)
```

The `GroupItem` class contains the attributes for the group resources on Tableau Server. The `GroupItem` class defines the information you can request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload.

Source file: models/group_item.py

**Attributes**

Name | Description
:--- | :---
`domain_name` |  The name of the Active Directory domain (`local` if local authentication is used).
`id` |  The id of the group.
`users`  |   The list of users (`UserItem`).
`name` |  The name of the group.  The `name` is required when you create an instance of a group.
`minimum_site_role` | The role to grant users that are added to the group.
`license_mode` | The mode defining when to apply licenses for group members. When the mode is `onLogin`, a license is granted for each group member when they login to a site. When the mode is `onSync`, a license is granted for group members each time the domain is synced.


**Example**

```py
 newgroup = TSC.GroupItem('My Group')

 # call groups.create() with new group
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


REST API [Add User to Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#add_user_to_group)

**Parameters**

Name | Description
:--- | :---
`group_item`  | The `group_item` specifies the group to update.
`user_id` | The id of the user.




**Returns**

None.


**Example**

```py
# Adding a user to a group
#
# get the group item
  all_groups, pagination_item = server.groups.get()
  mygroup = all_groups[1]

# The id for Ian is '59a8a7b6-be3a-4d2d-1e9e-08a7b6b5b4ba'

# add Ian to the group
  server.groups.add_user(mygroup, '59a8a7b6-be3a-4d2d-1e9e-08a7b6b5b4ba')



```

<br>
<br>

#### groups.create

```py
create(group_item)
```

Creates a new local group in Tableau Server.


REST API: [Create Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_group)


**Parameters**

Name | Description
:--- | :---
`group_item`  |  The `group_item` specifies the group to add. You first create a new instance of a `GroupItem` and pass that to this method.




**Returns**
Adds new `GroupItem`.


**Example**

```py

# Create a new group

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('https://SERVERURL')


# create a new instance with the group name
  newgroup = TSC.GroupItem('My Group')
  newgroup.minimum_site_role = TSC.UserItem.Roles.ExplorerCanPublish

# call the create method
  newgroup = server.groups.create(newgroup)

# print the names of the groups on the server
  all_groups, pagination_item = server.groups.get()
  for group in all_groups :
      print(group.name, group.id)
```

<br>
<br>

#### groups.create_AD_group

```py
create_AD_group(group_item, asJob=False)
```

Creates an active directory group in Tableau Server.


REST API: [Create Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_group)


**Parameters**

Name | Description
:--- | :---
`group_item`  |  The `group_item` specifies the group to add. You first create a new instance of a `GroupItem` and pass that to this method.
`asJob` | Boolean flag used to specify an asynchronous operation. If set to `True`, the return value will be a JobItem containing the status of the queued job. See [JobItem class](#jobitem-class).




**Returns**
Returns the created `GroupItem` or a `JobItem` if asJob flag was set to True.


**Example**

```py

# Create a new group

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('https://SERVERURL')


# create a new instance with the group name
  newgroup = TSC.GroupItem('AD_Group_Name', 'AD_Domain_Name')
  newgroup.minimum_site_role = TSC.UserItem.Roles.SiteAdministratorExplorer
  newgroup.license_mode = TSC.GroupItem.LicenseMode.onSync

# call the create method
  newgroup = server.groups.create_AD_group(newgroup)
  
# call the create method asynchronously
  newgroup_job = server.groups.create_AD_group(newgroup, asJob=True)

```

<br>
<br>

#### groups.delete

```py
groups.delete(group_id)
```

Deletes the group on the site.

REST API: [Delete Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#remove_user_from_site)


**Parameters**

Name | Description
:--- | :---
`group_id`  |  The identifier (`id`) for the group that you want to remove from the server.


**Exceptions**

Error | Description
:--- | :---
`Group ID undefined`  |  Raises an exception if a valid `group_id` is not provided.


**Example**

```py
#  Delete a group from the site

# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('https://SERVERURL')

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


To get information about the users in a group, you must first populate the `GroupItem` with user information using the [groups.populate_users](api-ref#groupspopulate_users) method.


REST API: [Get Users on Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#get_users_on_site)

**Parameters**

Name | Description
:--- | :---
`req_options` |  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific group, you could specify the name of the group or the group id.


**Returns**

Returns a list of `GroupItem` objects and a `PaginationItem`  object.  Use these values to iterate through the results.


**Example**


```py
# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('https://SERVERURL')

  with server.auth.sign_in(tableau_auth):

       # get the groups on the server
       all_groups, pagination_item = server.groups.get()

       # print the names of the first 100 groups
       for group in all_groups :
           print(group.name, group.id)
```


<br>
<br>

#### groups.populate_users

```py
groups.populate_users(group_item, req_options=None)
```

Populates the `group_item` with the list of users.


REST API:  [Get Users in Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#get_users_in_group)

**Parameters**

Name | Description
:--- | :---
`group_item`  |  The `group_item` specifies the group to populate with user information.
`req_options` | (Optional) Additional request options to send to the endpoint.



**Exceptions**

`Group item missing ID. Group must be retrieved from server first.` :  Raises an error if the `group_item` is unspecified.


**Returns**

None. A list of `UserItem` objects are added to the group (`group_item.users`).


**Example**

```py
# import tableauserverclient as TSC

# server = TSC.Server('https://SERVERURL')
#
   ...

# get the group
  all_groups, pagination_item = server.groups.get()
  mygroup = all_groups[1]

# get the user information
  pagination_item = server.groups.populate_users(mygroup)


# print the names of the users
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




REST API: [Remove User from Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#remove_user_to_group)


**Parameters**

Name | Description
:--- | :---
`group_item`  |  The `group_item` specifies the group to remove the user from.
`user_id` |  The id for the user.



**Exceptions**

Error | Description
:--- | :---
`Group must be populated with users first.` |  Raises an error if the `group_item` is unpopulated.


**Returns**

None. The user is removed from the group.


**Example**

```py
#  Remove a user from a group

# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('https://SERVERURL')

  with server.auth.sign_in(tableau_auth):

     # get a group
     all_groups, pagination_item = server.groups.get()
     mygroup = all_groups[0]

     # remove user '9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d'
     server.groups.remove_user(mygroup, '9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')

```

<br>
<br>


#### groups.update

```py
groups.update(group_item, as_job=False)
```

Updates a group in Tableau Server.

REST API: [Update Group](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_usersgroups.htm#update_group)


**Parameters**

Name | Description
:--- | :---
`group_item`  |  The `group_item` specifies the group to update.
`as_job` |  (Optional) If this value is set to `True`, the update operation will be asynchronous and return a JobItem. This is only supported for Active Directory groups. By default, this value is set to `False`. 


**Exceptions**

Error | Description
:--- | :---
`Group item missing ID.` |  Raises an error if the `group_item` is missing the `id` attribute.
`Local groups cannot be updated asynchronously.` | The `as_job` attribute was set to `True` for a local group.


**Returns**

The updated `GroupItem` object. If `as_job` was set to `True`, a `JobItem` will be returned instead.


**Example**

```py
# Fetch an existing group from server.
groups, pagination = server.groups.get()
group = groups[0]

# Set update-able fields. Any of these can be added or removed.
## Local group
group.name = "new group name"
group.minimum_site_role = TSC.UserItem.Roles.SiteAdministratorExplorer

## Active Directory group
group.minimum_site_role = TSC.UserItem.Roles.SiteAdministratorExplorer
group.license_mode = TSC.GroupItem.LicenseMode.onLogin

# Update group - synchronous
group = server.groups.update(group)

# Update group - asynchronous (only for Active Directory groups)
job = server.groups.update(group, as_job=True)
```

<br>
<br>

---

## Jobs

Using the TSC library, you can get information about an asynchronous process (or *job*) on the server. These jobs can be created when Tableau runs certain tasks that could be long running, such as importing or synchronizing users from Active Directory, or running an extract refresh. For example, the REST API methods to create or update groups, to run an extract refresh task, or to publish workbooks can take an `asJob` parameter (`asJob-true`) that creates a background process (the *job*) to complete the call. Information about the asynchronous job is returned from the method.

If you have the identifier of the job, you can use the TSC library to find out the status of the asynchronous job.

The job properties are defined in the `JobItem` class. The class corresponds to the properties for jobs you can access using the Tableau Server REST API. The job methods are based upon the endpoints for jobs in the REST API and operate on the `JobItem` class.


### JobItem class

```py
JobItem(id, type, created_at, started_at=None, completed_at=None, finish_code=0)

```

The `JobItem` class contains information about the specified job running on Tableau Server. The `JobItem` class defines the information you can query from Tableau Server. The class members correspond to the attributes of a server response payload.

Source file: models/job_item.py

**Attributes**

Name  |  Description
:--- | :---
`id`  |  The `id` of the job.
`type` | The type of task. The types correspond to the job type categories listed for the [Query Job](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_job) REST API.
`created_at` | The time the job was created.
`started_at` | The time the job started.
`completed_at` | The time the job finished.
`finish_code` | The return code from job.


### Jobs methods


The Jobs methods are based upon the endpoints for jobs in the REST API and operate on the `JobItem` class.


Source files: server/endpoint/jobs_endpoint.py

<br>
<br>


#### jobs.get


```py
jobs.get(job_id)

```

Gets information about the specified job.

REST API: [Query Job](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_job)


**Parameters**

Name | Description
:--- | :---
`job_id`  |  The `job_id` specifies the id of the job that is returned from an asynchronous task, such as extract refresh, or an import or update to groups using Active Directory




**Exceptions**

Error | Description
:--- | :---
`404018 Resource Not Found` |  Raises an error if the `job_id` is not found.


**Returns**

Returns the `JobItem` requested.


**Example**

```py
#  Query a Job

# import tableauserverclient as TSC
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
# server = TSC.Server('https://SERVERURL')

  with server.auth.sign_in(tableau_auth):

     # get the id of the job from response to extract refresh task,
     # or another asynchronous REST API call.
     # in this case, "576b616d-341a-4539-b32c-1ed0eb9db548"


    myJobId = '576b616d-341a-4539-b32c-1ed0eb9db548'
    jobinfo = server.jobs.get(myJobID)

    print(jobinfo)

    # <Job#576b616d-341a-4539-b32c-1ed0eb9db548 RefreshExtract created_at(2018-04-10T23:43:21Z) started_at(2018-04-10T23:43:25Z) completed_at(2018-04-10T23:43:26Z) finish_code(1)>




```


<br>
<br>

---

## Projects

Using the TSC library, you can get information about all the projects on a site, or you can create, update projects, or remove projects.

The project resources for Tableau are defined in the `ProjectItem` class. The class corresponds to the project resources you can access using the Tableau Server REST API. The project methods are based upon the endpoints for projects in the REST API and operate on the `ProjectItem` class.





<br>

### ProjectItem class

```py

ProjectItem(name, description=None, content_permissions=None,  parent_id=None)

```
The project resources for Tableau are defined in the `ProjectItem` class. The class corresponds to the project resources you can access using the Tableau Server REST API.

**Attributes**

Name  |  Description
:--- | :---
`content_permissions`  |  Sets or shows the permissions for the content in the project. The options are either `LockedToProject` or `ManagedByOwner`.
`name` | Name of the project.
`description` | The description of the project.
`id`  | The project id.
`parent_id` | The id of the parent project. Use this option to create project hierarchies. For information about managing projects, project hierarchies, and permissions, see [Use Projects to Manage Content Access](https://help.tableau.com/current/server/en-us/projects.htm).



Source file: models/project_item.py


#### ProjectItem.ContentPermissions

The `ProjectItem` class has a sub-class that defines the permissions for the project (`ProjectItem.ContentPermissions`).  The options are `LockedToProject` and `ManagedByOwner`.  For information on these content permissions, see [Lock Content Permissions to the Project](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_project).

Name | Description
:--- | :---
`ProjectItem.ContentPermissions.LockedToProject`    |     Locks all content permissions to the project.
`ProjectItem.ContentPermissions.ManagedByOwner`  |  Users can manage permissions for content that they own. This is the default.

**Example**

```py

# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc


locked_true = TSC.ProjectItem.ContentPermissions.LockedToProject
print(locked_true)
# prints 'LockedToProject'

by_owner = TSC.ProjectItem.ContentPermissions.ManagedByOwner
print(by_owner)
# prints 'ManagedByOwner'


# pass the content_permissions to new instance of the project item.
new_project = TSC.ProjectItem(name='My Project', content_permissions=by_owner, description='Project example')

```

<br>
<br>

###  Project methods

The project methods are based upon the endpoints for projects in the REST API and operate on the `ProjectItem` class.


Source files: server/endpoint/projects_endpoint.py

<br>
<br>


#### projects.create

```py
projects.create(project_item)
```


Creates a project on the specified site.

To create a project, you first create a new instance of a `ProjectItem` and pass it to the create method. To specify the site to create the new project, create a `TableauAuth` instance using the content URL for the site (`site_id`), and sign in to that site.  See the [TableauAuth class](#tableauauth-class).


REST API: [Create Project](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_project)

**Parameters**

Name | Description
:--- | :---
`project_item` | Specifies the properties for the project. The `project_item` is the request package. To create the request package, create a new instance of `ProjectItem`.


**Returns**
Returns the new project item.



**Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', site_id='CONTENTURL')
server = TSC.Server('https://SERVER')

with server.auth.sign_in(tableau_auth):
    # create project item
    new_project = TSC.ProjectItem(name='Example Project', content_permissions='LockedToProject', description='Project created for testing')
    # create the project
    new_project = server.projects.create(new_project)

```

<br>
<br>


#### projects.get

```py
projects.get()

```

Return a list of project items for a site.


To specify the site, create a `TableauAuth` instance using the content URL for the site (`site_id`), and sign in to that site.  See the [TableauAuth class](#tableauauth-class).

REST API: [Query Projects](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_projects)


**Parameters**

None.

**Returns**

Returns a list of all `ProjectItem` objects and a `PaginationItem`. Use these values to iterate through the results.



 **Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', site_id='CONTENTURL')
server = TSC.Server('https://SERVER')

with server.auth.sign_in(tableau_auth):
        # get all projects on site
        all_project_items, pagination_item = server.projects.get()
        print([proj.name for proj in all_project_items])

```

<br>
<br>


#### projects.update

```py
projects.update(project_item)
```

Modify the project settings.

You can use this method to update the project name, the project description, or the project permissions. To specify the site, create a `TableauAuth` instance using the content URL for the site (`site_id`), and sign in to that site.  See the [TableauAuth class](#tableauauth-class).

REST API: [Update Project](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_project)

**Parameters**

Name  |  Description
:--- | :---
`project_item` |  The project item object must include the project ID. The values in the project item override the current project settings.


**Exceptions**

Error   |  Description
 :--- | : ---
`Project item missing ID.`  | Raises an exception if the project item does not have an ID. The project ID is sent to the server as part of the URI.


**Returns**

Returns the updated project information.

See [ProjectItem class](#projectitem-class)

**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc

  ...
  # get list of projects
  all_project_items, pagination_item = server.projects.get()


  # update project item #7 with new name, etc.
  my_project = all_projects[7]
  my_project.name ='New name'
  my_project.description = 'New description'

  # call method to update project
  updated_project = server.projects.update(my_project)




```
<br>
<br>


#### projects.delete

```py
projects.delete(project_id)
```

Deletes a project by ID.


To specify the site, create a `TableauAuth` instance using the content URL for the site (`site_id`), and sign in to that site.  See the [TableauAuth class](#tableauauth-class).


REST API: [Delete Project](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#delete_project)


**Parameters**

Name  |  Description
:--- | :---
`project_id`   | The ID of the project to delete.




**Exceptions**

Error  |  Description
:--- | :---
`Project ID undefined.`  |  Raises an exception if the project item does not have an ID. The project ID is sent to the server as part of the URI.


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc.

 server.projects.delete('1f2f3e4e-5d6d-7c8c-9b0b-1a2a3f4f5e6e')

```


<br>
<br>

---

## Requests

The TSC library provides a `RequestOptions` class that you can use to filter results returned from the server.

You can use the `Sort` and `RequestOptions` classes to filter and sort the following endpoints:

- Users
- Datasources
- Groups
- Workbooks
- Views


You can use the `ImageRequestOptions` and `PDFRequestOptions` to set options for views returned as images and PDF files.

For more information about filtering and sorting, see [Filter and Sort](filter-sort).


<br>



### RequestOptions class

```py
RequestOptions(pagenumber=1, pagesize=100)

```



**Attributes**

Name  |  Description
:--- | :---
`pagenumber` | The page number of the returned results. The default value is 1.
`pagesize` |  The number of items to return with each page (the default value is 100).
`sort()`      | Returns a iterable set of `Sort` objects.
`filter()` | Returns an iterable set of `Filter` objects.

<br>
<br>



#### RequestOptions.Field class

The `RequestOptions.Field` class corresponds to the fields used in filter expressions in the Tableau REST API. For more information, see [Filtering and Sorting](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_filtering_and_sorting.htm) in the Tableau REST API.

**Attributes**

**Attributes**

Field  |  Description
:--- | :---
`CreatedAt` |  Same as 'createdAt' in the REST API. TSC. `RequestOptions.Field.CreatedAt`
`LastLogin` | Same as 'lastLogin' in the REST API.  `RequestOptions.Field.LastLogin`
`Name` | Same as 'name' in the REST API.  `RequestOptions.Field.Name`
`OwnerName` | Same as 'ownerName' in the REST API.  `RequestOptions.Field.OwnerName`
`SiteRole` | Same as 'siteRole' in the REST API.  `RequestOptions.Field.SiteRole`
`Tags` | Same as 'tags' in the REST API.  `RequestOptions.Field.Tags`
`UpdatedAt` | Same as 'updatedAt' in the REST API.  `RequestOptions.Field.UpdatedAt`


<br>
<br>



#### RequestOptions.Operator class

Specifies the operators you can use to filter requests.


**Attributes**

Operator  |  Description
:--- | :---
`Equals` | Sets the operator to equals (same as `eq` in the REST API). `TSC.RequestOptions.Operator.Equals`
`GreaterThan` |  Sets the operator to greater than (same as `gt` in the REST API). `TSC.RequestOptions.Operator.GreaterThan`
`GreaterThanOrEqual` | Sets the operator to greater than or equal (same as `gte` in the REST API). `TSC.RequestOptions.Operator.GreaterThanOrEqual`
`LessThan` | Sets the operator to less than (same as `lt` in the REST API). `TSC.RequestOptions.Operator.LessThan`
`LessThanOrEqual` | Sets the operator to less than or equal (same as `lte` in the REST API). `TSC.RequestOptions.Operator.LessThanOrEqual`
`In` | Sets the operator to in (same as `in` in the REST API). `TSC.RequestOptions.Operator.In`

<br>
<br>



#### RequestOptions.Direction class

Specifies the direction to sort the returned fields.


**Attributes**

Name  |  Description
:--- | :---
`Asc` | Sets the sort direction to ascending (`TSC.RequestOptions.Direction.Asc`)
`Desc`  |  Sets the sort direction to descending (`TSC.RequestOptions.Direction.Desc`).

<br>
<br>

### CSVRequestOptions class

```py
CSVRequestOptions(maxage=-1)
```
Use this class to specify view filters to be applied when the CSV data is generated. Optionally, you can specify the maximum age of the CSV data cached on the server by providing a `maxage` value. See `views.populate_csv`.

**Attributes**

Name  |  Description
:--- | :---
`maxage` | Optional. The maximum number of minutes the CSV data will be cached on the server before being refreshed. The value must be an integer between `1` and `240` minutes. `0` will be interpreted as 1 minute on server, as that is the shortest interval allowed. By default, `maxage` is set to `-1`, indicating the default behavior configured in server settings.

**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, get a specific view, etc.

# set view filters
csv_req_option = TSC.CSVRequestOptions(maxage=5)
csv_req_option.vf('Region', 'South')
csv_req_option.vf('Category', 'Furniture')

# retrieve the csv data for the view
server.views.populate_csv(view_item, csv_req_option)
```

### ImageRequestOptions class

```py
ImageRequestOptions(imageresolution=None, maxage=-1)
```
Use this class to specify the resolution of the view and, optionally, the maximum age of the image cached on the server. You can also use this class to specify view filters to be applied when the image is generated. See `views.populate_image`.

**Attributes**

Name  |  Description
:--- | :---
`imageresolution` | The resolution of the view returned as an image. If unspecified, the `views.populate_image` method returns an image with standard resolution (the width of the returned image is 784 pixels). If you set this parameter value to high (`Resolution.High`), the width of the returned image is 1568 pixels. For both resolutions, the height varies to preserve the aspect ratio of the view.
`maxage` | Optional. The maximum number of minutes the image will be cached on the server before being refreshed. The value must be an integer between `1` and `240` minutes. `0` will be interpreted as 1 minute on server, as that is the shortest interval allowed. By default, `maxage` is set to `-1`, indicating the default behavior configured in server settings.

**View Filters**

You can use the `vf('filter_name', 'filter_value')` method to add view filters. When the image is generated, the specified filters will be applied to the view.

**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, get a specific view, etc.

# set the image request option
image_req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High, maxage=1)

# (optional) set a view filter
image_req_option.vf('Category', 'Furniture')

# retrieve the image for the view
server.views.populate_image(view_item, image_req_option)

```

### PDFRequestOptions class

```py
PDFRequestOptions(page_type=None, orientation=None, maxage=-1)
```
Use this class to specify the format of the PDF that is returned for the view. Optionally, you can specify the maximum age of the rendered PDF that is cached on the server by providing a `maxage` value. See `views.populate_pdf`.

**Attributes**

Name  |  Description
:--- | :---
`page_type` | The type of page returned in PDF format for the view. The page_type is set using the `PageType` class: <br> `PageType.A3`<br> `PageType.A4`<br> `PageType.A5`<br> `PageType.B5`<br> `PageType.Executive`<br> `PageType.Folio`<br>  `PageType.Ledger`<br> `PageType.Legal`<br> `PageType.Letter`<br> `PageType.Note`<br> `PageType.Quarto`<br> `PageType.Tabloid`
`orientation` | The orientation of the page. The options are portrait and landscape. The options are set using the `Orientation` class: <br>`Orientation.Portrait`<br> `Orientation.Landscape`
`maxage` | Optional. The maximum number of minutes the rendered PDF will be cached on the server before being refreshed. The value must be an integer between `1` and `240` minutes. `0` will be interpreted as 1 minute on server, as that is the shortest interval allowed. By default, `maxage` is set to `-1`, indicating the default behavior configured in server settings.

**View Filters**
You can use the `vf('filter_name', 'filter_value')` method to add view filters. When the PDF is generated, the specified filters will be applied to the view.

**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, get a specific view, etc.

# set the PDF request options
pdf_req_option = TSC.PDFRequestOptions(page_type=TSC.PDFRequestOptions.PageType.A4,
				       orientation=TSC.PDFRequestOptions.Orientation.Landscape,
				       maxage=1)

# (optional) set a view filter
pdf_req_option.vf('Region', 'West')

# retrieve the PDF for a view
server.views.populate_pdf(view_item, pdf_req_option)

```


<br>
<br>

---

## Schedules

Using the TSC library, you can schedule extract refresh or subscription tasks on Tableau Server. You can also get and update information about the scheduled tasks, or delete scheduled tasks.

If you have the identifier of the job, you can use the TSC library to find out the status of the asynchronous job.

The schedule properties are defined in the `ScheduleItem` class. The class corresponds to the properties for schedules you can access in Tableau Server or by using the Tableau Server REST API. The Schedule methods are based upon the endpoints for jobs in the REST API and operate on the `JobItem` class.


### ScheduleItem class

```py
ScheduleItem(name, priority, schedule_type, execution_order, interval_item)

```

The `ScheduleItem` class contains information about the specified schedule running on Tableau Server. The `ScheduleItem` class defines the information you can query and set. The class members correspond to the attributes of a server response payload.

Source file: models/schedule_item.py

**Attributes**

Name  |  Description
:--- | :---
`name`  |  The `name` of the schedule.
`id` | The identifier for the schedule. Use the `schedules.get()` method to get the identifiers of the schedules on the server.
`schedule_type` | The type of task. The types are either an `Extract` for an extract refresh task or a `Subscription` for a scheduled subscription.
`execution_order` | Specifies how the scheduled task should run. The choices are `Parallel`which uses all available background processes for this scheduled task, or `Serial`, which limits this schedule to one background process.
`interval_item` | Specifies the frequency that the scheduled task should run. The `interval_item` is an instance of the `IntervalItem` class. The `interval_item` has properties for frequency (hourly, daily, weekly, monthly), and what time and date the scheduled item runs. You set this value by declaring an `IntervalItem` object that is one of the following: `HourlyInterval`, `DailyInterval`, `WeeklyInterval`, or `MonthlyInterval`.


#### IntervalItem class
This class sets the frequency and start time of the scheduled item. This class contains the classes for the hourly, daily, weekly, and monthly intervals. This class mirrors the options you can set using the REST API and the Tableau Server interface.

**Attributes**

Name  |  Description
:--- | :---
`HourlyInterval`  | Runs scheduled item hourly. To set the hourly interval, you create an instance of the `HourlyInterval` class and assign the following values: `start_time`, `end_time`, and `interval_value`. To set the `start_time` and `end_time`, assign the time value using this syntax: `start_time=time(`*hour*`,` *minute*`)` and `end_time=time(`*hour*`,` *minute*`)`. The *hour* is specified in 24 hour time. The `interval_value` specifies how often the to run the task within the start and end time. The options are expressed in hours. For example, `interval_value=.25` is every 15 minutes. The values are `.25`, `.5`, `1`, `2`, `4`, `6`, `8`, `12`. Hourly schedules that run more frequently than every 60 minutes must have start and end times that are on the hour.
`DailyInterval`  | Runs the scheduled item daily. To set the daily interval, you create an instance of the `DailyInterval` and assign the `start_time`. The start time uses the syntax `start_time=time(`*hour*`,` *minute*`)`.
`WeeklyInterval`  |  Runs the scheduled item once a week. To set the weekly interval, you create an instance of the `WeeklyInterval` and assign the start time and multiple instances for the `interval_value` (days of week and start time). The start time uses the syntax `time(`*hour*`,` *minute*`)`. The `interval_value` is the day of the week, expressed as a `IntervalItem`. For example `TSC.IntervalItem.Day.Monday` for Monday.
`MonthlyInterval`  |  Runs the scheduled item once a month. To set the monthly interval, you create an instance of the `MonthlyInterval` and assign the start time and day. The




### Schedule methods

The schedule methods are based upon the endpoints for schedules in the REST API and operate on the `ScheduleItem` class.


Source files: server/endpoint/schedules_endpoint.py

#### schedule.create

```py
schedule.create(schedule_item)
```
Creates a new schedule for an extract refresh or a subscription.


REST API: [Create Schedule](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_schedule)



**Parameters**

Name  |  Description
:--- | :---
`schedule_item` | The settings for the schedule that you want to create. You need to create an instance of `schedule_item` and pass it to the `create` method. The `schedule_item` includes the `interval_item` which specifies the frequency, or interval, that the schedule should run. See `ScheduleItem` and `IntervalItem`.


**Returns**

Returns a new instance of `schedule_item`.

**Exceptions**

Error  |  Description
:--- | :---
`Interval item must be defined.`  |  Raises an exception if the `schedule_item.interval_item` is not specified. The interval item specifies whether the interval is hourly, daily, weekly, or monthly.


**Example**

```py
import tableauserverclient as TSC
# sign in, etc.
 # Create an interval to run every 2 hours between 2:30AM and 11:00PM
        hourly_interval = TSC.HourlyInterval(start_time=time(2, 30),
                                             end_time=time(23, 0),
                                             interval_value=2)
 # Create schedule item
        hourly_schedule = TSC.ScheduleItem("Hourly-Schedule", 50, TSC.ScheduleItem.Type.Extract, TSC.ScheduleItem.ExecutionOrder.Parallel, hourly_interval)
 # Create schedule
        hourly_schedule = server.schedules.create(hourly_schedule)
```
<br>
<br>


#### schedule.delete

```py
schedule.delete(schedule_id)
```

Deletes an existing schedule for an extract refresh or a subscription.


REST API: [Delete Schedule](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#delete_schedule)



**Parameters**

Name  |  Description
:--- | :---
`schedule_id` | The identifier (`schedule_item.id`) of the schedule to delete. Use the `schedule.get()` method to get the identifiers of the schedules on the server.


**Returns**

None.

**Exceptions**

Error  |  Description
:--- | :---
`Schedule ID undefined`  |  The identifier is not a valid identifier for a schedule on the server.


#### schedule.get

```py
schedule.get([req_options=None])
```

Returns all schedule items from the server.


REST API: [Query Schedules](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_schedules)



**Parameters**

Name  |  Description
:--- | :---
`req_options` | (Optional) Additional request options to send to the endpoint.

#### schedule.update

<br>
<br>


**Hourly schedule example**
```py
import tableauserverclient as TSC
# sign in, etc.
 # Create an interval to run every 2 hours between 2:30AM and 11:00PM
        hourly_interval = TSC.HourlyInterval(start_time=time(2, 30),
                                             end_time=time(23, 0),
                                             interval_value=2)
 # Create schedule item
        hourly_schedule = TSC.ScheduleItem("Hourly-Schedule", 50, TSC.ScheduleItem.Type.Extract, TSC.ScheduleItem.ExecutionOrder.Parallel, hourly_interval)
 # Create schedule
        hourly_schedule = server.schedules.create(hourly_schedule)
```

**Daily schedule example**
```py
import tableauserverclient as TSC
# sign in, etc.
 # Create a daily interval to run every day at 12:30AM
        Daily_interval = TSC.DailyInterval(start_time=time(0, 30))
 # Create schedule item using daily interval
        daily_schedule = TSC.ScheduleItem("Daily-Schedule", 60, TSC.ScheduleItem.Type.Subscription, TSC.ScheduleItem.ExecutionOrder.Serial, daily_interval)
 # Create daily schedule
        daily_schedule = server.schedules.create(daily_schedule)

```

**Weekly schedule example**
```py
import tableauserverclient as TSC
# sign in, etc.
 # Create a weekly interval to run every Monday, Wednesday, and Friday at 7:15PM
        weekly_interval = TSC.WeeklyInterval(time(19, 15),
                                             TSC.IntervalItem.Day.Monday,
                                             TSC.IntervalItem.Day.Wednesday,
                                             TSC.IntervalItem.Day.Friday)
 # Create schedule item using weekly interval
        weekly_schedule = TSC.ScheduleItem("Weekly-Schedule", 70,
                                          TSC.ScheduleItem.Type.Extract,
                                          TSC.ScheduleItem.ExecutionOrder.Serial, weekly_interval)
 # Create weekly schedule
        weekly_schedule = server.schedules.create(weekly_schedule)

```

**Monthly schedule example**
```py
import tableauserverclient as TSC
# sign in, etc.
 # Create a monthly interval to run on the 15th of every month at 11:30PM
        monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30),
                                               interval_value=15)
 # Create schedule item using monthly interval
        monthly_schedule = TSC.ScheduleItem("Monthly-Schedule", 80,
                                           TSC.ScheduleItem.Type.Subscription
                                           TSC.ScheduleItem.ExecutionOrder.Parallel, monthly_interval)
 # Create monthly schedule
        monthly_schedule = server.schedules.create(monthly_schedule)
```



<br>
<br>

---


## Server

In the Tableau REST API, the server (`https://MY-SERVER/`) is the base or core of the URI that makes up the various endpoints or methods for accessing resources on the server (views, workbooks, sites, users, data sources, etc.)
The TSC library provides a `Server` class that represents the server. You create a server instance to sign in to the server and to call the various methods for accessing resources.


<br>
<br>


### Server class

```py
Server(server_address)
```
The `Server` class contains the attributes that represent the server on Tableau Server. After you create an instance of the `Server` class, you can sign in to the server and call methods to access all of the resources on the server.

**Attributes**

Attribute | Description
:--- | :---
`server_address`  |  Specifies the address of the Tableau Server or Tableau Online (for example, `https://MY-SERVER/`).
`version`   |  Specifies the version of the REST API to use (for example, `'2.5'`). When you use the TSC library to call methods that access Tableau Server, the `version` is passed to the endpoint as part of the URI (`https://MY-SERVER/api/2.5/`). Each release of Tableau Server supports specific versions of the REST API. New versions of the REST API are released with Tableau Server. By default, the value of `version` is set to `'2.3'`, which corresponds to Tableau Server 10.0.  You can view or set this value. You might need to set this to a different value, for example, if you want to access features that are supported by the server and a later version of the REST API.  For more information, see [REST API Versions](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm).



**Example**

```py
import tableauserverclient as TSC


# create a instance of server
server = TSC.Server('https://MY-SERVER')

# sign in, etc.

# change the REST API version to match the server
server.use_server_version()

# or change the REST API version to match a specific version
# for example, 2.8
# server.version = '2.8'

```

#### Server.*Resources*

When you create an instance of the `Server` class, you have access to the resources on the server after you sign in. You can select these resources and their methods as members of the class, for example: `server.views.get()`



Resource   |  Description
 :--- | : ---
*server*.auth   |   Sets authentication for sign in and sign out. See [Auth](#authentication)  |
*server*.views  |   Access the server views and methods.  See [Views](#views)
*server*.users  |   Access the user resources and methods.  See [Users](#users)
*server*.sites  |   Access the sites.  See [Sites](#sites)
*server*.groups   | Access the groups resources and methods. See [Groups](#groups)
*server*.jobs  | Access the jobs resources and methods. See [Jobs](#jobs)
*server*.workbooks  |  Access the resources and methods for workbooks. See [Workbooks](#workbooks)
*server*.datasources  |  Access the resources and methods for data sources. See [Data Sources](#data-sources)
*server*.projects  |   Access the resources and methods for projects. See [Projects](#projects)
*server*.schedules  |  Access the resources and methods for schedules. See [Schedules](#schedules)
*server*.subscriptions | Access the resources and methods for subscriptions. See [Subscriptions](#subscriptions)
*server*.server_info  |  Access the resources and methods for server information. See [ServerInfo class](#serverinfoitem-class)

<br>
<br>

#### Server.PublishMode

The `Server` class has `PublishMode` class that enumerates the options that specify what happens when you publish a workbook or data source. The options are `Overwrite`,  `Append`, or `CreateNew`.


**Properties**

Resource   |  Description
 :--- | : ---
`PublishMode.Overwrite`  | Overwrites the workbook or data source.
`PublishMode.Append` |  Appends to the workbook or data source.
`PublishMode.CreateNew` |  Creates a new workbook or data source.


**Example**

```py
 import tableauserverclient as TSC
 # login, etc.

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
The `ServerInfoItem` class contains the build and version information for Tableau Server. The server information is accessed with the `server_info.get()` method, which returns an instance of the `ServerInfo` class.

**Attributes**

Name  |  Description
:--- | :---
`product_version`  |  Shows the version of the Tableau Server or Tableau Online (for example, 10.2.0).
`build_number`   |  Shows the specific build number (for example, 10200.17.0329.1446).
`rest_api_version`  |  Shows the supported REST API version number. Note that this might be different from the default value specified for the server, with the `Server.version` attribute. To take advantage of new features, you should query the server and set the `Server.version` to match the supported REST API version number.


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

REST API: [Server Info](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#server_info)

**Parameters**
 None

**Exceptions**

Error  |  Description
:--- | :---
`404003	UNKNOWN_RESOURCE`  |  Raises an exception if the server info endpoint is not found.

**Example**

```py
import tableauserverclient as TSC

# create a instance of server
server = TSC.Server('https://MY-SERVER')

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

---

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
`storage_quota` | (Optional) 	Specifies the maximum amount of space for the new site, in megabytes. If you set a quota and the site exceeds it, publishers will be prevented from uploading new content until the site is under the limit again.
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

Source file: models/site_item.py

<br>
<br>


### Site methods

The TSC library provides methods that operate on sites for Tableau Server and Tableau Online. These methods correspond to endpoints or methods for sites in the Tableau REST API.


Source file: server/endpoint/sites_endpoint.py

<br>
<br>

#### sites.create

```py
sites.create(site_item)
```

Creates a new site on the server for the specified site item object.

Tableau Server only.


REST API: [Create Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_site)



**Parameters**

Name  |  Description
:--- | :---
`site_item` | The settings for the site that you want to create. You need to create an instance of `SiteItem` and pass it to the `create` method.


**Returns**

Returns a new instance of `SiteItem`.


**Example**

```py
import tableauserverclient as TSC

# create an instance of server
server = TSC.Server('https://MY-SERVER')

# create shortcut for admin mode
content_users=TSC.SiteItem.AdminMode.ContentAndUsers

# create a new SiteItem
new_site = TSC.SiteItem(name='Tableau', content_url='tableau', admin_mode=content_users, user_quota=15, storage_quota=1000, disable_subscriptions=True)

# call the sites create method with the SiteItem
new_site = server.sites.create(new_site)
```
<br>
<br>

#### sites.get

```py
sites.get()
```

Queries all the sites on the server.


REST API: [Query Sites](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_sites)


**Parameters**

 None.

**Returns**

Returns a list of all `SiteItem` objects and a `PaginationItem`. Use these values to iterate through the results.


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc.

  # query the sites
  all_sites, pagination_item = server.sites.get()

  # print all the site names and ids
  for site in all_sites:
       print(site.id, site.name, site.content_url, site.state)


```

<br>
<br>



#### sites.get_by_id

```py
sites.get_by_id(site_id)
```

Queries the site with the given ID.


REST API: [Query  Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_site)

**Parameters**

Name  |  Description
:--- | :---
`site_id`  | The id for the site you want to query.


**Exceptions**

Error   |  Description
 :--- | : ---
`Site ID undefined.` | Raises an error if an id is not specified.


**Returns**

Returns the `SiteItem`.


**Example**

```py

# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc.

 a_site = server.sites.get_by_id('9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d')
 print("\nThe site with id '9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d' is: {0}".format(a_site.name))

```

<br>
<br>

#### sites.get_by_name

```py
sites.get_by_name(site_name)
```

Queries the site with the specified name.


REST API: [Query  Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_site)

**Parameters**

Name  |  Description
:--- | :---
`site_name`  | The name of the site you want to query.


**Exceptions**

Error   |  Description
 :--- | : ---
`Site Name undefined.` | Raises an error if an name is not specified.


**Returns**

Returns the `SiteItem`.


**Example**

```py

# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc.

 a_site = server.sites.get_by_name('MY_SITE')


```

<br>
<br>



#### sites.update

```py
sites.update(site_item)
```

Modifies the settings for site.


The site item object must include the site ID and overrides all other settings.


REST API: [Update Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_site)


**Parameters**

Name  |  Description
:--- | :---
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




#### sites.delete


```py
Sites.delete(site_id)
```

Deletes the specified site.


REST API: [Delete Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#delete_site)


**Parameters**

Name   |  Description
 :--- | : ---
`site_id`    |       The id of the site that you want to delete.



**Exceptions**

Error  |  Description
:---  | :---
`Site ID Undefined.`   |    The site id must be present and must match the id of the site you are deleting.



**Example**

```py

# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# sign in, etc.

server.sites.delete('9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d')

```

<br>
<br>

---


## Sort

The `Sort` class is used with request options (`RequestOptions`) where you can filter and sort on the results returned from the server.

You can use the sort and request options to filter and sort the following endpoints:

- Users
- Datasources
- Workbooks
- Views

### Sort class

```py
sort(field, direction)
```



**Attributes**

Name  |  Description
:--- | :---
`field`  |  Sets the field to sort on. The fields are defined in the `RequestOption` class.
`direction` | The direction to sort, either ascending (`Asc`) or descending (`Desc`). The options are defined in the `RequestOptions.Direction` class.

**Example**

```py

# create a new instance of a request option object
req_option = TSC.RequestOptions()

# add the sort expression, sorting by name and direction
req_option.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name,
                             TSC.RequestOptions.Direction.Asc))
matching_workbooks, pagination_item = server.workbooks.get(req_option)

for wb in matching_workbooks:
    print(wb.name)
```

For information about using the `Sort` class, see [Filter and Sort](filter-sort).

<br>
<br>

---

## Subscriptions

Using the TSC library, you can manage subscriptions to views or workbooks on a site. You can get information about all the subscriptions on a site, or information about a specific subscription on a site, and you can create, update, or delete subscriptions.

### SubscriptionItem class

The subscription resources for Tableau Server are defined in the `SubscriptionItem` class. The class corresponds to the subscription resources you can access using the Tableau Server REST API. The subscription methods are based upon the endpoints for subscriptions in the REST API and operate on the `SubscriptionItem` class.

```py
SubscriptionItem(subject, schedule_id, user_id, target)

```

**Attributes**

Name | Description
:--- | :---
`id` |   The id of the subscription on the site.
`attach_image` | Setting this to `True` will cause the subscriber to receive mail with .png images of workbooks or views attached to it. By default, this value is set to `True`. If `attach_pdf` is set to `False`, then this value cannot be set to `False`.
`attach_pdf` | Setting this to `True` will cause the subscriber to receive mail with a .pdf file containing images of workbooks or views attached to it. By default, this value is set to `False`.
`message` | The text body of the subscription email message.
`page_orientation` | The orientation of the pages produced when `attach_pdf` is `True`. If this parameter is not present the page orientation will default to `Portrait`. See chart below for a full list of values.
`page_size_option` | The type of page produced, which determines the page dimensions when `attach_pdf` is `True`. If this parameter is not present the page type will default to `Letter`. See chart below for a full list of values.
`schedule_id` | The id of the schedule associated with the specific subscription.
`send_if_view_empty` | Applies to views only (see `target` attribute). If `True`, an image is sent even if the view specified in a subscription is empty. If `False`, nothing is sent if the view is empty. The default value is `True`.
`subject`|  The subject of the subscription. This is the description that you provide to identify the subscription.
`suspended` | Setting this value to `True` stops email delivery for the specified subscription. Setting it to `False` will resume email delivery for the subscription.
`target` | The target of the subscription, that is, the content that is subscribed to (view, workbook). The target is an instance of the `target` class. The `target` has two properties, the `id` of the workbook or view (`target.id`), and the `type` (`target.type`), which can either `view` or `workbook`. The `send_if_view_empty` attribute can only be set to `True` if the `target.type` is set to `View`.
`user_id` | The identifier of the user (person) who receives the subscription.

<br>
**Valid PDF options (applies only if `attach_pdf` is set to `True`)**

Attribute | Valid options
:--- | :---
`page_orientation` | `TSC.PDFRequestOptions.Orientation.Landscape` <br> `TSC.PDFRequestOptions.Orientation.Portrait`
`page_size_option` | `TSC.PDFRequestOptions.PageType.A3`<br> `TSC.PDFRequestOptions.PageType.A4`<br> `TSC.PDFRequestOptions.PageType.A5`<br> `TSC.PDFRequestOptions.PageType.B5`<br> `TSC.PDFRequestOptions.PageType.Executive`<br> `TSC.PDFRequestOptions.PageType.Folio`<br>  `TSC.PDFRequestOptions.PageType.Ledger`<br> `TSC.PDFRequestOptions.PageType.Legal`<br> `TSC.PDFRequestOptions.PageType.Letter`<br> `TSC.PDFRequestOptions.PageType.Note`<br> `TSC.PDFRequestOptions.PageType.Quarto`<br> `TSC.PDFRequestOptions.PageType.Tabloid`


Source files:
server/endpoints/subscription_item.py
server/request_options.py


###  Subscription methods

The Tableau Server Client provides several methods for interacting with subscription resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API.



Source files: server/endpoints/subscriptions_endpoint.py

<br>
<br>

#### subscription.create

```py
subscription.create(subscription_item)
```
Creates a subscription to a view or workbook for a specific user on a specific schedule.
When a user is subscribed to the content, Tableau Server sends the content to the user in email on the schedule that's defined on Tableau Server and specified in the `subscription_item`.

To create a new subscription you need to first create a new `subscription_item` (from `SubscriptionItem` class).


REST API: [Create Subscription](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#create_subscription)

**Parameters**

Name   |  Description
 :--- | : ---
`subscription_item` |  Specifies the user to subscribe, the content to subscribe to, the schedule to associate the subscription with, and other metadata for the subscription.


**Returns**

Returns the new `SubscriptionItem` object.




**Example**

```py
# Create the target (content) of the subscription with its ID and type.
# ID can be obtained by calling workbooks.get() or views.get().
target = TSC.Target('c7a9327e-1cda-4504-b026-ddb43b976d1d', 'workbook')

# Store the schedule ID and user ID.
# IDs can be obtained by calling schedules.get() and users.get().
schedule_id = 'b60b4efd-a6f7-4599-beb3-cb677e7abac1'
user_id = '28ce5884-ed38-49a9-aa10-8f5fbd59bbf6'

# Create the new SubscriptionItem object with variables from above.
new_sub = TSC.SubscriptionItem('My Subscription', schedule_id, user_id, target)

# (Optional) Set other fields. Any of these can be added or removed.
new_sub.attach_image = False
new_sub.attach_pdf = True
new_sub.message = "You have an alert!"
new_sub.page_orientation = TSC.PDFRequestOptions.Orientation.Landscape
new_sub.page_size_option = TSC.PDFRequestOptions.PageType.B4
new_sub.send_if_view_empty = True

# Create the new subscription on the site you are logged in.
new_sub = server.subscriptions.create(new_sub)
print(new_sub.subject)
```


<br>
<br>



#### subscriptions.delete

```py
subscriptions.delete(subscription_id)
```



Deletes the specified subscription from the site.

REST API: [Delete Subscription](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#delete_subscription)


**Parameters**

Name   |  Description
 :--- | : ---
`subscription_id`  |  The identifier (`id`) for the subscription that you want to remove from the site.


**Exceptions**

Error   |  Description
 :--- | : ---
`Subscription ID undefined`   |  Raises an exception if a valid `subscription_id` is not provided.


**Example**

```py
#  Remove a subscription from the site

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', site_id='SITE')
#  server = TSC.Server('https://SERVERURL')


   with server.auth.sign_in(tableau_auth):
     server.subscriptions.delete('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')

```
<br>
<br>

<br>
<br>

#### subscription.get

```py
subscription.get(req_options=None)
```
Returns information about the subscriptions on the specified site.


REST API: [Query Subscriptions](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_subscriptions)

**Parameters**

Name   |  Description
 :--- | : ---
`req_options` |  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific subscription, you could specify the subject of the subscription or the id of the subscription.


**Returns**
Returns a list of `SubscriptionItem` objects and a `PaginationItem` object. Use these values to iterate through the results.


<br>
<br>

#### subscription.get_by_id


```py
subscription.get_by_id(subscription_id)
```

Returns information about the specified subscription.

REST API: [Query Subscription](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_subscription)


**Parameters**

Name   |  Description
 :--- | : ---
`subscription_id`  |  The `subscription_id` specifies the subscription to query.



**Exceptions**

Error   |  Description
 :--- | : ---
`No Subscription ID provided.`  |  Raises an exception if a valid `subscription_id` is not provided.


**Returns**

The `SubscriptionItem`.  See [SubscriptionItem class](#subscriptionitem-class)


**Example**

```py
  sub1 = server.subscription.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
  print(sub1.subject)

```

<br>
<br>

#### subscription.update

```py
subscription.update(subscription_item)
```
Updates a specific subscription. To update a subscription, you must first query it from server using the `subscriptions.get()` or `subscriptions.get_by_id()` method.


REST API: [Update Subscription](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_subscription)

**Parameters**

Name   |  Description
 :--- | : ---
`subscription_item` |  Specifies the user to subscribe, the content to subscribe to, the schedule to associate the subscription with, and other metadata for the subscription.


**Returns**

Returns the updated `SubscriptionItem` object.


**Example**

```py
# Fetch an existing subscription from server. You can also use the subscriptions.get() method
sub = server.subscriptions.get_by_id('59cec1ec-15a0-4eb3-bc9d-056b87aa0a18')

# Set update-able fields. Any of these can be added or removed.
sub.subject = "Updated subject"
sub.attach_image = True
sub.attach_pdf = True
sub.page_orientation = TSC.PDFRequestOptions.Orientation.Landscape
sub.page_size_option = TSC.PDFRequestOptions.PageType.Folio
sub.suspended = True
sub.schedule_id = 'cf2f4465-9c4b-4536-b7cc-59994e9b7dde'
sub.send_if_view_empty = True

# Create the new subscription on the site you are logged in.
sub = server.subscriptions.update(sub)
print(new_sub.subject)
```

<br>
<br>

---

## Tasks

Using the TSC library, you can get information about all the tasks on a site and you can remove tasks. To create new tasks see [Schedules](#schedules).

The task resources for Tableau Server are defined in the `TaskItem` class. The class corresponds to the task resources you can access using the Tableau Server REST API. The task methods are based upon the endpoints for tasks in the REST API and operate on the `TaskItem` class.  

### TaskItem class

```py
TaskItem(id, task_type, priority, consecutive_failed_count=0, schedule_id=None, target=None)
```

**Attributes**

Name | Description  
:--- | :---  
`id` |   The id of the task on the site.
`task_type` | Type of extract task - full or incremental refresh.
`priority` | The priority of the task on the server.
`consecutive_failed_count` | The number of failed consecutive executions.
`schedule_id` | The id of the schedule on the site.
`target` | An object, `datasource` or `workbook`, which is associated to the task. Source file: models/target.py


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('server')

  task = server.tasks.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
  print(task)

```

Source file: models/task_item.py

<br> 
<br>


###  Tasks methods

The Tableau Server Client provides several methods for interacting with task resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API.

Source file: server/endpoint/tasks_endpoint.py
<br> 
<br>

#### tasks.get

```py
tasks.get(req_options=None)
```

Returns information about the tasks on the specified site.

REST API: [Get Extract Refresh Tasks on Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#get_extract_refresh_tasks)


**Parameters**

Name   |  Description     
 :--- | : ---    
`req_options` |  (Optional) You can pass the method a request object that contains additional parameters to filter the request.


**Returns**

Returns a list of `TaskItem` objects and a `PaginationItem` object.  Use these values to iterate through the results. 


**Example**


```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('https://SERVERURL')

with server.auth.sign_in(tableau_auth):
    all_tasks, pagination_item = server.tasks.get()
    print("\nThere are {} tasks on site: ".format(pagination_item.total_available))
    print([task.id for task in all_tasks])
```

<br>
<br>

#### tasks.get_by_id


```py
tasks.get_by_id(task_id)
```

Returns information about the specified task.   

REST API: [Query Extract Refresh Task On Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#get_extract_refresh_task){:target="_blank"}


**Parameters**

Name   |  Description     
 :--- | : ---    
`task_id`  |  The `task_id` specifies the task to query. 


**Exceptions**

Error   |  Description     
 :--- | : ---    
`Task ID undefined.`  |  Raises an exception if a valid `task_id` is not provided.


**Returns**

The `TaskItem`.  See [TaskItem class](#taskitem-class)


**Example**

```py
task1 = server.tasks.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
print(task1.task_type)
```

<br>   
<br>  

#### tasks.run


```py
tasks.run(task_item)
```

Runs the specified extract refresh task. 

To run a extract refresh task you need to first lookup the task `task_item` (`TaskItem` class).

REST API: [Run Extract Refresh Task](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#run_extract_refresh_task){:target="_blank"}


**Parameters**

Name   |  Description     
 :--- | : ---    
`task_item` |  You can pass the method a task object.


**Returns**

Returns the REST API response.

**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('server')
# login, etc.

task = server.tasks.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
server.tasks.run(task)
```

<br>   
<br> 

#### tasks.delete


```py
tasks.delete(task_id)
```

Deletes an extract refresh task.

REST API: [Run Extract Refresh Task](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_jobstasksschedules.htm#delete_workbook){:target="_blank"}

**Parameters**

Name   |  Description     
 :--- | : ---    
`task_id`  |  The `task_id` specifies the task to delete. 


**Exceptions**

Error   |  Description     
 :--- | : ---    
`Task ID undefined.`  |  Raises an exception if a valid `task_id` is not provided.


**Example**

```py
  server.tasks.delete('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')

```

<br>   
<br>  


---

## Users

Using the TSC library, you can get information about all the users on a site, and you can add or remove users, or update user information.

The user resources for Tableau Server are defined in the `UserItem` class. The class corresponds to the user resources you can access using the Tableau Server REST API. The user methods are based upon the endpoints for users in the REST API and operate on the `UserItem` class.


### UserItem class

```py
UserItem(name, site_role, auth_setting=None)
```

The `UserItem` class contains the members or attributes for the view resources on Tableau Server. The `UserItem` class defines the information you can request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload.

**Attributes**

Name | Description
:--- | :---
`auth_setting` | (Optional) This attribute is only for Tableau Online. The new authentication type for the user. You can assign the following values for this attribute: `SAML` (the user signs in using SAML) or `ServerDefault` (the user signs in using the authentication method that's set for the server). These values appear in the **Authentication** tab on the **Settings** page in Tableau Online -- the `SAML` attribute value corresponds to **Single sign-on**, and the `ServerDefault` value corresponds to **TableauID**.
`domain_name`  |    The name of the site.
`external_auth_user_id` |   Represents ID stored in Tableau's single sign-on (SSO) system. The `externalAuthUserId` value is returned for Tableau Online. For other server configurations, this field contains null.
`id` |   The id of the user on the site.
`last_login` | The date and time the user last logged in.
`workbooks` |  The workbooks the user owns. You must run the populate_workbooks method to add the workbooks to the `UserItem`.
`email` |  The email address of the user.
`fullname` | The full name of the user.
`name` |   The name of the user. This attribute is required when you are creating a `UserItem` instance.
`site_role` |  The role the user has on the site. This attribute is required if you are creating a `UserItem` instance. See *User Roles* below for details.
`groups` | The groups that the user belongs to. You must run the populate_groups method to add the groups to the `UserItem`.

**User Roles**

The possible user roles for the `site_role` attribute are the following:

* `Creator`
* `Explorer`
* `ExplorerCanPublish`
* `ServerAdministrator`
* `SiteAdministratorExplorer`
* `SiteAdministratorCreator`
* `Unlicensed`
* `ReadOnly`
* `Viewer`

Note: If any operations related to a user's `site_role` cause a 400 error response (for example: `Invalid site role: 'Explorer' is malformed or is not a supported user role in this version of Tableau`), ensure you are [using the latest REST API version for your server](versions#use-the-rest-api-version-supported-by-the-server).

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


###  Users methods

The Tableau Server Client provides several methods for interacting with user resources, or endpoints. These methods correspond to endpoints in the Tableau Server REST API.

Source file: server/endpoint/users_endpoint.py
<br>
<br>

#### users.add

```py
users.add(user_item)
```

Adds the user to the site.

To add a new user to the site you need to first create a new `user_item` (from `UserItem` class). When you create a new user, you specify the name of the user and their site role. For Tableau Online, you also specify the `auth_setting` attribute in your request.  When you add user to Tableau Online, the name of the user must be the email address that is used to sign in to Tableau Online. After you add a user, Tableau Online sends the user an email invitation. The user can click the link in the invitation to sign in and update their full name and password.

REST API: [Add User to Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#add_user_to_site)

**Parameters**

Name   |  Description
 :--- | : ---
`user_item` |  You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific user, you could specify the name of the user or the user's id.


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

#### users.get

```py
users.get(req_options=None)
```

Returns information about the users on the specified site.

To get information about the workbooks a user owns or has view permission for, you must first populate the `UserItem` with workbook information using the [populate_workbooks(*user_item*)](#populate-workbooks-user) method.


REST API: [Get Users on Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#get_users_on_site)

**Parameters**

Name   |  Description
 :--- | : ---
`req_options` |  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific user, you could specify the name of the user or the user's id.


**Returns**

Returns a list of `UserItem` objects and a `PaginationItem` object.  Use these values to iterate through the results.


**Example**


```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('https://SERVERURL')

with server.auth.sign_in(tableau_auth):
    all_users, pagination_item = server.users.get()
    print("\nThere are {} user on site: ".format(pagination_item.total_available))
    print([user.name for user in all_users])
```

<br>
<br>

#### users.get_by_id


```py
users.get_by_id(user_id)
```

Returns information about the specified user.

REST API: [Query User On Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_user_on_site)


**Parameters**

Name   |  Description
 :--- | : ---
`user_id`  |  The `user_id` specifies the user to query.


**Exceptions**

Error   |  Description
 :--- | : ---
`User ID undefined.`  |  Raises an exception if a valid `user_id` is not provided.


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

#### users.populate_groups

```py
users.populate_groups(user_item, req_options=None):
```

Returns the groups that the user belongs to.

**Parameters**

Name   |  Description
 :--- | : ---
`user_item`  |  The `user_item` specifies the user to populate with group membership.




**Exceptions**

Error   |  Description
 :--- | : ---
`User item missing ID.` |  Raises an error if the `user_item` is unspecified.


**Returns**

A list of `GroupItem`

A `PaginationItem` that points (`user_item.groups`). See [UserItem class](#useritem-class)


**Example**

```py
# first get all users, call server.users.get()
# get groups for user[0]
    ...

  page_n = server.users.populate_groups(all_users[0])
  print("\nUser {0} is a member of {1} groups".format(all_users[0].name, page_n.total_available))
  print("\nThe groups are:")
  for group in all_users[0].groups :
      print(group.name)

    ...
```




<br>
<br>

#### users.populate_workbooks

```py
users.populate_workbooks(user_item, req_options=None):
```

Returns information about the workbooks that the specified user owns and has Read (view) permissions for.


This method retrieves the workbook information for the specified user. The REST API is designed to return only the information you ask for explicitly. When you query for all the users, the workbook information for each user is not included. Use this method to retrieve information about the workbooks that the user owns or has Read (view) permissions. The method adds the list of workbooks to the user item object (`user_item.workbooks`).

REST API:  [Query Datasource Connections](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_data_source_connections)

**Parameters**

Name   |  Description
 :--- | : ---
`user_item`  |  The `user_item` specifies the user to populate with workbook information.




**Exceptions**

Error   |  Description
 :--- | : ---
`User item missing ID.` |  Raises an error if the `user_item` is unspecified.


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

#### users.remove

```py
users.remove(user_id)
```



Removes the specified user from the site.

REST API: [Remove User from Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#remove_user_from_site)


**Parameters**

Name   |  Description
 :--- | : ---
`user_id`  |  The identifier (`id`) for the user that you want to remove from the server.


**Exceptions**

Error   |  Description
 :--- | : ---
`User ID undefined`   |  Raises an exception if a valid `user_id` is not provided.


**Example**

```py
#  Remove a user from the site

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('https://SERVERURL')

   with server.auth.sign_in(tableau_auth):
     server.users.remove('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')

```
<br>
<br>




#### users.update

```py
users.update(user_item, password=None)
```

Updates information about the specified user.

The information you can modify depends upon whether you are using Tableau Server or Tableau Online, and whether you have configured Tableau Server to use local authentication or Active Directory. For more information, see [Update User](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_user).



REST API: [Update User](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_user)

**Parameters**

Name   |  Description
 :--- | : ---
`user_item`  |  The `user_item` specifies the user to update.
`password`  | (Optional) The new password for the user.



**Exceptions**

Error   |  Description
 :--- | : ---
`User item missing ID.` |  Raises an error if the `user_item` is unspecified.


**Returns**

An updated `UserItem`.    See [UserItem class](#useritem-class)


**Example**

```py

#  import tableauserverclient as TSC
#  tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
#  server = TSC.Server('https://SERVERURL')

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


---

## Views

Using the TSC library, you can get information about views in a site or a workbook.

The view resources for Tableau Server are defined in the `ViewItem` class. The class corresponds to the view resources you can access using the Tableau Server REST API. The view methods are based upon the endpoints for views in the REST API and operate on the `ViewItem` class.

<br>

### ViewItem class

```
ViewItem()
```

The `ViewItem` class contains the members or attributes for the view resources on Tableau Server. The `ViewItem` class defines the information you can request or query from Tableau Server. The class members correspond to the attributes of a server request or response payload.

Source file: models/view_item.py

**Attributes**

Name | Description
:--- | :---
`content_url` | The name of the view as it would appear in a URL.
`csv` | The CSV data of the view. You must first call the `views.populate_csv` method to access the CSV data.
`id` | The identifier of the view item.
`image` | The image of the view. You must first call the `views.populate_image`method to access the image.
`name`  | The name of the view.
`owner_id` |  The ID for the owner of the view.
`pdf` | The PDF of the view. You must first call the `views.populate_pdf` method to access the PDF content.
`preview_image` | The thumbnail image for the view. You must first call the `views.populate_preview_image` method to access the preview image.
`project_id` | The ID of the project that contains the view.
`total_views`  |  The usage statistics for the view. Indicates the total number of times the view has been looked at.
`workbook_id`  |  The ID of the workbook associated with the view.


<br>
<br>


### Views methods

The Tableau Server Client provides methods for interacting with view resources, or endpoints. These methods correspond to the endpoints for views in the Tableau Server REST API.

Source file: server/endpoint/views_endpoint.py

<br>
<br>

#### views.get
```
views.get(req_options=None, usage=False)
```

Returns the list of views items for a site.


REST API: [Query Views for Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_views_for_site)

**Version**

This endpoint is available with REST API version 2.0 and up.

**Parameters**

Name | Description
:--- | :---
`req_options`  |  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific view, you could specify the name of the view or its ID.
`usage` | (Optional) If true (`usage=True`) returns the usage statistics for the views. The default is `usage=False`.



**Returns**

Returns a list of all `ViewItem` objects and a `PaginationItem`. Use these values to iterate through the results.

**Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password')
server = TSC.Server('https://servername')

with server.auth.sign_in(tableau_auth):
    all_views, pagination_item = server.views.get()
    print([view.name for view in all_views])
```

**Example using Pager**

You can also use the provided Pager generator to get all views on site, without having to page through the results.
```py
for view in TSC.Pager(server.views):
    print(view.name)
```

See [ViewItem class](#viewitem-class)


<br>
<br>

#### views.get_by_id
```
views.get_by_id(view_id)
```

Returns the details of a specific view.


REST API: [Get View](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#get_view)

**Version**

This endpoint is available REST API version 3.1 and up.

**Parameters**

Name | Description
:--- | :---
`view_id`  |  The ID of the view to retrieve.



**Returns**

Returns a single `ViewItem` object.

**Example**

```py
import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password')
server = TSC.Server('https://servername')

with server.auth.sign_in(tableau_auth):
    view = server.view.get_by_id('d79634e1-6063-4ec9-95ff-50acbf609ff5')
    print(view.name)
```

See [ViewItem class](#viewitem-class)


<br>
<br>

#### views.populate_preview_image

```py
 views.populate_preview_image(view_item)
```

Populates a preview image for the specified view.

This method gets the preview image (thumbnail) for the specified view item. The method uses the `id` and `workbook_id` fields to query the preview image. The method populates the `preview_image` for the view.

REST API: [Query View Preview Image](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_view_with_preview)

**Version**

This endpoint is available with REST API version 2.0 and up.

**Parameters**

Name | Description
:--- | :---
`view_item`  |  Specifies the view to populate.


**Exceptions**

Error | Description
:--- | :---
`View item missing ID or workbook ID` |  Raises an error if the ID of the view or workbook is missing.


**Returns**

None. The preview image is added to `view_item` and can be accessed by its `preview_image` field.

**Example**
```py
# Sign in, get view, etc.

# Populate and save the preview image as 'view_preview_image.png'
server.views.populate_preview_image(view_item)
with open('./view_preview_image.png', 'wb') as f:
	f.write(view_item.preview_image)
```

See [ViewItem class](#viewitem-class)

<br>
<br>

#### views.populate_image

```py
views.populate_image(view_item, req_options=None)
```

Populates the image of the specified view.

This method uses the `id` field to query the image, and populates the image content as the `image` field.

REST API: [Query View Image](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_view_image)

**Version**

This endpoint is available with REST API version 2.5 and up.

**Parameters**

Name | description
:--- | :---
`view_item` | Specifies the view to populate.
`req_options` | (Optional) You can pass in request options to specify the image resolution (`imageresolution`) and the maximum age of the view image cached on the server (`maxage`). See [ImageRequestOptions class](#imagerequestoptions-class) for more details.

**Exceptions**

Error | Description
:--- | :---
`View item missing ID` | Raises an error if the ID of the view is missing.

**Returns**

None. The image is added to the `view_item` and can be accessed by its `image` field.

**Example**
```py
# Sign in, get view, etc.

# Populate and save the view image as 'view_image.png'
server.views.populate_image(view_item)
with open('./view_image.png', 'wb') as f:
	f.write(view_item.image)
```

See [ViewItem class](#viewitem-class)

<br>
<br>

#### views.populate_csv
```
views.populate_csv(view_item, req_options=None)
```

Populates the CSV data of the specified view.

This method uses the `id` field to query the CSV data, and populates the data as the `csv` field.

REST API: [Query View Data](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_view_data)

**Version**

This endpoint is available with REST API version 2.7 and up.

**Parameters**

Name | description
:--- | :---
`view_item` | Specifies the view to populate.
`req_options` | (Optional) You can pass in request options to specify the maximum age of the CSV cached on the server. See [CSVRequestOptions class](#csvrequestoptions-class) for more details.

**Exceptions**

Error | Description
:--- | :---
`View item missing ID` | Raises an error if the ID of the view is missing.

**Returns**

None. The CSV data is added to the `view_item` and can be accessed by its `csv` field.

**Example**
```py
# Sign in, get view, etc.

# Populate and save the CSV data in a file
server.views.populate_csv(view_item)
with open('./view_data.csv', 'wb') as f:
	# Perform byte join on the CSV data
	f.write(b''.join(view_item.csv))
```

See [ViewItem class](#viewitem-class)

<br>
<br>

#### views.populate_pdf
```
views.populate_pdf(view_item, req_options=None)
```

Populates the PDF content of the specified view.

This method populates a PDF with image(s) of the view you specify.

REST API: [Query View PDF](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_view_pdf)

**Version**

This endpoint is available with REST API version 2.7 and up.

**Parameters**

Name | description
:--- | :---
`view_item` | Specifies the view to populate.
`req_options` | (Optional) You can pass in request options to specify the page type and orientation of the PDF content, as well as the maximum age of the PDF rendered on the server. See [PDFRequestOptions class](#pdfrequestoptions-class) for more details.

**Exceptions**

Error | Description
:--- | :---
`View item missing ID` | Raises an error if the ID of the view is missing.

**Returns**

None. The PDF content is added to the `view_item` and can be accessed by its `pdf` field.

**Example**
```py
# Sign in, get view, etc.

# Populate and save the view pdf as 'view_pdf.pdf'
server.views.populate_pdf(view_item)
with open('./view_pdf.pdf', 'wb') as f:
	f.write(view_item.pdf)
```

See [ViewItem class](#viewitem-class)

<br>
<br>


---


## Workbooks

Using the TSC library, you can get information about a specific workbook or all the workbooks on a site, and  you can publish, update, or delete workbooks.

The project resources for Tableau are defined in the `WorkbookItem` class. The class corresponds to the workbook resources you can access using the Tableau REST API. The workbook methods are based upon the endpoints for projects in the REST API and operate on the `WorkbookItem` class.





<br>
<br>

### WorkbookItem class

```py

 WorkbookItem(project_id, name=None, show_tabs=False)

```
The workbook resources for Tableau are defined in the `WorkbookItem` class. The class corresponds to the workbook resources you can access using the Tableau REST API. Some workbook methods take an instance of the `WorkbookItem` class as arguments. The workbook item specifies the project


**Attributes**

Name  |  Description
:--- | :---
`connections` |  The list of data connections (`ConnectionItem`) for the data sources used by the workbook. You must first call the [workbooks.populate_connections](#workbooks.populate_connections) method to access this data. See the [ConnectionItem class](#connectionitem-class).
`content_url` |  The name of the data source as it would appear in a URL.
`created_at` |  The date and time when the data source was created.
`id` |  The identifier for the workbook. You need this value to query a specific workbook or to delete a workbook with the `get_by_id` and `delete` methods.
`name` | The name of the workbook.
`owner_id` | The ID of the owner.
`preview_image`  | The thumbnail image for the view. You must first call the [workbooks.populate_preview_image](#workbooks.populate_preview_image) method to access this data.
`project_id`  | The project id.
`project_name` | The name of the project.
`size` | The size of the workbook (in megabytes).
`show_tabs`  |  (Boolean) Determines whether the workbook shows tabs for the view.
`tags` |  The tags that have been added to the workbook.
`updated_at` |  The date and time when the workbook was last updated.
`views`   | The list of views (`ViewItem`) for the workbook. You must first call the [workbooks.populate_views](#workbooks.populate_views) method to access this data. See the [ViewItem class](#viewitem-class).
`webpage_url` | The full URL of the workbook.





**Example**

```py
# creating a new instance of a WorkbookItem
#
import tableauserverclient as TSC

# Create new workbook_item with project id '3a8b6148-493c-11e6-a621-6f3499394a39'

 new_workbook = TSC.WorkbookItem('3a8b6148-493c-11e6-a621-6f3499394a39')


```

Source file: models/workbook_item.py

<br>
<br>

### Workbook methods

The Tableau Server Client (TSC) library provides methods for interacting with workbooks. These methods correspond to endpoints in the Tableau Server REST API.  For example, you can use the library to publish, update, download, or delete workbooks on the site.
The methods operate on a workbook object (`WorkbookItem`) that represents the workbook resources.



Source files: server/endpoint/workbooks_endpoint.py

<br>
<br>

#### workbooks.get

```py
workbooks.get(req_options=None)
```

Queries the server and returns information about the workbooks the site.





REST API: [Query Workbooks for Site](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_workbooks_for_site)


**Parameters**

Name | Description
:--- | :---
`req_options`  |  (Optional) You can pass the method a request object that contains additional parameters to filter the request. For example, if you were searching for a specific workbook, you could specify the name of the workbook or the name of the owner. See [Filter and Sort](filter-sort)


**Returns**

Returns a list of all `WorkbookItem` objects and a `PaginationItem`. Use these values to iterate through the results.


**Example**

```py

import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password', site_id='site')
server = TSC.Server('https://servername')

with server.auth.sign_in(tableau_auth):
  all_workbooks_items, pagination_item = server.workbooks.get()
  # print names of first 100 workbooks
  print([workbook.name for workbook in all_workbooks_items])



```

<br>
<br>



#### workbooks.get_by_id

```py
workbooks.get_by_id(workbook_id)
```

Returns information about the specified workbook on the site.

REST API: [Query Workbook](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_workbook)


**Parameters**

Name | Description
:--- | :---
`workbook_id`  |  The `workbook_id` specifies the workbook to query. The ID is a LUID (64-bit hexadecimal string).


**Exceptions**

Error   |  Description
 :--- | : ---
`Workbook ID undefined`  |  Raises an exception if a `workbook_id` is not provided.


**Returns**

The `WorkbookItem`.  See [WorkbookItem class](#workbookitem-class)


**Example**

```py

workbook = server.workbooks.get_by_id('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')
print(workbook.name)

```


<br>
<br>


#### workbooks.publish

```py
workbooks.publish(workbook_item, file_path, publish_mode)
```

Publish a workbook to the specified site.

**Note:** The REST API cannot automatically include
extracts or other resources that the workbook uses. Therefore,
 a .twb file that uses data from an Excel or csv file on a local computer cannot be published,
unless you package the data and workbook in a .twbx file, or publish the data source separately.

For workbooks that are larger than 64 MB, the publish method automatically takes care of chunking the file in parts for uploading. Using this method is considerably more convenient than calling the publish REST APIs directly.

REST API: [Publish Workbook](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#publish_workbook), [Initiate File Upload](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#initiate_file_upload), [Append to File Upload](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#append_to_file_upload)



**Parameters**

Name | Description
:--- | :---
`workbook_item`  |  The `workbook_item` specifies the workbook you are publishing. When you are adding a workbook, you need to first create a new instance of a `workbook_item` that includes a `project_id` of an existing project. The name of the workbook will be the name of the file, unless you also specify a name for the new workbook when you create the instance. See [WorkbookItem](#workbookitem-class).
`file_path`  |  The path and name of the workbook to publish.
`mode`     |  Specifies whether you are publishing a new workbook (`CreateNew`) or overwriting an existing workbook (`Overwrite`).  You cannot appending workbooks.  You can also use the publish mode attributes, for example: `TSC.Server.PublishMode.Overwrite`.
`connection_credentials` | (Optional)  The credentials (if required) to connect to the workbook's data source. The `ConnectionCredentials` object contains the authentication information for the data source (user name and password, and whether the credentials are embedded or OAuth is used).



**Exceptions**

Error | Description
:--- | :---
`File path does not lead to an existing file.`  |  Raises an error of the file path is incorrect or if the file is missing.
`Invalid mode defined.`  |  Raises an error if the publish mode is not one of the defined options.
`Workbooks cannot be appended.` | The `mode` must be set to `Overwrite` or `CreateNew`.
`Only .twb or twbx files can be published as workbooks.`  |  Raises an error if the type of file specified is not supported.

See the REST API [Publish Workbook](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#publish_workbook) for additional error codes.

**Returns**

The `WorkbookItem` for the workbook that was published.


**Example**

```py

import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password', site_id='site')
server = TSC.Server('https://servername')

with server.auth.sign_in(tableau_auth):
   # create a workbook item
   wb_item = TSC.WorkbookItem(name='Sample', project_id='1f2f3e4e-5d6d-7c8c-9b0b-1a2a3f4f5e6e')
   # call the publish method with the workbook item
   wb_item = server.workbooks.publish(wb_item, 'SampleWB.twbx', 'Overwrite')
```

<br>
<br>

#### workbooks.refresh

```py
workbooks.refresh(workbook_item)
```


Refreshes the extract of an existing workbook.

REST API: [Update Workbook Now](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooksviews.htm#update_workbook_now)

**Parameters**

Name | Description
:--- | :---
`workbook_item`  |  The `workbook_item` specifies the settings for the workbook you are refreshing.

**Exceptions**

Error | Description
:--- | :---
`Workbook item missing ID. Workbook must be retrieved from server first.` | Raises an error if the `workbook_item` is unspecified. Use the `workbooks.get()` or `workbooks.get_by_id()` methods to retrieve the workbook item from the server.


```py

import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password', site_id='site')
server = TSC.Server('https://servername')

with server.auth.sign_in(tableau_auth):

    # get the workbook item from the site
    workbook = server.workbooks.get_by_id('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')

    # call the update method
    workbook = server.workbooks.refresh(workbook)
    print("\nThe data of workbook {0} is refreshed.".format(workbook.name))


```


<br>
<br>

#### workbooks.update

```py
workbooks.update(workbook_item)
```


Modifies an existing workbook. Use this method to change the owner or the project that the workbook belongs to, or to change whether the workbook shows views in tabs. The workbook item must include the workbook ID and overrides the existing settings.

REST API: [Update Workbooks](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_workbook)

**Parameters**

Name | Description
:--- | :---
`workbook_item`  |  The `workbook_item` specifies the settings for the workbook you are updating. You can change the `owner_id`, `project_id`, and the `show_tabs` values. See [WorkbookItem](#workbookitem-class).


**Exceptions**

Error | Description
:--- | :---
`Workbook item missing ID. Workbook must be retrieved from server first.` | Raises an error if the `workbook_item` is unspecified. Use the `workbooks.get()` or `workbooks.get_by_id()` methods to retrieve the workbook item from the server.


```py

import tableauserverclient as TSC
tableau_auth = TSC.TableauAuth('username', 'password', site_id='site')
server = TSC.Server('https://servername')

with server.auth.sign_in(tableau_auth):

    # get the workbook item from the site
    workbook = server.workbooks.get_by_id('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')
    print("\nUpdate {0} workbook. Project was {1}".format(workbook.name, workbook.project_name))


    # make an change, for example a new project ID
    workbook.project_id = '1f2f3e4e-5d6d-7c8c-9b0b-1a2a3f4f5e6e'

    # call the update method
    workbook = server.workbooks.update(workbook)
    print("\nUpdated {0} workbook. Project is now {1}".format(workbook.name, workbook.project_name))


```


<br>
<br>



#### workbooks.delete

```py
workbooks.delete(workbook_id)
```

Deletes a workbook with the specified ID.



To specify the site, create a `TableauAuth` instance using the content URL for the site (`site_id`), and sign in to that site.  See the [TableauAuth class](#tableauauth-class).


REST API: [Delete Workbook](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#delete_workbook1)


**Parameters**

Name  |  Description
:--- | :---
`workbook_id`   | The ID of the workbook to delete.




**Exceptions**

Error  |  Description
:--- | :---
`Workbook ID undefined.`  |  Raises an exception if the project item does not have an ID. The project ID is sent to the server as part of the URI.


**Example**

```py
# import tableauserverclient as TSC
# server = TSC.Server('https://MY-SERVER')
# tableau_auth sign in, etc.

 server.workbooks.delete('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')

```


<br>
<br>


#### workbooks.download

```py
workbooks.download(workbook_id, filepath=None, no_extract=False)
```

Downloads a workbook to the specified directory (optional).


REST API: [Download Workbook](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#download_workbook)


**Parameters**

Name | Description
:--- | :---
`workbook_id` |  The ID for the `WorkbookItem` that you want to download from the server.
`filepath` |  (Optional) Downloads the file to the location you specify. If no location is specified, the file is downloaded to the current working directory. The default is `Filepath=None`.
`no_extract` | (Optional) Specifies whether to download the file without the extract. When the workbook has an extract, if you set the parameter `no_extract=True`, the extract is not included. You can use this parameter to improve performance if you are downloading workbooks that have large extracts. The default is to include the extract, if present (`no_extract=False`). Available starting with Tableau Server REST API version 2.5.



**Exceptions**

Error | Description
:--- | :---
`Workbook ID undefined`   |  Raises an exception if a valid `datasource_id` is not provided.


**Returns**

The file path to the downloaded workbook.


**Example**

```py

  file_path = server.workbooks.download('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')
  print("\nDownloaded the file to {0}.".format(file_path))

```


<br>
<br>


#### workbooks.populate_views

```py
workbooks.populate_views(workbook_item)
```

Populates (or gets) a list of views for a workbook.

You must first call this method to populate views before you can iterate through the views.

This method retrieves the view information for the specified workbook. The REST API is designed to return only the information you ask for explicitly. When you query for all the data sources, the view information is not included. Use this method to retrieve the views. The method adds the list of views to the workbook item (`workbook_item.views`). This is a list of `ViewItem`.

REST API:  [Query Views for Workbook](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_views_for_workbook)

**Parameters**

Name | Description
:--- | :---
`workbook_item`  |  The `workbook_item` specifies the workbook to populate with views information. See [WorkbookItem class](#workbookitem-class).




**Exceptions**

Error | Description
:--- | :---
`Workbook item missing ID. Workbook must be retrieved from server first.` |  Raises an error if the `workbook_item` is unspecified. You can retrieve the workbook items using the `workbooks.get()` and `workbooks.get_by_id()` methods.


**Returns**

None. A list of `ViewItem` objects are added to the workbook (`workbook_item.views`).


**Example**

```py
# import tableauserverclient as TSC

# server = TSC.Server('https://SERVERURL')
#
   ...

# get the workbook item
  workbook = server.workbooks.get_by_id('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')


# get the view information
  server.workbooks.populate_views(workbook)

# print information about the views for the work item
  print("\nThe views for {0}: ".format(workbook.name))
  print([view.name for view in workbook.views])

  ...

```

<br>
<br>

#### workbooks.populate_connections

```py
workbooks.populate_connections(workbook_item)
```

Populates a list of data source connections for the specified workbook.

You must populate connections before you can iterate through the
connections.

This method retrieves the data source connection information for the specified workbook. The REST API is designed to return only the information you ask for explicitly. When you query all the workbooks, the data source connection information is not included. Use this method to retrieve the connection information for any data sources used by the workbook. The method adds the list of data connections to the workbook item (`workbook_item.connections`). This is a list of `ConnectionItem`.

REST API:  [Query Workbook Connections](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_workbook_connections)

**Parameters**

Name | Description
:--- | :---
`workbook_item`  |  The `workbook_item` specifies the workbook to populate with data connection information.




**Exceptions**

Error | Description
:--- | :---
`Workbook item missing ID. Workbook must be retrieved from server first.` |  Raises an error if the `workbook_item` is unspecified.


**Returns**

None. A list of `ConnectionItem` objects are added to the data source (`workbook_item.connections`).


**Example**

```py
# import tableauserverclient as TSC

# server = TSC.Server('https://SERVERURL')
#
   ...

# get the workbook item
  workbook = server.workbooks.get_by_id('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')


# get the connection information
  server.workbooks.populate_connections(workbook)

# print information about the data connections for the workbook item
  print("\nThe connections for {0}: ".format(workbook.name))
  print([connection.id for connection in workbook.connections])


  ...

```

<br>
<br>


#### workbooks.populate_preview_image

```py
workbooks.populate_preview_image(workbook_item)
```

This method gets the preview image (thumbnail) for the specified workbook item.

The method uses the `view.id` and `workbook.id` to identify the preview image. The method populates the `workbook_item.preview_image`.

REST API: [Query View Preview Image](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#query_workbook_preview_image)

**Parameters**

Name | Description
:--- | :---
`view_item`  |  The view item specifies the `view.id` and `workbook.id` that identifies the preview image.



**Exceptions**

Error | Description
:--- | :---
`View item missing ID or workbook ID` |  Raises an error if the ID for the view item or workbook is missing.



**Returns**

None. The preview image is added to the view.



**Example**

```py

# import tableauserverclient as TSC

# server = TSC.Server('https://SERVERURL')

   ...

  # get the workbook item
  workbook = server.workbooks.get_by_id('1a1b1c1d-2e2f-2a2b-3c3d-3e3f4a4b4c4d')

  # add the png thumbnail to the workbook item
  server.workbooks.populate_preview_image(workbook)


```

<br>
<br>

#### workbooks.update_connection

```py
workbooks.update_conn(workbook_item, connection_item)
```

Updates a workbook connection information (server address, server port, user name, and password).

The workbook connections must be populated before the strings can be updated. See [workbooks.populate_connections](#workbooks.populate_connections)

REST API:  [Update Workbook Connection](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm#update_workbook_connection)

**Parameters**

Name | Description
:--- | :---
`workbook_item`  |  The `workbook_item` specifies the workbook to populate with data connection information.
`connection_item` | The `connection_item` that has the information you want to update.



**Returns**

None. The connection information is updated with the information in the `ConnectionItem`.




**Example**

```py

# query for workbook connections
server.workbooks.populate_connections(workbook)

# update connection item user name and password
connection = workbook.connections[0]
connection.username = 'USERNAME'
connection.password = 'PASSWORD'

# call the update method
server.workbooks.update_conn(workbook, connection)
```

<br>
<br>

#### workbooks.populate_pdf
```
workbooks.populate_pdf(workbook_item, req_options=None)
```

Populates the PDF content of the specified workbook.

This method populates a PDF with image(s) of the workbook view(s) you specify.

REST API: [Download Workbook PDF](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooksviews.htm#download_workbook_pdf)

**Version**

This endpoint is available with REST API version 3.4 and up.

**Parameters**

Name | description
:--- | :---
`workbook_item` | Specifies the workbook to populate.
`req_options` | (Optional) You can pass in request options to specify the page type and orientation of the PDF content, as well as the maximum age of the PDF rendered on the server. See [PDFRequestOptions class](#pdfrequestoptions-class) for more details.

**Exceptions**

Error | Description
:--- | :---
`Workbook item missing ID` | Raises an error if the ID of the workbook is missing.

**Returns**

None. The PDF content is added to the `workbook_item` and can be accessed by its `pdf` field.

**Example**
```py
# Sign in, get view, etc.

# Populate and save the workbook pdf as 'workbook_pdf.pdf'
server.workbooks.populate_pdf(workbook_item)
with open('./workbook_pdf.pdf', 'wb') as f:
	f.write(workbook_item.pdf)
```

<br>
<br>


