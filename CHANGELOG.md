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
