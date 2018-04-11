import xml.etree.ElementTree as ET
from .exceptions import UnpopulatedPropertyError


class ViewItem(object):
    def __init__(self):
        self._content_url = None
        self._id = None
        self._image = None
        self._initial_tags = set()
        self._name = None
        self._owner_id = None
        self._preview_image = None
        self._project_id = None
        self._pdf = None
        self._csv = None
        self._total_views = None
        self._workbook_id = None
        self.tags = set()

    def _set_preview_image(self, preview_image):
        self._preview_image = preview_image

    def _set_image(self, image):
        self._image = image

    def _set_pdf(self, pdf):
        self._pdf = pdf

    def _set_csv(self, csv):
        self._csv = csv

    @property
    def content_url(self):
        return self._content_url

    @property
    def id(self):
        return self._id

    @property
    def image(self):
        if self._image is None:
            error = "View item must be populated with its png image first."
            raise UnpopulatedPropertyError(error)
        return self._image()

    @property
    def name(self):
        return self._name

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def preview_image(self):
        if self._preview_image is None:
            error = "View item must be populated with its preview image first."
            raise UnpopulatedPropertyError(error)
        return self._preview_image()

    @property
    def project_id(self):
        return self._project_id

    @property
    def pdf(self):
        if self._pdf is None:
            error = "View item must be populated with its pdf first."
            raise UnpopulatedPropertyError(error)
        return self._pdf()

    @property
    def csv(self):
        if self._csv is None:
            error = "View item must be populated with its csv first."
            raise UnpopulatedPropertyError(error)
        return self._csv()

    @property
    def total_views(self):
        if self._total_views is None:
            error = "Usage statistics must be requested when querying for view."
            raise UnpopulatedPropertyError(error)
        return self._total_views

    @property
    def workbook_id(self):
        return self._workbook_id

    @classmethod
    def from_response(cls, resp, ns, workbook_id=''):
        return cls.from_xml_element(ET.fromstring(resp), ns, workbook_id)

    @classmethod
    def from_xml_element(cls, parsed_response, ns, workbook_id=''):
        all_view_items = list()
        all_view_xml = parsed_response.findall('.//t:view', namespaces=ns)
        for view_xml in all_view_xml:
            view_item = cls()
            usage_elem = view_xml.find('.//t:usage', namespaces=ns)
            workbook_elem = view_xml.find('.//t:workbook', namespaces=ns)
            owner_elem = view_xml.find('.//t:owner', namespaces=ns)
            project_elem = view_xml.find('.//t:project', namespaces=ns)
            view_item._id = view_xml.get('id', None)
            view_item._name = view_xml.get('name', None)
            view_item._content_url = view_xml.get('contentUrl', None)
            if usage_elem is not None:
                total_view = usage_elem.get('totalViewCount', None)
                if total_view:
                    view_item._total_views = int(total_view)

            if owner_elem is not None:
                view_item._owner_id = owner_elem.get('id', None)

            if project_elem is not None:
                view_item._project_id = project_elem.get('id', None)

            if workbook_id:
                view_item._workbook_id = workbook_id
            elif workbook_elem is not None:
                view_item._workbook_id = workbook_elem.get('id', None)

            all_view_items.append(view_item)
        return all_view_items
