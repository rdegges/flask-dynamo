from os.path import abspath, dirname, join, normpath

from setuptools import setup

from flask_dynamo import __version__ as version


setup(

    # Basic package information:
    name = 'flask-dynamo',
    version = version,
    packages = ['flask_dynamo'],

    # Packaging options:
    zip_safe = False,
    include_package_data = True,

    # Package dependencies:
    install_requires = ['Flask>=0.10.1'],

    # Metadata for PyPI:
    author = 'Randall Degges',
    author_email = 'r@rdegges.com',
    license = 'UNLICENSE',
    url = 'https://github.com/rdegges/flask-dynamo',
    keywords = 'python dynamodb dynamo aws amazon flask web database',
    description = 'Flask integration for DynamoDB.',
    long_description = open(normpath(join(dirname(abspath(__file__)), 'README.md'))).read()

)
