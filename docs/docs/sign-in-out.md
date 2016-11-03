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

<div class="alert alert-info">
    <b>Note:</b> When you sign in, the TSC library manages the authenticated session for you, however it is still
    limited by the maximum session length (of four hours) on Tableau Server.
</div>


Alternatively, for short programs, consider using a `with` block:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    # Do awesome things here!
```

The TSC library signs you out of Tableau Server when you exit out of the `with` block.
