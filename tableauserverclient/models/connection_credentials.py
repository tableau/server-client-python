class ConnectionCredentials(object):
    def __init__(self, name, password, embed=True):
        self.password = password
        self.embed = embed
        self.name = name
