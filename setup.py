try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup


class LiveTestCommand(Command):

    description = "Run tests against a live server"

    # [('long', 'short', 'description')]
    user_options = [('server=', 's', "Server to connect to"),
                    ('site=', 't', "Sute to connect to"),
                    ('username=', 'u', "Username for tests (system admin)")]

    def initialize_options(self):
        self.server = None
        self.username = None
        self.password = None
        self.site = None

    def finalize_options(self):
        if self.server is None:
            self.server = "DEFAULT SERVER"
        if self.username is None:
            self.username = "DEFAULT USERNAME"
        if self.site is None:
            self.site = ""

        import getpass
        self.password = getpass.getpass()

    def run(self):
        import subprocess as sp
        import os

        with open(os.devnull, 'wb') as silent:
            sp.check_call(['python', 'smoke.py', self.server, self.username, self.password, self.site], stdout=silent)


setup(
    name='tableauserverclient',
    version='0.3',
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
    ],
    cmdclass={'livetest': LiveTestCommand}
)
