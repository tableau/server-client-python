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

### Query Site by ID

Gets the site with the given ID.

```py
Sites.get_by_id('a1b2c3d4')
```

### Query Sites

Gets all the sites on the server.

```py
Sites.get()
```

### Update Site

Modifies a site. The site item object includes the site ID and overrides all other settings.

```py
Sites.update(site_item_object)
```

### Delete Site

Deletes the site with the given ID.

```py
Sites.delete('a1b2c3d4')
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

### Query Projects

### Update Project

### Delete Project


## Workbooks and views

Source files: server/endpoint/workbooks.py, server/endpoint/views_endpoint.py, models/view_item.py

### Publish Workbook

### Add Tags to Workbook

### Query Views for Workbook

### Query View Preview Image

### Query Workbook

### Query Workbook Connections

### Query Workbook Preview Image

### Query Workbooks for Site

### Query Workbooks for User

### Download Workbook

### Update Workbook

### Update Workbook Connection

### Delete Workbook

### Delete Tag from Workbook


## Data sources

Source files: server/endpoint/datasources_endpoint.py, models/datasource_item.py

### Publish Datasource

### Query Datasource

### Query Datasources

### Query Datasource Connections

### Download Datasource

### Update Datasource

### Update Datasource Connection

### Delete Datasource


## Users and groups

Source files: server/endpoint/users_endpoint.py, server/endpoint/groups_endpoint.py, models/user_item.py,
models/group_item.py

### Create Group

### Add User to Group

### Add User to Site

### Get Users in Group

### Get Users on Site

### Query Groups

### Query User On Site

### Update Group

### Update User

### Remove User from Group

### Remove User from Site

### Delete Group



## File Uploads

Source files: server/endpoint/fileuploads_endpoint.py, models/fileupload_item.py

### Initiate File Upload

### Append to File Upload

