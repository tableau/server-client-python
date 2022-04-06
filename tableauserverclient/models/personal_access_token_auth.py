class PersonalAccessTokenAuth(object):
    def __init__(self, token_name, personal_access_token, site_id=None):
        self.token_name = token_name
        self.personal_access_token = personal_access_token
        self.site_id = site_id if site_id is not None else ""
        # Personal Access Tokens doesn't support impersonation.
        self.user_id_to_impersonate = None

    @property
    def credentials(self):
        return {
            "personalAccessTokenName": self.token_name,
            "personalAccessTokenSecret": self.personal_access_token,
        }

    def __repr__(self):
        return "<PersonalAccessToken name={} token={}>".format(self.token_name, self.personal_access_token)
