try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tableauserverapi',
    version='0.1',
    author='Tableau Software',
    author_email='github@tableau.com',
    url='https://github.com/tableau/server-api-python',
    packages=['tableauserverapi', 'tableauserverapi.models', 'tableauserverapi.server',
              'tableauserverapi.server.endpoint'],
    license='MIT',
    description='A Python module for working with the Tableau Server REST API.',
    test_suite='test',
    install_requires=[
        'requests>=2.11,<2.12.0a0',
        'requests-mock>=1.0,<1.1a0'
    ]
)