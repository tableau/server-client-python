from .request_options_base import RequestOptionsBase


class ImageRequestOptions(RequestOptionsBase):
    class Resolution:
        High = 'high'

    def __init__(self, imageresolution=None):
        self.imageresolution = imageresolution

    def image_resolution(self, imageresolution):
        self.imageresolution = imageresolution
        return self

    def apply_query_params(self, url):
        params = []
        if self.image_resolution:
            params.append('resolution={0}'.format(self.imageresolution))

        return "{0}?{1}".format(url, '&'.join(params))
