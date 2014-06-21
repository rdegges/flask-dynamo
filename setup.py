"""
flask-dynamo
~~~~~~~~~~~~

DynamoDB integration for Flask!

Please visit this project's GitHub page to view all docs:
https://github.com/rdegges/flask-dynamo

-Randall
"""


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
    install_requires = ['boto>=2.29.1', 'Flask>=0.10.1'],

    # Metadata for PyPI:
    author = 'Randall Degges',
    author_email = 'r@rdegges.com',
    license = 'UNLICENSE',
    url = 'https://github.com/rdegges/flask-dynamo',
    keywords = 'python dynamodb dynamo aws amazon flask web database',
    description = 'DynamoDB integration for Flask.',
    long_description = __doc__,

)
