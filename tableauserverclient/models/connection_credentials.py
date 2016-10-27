class ConnectionCredentials(object):
	"""Connection Credentials for Workbooks and Datasources publish request

	Consider removing this object and other variables holding secrets 
	as soon as poobible after use to avoid them hanging around in memory.

	"""
    def __init__(self, name, password, embed=True):
       	self.name = name
        self.password = password
        self.embed = embed
 