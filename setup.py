import versioneer
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
    test_suite='test',
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'requests>=2.11,<3.0'
    ],
    tests_require=[
        'requests-mock>=1.0,<2.0',
        'pytest'
    ]
)
