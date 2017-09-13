OLD_NAMESPACE = 'http://tableausoftware.com/api'
NEW_NAMESPACE = 'http://tableau.com/api'

NAMESPACE = None

class Namespace(object):
    def __init__(self):
        self._namespace = {'t': NEW_NAMESPACE}
        self._detected = False

    def __call__(self):
        return self._namespace

    def detect(self, xml):
        if self._detected:
            return

        lines = (n for n in xml.split('\n') if n.startswith('<tsResponse'))

        for n in lines:
            pieces = (p for p in n.split('xmlns') if p.startswith('='))
            for piece in pieces:
                ns = piece.replace('=', '').replace('"', '').strip()
                if ns == OLD_NAMESPACE:
                    self._namespace = {'t': OLD_NAMESPACE}
                    self._detected = True
                elif ns == NEW_NAMESPACE:
                    self._namespace = {'t': NEW_NAMESPACE}
                    self._detected = True


def namespace():
    return NAMESPACE


def set_namespace_from_xml(raw_response):
    global NAMESPACE
    if NAMESPACE:
        return

    ns = Namespace()
    ns.detect(raw_response)
    NAMESPACE = ns()
