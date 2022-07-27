---
title: Sign In and Out
layout: docs
---

The first step to using the TSC library is to sign in to your Tableau Server (or Tableau Online). This page explains how to sign in, sign out, and switch sites, with examples for both Tableau Server and Tableau Online.

* TOC
{:toc}

## Sign In

Signing in can be done two different ways:

* Personal Access Tokens - In most cases this is the preferred method because it improves security by avoiding the need to use or store passwords directly. Access tokens also expire by default if not used after 15 consecutive days. This option is available for Tableau Server 2019.4 and newer. Refer to [Personal Access Tokens](https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm) for more details.
* Username and Password - Direct sign in with account username and password.

Examples showing both of these cases are included below.

**Note:** When you sign in, the TSC library manages the authenticated session for you. However, the validity of the underlying credentials token is limited by the maximum session length set on your Tableau Server (2 hours by default).

### Sign in with Personal Access Token

To sign in to Tableau Server or Tableau Online with a personal access token, you'll need the following values:

Name | Description
:--- | :---
TOKEN_NAME | The personal access token name (from the My Account settings page)
TOKEN_VALUE | The personal access token value (from the My Account settings page)
**Tableau Server** |
SITENAME | The Tableau Server site you are authenticating with. For example in the site URL http://MyServer/#/site/MarketingTeam/projects, the site name is MarketingTeam. In the REST API documentation, this field is also referred to as contentUrl. This value can be omitted to connect with the Default site on the server.
SERVER_URL | The Tableau Server you are authenticating with. If your server has SSL enabled, this should be an HTTPS link.
**Tableau Online** |
SITENAME | The Tableau Online site you are authenticating with. For example in the site URL https://10ay.online.tableau.com/#/site/umbrellacorp816664/workbooks, the site name is umbrellacorp816664. In the REST API documentation, this field is also referred to as contentUrl. This value is always required when connecting to Tableau Online.
SERVER_URL | The Tableau Online instance you are authenticating with. In the example above the server URL would be https://10ay.online.tableau.com. This will always be an an HTTPS link.

This example illustrates using the above values to sign in with a personal access token, do some operations, and then sign out:

```py
import tableauserverclient as TSC

tableau_auth = TSC.PersonalAccessTokenAuth('TOKEN_NAME', 'TOKEN_VALUE', 'SITENAME')
server = TSC.Server('https://SERVER_URL', use_server_version=True)
server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```

### Sign in with Username and Password

To sign in to Tableau Server or Tableau Online with a username and password, you'll need the following values:

Name | Description
:--- | :---
USERNAME | The user name
PASSWORD | The user password
SITENAME | The same as described in the previous section
SERVER_URL | The same as described in the previous section

This example illustrates using the above values to sign in with a username and password, do some operations, and then sign out:

```py
import tableauserverclient as TSC

tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', 'SITENAME')
server = TSC.Server('https://SERVER_URL', use_server_version=True)
server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```

### Handling SSL certificates for Tableau Server

If you're connecting to a Tableau Server instance that uses self-signed or non-public SSL certificates, you may need to provide those as part of the sign in process. An example of this could be an on-premise Tableau Server that is using internally-generated SSL certificates. You may see an error like `SSL: CERTIFICATE_VERIFY_FAILED` if you connect with a Tableau Server but don't have the SSL certificates configured correctly.

The solution here is to call `server.add_http_options()` and include the local path containing the SSL certificate file:

```py
import tableauserverclient as TSC

tableau_auth = TSC.PersonalAccessTokenAuth('TOKEN_NAME', 'TOKEN_VALUE', 'SITENAME')
server = TSC.Server('https://SERVER_URL', use_server_version=True)
server.add_http_options({'verify': '/path/to/certfile.pem'})
server.auth.sign_in(tableau_auth)

# Do awesome things here!

server.auth.sign_out()
```

The TSC library uses the Python Requests library under the hood, so you can learn more about the `verify` option on the [Python Requests advanced usage](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification) documentation.

You can also set `verify` to `False` to disable the SSL certificate verification step, but this is only useful for development and _should not be used for real production work_.

### 405000 Method Not Allowed Response

In some cases, you may find that sign in fails with a 405 message:
```
405000: Method Not Allowed
    The HTTP method 'GET' is not supported for the given resource
```

The most likely cause of this is signing in to a Tableau Server using the HTTP address which the server redirects to a secure HTTPS address. However, during the redirect the POST request turns into a GET request which is then considered an invalid method for the login entrypoint. (For security reasons, the server is following the standards correctly in this case).

The solution is to avoid the redirect by using the HTTPS URL for the site. For example, instead of:
```py
server = TSC.Server('http://SERVER_URL')
```

Switch to the HTTPS (SSL) URL instead:
```py
server = TSC.Server('https://SERVER_URL')
```

## Sign Out

Signing out cleans up the current session and invalidates the authentication token being held by the TSC library.

As shown in the examples above, the sign out call is simply:

```py
server.auth.sign_out()
```

## Simplify by using Python with block

The sign in/out flow can be simplified (and handled in a more Python way) by using the built-in support for the `with` block. After the block execution completes, the sign out is called automatically.

For example:

```py
import tableauserverclient as TSC

tableau_auth = TSC.PersonalAccessTokenAuth('TOKEN_NAME', 'TOKEN_VALUE', 'SITENAME')
server = TSC.Server('https://SERVER_URL')

with server.auth.sign_in(tableau_auth):
    all_wb, pagination_item = server.workbooks.get()
    print("\nThere are {} workbooks on site: ".format(pagination_item.total_available))
    for wb in all_wb:
        print(wb.id, wb.name)
```

All of the samples provided in TSC library use this technique.

## Switch Site

Tableau Server has a feature which enables switching to another site without having to authenticate again. (The user must have access permissions for the new site as well.)

**Note:** This method is not available on Tableau Online.

The following example will switch the authenticated user to the NEW_SITENAME site on the same server:

```py
# assume we already have an authenticated server object

server.auth.switch_site('NEW_SITENAME')
```
