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

The `SERVER_URL` is the URL of the Tableau server without subpaths. For local Tableau servers, in the form of: `https://www.MY_SERVER.com`. For Tableau Online, `https://10ax.online..tableau.com/`.

`SITENAME` is same as the `contentURL`, or site subpath, of your full site URL. This parameter can be omitted when signing in to the Default site of a locally installed Tableau server.

Optionally, you can override the Tableau API version by adding `server.version = '<VERSION_NUMBER>'` before the `auth.signin` call. 

The TSC library signs you out of Tableau Server when you exit out of the `with` block.

<div class="alert alert-info">
    <b>Note:</b> When you sign in, the TSC library manages the authenticated session for you, however the validity of the underlying 
    credentials token is limited by the maximum session length set on your Tableau Server (2 hours by default).
</div>

An option to using a `with` block is to call the `Auth.sign_in` and `Auth.sign_out` functions explicitly.

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```
