"""
flask-dynamo
~~~~~~~~~~~~

DynamoDB integration for Flask!

Please visit this project's GitHub page to view all docs:
https://github.com/rdegges/flask-dynamo

-Randall
"""


from subprocess import call

from setuptools import Command, setup


VERSION = '0.1.0'


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        import sys
        import py.test
        raise SystemExit(py.test.main(args=[]))


setup(

    # Basic package information:
    name = 'flask-dynamo',
    version = VERSION,
    packages = ['flask_dynamo'],

    # Packaging options:
    zip_safe = False,
    include_package_data = True,

    # Package dependencies:
    install_requires = ['boto3>=1.1.4', 'Flask>=0.10.1'],

    # Metadata for PyPI:
    author = 'Randall Degges',
    author_email = 'r@rdegges.com',
    license = 'UNLICENSE',
    url = 'https://github.com/rdegges/flask-dynamo',
    keywords = 'python dynamodb dynamo aws amazon flask web database',
    description = 'DynamoDB integration for Flask.',
    long_description = __doc__,

    # Classifiers:
    platforms = 'any',
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    # Test helper:
    cmdclass = {'test': RunTests},

)
