from .. import NAMESPACE


class TaggedResourceItem(object):
    def __init__(self):
        self._initial_tags = set()
        self.tags = set()

    def _get_initial_tags(self):
        return self._initial_tags

    def _set_initial_tags(self, initial_tags):
        self._initial_tags = initial_tags