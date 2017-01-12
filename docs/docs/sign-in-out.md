---
title: Sign In and Out
layout: docs
---
## Signing in and out
To sign in and out of Tableau Server, call the `Auth.sign_in` and `Auth.sign_out` functions like so:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```

Alternatively, for short programs, consider using a `with` block:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    # Do awesome things here!

# No need to call auth.sign_out() as the Auth context manager will handle that on exiting the with block
```

<div class="alert alert-info">
    <b>Note:</b> When you sign in, the TSC library manages the authenticated session for you, however it is still
    limited by the maximum session length (of four hours) on Tableau Server.
</div>

### Disabling certificate verification and warnings
Certain environments may throw errors related to SSL configuration, such as self-signed certificates or expired certificates. These errors can be avoided by disabling certificate verification with ```add_http_options```:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
server = TSC.Server('http://SERVER_URL')
server.add_http_options({'verify': False})
```

However, each subsequent REST API call will print an ```InsecureRequestWarning```:
```
InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/security.html
InsecureRequestWarning)
```

These warnings can be disabled by adding the following lines to your script:
```py
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
```

### A better way to avoid certificate warnings
Instead of disabling warnings and certificate verification to workaround issues with untrusted certificates, the best practice is to use a certificate signed by a Certificate Authority.

If you have the ability to do so, we recommend the following Certificate Authorities:
* [GlobalSign](https://www.globalsign.com/en/)
* [Let's Encrypt](https://letsencrypt.org/) - a free, automated, and open Certificate Authority
* [SSL.com](https://www.ssl.com/)
