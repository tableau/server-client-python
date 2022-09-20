# This sample verifies that tableau server client is installed
# and you can run it. It also shows the version of the client.

import tableauserverclient as TSC

server = TSC.Server("Fake-Server-Url", use_server_version=False)
print("Client details:")
print(TSC.server.endpoint.Endpoint._make_common_headers("fake-token", "any-content"))
