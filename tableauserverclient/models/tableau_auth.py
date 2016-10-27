class TableauAuth(object):
    def __init__(self, username, password, site='', user_id_to_impersonate=None):
        self.user_id_to_impersonate = user_id_to_impersonate
        self.password = password
        self.site = site
        self.username = username
