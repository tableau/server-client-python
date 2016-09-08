class RequestOptions(object):
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
        if self.page_number:
            params.append('pageNumber={0}'.format(self.pagenumber))
        if self.page_size:
            params.append('pageSize={0}'.format(self.pagesize))
        if len(self.sort) > 0:
            params.append('sort={}'.format(','.join(str(sort_item) for sort_item in self.sort)))
        if len(self.filter) > 0:
            params.append('filter={}'.format(','.join(str(filter_item) for filter_item in self.filter)))

        return "{0}?{1}".format(url, '&'.join(params))
