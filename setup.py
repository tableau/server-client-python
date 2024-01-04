import versioneer
from setuptools import setup

"""
once versioneer 0.25 gets released, we can move this from setup.cfg to pyproject.toml
[tool.versioneer]
VCS = "git"
style = "pep440-pre"
versionfile_source = "tableauserverclient/_version.py"
versionfile_build = "tableauserverclient/_version.py"
tag_prefix = "v"
"""
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
