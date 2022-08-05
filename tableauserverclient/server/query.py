from typing import Tuple
from .filter import Filter
from .request_options import RequestOptions
from .sort import Sort
import math


def to_camel_case(word: str) -> str:
    return word.split("_")[0] + "".join(x.capitalize() or "_" for x in word.split("_")[1:])


"""
This interface allows more fluent queries against Tableau Server
e.g server.users.get(name="user@domain.com")
see pagination_sample
"""


class QuerySet:
    def __init__(self, model):
        self.model = model
        self.request_options = RequestOptions()
        self._result_cache = None
        self._pagination_item = None

    def __iter__(self):
        # Not built to be re-entrant. Starts back at page 1, and empties
        # the result cache.
        self.request_options.pagenumber = 1
        self._result_cache = None
        total = self.total_available
        size = self.page_size
        yield from self._result_cache

        # Loop through the subsequent pages.
        for page in range(1, math.ceil(total / size)):
            self.request_options.pagenumber = page + 1
            self._result_cache = None
            self._fetch_all()
            yield from self._result_cache

    def __getitem__(self, k):
        page = self.page_number
        size = self.page_size

        # Create a range object for quick checking if k is in the cached result.
        page_range = range((page - 1) * size, page * size)

        if isinstance(k, slice):
            # Parse out the slice object, and assume reasonable defaults if no value provided.
            step = k.step if k.step is not None else 1
            start = k.start if k.start is not None else 0
            stop = k.stop if k.stop is not None else self.total_available

            # If negative values present in slice, convert to positive values
            if start < 0:
                start += self.total_available
            if stop < 0:
                stop += self.total_available
            if start < stop and step < 0:
                # Since slicing is left inclusive and right exclusive, shift
                # the start and stop values by 1 to keep that behavior
                start, stop = stop - 1, start - 1
                slice_stop = stop if stop > 0 else None
                k = slice(start, slice_stop, step)

            # Fetch items from cache if present, otherwise, recursively fetch.
            k_range = range(start, stop, step)
            if all(i in page_range for i in k_range):
                return self._result_cache[k]
            return [self[i] for i in k_range]

        if k < 0:
            k += self.total_available

        if k in page_range:
            # Fetch item from cache if present
            return self._result_cache[k % size]
        elif k in range(self.total_available):
            # Otherwise, check if k is even sensible to return
            self._result_cache = None
            # Add one to k, otherwise it gets stuck at page boundaries, e.g. 100
            self.request_options.pagenumber = max(1, math.ceil((k + 1) / size))
            return self[k]
        else:
            # If k is unreasonable, raise an IndexError.
            raise IndexError

    def _fetch_all(self):
        """
        Retrieve the data and store result and pagination item in cache
        """
        if self._result_cache is None:
            self._result_cache, self._pagination_item = self.model.get(self.request_options)

    def __len__(self) -> int:
        return self.total_available

    @property
    def total_available(self) -> int:
        self._fetch_all()
        return self._pagination_item.total_available

    @property
    def page_number(self) -> int:
        self._fetch_all()
        return self._pagination_item.page_number

    @property
    def page_size(self) -> int:
        self._fetch_all()
        return self._pagination_item.page_size

    def filter(self, *invalid, **kwargs):
        if invalid:
            raise RuntimeError(f"Only accepts keyword arguments.")
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

    def _parse_shorthand_filter(self, key: str) -> Tuple[str, str]:
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

    def _parse_shorthand_sort(self, key: str) -> Tuple[str, str]:
        direction = RequestOptions.Direction.Asc
        if key.startswith("-"):
            direction = RequestOptions.Direction.Desc
            key = key[1:]

        key = to_camel_case(key)
        if key not in RequestOptions.Field.__dict__.values():
            raise ValueError("Sort key name %s is not valid.", key)
        return (key, direction)
