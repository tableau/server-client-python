## 0.14.1 (9 Dec 2020)
* Fixed filter query issue for server version below 2020.1 (#745)
* Fixed large workbook/datasource publish issue (#757)

## 0.14.0 (6 Nov 2020)
* Added django-style filtering and sorting (#615)
* Added encoding tag-name before deleting (#687)
* Added 'Execute' Capability to permissions (#700)
* Added support for publishing workbook using file objects (#704)
* Added new fields to datasource_item (#705)
* Added all fields for users.get to get email and fullname (#713)
* Added support publishing datasource using file objects (#714)
* Improved request options by removing manual query param generation (#686)
* Improved publish_workbook sample to take in site (#694)
* Improved schedules.update() by removing constraint that required an interval (#711)
* Fixed site update/create not checking booleans properly (#723)

## 0.13 (1 Sept 2020)
* Added notes field to JobItem (#571)
* Added webpage_url field to WorkbookItem (#661)
* Added support for switching between sites (#655)
* Added support for querying favorites for a user (#656)
* Added support for Python 3.8 (#659)
* Added support for Data Alerts (#667)
* Added support for basic Extract operations - Create, Delete, en/re/decrypt for site (#672)
* Added support for creating and querying Active Directory groups (#674)
* Added support for asynchronously updating a group (#674)
* Improved handling of invalid dates (#529)
* Improved consistency of update_permission endpoints (#668)
* Documentation updates (#658, #669, #670, #673, #683)

## 0.12.1 (22 July 2020)

* Fixed login.py sample to properly handle sitename (#652)

## 0.12 (10 July 2020)

* Added hidden_views parameter to workbook publish method (#614)
* Added simple paging endpoint for GraphQL/Metadata API (#623)
* Added endpoints to Metadata API for retrieving backfill/eventing status (#626)
* Added maxage parameter to CSV and PDF export options (#635)
* Added support for querying, adding, and deleting favorites (#638)
* Added a sample for publishing datasources (#644)

## 0.11 (1 May 2020)

* Added more fields to Data Acceleration config (#588)
* Added OpenID as an auth setting enum (#610)
* Added support for Data Acceleration Reports (#596)
* Added support for view permissions (#526)
* Materialized views changed to Data Acceleration (#576)
* Improved consistency across workbook/datasource endpoints (#570)
* Fixed print error in update_connection.py (#602)
* Fixed log error in add user endpoint (#608)

## 0.10 (21 Feb 2020)

* Added a way to handle non-xml errors (#515)
* Added Webhooks endpoints for create, delete, get, list, and test (#523, #532)
* Added delete method in the tasks endpoint (#524)
* Added description attribute to WorkbookItem (#533)
* Added support for materializeViews as schedule and task types (#542)
* Added warnings to schedules (#550, #551)
* Added ability to update parent_id attribute of projects (#560, #567)
* Improved filename behavior for download endpoints (#517)
* Improved logging (#508)
* Fixed runtime error in permissions endpoint (#513)
* Fixed move_workbook_sites sample (#503)
* Fixed project permissions endpoints (#527)
* Fixed login.py sample to accept site name (#549)

## 0.9 (4 Oct 2019)

* Added Metadata API endpoints (#431)
* Added site settings for Data Catalog and Prep Conductor (#434)
* Added new fields to ViewItem (#331)
* Added support and samples for Tableau Server Personal Access Tokens (#465)
* Added Permissions endpoints (#429)
* Added tags to ViewItem (#470)
* Added Databases and Tables endpoints (#445)
* Added Flow endpoints (#494)
* Added ability to filter projects by topLevelProject attribute (#497)
* Improved server_info endpoint error handling (#439)
* Improved Pager to take in keyword arguments (#451)
* Fixed UUID serialization error while publishing workbook (#449)
* Fixed materalized views in request body for update_workbook (#461)

## 0.8.1 (17 July 2019)

* Fixed update_workbook endpoint (#454)

## 0.8 (8 Apr 2019)

* Added Max Age to download view image request (#360)
* Added Materialized Views (#378, #394, #396)
* Added PDF export of Workbook (#376)
* Added Support User Role (#392)
* Added Flows (#403)
* Updated Pager to handle un-paged results (#322)
* Fixed checked upload (#309, #319, #326, #329)
* Fixed embed_password field on publish (#416)

## 0.7 (2 Jul 2018)

* Added cancel job (#299)
* Added Get background jobs (#298)
* Added Multi-credential support (#276)
* Added Update Groups (#279)
* Adding project_id to view (#285)
* Added ability to rename workbook using `update workbook` (#284)
* Added Sample for exporting full pdf using pdf page combining (#267)
* Added Sample for exporting data, images, and single view pdfs (#263)
* Added view filters to the populate request options (#260)
* Add Async publishing for workbook and datasource endpoints (#311)
* Fixed ability to update datasource server connection port (#283)
* Fixed next project handling (#267)
* Cleanup debugging output to strip out non-xml response
* Improved refresh sample for readability (#288)

## 0.6.1 (26 Jan 2018)

* Fixed #257 where refreshing extracts does not work due to a missing "self"

## 0.6 (17 Jan 2018)

* Added support for add a datasource/workbook refresh to a schedule (#244)
* Added support for updating datasource connections (#253) 
* Added Refresh Now for datasource and workbooks (#250)
* Fixed Typos in the docs (#251)

## 0.5.1 (21 Sept 2017)

* Fix a critical issue caused by #224 that was the result of lack of test coverage (#226)

## 0.5 (20 Sept 2017)

* Added revision settings to update site (#187)
* Added support for certified data sources (#189)
* Added support for include/exclude extract (#203)
* Added auto-paging for group users (#204)
* Added ability to add workbooks to a schedule (#206)
* Added the ability to create nested projects (#208)
* Fixed sort order when using pager (#192)
* Docs Updates and new samples (#196, #199, #200, #201)

## 0.4.1 (18 April 2017)

* Fix #177 to remove left in debugging print

## 0.4 (18 April 2017)
 
Yikes, it's been too long.

* Added API version annotations to endpoints (#125)
* Added New High Res Image Api Endpoint
* Added Tags to Datasources, Views
* Added Ability to run an Extract Refresh task (#159)
* Auto versioning enabled (#169)
* Download twbx/tdsx without the extract payload (#143, #144)
* New Sample to initialize a server (#95)
* Added ability to update connection information (#149)
* Added Ability to get a site by name (#153)
* Dates are now DateTime Objects (#102)
* Bugfixes (#162, #166)

## 0.3 (11 January 2017)

* Return DateTime objects instead of strings (#102)
* UserItem now is compatible with Pager (#107, #109)
* Deprecated site in favor of site_id (#97)
* Improved handling of large downloads (#105, #111)
* Added support for oAuth when publishing (#117)
* Added Testing against Py36 (#122, #123)
* Added Version Checking to use highest supported REST api version (#100)
* Added Infrastructure for throwing error if trying to do something that is not supported by REST api version (#124)
* Various Code Cleanup
* Added Documentation (#98)
* Improved Test Infrastructure (#91)

## 0.2 (02 November 2016)

* Added Initial Schedules Support (#48)
* Added Initial Create Group endpoint (#69)
* Added Connection Credentials for publishing datasources/workbooks (#80)
* Added Pager object for handling pagination results and sample (#72, #90)
* Added ServerInfo endpoint (#84)
* Deprecated `site` as a parameter to `TableauAuth` in favor of `site_id`
* Code Cleanup
* Bugfixes

## 0.1 (12 September 2016)

* Initial Release to the world
