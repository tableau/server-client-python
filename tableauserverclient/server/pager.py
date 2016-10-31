from . import RequestOptions


class Pager(object):
    """
    Generator that takes an endpoint with `.get` and lazily loads items from Server.
    Supports all `RequestOptions` including starting on any page.
    """

    def __init__(self, endpoint, request_opts=None):
        self._endpoint = endpoint.get
        self._options = request_opts

        # If we have options we could be starting on any page, backfill the count
        if self._options:
            self._count = ((self._options.pagenumber - 1) * self._options.pagesize)
        else:
            self._count = 0

    def __iter__(self):
        # Fetch the first page
        current_item_list, last_pagination_item = self._endpoint(self._options)

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

    def _load_next_page(self, last_pagination_item):
        next_page = last_pagination_item.page_number + 1
        opts = RequestOptions(pagenumber=next_page, pagesize=last_pagination_item.page_size)
        if self._options is not None:
            opts.sort, opts.filter = self._options.sort, self._options.filter
        current_item_list, last_pagination_item = self._endpoint(opts)
        return current_item_list, last_pagination_item
