####
# Getting started Part Two of Three
# This script demonstrates how to use the Tableau Server Client to sign in and view content. 
# It assumes that you have already got a Tableau site and can visit it in a browser
#
# To make it easy to run, it doesn't take any arguments - you need to edit the code with your info
####

import getpass
import tableauserverclient as TSC


# 0 - launch your Tableau site in a web browser and look at the url to set the values below
def main():
    # 1 - replace with your server domain: stop at the slash
    server_url = "https://10ax.online.tableau.com"

    # 2 - optional - change to false **for testing only** if you get a certificate error
    use_ssl = True

    server = TSC.Server(server_url, use_server_version=True, http_options={"verify": use_ssl})
    print("Connected to {}".format(server.server_info.baseurl))

    # 3 - replace with your site name exactly as it looks in the url
    # e.g https://my-server/#/site/this-is-your-site-url-name/not-this-part
    site_url_name = ""  # leave empty if there is no site name in the url (you are on the default site)

    # 4 - login
    # a) replace with your Personal Access Token values from the page 'My Account' on your Tableau site
    token_name = "your-token-name"
    token_value = "your-token-value-long-random-string"
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_url_name)

    # OR b) to sign in with a username and password, uncomment this section and remove the three lines above
    # REMEMBER: if you are using Tableau Online, you cannot log in with username+password.
    """
    username = "your-username-here"
    password = getpass.getpass("Your password:")  # so you don't save it in this file
    tableau_auth = TSC.TableauAuth(username, password, site_id=site_url_name)
    """
    
    # OR c) to sign in with a JWT, uncomment this section and remove the three lines for PAT above
    # You must have configured a Connected App and generated a JWT before you use this method.
    """
    jwt = "long-generated-string-that-encodes-information"
    tableau_auth = TSC.JWTAuth(jwt, site_id=site_url_name)
    """    

    with server.auth.sign_in(tableau_auth):
        projects, pagination = server.projects.get()
        if projects:
            print("{} projects".format(pagination.total_available))
            project = projects[0]
            print(project.name)

        print("Done")


if __name__ == "__main__":
    main()
