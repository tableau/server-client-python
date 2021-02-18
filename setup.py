import sys
import versioneer

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Only install pytest and runner when test command is run
# This makes work easier for offline installs or low bandwidth machines
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []
test_requirements = ['mock', 'pycodestyle', 'pytest', 'requests-mock>=1.0,<2.0']

setup(
    name='tableauserverclient',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/server-client-python',
    packages=['tableauserverclient', 'tableauserverclient.models', 'tableauserverclient.server',
              'tableauserverclient.server.endpoint'],
    license='MIT',
    description='A Python module for working with the Tableau Server REST API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    test_suite='test',
    setup_requires=pytest_runner,
    install_requires=[
        'requests>=2.11,<3.0',
    ],
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements
    }
)
