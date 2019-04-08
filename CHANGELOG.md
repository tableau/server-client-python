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
