class Sort:
    """
    Used with request options (RequestOptions) where you can filter and sort on
    the results returned from the server.

    Parameters
    ----------
    field : str
        Sets the field to sort on. The fields are defined in the RequestOption class.

    direction : str
        The direction to sort, either ascending (Asc) or descending (Desc). The
        options are defined in the RequestOptions.Direction class.

    Examples
    --------

    >>> # create a new instance of a request option object
    >>> req_option = TSC.RequestOptions()

    >>> # add the sort expression, sorting by name and direction
    >>> req_option.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name,
                             TSC.RequestOptions.Direction.Asc))
    >>> matching_workbooks, pagination_item = server.workbooks.get(req_option)

    >>> for wb in matching_workbooks:
    >>>     print(wb.name)
    """

    def __init__(self, field, direction):
        self.field = field
        self.direction = direction

    def __str__(self):
        return f"{self.field}:{self.direction}"
