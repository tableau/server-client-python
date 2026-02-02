import versioneer
from setuptools import setup

setup(
    # This line is required to set the version number when building the wheel
    # not yet sure how to move this to pyproject.toml - it may require work in versioneer
    cmdclass=versioneer.get_cmdclass()
)
