class RequestOptionsBase(object):
    def apply_query_params(self, url):
        raise NotImplementedError()


class RequestOptions(RequestOptionsBase):
    class Operator:
        Equals = 'eq'
        GreaterThan = 'gt'
        GreaterThanOrEqual = 'gte'
        LessThan = 'lt'
        LessThanOrEqual = 'lte'
        In = 'in'

    class Field:
        CreatedAt = 'createdAt'
        LastLogin = 'lastLogin'
        Name = 'name'
        OwnerName = 'ownerName'
        SiteRole = 'siteRole'
        Tags = 'tags'
        UpdatedAt = 'updatedAt'

    class Direction:
        Desc = 'desc'
        Asc = 'asc'

    def __init__(self, pagenumber=1, pagesize=100):
        self.pagenumber = pagenumber
        self.pagesize = pagesize
        self.sort = set()
        self.filter = set()

    def page_size(self, page_size):
        self.pagesize = page_size
        return self

    def page_number(self, page_number):
        self.pagenumber = page_number
        return self

    def apply_query_params(self, url):
        params = []

        if '?' in url:
            url, existing_params = url.split('?')
            params.append(existing_params)

        if self.page_number:
            params.append('pageNumber={0}'.format(self.pagenumber))
        if self.page_size:
            params.append('pageSize={0}'.format(self.pagesize))
        if len(self.sort) > 0:
            sort_options = (str(sort_item) for sort_item in self.sort)
            ordered_sort_options = sorted(sort_options)
            params.append('sort={}'.format(','.join(ordered_sort_options)))
        if len(self.filter) > 0:
            filter_options = (str(filter_item) for filter_item in self.filter)
            ordered_filter_options = sorted(filter_options)
            params.append('filter={}'.format(','.join(ordered_filter_options)))

        return "{0}?{1}".format(url, '&'.join(params))


class ImageRequestOptions(RequestOptionsBase):
    # if 'high' isn't specified, the REST API endpoint returns an image with standard resolution
    class Resolution:
        High = 'high'

    def __init__(self, imageresolution=None):
        self.image_resolution = imageresolution

    def apply_query_params(self, url):
        params = []
        if self.image_resolution:
            params.append('resolution={0}'.format(self.image_resolution))

        return "{0}?{1}".format(url, '&'.join(params))


class PDFRequestOptions(RequestOptionsBase):
    # if 'high' isn't specified, the REST API endpoint returns an image with standard resolution
    class PageType:
        A3 = "a3"
        A4 = "a4"
        A5 = "a5"
        B4 = "b4"
        B5 = "b5"
        Executive = "executive"
        Folio = "folio"
        Ledger = "ledger"
        Legal = "legal"
        Letter = "letter"
        Note = "note"
        Quarto = "quarto"
        Tabloid = "tabloid"

    class Orientation:
        Portrait = "portrait"
        Landscape = "landscape"

    def __init__(self, page_type=None, orientation=None):
        self.page_type = page_type
        self.orientation = orientation

    def apply_query_params(self, url):
        params = []
        if self.page_type:
            params.append('type={0}'.format(self.page_type))

        if self.orientation:
            params.append('orientation={0}'.format(self.orientation))

        return "{0}?{1}".format(url, '&'.join(params))
