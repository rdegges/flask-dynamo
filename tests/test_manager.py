"""Tests for our manager."""


from os import environ
from time import sleep
from unittest import TestCase
from uuid import uuid4
from mock import patch

from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from flask import Flask
from flask.ext.dynamo import Dynamo
from flask.ext.dynamo.errors import ConfigurationError


class DynamoUnitTest(TestCase):
    """ Unit level tests for the Dynamo extensions, don't actually connect to dynamo.
    """
    @patch('flask_dynamo.manager.DynamoDBConnection')
    def test_connect_locally(self, connection_mock):

        # set minimal params for local connection
        app = Flask(__name__)
        app.config['DYNAMO_TABLES'] = ['Fake Table']
        app.config['AWS_ACCESS_KEY_ID'] = 'testkey'
        app.config['AWS_SECRET_ACCESS_KEY'] = 'testsecret'
        app.config['DYNAMO_ENABLE_LOCAL'] = True
        app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
        app.config['DYNAMO_LOCAL_PORT'] = 1234

        dynamo = Dynamo(app)
        with app.app_context():
            connection = dynamo.connection
        connection_mock.assert_called_once_with(
                aws_access_key_id='testkey',
                aws_secret_access_key='testsecret',
                host='localhost',
                port=1234,
                is_secure=False)
        self.assertEqual(connection.__class__.__name__, 'MagicMock')

    @patch('flask_dynamo.manager.connect_to_region')
    def test_connect_to_region(self, connect_to_region_mock):
        # connect_to_region_mock.return_value = None
        # set minimal params for local connection
        app = Flask(__name__)
        app.config['DYNAMO_TABLES'] = ['Fake Table']
        app.config['AWS_ACCESS_KEY_ID'] = 'testkey'
        app.config['AWS_SECRET_ACCESS_KEY'] = 'testsecret'

        dynamo = Dynamo(app)
        with app.app_context():
            connection = dynamo.connection
        connect_to_region_mock.assert_called_once_with(
                Dynamo.DEFAULT_REGION,
                aws_access_key_id='testkey',
                aws_secret_access_key='testsecret',
                is_secure=True)
        self.assertEqual(connection.__class__.__name__, 'MagicMock')


class DynamoIntegrationTest(TestCase):
    """Test our Dynamo extension end to end.
    Actually connects to DynamoDB so requires credentials set in environment
    """

    def setUp(self):
        """
        Set up a simple Flask app for testing.

        This will be used throughout our tests.
        """
        self.prefix = uuid4().hex

        self.app = Flask(__name__)
        self.app.config['DEBUG'] = True
        self.app.config['DYNAMO_TABLES'] = [
            Table('%s-phones' % self.prefix, schema=[HashKey('number')]),
            Table('%s-users' % self.prefix, schema=[HashKey('username')]),
        ]

        self.dynamo = Dynamo(self.app)

        with self.app.app_context():
            self.dynamo.create_all()
            sleep(60)

    def test_settings(self):
        self.assertEqual(len(self.app.config['DYNAMO_TABLES']), 2)
        self.assertEqual(self.app.config['AWS_ACCESS_KEY_ID'], environ.get('AWS_ACCESS_KEY_ID'))
        self.assertEqual(self.app.config['AWS_SECRET_ACCESS_KEY'], environ.get('AWS_SECRET_ACCESS_KEY'))
        self.assertEqual(self.app.config['AWS_REGION'], environ.get('AWS_REGION') or self.dynamo.DEFAULT_REGION)

        # Test DynamoDB local settings.
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['DYNAMO_TABLES'] = [
            Table('%s-phones' % self.prefix, schema=[HashKey('number')]),
            Table('%s-users' % self.prefix, schema=[HashKey('username')]),
        ]
        app.config['DYNAMO_ENABLE_LOCAL'] = True

        self.assertRaises(ConfigurationError, Dynamo, app)

        app.config['DYNAMO_LOCAL_HOST'] = 'localhost'

        self.assertRaises(ConfigurationError, Dynamo, app)

        app.config['DYNAMO_LOCAL_PORT'] = 8000
        self.assertIsInstance(Dynamo(app), object)

    def test_connection(self):
        with self.app.app_context():
            self.assertIsInstance(self.dynamo.connection, DynamoDBConnection)

    def test_tables(self):
        with self.app.app_context():
            self.assertEqual(len(self.dynamo.tables.keys()), 2)

            for table_name, table in self.dynamo.tables.iteritems():
                self.assertIsInstance(table, Table)
                self.assertEqual(table.table_name, table_name)

    def test_table_access(self):
        with self.app.app_context():
            for table_name, table in self.dynamo.tables.iteritems():
                self.assertEqual(getattr(self.dynamo, table_name), table)

    def tearDown(self):
        """Destroy all provisioned resources."""
        with self.app.app_context():
            self.dynamo.destroy_all()
            sleep(60)
