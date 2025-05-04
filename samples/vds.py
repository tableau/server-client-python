####
# Getting Started Part Three of Three
# This script demonstrates all the different types of 'content' a server contains
#
# To make it easy to run, it doesn't take any arguments - you need to edit the code with your info
####

from typing import Dict, Any
from rich import print

import getpass
import tableauserverclient as TSC


def main():
    # 1 - replace with your server domain: stop at the slash
    server_url = ""

    # 2 - optional - change to false **for testing only** if you get a certificate error
    use_ssl = True

    server = TSC.Server(server_url, use_server_version=True, http_options={"verify": use_ssl})
    print(f"Connected to {server.server_info.baseurl}")

    # 3 - replace with your site name exactly as it looks in the url
    # e.g https://my-server/#/site/this-is-your-site-url-name/not-this-part
    site_url_name = ""  # leave empty if there is no site name in the url (you are on the default site)

    # 4 - replace with your username.
    # REMEMBER: if you are using Tableau Online, your username is the entire email address
    username = ""
    password = "" #getpass.getpass("Enter your password:")  # so you don't save it in this file
    tableau_auth = TSC.TableauAuth(username, password, site_id=site_url_name)

    # OR instead of username+password, use a Personal Access Token (PAT) (required by Tableau Cloud)
    # token_name = "your-token-name"
    # token_value = "your-token-value-long-random-string"
    # tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_url_name)

    with server.auth.sign_in(tableau_auth):
        # schema - may be used to understand the schema of the VDS API
        print(server.vizql.VizQL_Schema)
        # query
        query_dict: Dict[str, Any] = {
            "fields": [{"fieldCaption": "School Code"}],
            "filters": [
                {
                    "field": {"fieldCaption": "Enrollment (K-12)", "function": "SUM"},
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "MIN",
                    "min": 500
                }
            ]
        }
        datasource_id = "e4d75fd4-af1c-4fb8-a049-058e3fef57bc"
        
        # query metadata
        vds_metadata = server.vizql.query_vds_metadata(
            datasource_id=datasource_id
        )
        if vds_metadata:
            print(vds_metadata)
            
        # query data
        vds_data = server.vizql.query_vds_data(
            query=query_dict,
            datasource_id=datasource_id
        )
        if vds_data:
            print(vds_data)
if __name__ == "__main__":
    main()
