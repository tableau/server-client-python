from ..models.property_decorators import property_is_int
import logging

logger = logging.getLogger("tableau.request_options")


class RequestOptionsBase(object):
    # This method is used if server api version is below 3.7 (2020.1)
    def apply_query_params(self, url):
        try:
            params = self.get_query_params()
            params_list = ["{}={}".format(k, v) for (k, v) in params.items()]

            logger.debug("Applying options to request: <%s(%s)>", self.__class__.__name__, ",".join(params_list))

            if "?" in url:
                url, existing_params = url.split("?")
                params_list.append(existing_params)

            return "{0}?{1}".format(url, "&".join(params_list))
        except NotImplementedError:
            raise

    def get_query_params(self):
        raise NotImplementedError()


class RequestOptions(RequestOptionsBase):
    class Operator:
        Equals = "eq"
        GreaterThan = "gt"
        GreaterThanOrEqual = "gte"
        LessThan = "lt"
        LessThanOrEqual = "lte"
        In = "in"
        Has = "has"

    class Field:
        Args = "args"
        CompletedAt = "completedAt"
        CreatedAt = "createdAt"
        DomainName = "domainName"
        DomainNickname = "domainNickname"
        HitsTotal = "hitsTotal"
        IsLocal = "isLocal"
        JobType = "jobType"
        LastLogin = "lastLogin"
        MinimumSiteRole = "minimumSiteRole"
        Name = "name"
        Notes = "notes"
        OwnerDomain = "ownerDomain"
        OwnerEmail = "ownerEmail"
        OwnerName = "ownerName"
        ParentProjectId = "parentProjectId"
        Progress = "progress"
        ProjectName = "projectName"
        PublishSamples = "publishSamples"
        SiteRole = "siteRole"
        StartedAt = "startedAt"
        Status = "status"
        Subtitle = "subtitle"
        Tags = "tags"
        Title = "title"
        TopLevelProject = "topLevelProject"
        Type = "type"
        UpdatedAt = "updatedAt"
        UserCount = "userCount"

    class Direction:
        Desc = "desc"
        Asc = "asc"

    def __init__(self, pagenumber=1, pagesize=100):
        self.pagenumber = pagenumber
        self.pagesize = pagesize
        self.sort = set()
        self.filter = set()

        # This is private until we expand all of our parsers to handle the extra fields
        self._all_fields = False

    def page_size(self, page_size):
        self.pagesize = page_size
        return self

    def page_number(self, page_number):
        self.pagenumber = page_number
        return self

    def get_query_params(self):
        params = {}
        if self.pagenumber:
            params["pageNumber"] = self.pagenumber
        if self.pagesize:
            params["pageSize"] = self.pagesize
        if len(self.sort) > 0:
            sort_options = (str(sort_item) for sort_item in self.sort)
            ordered_sort_options = sorted(sort_options)
            params["sort"] = ",".join(ordered_sort_options)
        if len(self.filter) > 0:
            filter_options = (str(filter_item) for filter_item in self.filter)
            ordered_filter_options = sorted(filter_options)
            params["filter"] = ",".join(ordered_filter_options)
        if self._all_fields:
            params["fields"] = "_all_"
        return params


class _FilterOptionsBase(RequestOptionsBase):
    """Provide a basic implementation of adding view filters to the url"""

    def __init__(self):
        self.view_filters = []

    def get_query_params(self):
        raise NotImplementedError()

    def vf(self, name, value):
        self.view_filters.append((name, value))
        return self

    def _append_view_filters(self, params):
        for name, value in self.view_filters:
            params["vf_" + name] = value


class CSVRequestOptions(_FilterOptionsBase):
    def __init__(self, maxage=-1):
        super(CSVRequestOptions, self).__init__()
        self.max_age = maxage

    @property
    def max_age(self):
        return self._max_age

    @max_age.setter
    @property_is_int(range=(0, 240), allowed=[-1])
    def max_age(self, value):
        self._max_age = value

    def get_query_params(self):
        params = {}
        if self.max_age != -1:
            params["maxAge"] = self.max_age

        self._append_view_filters(params)
        return params


class ExcelRequestOptions(RequestOptionsBase):
    def __init__(self, maxage: int = -1) -> None:
        super().__init__()
        self.max_age = maxage

    @property
    def max_age(self) -> int:
        return self._max_age

    @max_age.setter
    @property_is_int(range=(0, 240), allowed=[-1])
    def max_age(self, value: int) -> None:
        self._max_age = value

    def get_query_params(self):
        params = {}
        if self.max_age != -1:
            params["maxAge"] = self.max_age

        return params


class ImageRequestOptions(_FilterOptionsBase):
    # if 'high' isn't specified, the REST API endpoint returns an image with standard resolution
    class Resolution:
        High = "high"

    def __init__(self, imageresolution=None, maxage=-1):
        super(ImageRequestOptions, self).__init__()
        self.image_resolution = imageresolution
        self.max_age = maxage

    @property
    def max_age(self):
        return self._max_age

    @max_age.setter
    @property_is_int(range=(0, 240), allowed=[-1])
    def max_age(self, value):
        self._max_age = value

    def get_query_params(self):
        params = {}
        if self.image_resolution:
            params["resolution"] = self.image_resolution
        if self.max_age != -1:
            params["maxAge"] = self.max_age
        self._append_view_filters(params)
        return params


class PDFRequestOptions(_FilterOptionsBase):
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
        Unspecified = "unspecified"

    class Orientation:
        Portrait = "portrait"
        Landscape = "landscape"

    def __init__(self, page_type=None, orientation=None, maxage=-1):
        super(PDFRequestOptions, self).__init__()
        self.page_type = page_type
        self.orientation = orientation
        self.max_age = maxage

    @property
    def max_age(self):
        return self._max_age

    @max_age.setter
    @property_is_int(range=(0, 240), allowed=[-1])
    def max_age(self, value):
        self._max_age = value

    def get_query_params(self):
        params = {}
        if self.page_type:
            params["type"] = self.page_type

        if self.orientation:
            params["orientation"] = self.orientation

        if self.max_age != -1:
            params["maxAge"] = self.max_age

        self._append_view_filters(params)

        return params
