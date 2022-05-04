class JsonWebTokenAuth(object):
    def __init__(self, json_web_token, site_id=None):
        self.json_web_token = json_web_token
        self.site_id = site_id if site_id is not None else ""

    @property
    def credentials(self):
        return {
            "jsonWebToken": self.json_web_token,
        }

    def __repr__(self):
        return "<jwt={}>".format(self.json_web_token)
