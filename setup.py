import versioneer
from setuptools import setup

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # not yet sure how to move this to pyproject.toml
    packages=[
        "tableauserverclient",
        "tableauserverclient.helpers",
        "tableauserverclient.models",
        "tableauserverclient.server",
        "tableauserverclient.server.endpoint",
    ],
)
