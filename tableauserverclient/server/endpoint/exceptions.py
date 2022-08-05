from defusedxml.ElementTree import fromstring


class ServerResponseError(Exception):
    def __init__(self, code, summary, detail, url=None):
        self.code = code
        self.summary = summary
        self.detail = detail
        self.url = url
        super(ServerResponseError, self).__init__(str(self))

    def __str__(self):
        return "\n\n\t{0}: {1}\n\t\t{2}".format(self.code, self.summary, self.detail)

    @classmethod
    def from_response(cls, resp, ns, url=None):
        # Check elements exist before .text
        parsed_response = fromstring(resp)
        try:
            error_response = cls(
                parsed_response.find("t:error", namespaces=ns).get("code", ""),
                parsed_response.find(".//t:summary", namespaces=ns).text,
                parsed_response.find(".//t:detail", namespaces=ns).text,
                url,
            )
        except Exception as e:
            raise NonXMLResponseError(resp)
        return error_response


class InternalServerError(ServerResponseError):
    def __init__(self, server_response, url=None):
        self.code = server_response.status_code
        self.content = server_response.content
        self.url = url

    def __str__(self):
        return "\n\nError status code: {0}\n{1}\n{2}".format(self.code, self.content, self.url)


class MissingRequiredFieldError(Exception):
    pass


class ServerInfoEndpointNotFoundError(Exception):
    pass


class EndpointUnavailableError(Exception):
    pass


class ItemTypeNotAllowed(Exception):
    pass


class NonXMLResponseError(Exception):
    pass


class InvalidGraphQLQuery(Exception):
    pass


class GraphQLError(Exception):
    def __init__(self, error_payload):
        self.error = error_payload

    def __str__(self):
        from pprint import pformat

        return pformat(self.error)


class JobFailedException(Exception):
    def __init__(self, job):
        self.notes = job.notes
        self.job = job

    def __str__(self):
        return f"Job {self.job.id} failed with notes {self.notes}"


class JobCancelledException(JobFailedException):
    pass


class FlowRunFailedException(Exception):
    def __init__(self, flow_run):
        self.background_job_id = flow_run.background_job_id
        self.flow_run = flow_run

    def __str__(self):
        return f"FlowRun {self.flow_run.id} failed with job id {self.background_job_id}"


class FlowRunCancelledException(FlowRunFailedException):
    pass
