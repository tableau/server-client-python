####
# Getting Started: Optional Part 4
# This script demonstrates how to connect to Tableau Cloud/Server through a proxy.
# To make it easy to run, it doesn't take any arguments - you need to edit the code with your info
####

import getpass
import tableauserverclient as TSC


def main():
    # 1 - replace with your server url
    server_url = "https://10ax.online.tableau.com"

    # 2 - add your proxy details to the server connection info
    # You can also set any of the parameters of the requests.send() call shown here: stream, cert, or timeout
    # https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests
    use_ssl = True
    my_proxies = {
        'http': 'http://10.10.1.10:3128',
        'https': 'http://10.10.1.10:1080',
    }
    server = TSC.Server(server_url, use_server_version=True, http_options={"verify": use_ssl, "proxies": my_proxies})

    print("Connected to {}".format(server.server_info.baseurl))

    # 3 - replace with your site name exactly as it looks in a url
    # e.g https://my-server/#/this-is-your-site-url-name/
    site_url_name = ""  # leave empty if there is no site name in the url (you are on the default site)

    # 4
    username = "your-username-here"
    password = getpass.getpass("Your password:")  # so you don't save it in this file
    tableau_auth = TSC.TableauAuth(username, password, site_id=site_url_name)

    # OR instead of username+password, use a Personal Access Token (PAT) (required by Tableau Cloud)
    # by commenting out the three lines above, and uncommenting these three lines
    # token_name = "your-token-name"
    # token_value = "your-token-value-long-random-string"
    # tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_url_name)

    with server.auth.sign_in(tableau_auth):
        projects, pagination = server.projects.get()
        if projects:
            print("{} projects".format(pagination.total_available))
            for project in projects:
                print(project.name)

        jobs, pagination = server.jobs.get()
        if jobs:
            print("{} jobs".format(pagination.total_available))
            print(jobs[0])


if __name__ == "__main__":
    main()
