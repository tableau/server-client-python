try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tableauserverclient',
    version='0.2',
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/server-client-python',
    packages=['tableauserverclient', 'tableauserverclient.models', 'tableauserverclient.server',
              'tableauserverclient.server.endpoint'],
    license='MIT',
    description='A Python module for working with the Tableau Server REST API.',
    test_suite='test',
    install_requires=[
        'requests>=2.11,<2.12.0a0'
    ],
    tests_require=[
        'requests-mock>=1.0,<1.1a0'
    ]
)
