class Credentials:
    def __init__(self, site_id=None, user_id_to_impersonate=None):
        self.site_id = site_id or ""
        self.user_id_to_impersonate = user_id_to_impersonate or None

    @property
    def credentials(self):
        credentials = "Credentials can be username/password, Personal Access Token, or JWT"
        +"This method returns values to set as an attribute on the credentials element of the request"

    def __repr__(self):
        return "All Credentials types must have a debug display that does not print secrets"


def deprecate_site_attribute():
    import warnings

    warnings.warn(
        "TableauAuth(..., site=...) is deprecated, " "please use TableauAuth(..., site_id=...) instead.",
        DeprecationWarning,
    )


# The traditional auth type: username/password
class TableauAuth(Credentials):
    def __init__(self, username, password, site=None, site_id=None, user_id_to_impersonate=None):
        if site is not None:
            deprecate_site_attribute()
            site_id = site
        super().__init__(site_id, user_id_to_impersonate)
        if password is None:
            raise TabError("Must provide a password when using traditional authentication")
        self.password = password
        self.username = username

    @property
    def credentials(self):
        return {"name": self.username, "password": self.password}

    def __repr__(self):
        return "<Credentials username={} password={}>".format(self.username, "<redacted>")

    @property
    def site(self):
        deprecate_site_attribute()
        return self.site_id

    @site.setter
    def site(self, value):
        deprecate_site_attribute()
        self.site_id = value


class PersonalAccessTokenAuth(Credentials):
    def __init__(self, token_name, personal_access_token, site_id=None):
        super().__init__(site_id=site_id)
        self.token_name = token_name
        self.personal_access_token = personal_access_token

    @property
    def credentials(self):
        return {
            "personalAccessTokenName": self.token_name,
            "personalAccessTokenSecret": self.personal_access_token,
        }

    def __repr__(self):
        return "<PersonalAccessToken name={} token={}>(site={})".format(
            self.token_name, self.personal_access_token[:2] + "...", self.site_id
        )
