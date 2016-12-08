import sys
import tableauserverclient as TSC

server, username, password, site = sys.argv[1:]


authz = TSC.TableauAuth(username, password)
server = TSC.Server(server)

server.auth.sign_in(authz)

for w in TSC.Pager(server.workbooks):
    print(w)

for u in TSC.Pager(server.users):
    print(u)

for p in TSC.Pager(server.projects):
    print(p)

for h in TSC.Pager(server.schedules):
    print(h)

server.auth.sign_out()
