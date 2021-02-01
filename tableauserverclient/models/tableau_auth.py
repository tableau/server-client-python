from typing import Dict


class TableauAuth(object):
    def __init__(self, username: str, password: str, site=None, site_id: str = '', user_id_to_impersonate: str = None):
        if site is not None:
            import warnings
            warnings.warn('TableauAuth(...site=""...) is deprecated, '
                          'please use TableauAuth(...site_id=""...) instead.',
                          DeprecationWarning)
            site_id = site

        self.user_id_to_impersonate = user_id_to_impersonate
        self.password = password
        self.site_id = site_id
        self.username = username

    @property
    def site(self) -> str:
        import warnings
        warnings.warn('TableauAuth.site is deprecated, use TableauAuth.site_id instead.',
                      DeprecationWarning)
        return self.site_id

    @site.setter
    def site(self, value: str):
        import warnings
        warnings.warn('TableauAuth.site is deprecated, use TableauAuth.site_id instead.',
                      DeprecationWarning)
        self.site_id = value

    @property
    def credentials(self) -> Dict[str, str]:
        return {'name': self.username, 'password': self.password}
