import xml.etree.ElementTree as ET


class PaginationItem(object):
    def __init__(self, page_number=None, page_size=None, total_available=None):
        self._page_number = page_number
        self._page_size = page_size
        self._total_available = total_available

    @property
    def page_number(self):
        return self._page_number

    @property
    def page_size(self):
        return self._page_size

    @property
    def total_available(self):
        return self._total_available

    @classmethod
    def from_response(cls, resp, ns):
        parsed_response = ET.fromstring(resp)
        pagination_xml = parsed_response.find('t:pagination', namespaces=ns)
        pagination_item = cls()
        if pagination_xml is not None:
            pagination_item._page_number = int(pagination_xml.get('pageNumber', '-1'))
            pagination_item._page_size = int(pagination_xml.get('pageSize', '-1'))
            pagination_item._total_available = int(pagination_xml.get('totalAvailable', '-1'))
        return pagination_item

    @classmethod
    def from_swagger(cls, swag):
        # This entire class could go away with SWAGGER
        return swag