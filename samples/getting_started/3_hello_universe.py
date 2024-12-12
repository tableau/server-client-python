####
# Getting Started Part Three of Three
# This script demonstrates all the different types of 'content' a server contains
#
# To make it easy to run, it doesn't take any arguments - you need to edit the code with your info
####

import getpass
import tableauserverclient as TSC


def main():
    # 1 - replace with your server url
    server_url = "https://10ax.online.tableau.com"

    # 2 - change to false **for testing only** if you get a certificate error
    use_ssl = True
    server = TSC.Server(server_url, use_server_version=True, http_options={"verify": use_ssl})

    print(f"Connected to {server.server_info.baseurl}")

    # 3 - replace with your site name exactly as it looks in a url
    # e.g https://my-server/#/this-is-your-site-url-name/
    site_url_name = ""  # leave empty if there is no site name in the url (you are on the default site)

    # 4
    username = "your-username-here"
    password = getpass.getpass("Your password:")  # so you don't save it in this file
    tableau_auth = TSC.TableauAuth(username, password, site_id=site_url_name)

    # OR instead of username+password, use a Personal Access Token (PAT) (required by Tableau Cloud)
    # token_name = "your-token-name"
    # token_value = "your-token-value-long-random-string"
    # tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_url_name)

    with server.auth.sign_in(tableau_auth):
        projects, pagination = server.projects.get()
        if projects:
            print(f"{pagination.total_available} projects")
            for project in projects:
                print(project.name)

        workbooks, pagination = server.datasources.get()
        if workbooks:
            print(f"{pagination.total_available} workbooks")
            print(workbooks[0])

        views, pagination = server.views.get()
        if views:
            print(f"{pagination.total_available} views")
            print(views[0])

        datasources, pagination = server.datasources.get()
        if datasources:
            print(f"{pagination.total_available} datasources")
            print(datasources[0])

        # I think all these other content types can go to a hello_universe script
        # data alert, dqw, flow, ... do any of these require any add-ons?
        jobs, pagination = server.jobs.get()
        if jobs:
            print(f"{pagination.total_available} jobs")
            print(jobs[0])

        schedules, pagination = server.schedules.get()
        if schedules:
            print(f"{pagination.total_available} schedules")
            print(schedules[0])

        tasks, pagination = server.tasks.get()
        if tasks:
            print(f"{pagination.total_available} tasks")
            print(tasks[0])

        webhooks, pagination = server.webhooks.get()
        if webhooks:
            print(f"{pagination.total_available} webhooks")
            print(webhooks[0])

        users, pagination = server.users.get()
        if users:
            print(f"{pagination.total_available} users")
            print(users[0])

        groups, pagination = server.groups.get()
        if groups:
            print(f"{pagination.total_available} groups")
            print(groups[0])


if __name__ == "__main__":
    main()
