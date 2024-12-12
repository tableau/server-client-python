# This sample verifies that tableau server client is installed
# and you can run it. It also shows the version of the client.

import logging
import tableauserverclient as TSC


logger = logging.getLogger("Sample")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


server = TSC.Server("Fake-Server-Url", use_server_version=False)
print("Client details:")
logger.info(server.server_address)
logger.debug(TSC.server.endpoint.Endpoint.set_user_agent({}))
