---
title: Sign In and Out
layout: docs
---

To sign in and out of Tableau Server, call the server's `.auth.signin` method in a`with` block.

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', `SITENAME`)
server = TSC.Server('https://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    # Do awesome things here!
```

`SERVER_URL` is the URL of your Tableau server without subpaths. For local Tableau servers, an example would be:      `https://www.MY_SERVER.com`. For Tableau Online, an example would be: `https://10ax.online.tableau.com/`.

`SITENAME` is the subpath of your full site URL (also called `contentURL` in the REST API). `MYSITE` would be the site name of `https://10ax.online.tableau.com/MYSITE`. This parameter can be omitted when signing in to the Default site of an in premise Tableau server.

Optionally, you can override the version of Tableau API you are authorizing against by adding `server.version = '<VERSION_NUMBER>'` before the `auth.signin` call. 

The TSC library signs you out of Tableau Server when you exit out of the `with` block.

<div class="alert alert-info">
    <b>Note:</b> When you sign in, the TSC library manages the authenticated session for you, however the validity of the underlying 
    credentials token is limited by the maximum session length set on your Tableau Server (2 hours by default).
</div>

An alternative to using a `with` block is to call the `Auth.sign_in` and `Auth.sign_out` functions explicitly.

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```
