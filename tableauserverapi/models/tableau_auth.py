class TableauAuth(object):
    def __init__(self, username, password, site='', impersonate_id=None):
        self.impersonate_id = impersonate_id
        self.password = password
        self.site = site
        self.username = username
