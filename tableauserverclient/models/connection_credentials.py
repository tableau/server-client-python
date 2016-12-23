from .property_decorators import property_is_boolean


class ConnectionCredentials(object):
    """Connection Credentials for Workbooks and Datasources publish request.

    Consider removing this object and other variables holding secrets
    as soon as possible after use to avoid them hanging around in memory.

    """

    def __init__(self, name, password, embed=True, oauth=False):
        self.name = name
        self.password = password
        self.embed = embed
        self.oauth = oauth

    @property
    def embed(self):
        return self._embed

    @embed.setter
    @property_is_boolean
    def embed(self, value):
        self._embed = value

    @property
    def oauth(self):
        return self._oauth

    @oauth.setter
    @property_is_boolean
    def oauth(self, value):
        self._oauth = value
