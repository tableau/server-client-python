## 0.5 (11 Sept 2017)

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
