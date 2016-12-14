import abc


class RequestOptionsBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def apply_query_params(self, url):
        return
