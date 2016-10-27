class TableauAuth(object):
	"""Authentication attributes for signin request

	Consider removing this object and other variables holding secrets 
	as soon as possible after use to avoid them hanging around in memory.

	"""
	def __init__(self, username, password, site='', user_id_to_impersonate=None):
        self.username = username
        self.password = password
        self.site = site
        self.user_id_to_impersonate = user_id_to_impersonate
