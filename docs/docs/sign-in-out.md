---
title: Sign In and Out
layout: docs
---

The simplest way to sign in to Tableau Server is to use the following code:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    # Do awesome things here!
```

This code does the following things:

* Creates an authentication object that stores your user name and password.
* Creates a server object that stores the URL of your server.
* Calls the `sign_in` function to pass the authentication object to the server object.

You might also notice that this example uses a `with` block to sign in. When you use a `with` block, the TSC library
manages the authentication token for the entirety of the session until you exit out of the `with` block. This is a best
practice to ensure that you do not forget to sign out of Tableau Server.

However, you can also call the `sign_in` and `sign_out` functions directly like so:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```
