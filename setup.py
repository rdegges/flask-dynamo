from os.path import abspath, dirname, join, normpath

from setuptools import setup


setup(

    # Basic package information:
    name = 'flask-dynamo',
    version = '0.1',
    packages = ('dynamo',),

    # Packaging options:
    zip_safe = False,
    include_package_data = True,

    # Package dependencies:
    install_requires = ['Flask>=0.7'],

    # Metadata for PyPI:
    author = 'Randall Degges',
    author_email = 'rdegges@gmail.com',
    license = 'UNLICENSE',
    url = 'https://github.com/rdegges/flask-dynamo',
    keywords = 'python dynamodb dynamo aws amazon flask web database',
    description = 'Flask integration for DynamoDB.',
    long_description = open(normpath(join(dirname(abspath(__file__)),
        'README.md'))).read()

)
