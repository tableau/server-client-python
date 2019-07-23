class PersonalAccessTokenAuth(object):
    def __init__(self, token_name, personal_access_token, site_id=''):
        self.token_name = token_name
        self.personal_access_token = personal_access_token
        self.site_id = site_id
        # Personal Access Tokens doesn't support impersonation.
        self.user_id_to_impersonate = None

    def credentials(self):
        return { 'clientId': self.token_name, 'personalAccessToken': self.personal_access_token }
