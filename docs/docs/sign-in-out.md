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

If a self-signed certificate is used, certificate verification can be disabled using ```add_http_options```:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')
server.add_http_options({'verify': False})
```

However, each subsequent REST API call will print an ```InsecureRequestWarning```:
```
C:\Program Files (x86)\Python35-32\lib\site-packages\requests\packages\urllib3\connectionpool.py:838: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/security.html
InsecureRequestWarning)
```

These warnings can be disabled with the following line:
```py
requests.packages.urllib3.disable_warnings(InsecureRequestWa‌​rning)
```

Instead of disabling warnings or certificate verification, we recommend using a Certificate Authority (CA) signed certificate. [Let's Encrypt](https://letsencrypt.org/) is a free, automated, and open Certificate Authority that can be used, although please note that no official Windows client currently exists.
