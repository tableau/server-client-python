OLD_NAMESPACE = 'http://tableausoftware.com/api'
NEW_NAMESPACE = 'http://tableau.com/api'

NAMESPACE = None


def namespace():
    return NAMESPACE


def set_namespace_from_xml(raw_response):
    global NAMESPACE
    if NAMESPACE:
        return

    lines = (n for n in raw_response.split('\n') if n.startswith('<tsResponse'))

    for n in lines:
        pieces = (p for p in n.split('xmlns') if p.startswith('='))
        for piece in pieces:
            ns = piece.replace('=', '').replace('"', '').strip()
            if ns == OLD_NAMESPACE:
                NAMESPACE = {'t': OLD_NAMESPACE}
            elif ns == NEW_NAMESPACE:
                NAMESPACE = {'t': NEW_NAMESPACE}
