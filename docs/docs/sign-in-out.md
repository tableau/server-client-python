---
title: Sign In and Out
layout: docs
---

To sign in and out of Tableau Server, call the `Auth.sign_in` and `Auth.sign_out` functions like so:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```

This code does the following things:

* Creates an authentication object that stores your user name and password.
* Creates a server object that stores the URL of your server.
* Calls the `sign_in` function to pass the authentication object to the server object.
* Call the `sign_out` function.


Alternatively, for short programs, consider using a `with` block:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    # Do awesome things here!
```

When you use a `with` block, the TSC library signs you out of Tableau Server when you exit out of the `with` block.
