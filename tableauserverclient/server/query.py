from .request_options import RequestOptions
from .filter import Filter
from .sort import Sort


def to_camel_case(word):
    return word.split("_")[0] + "".join(x.capitalize() or "_" for x in word.split("_")[1:])


class QuerySet:
    def __init__(self, model):
        self.model = model
        self.request_options = RequestOptions()
        self._result_cache = None
        self._pagination_item = None
        self._count = 0

    def __iter__(self):
        if self._count == getattr(self._pagination_item, 'total_available'):
            for result in self._result_cache:
                yield result
            return
        self._fetch_all()
        cache = self._result_cache.copy()
        while self._count < self._pagination_item.total_available:
            if len(cache) == 0:
                cache = self._load_next_page()
            try:
                yield cache.pop(0)
                self._count += 1
            except IndexError:
                return None


    def __getitem__(self, k):
        return list(self)[k]

    def _fetch_all(self):
        """
        Retrieve the data and store result and pagination item in cache
        """
        if self._result_cache is None:
            self._result_cache, self._pagination_item = self.model.get(self.request_options)

    @property
    def total_available(self):
        self._fetch_all()
        return self._pagination_item.total_available

    @property
    def page_number(self):
        self._fetch_all()
        return self._pagination_item.page_number

    @property
    def page_size(self):
        self._fetch_all()
        return self._pagination_item.page_size

    def filter(self, **kwargs):
        for kwarg_key, value in kwargs.items():
            field_name, operator = self._parse_shorthand_filter(kwarg_key)
            self.request_options.filter.add(Filter(field_name, operator, value))
        return self

    def order_by(self, *args):
        for arg in args:
            field_name, direction = self._parse_shorthand_sort(arg)
            self.request_options.sort.add(Sort(field_name, direction))
        return self

    def paginate(self, **kwargs):
        if "page_number" in kwargs:
            self.request_options.pagenumber = kwargs["page_number"]
        if "page_size" in kwargs:
            self.request_options.pagesize = kwargs["page_size"]
        return self

    def _parse_shorthand_filter(self, key):
        tokens = key.split("__", 1)
        if len(tokens) == 1:
            operator = RequestOptions.Operator.Equals
        else:
            operator = tokens[1]
            if operator not in RequestOptions.Operator.__dict__.values():
                raise ValueError("Operator `{}` is not valid.".format(operator))

        field = to_camel_case(tokens[0])
        if field not in RequestOptions.Field.__dict__.values():
            raise ValueError("Field name `{}` is not valid.".format(field))
        return (field, operator)

    def _parse_shorthand_sort(self, key):
        direction = RequestOptions.Direction.Asc
        if key.startswith("-"):
            direction = RequestOptions.Direction.Desc
            key = key[1:]

        key = to_camel_case(key)
        if key not in RequestOptions.Field.__dict__.values():
            raise ValueError("Sort key name %s is not valid.", key)
        return (key, direction)

    def _load_next_page(self):
        self.request_options.pagenumber += 1
        cache, self._pagination_item = self.model.get(self.request_options)
        self._result_cache += cache
        return cache
