import os.path

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')


def asset(filename):
    return os.path.join(TEST_ASSET_DIR, filename)


def read_xml_asset(filename):
    with open(asset(filename), 'rb') as f:
        return f.read().decode('utf-8')


def read_xml_assets(*args):
    return map(read_xml_asset, args)
