import versioneer
from setuptools import setup

setup(
    name='tableauserverclient',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/server-client-python',
    package_data={'tableauserverclient': ['py.typed']},
    packages=['tableauserverclient',
              'tableauserverclient.helpers',
              'tableauserverclient.models',
              'tableauserverclient.server',
              'tableauserverclient.server.endpoint'],
    license='MIT',
    description='A Python module for working with the Tableau Server REST API.',
    long_description="file: README.md",
    long_description_content_type='text/markdown',
    install_requires=[
        'defusedxml>=0.7.1',
        'requests>=2.11,<3.0',
    ],
    python_requires='>3.7.0',
    tests_require=[
        'argparse',  # technically only needed to run samples
        'black',
        'mock',
        'pytest',
        'requests-mock>=1.0,<2.0',
        'mypy>=0.920'
    ]
)
