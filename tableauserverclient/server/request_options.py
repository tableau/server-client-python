import sys
from typing import Optional

from typing_extensions import Self

from tableauserverclient.config import config
from tableauserverclient.models.property_decorators import property_is_int
import logging

from tableauserverclient.helpers.logging import logger


class RequestOptionsBase:
    # This method is used if server api version is below 3.7 (2020.1)
    def apply_query_params(self, url):
        try:
            params = self.get_query_params()
            params_list = [f"{k}={v}" for (k, v) in params.items()]

            logger.debug("Applying options to request: <%s(%s)>", self.__class__.__name__, ",".join(params_list))

            if "?" in url:
                url, existing_params = url.split("?")
                params_list.append(existing_params)

            return "{}?{}".format(url, "&".join(params_list))
        except NotImplementedError:
            raise


# If it wasn't a breaking change, I'd rename it to QueryOptions
"""
This class manages options can be used when querying content on the server
"""


class RequestOptions(RequestOptionsBase):
    def __init__(self, pagenumber=1, pagesize=None):
        self.pagenumber = pagenumber
        self.pagesize = pagesize or config.PAGE_SIZE
        self.sort = set()
        self.filter = set()
        # This is private until we expand all of our parsers to handle the extra fields
        self._all_fields = False

    def get_query_params(self) -> dict:
        params = {}
        if self.sort and len(self.sort) > 0:
            sort_options = (str(sort_item) for sort_item in self.sort)
            ordered_sort_options = sorted(sort_options)
            params["sort"] = ",".join(ordered_sort_options)
        if len(self.filter) > 0:
            filter_options = (str(filter_item) for filter_item in self.filter)
            ordered_filter_options = sorted(filter_options)
            params["filter"] = ",".join(ordered_filter_options)
        if self._all_fields:
            params["fields"] = "_all_"
        if self.pagenumber:
            params["pageNumber"] = self.pagenumber
        if self.pagesize:
            params["pageSize"] = self.pagesize
        return params

    def page_size(self, page_size):
        self.pagesize = page_size
        return self

    def page_number(self, page_number):
        self.pagenumber = page_number
        return self

    class Operator:
        Equals = "eq"
        GreaterThan = "gt"
        GreaterThanOrEqual = "gte"
        LessThan = "lt"
        LessThanOrEqual = "lte"
        In = "in"
        Has = "has"
        CaseInsensitiveEquals = "cieq"

    # These are fields in the REST API
    class Field:
        Args = "args"
        AuthenticationType = "authenticationType"
        Caption = "caption"
        Channel = "channel"
        CompletedAt = "completedAt"
        ConnectedWorkbookType = "connectedWorkbookType"
        ConnectionTo = "connectionTo"
        ConnectionType = "connectionType"
        ContentUrl = "contentUrl"
        CreatedAt = "createdAt"
        DatabaseName = "databaseName"
        DatabaseUserName = "databaseUserName"
        Description = "description"
        DisplayTabs = "displayTabs"
        DomainName = "domainName"
        DomainNickname = "domainNickname"
        FavoritesTotal = "favoritesTotal"
        Fields = "fields"
        FlowId = "flowId"
        FriendlyName = "friendlyName"
        HasAlert = "hasAlert"
        HasAlerts = "hasAlerts"
        HasEmbeddedPassword = "hasEmbeddedPassword"
        HasExtracts = "hasExtracts"
        HitsTotal = "hitsTotal"
        Id = "id"
        IsCertified = "isCertified"
        IsConnectable = "isConnectable"
        IsDefaultPort = "isDefaultPort"
        IsHierarchical = "isHierarchical"
        IsLocal = "isLocal"
        IsPublished = "isPublished"
        JobType = "jobType"
        LastLogin = "lastLogin"
        Luid = "luid"
        MinimumSiteRole = "minimumSiteRole"
        Name = "name"
        Notes = "notes"
        NotificationType = "notificationType"
        OwnerDomain = "ownerDomain"
        OwnerEmail = "ownerEmail"
        OwnerName = "ownerName"
        ParentProjectId = "parentProjectId"
        Priority = "priority"
        Progress = "progress"
        ProjectId = "projectId"
        ProjectName = "projectName"
        PublishSamples = "publishSamples"
        ServerName = "serverName"
        ServerPort = "serverPort"
        SheetCount = "sheetCount"
        SheetNumber = "sheetNumber"
        SheetType = "sheetType"
        SiteRole = "siteRole"
        Size = "size"
        StartedAt = "startedAt"
        Status = "status"
        SubscriptionsTotal = "subscriptionsTotal"
        Subtitle = "subtitle"
        TableName = "tableName"
        Tags = "tags"
        Title = "title"
        TopLevelProject = "topLevelProject"
        Type = "type"
        UpdatedAt = "updatedAt"
        UserCount = "userCount"
        UserId = "userId"
        ViewUrlName = "viewUrlName"
        WorkbookDescription = "workbookDescription"
        WorkbookName = "workbookName"

    class Direction:
        Desc = "desc"
        Asc = "asc"


"""
These options can be used by methods that are fetching data exported from a specific content item
"""


class _DataExportOptions(RequestOptionsBase):
    def __init__(self, maxage: int = -1):
        super().__init__()
        self.view_filters: list[tuple[str, str]] = []
        self.view_parameters: list[tuple[str, str]] = []
        self.max_age: Optional[int] = maxage
        """
        This setting will affect the contents of the workbook as they are exported.
        Valid language values are tableau-supported languages like de, es, en
        If no locale is specified, the default locale for that language will be used
        """
        self.language: Optional[str] = None

    @property
    def max_age(self) -> int:
        return self._max_age

    @max_age.setter
    @property_is_int(range=(0, 240), allowed=[-1])
    def max_age(self, value):
        self._max_age = value

    def get_query_params(self):
        params = {}
        if self.max_age != -1:
            params["maxAge"] = self.max_age
        if self.language:
            params["language"] = self.language

        self._append_view_filters(params)
        return params

    def vf(self, name: str, value: str) -> Self:
        """Apply a filter based on a column within the view.
        Note that when filtering on a boolean type field, the only valid values are 'true' and 'false'"""
        self.view_filters.append((name, value))
        return self

    def parameter(self, name: str, value: str) -> Self:
        """Apply a filter based on a parameter within the workbook.
        Note that when filtering on a boolean type field, the only valid values are 'true' and 'false'"""
        self.view_parameters.append((name, value))
        return self

    def _append_view_filters(self, params) -> None:
        for name, value in self.view_filters:
            params["vf_" + name] = value
        for name, value in self.view_parameters:
            params[name] = value


class _ImagePDFCommonExportOptions(_DataExportOptions):
    def __init__(self, maxage=-1, viz_height=None, viz_width=None):
        super().__init__(maxage=maxage)
        self.viz_height = viz_height
        self.viz_width = viz_width

    @property
    def viz_height(self):
        return self._viz_height

    @viz_height.setter
    @property_is_int(range=(0, sys.maxsize), allowed=(None,))
    def viz_height(self, value):
        self._viz_height = value

    @property
    def viz_width(self):
        return self._viz_width

    @viz_width.setter
    @property_is_int(range=(0, sys.maxsize), allowed=(None,))
    def viz_width(self, value):
        self._viz_width = value

    def get_query_params(self) -> dict:
        params = super().get_query_params()

        # XOR. Either both are None or both are not None.
        if (self.viz_height is None) ^ (self.viz_width is None):
            raise ValueError("viz_height and viz_width must be specified together")

        if self.viz_height is not None:
            params["vizHeight"] = self.viz_height

        if self.viz_width is not None:
            params["vizWidth"] = self.viz_width

        return params


class CSVRequestOptions(_DataExportOptions):
    extension = "csv"


class ExcelRequestOptions(_DataExportOptions):
    extension = "xlsx"


class ImageRequestOptions(_ImagePDFCommonExportOptions):
    extension = "png"

    # if 'high' isn't specified, the REST API endpoint returns an image with standard resolution
    class Resolution:
        High = "high"

    def __init__(self, imageresolution=None, maxage=-1, viz_height=None, viz_width=None):
        super().__init__(maxage=maxage, viz_height=viz_height, viz_width=viz_width)
        self.image_resolution = imageresolution

    def get_query_params(self):
        params = super().get_query_params()
        if self.image_resolution:
            params["resolution"] = self.image_resolution
        return params


class PDFRequestOptions(_ImagePDFCommonExportOptions):
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

    def __init__(self, page_type=None, orientation=None, maxage=-1, viz_height=None, viz_width=None):
        super().__init__(maxage=maxage, viz_height=viz_height, viz_width=viz_width)
        self.page_type = page_type
        self.orientation = orientation

    def get_query_params(self) -> dict:
        params = super().get_query_params()
        if self.page_type:
            params["type"] = self.page_type

        if self.orientation:
            params["orientation"] = self.orientation

        return params
