####
# Getting started Part Two of Three
# This script demonstrates how to use the Tableau Server Client to
# view the content on an existing site on Tableau Server/Online
# It assumes that you have already got a site and can visit it in a browser
#
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
    print(f"Connected to {server.server_info.baseurl}")

    # 3 - replace with your site name exactly as it looks in the url
    # e.g https://my-server/#/site/this-is-your-site-url-name/not-this-part
    site_url_name = ""  # leave empty if there is no site name in the url (you are on the default site)

    # 4 - replace with your username.
    # REMEMBER: if you are using Tableau Online, your username is the entire email address
    username = "your-username-here"
    password = getpass.getpass("Your password:")  # so you don't save it in this file
    tableau_auth = TSC.TableauAuth(username, password, site_id=site_url_name)

    # OR instead of username+password, uncomment this section to use a Personal Access Token
    # token_name = "your-token-name"
    # token_value = "your-token-value-long-random-string"
    # tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_url_name)

    with server.auth.sign_in(tableau_auth):
        projects, pagination = server.projects.get()
        if projects:
            print(f"{pagination.total_available} projects")
            project = projects[0]
            print(project.name)

        print("Done")


if __name__ == "__main__":
    main()
