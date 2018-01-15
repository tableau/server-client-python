import xml.etree.ElementTree as ET


class ServerResponseError(Exception):
    def __init__(self, code, summary, detail):
        self.code = code
        self.summary = summary
        self.detail = detail
        super(ServerResponseError, self).__init__(str(self))

    def __str__(self):
        return "\n\n\t{0}: {1}\n\t\t{2}".format(self.code, self.summary, self.detail)

    @classmethod
    def from_response(cls, resp, ns):
        # Check elements exist before .text
        parsed_response = ET.fromstring(resp)
        error_response = cls(parsed_response.find('t:error', namespaces=ns).get('code', ''),
                             parsed_response.find('.//t:summary', namespaces=ns).text,
                             parsed_response.find('.//t:detail', namespaces=ns).text)
        return error_response


class MissingRequiredFieldError(Exception):
    pass


class ServerInfoEndpointNotFoundError(Exception):
    pass


class EndpointUnavailableError(Exception):
    pass


class ItemTypeNotAllowed(Exception):
    pass
