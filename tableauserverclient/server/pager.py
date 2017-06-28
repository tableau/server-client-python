from . import RequestOptions
from . import Sort


class Pager(object):
    """
    Generator that takes an endpoint with `.get` and lazily loads items from Server.
    Supports all `RequestOptions` including starting on any page.
    """

    def __init__(self, endpoint, request_opts=None):
        if hasattr(endpoint, 'get'):
            # The simpliest case is to take an Endpoint and call its get
            self._endpoint = endpoint.get
        else:
            # but if they pass a callable then use that instead (used internally)
            self._endpoint = endpoint

        self._options = request_opts
        self._length = None

        # If we have options we could be starting on any page, backfill the count
        if self._options:
            self._count = ((self._options.pagenumber - 1) * self._options.pagesize)
        else:
            self._count = 0
            self._options = RequestOptions()

        # Pager assumes deterministic order but solr doesn't guarantee sort order unless specified
        if not self._options.sort:
            self._options.sort.add(Sort(RequestOptions.Field.Name, RequestOptions.Direction.Asc))

    def __iter__(self):
        # Fetch the first page
        current_item_list, last_pagination_item = self._endpoint(self._options)
        self._length = int(last_pagination_item.total_available)

        # Get the rest on demand as a generator
        while self._count < last_pagination_item.total_available:
            if len(current_item_list) == 0:
                current_item_list, last_pagination_item = self._load_next_page(last_pagination_item)

            try:
                yield current_item_list.pop(0)
                self._count += 1

            except IndexError:
                # The total count on Server changed while fetching exit gracefully
                raise StopIteration

    # def __len__(self):
    #     if not self._length:
    #         # We have no length yet, so get the first page and then we'll know total size
    #         # TODO This isn't needed if we convert to list
    #         next(self.__iter__())
    #         return self._length
    #     return self._length

    def _load_next_page(self, last_pagination_item):
        next_page = last_pagination_item.page_number + 1
        opts = RequestOptions(pagenumber=next_page, pagesize=last_pagination_item.page_size)
        if self._options is not None:
            opts.sort, opts.filter = self._options.sort, self._options.filter
        current_item_list, last_pagination_item = self._endpoint(opts)
        return current_item_list, last_pagination_item
