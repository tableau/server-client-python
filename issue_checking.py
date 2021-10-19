import tableauserverclient as TSC
from pprint import pprint


tableau_auth = TSC.TableauAuth('jfitzgerald', 'Rowan1S@sha2!VanShort')
server = TSC.Server('https://qa-near.tsi.lan')
server.add_http_options({'verify': False})

with server.auth.sign_in(tableau_auth):
    all_users, pagination_item = server.users.get()
    for user_item in all_users:
        pprint(vars(user_item))
        #print("User name: '{}' fullname: '{}', User email: '{}'".format(user_item.name,
        #   user_item.fullname,
        #  user_item.email))