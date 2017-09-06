"""Main Flask integration."""

from os import environ

from boto3.session import Session
from flask import current_app

from .errors import ConfigurationError


class DynamoLazyTables(object):
    """Manages access to Dynamo Tables."""
    def __init__(self, connection, table_config):
        self._table_config = table_config
        self._connection = connection

    def __getitem__(self, name):
        """Get the connection for a table by name."""
        return self._connection.Table(name)

    def keys(self):
        """The table names in our config."""
        return [t['TableName'] for t in self._table_config]

    def len(self):
        """The number of tables we are configured for."""
        return len(self.keys())

    def items(self):
        """The table tuples (name, connection.Table())."""
        for table_name in self.keys():
            yield (table_name, self[table_name])

    def _wait(self, table_name, type_waiter):
        waiter = self._connection.meta.client.get_waiter(type_waiter)
        waiter.wait(TableName=table_name)

    def wait_exists(self, table_name):
        self._wait(table_name, 'table_exists')

    def wait_not_exists(self, table_name):
        self._wait(table_name, 'table_not_exists')

    def create_all(self, wait=False):
        tables_name_list = [table.name for table in self._connection.tables.all()]
        for table in self._table_config:
            if table['TableName'] not in tables_name_list:
                self._connection.create_table(**table)
        if wait:
            for table in self._table_config:
                if table['TableName'] not in tables_name_list:
                    self.wait_exists(table['TableName'])

    def destroy_all(self, wait=False):
        for table in self._table_config:
            table = self._connection.Table(table['TableName'])
            table.delete()
        if wait:
            for table in self._table_config:
                self.wait_not_exists(table['TableName'])


class Dynamo(object):
    """DynamoDB engine manager."""

    DEFAULT_REGION = 'us-east-1'

    def __init__(self, app=None):
        """
        Initialize this extension.

        :param obj app: The Flask application (optional).
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize this extension.

        :param obj app: The Flask application.
        """

        self._init_settings(app)
        self._check_settings(app)

        app.extensions['dynamo'] = self

        conn = self._connection(app=app)

        self.tables = DynamoLazyTables(conn, app.config['DYNAMO_TABLES'])

    @staticmethod
    def _init_settings(app):
        """Initialize all of the extension settings."""
        app.config.setdefault('DYNAMO_SESSION', None)
        app.config.setdefault('DYNAMO_TABLES', [])
        app.config.setdefault('DYNAMO_ENABLE_LOCAL', environ.get('DYNAMO_ENABLE_LOCAL', False))
        app.config.setdefault('DYNAMO_LOCAL_HOST', environ.get('DYNAMO_LOCAL_HOST', None))
        app.config.setdefault('DYNAMO_LOCAL_PORT', environ.get('DYNAMO_LOCAL_PORT', None))
        app.config.setdefault('AWS_ACCESS_KEY_ID', environ.get('AWS_ACCESS_KEY_ID', None))
        app.config.setdefault('AWS_SECRET_ACCESS_KEY', environ.get('AWS_SECRET_ACCESS_KEY', None))
        app.config.setdefault('AWS_SESSION_TOKEN', environ.get('AWS_SESSION_TOKEN', None))
        app.config.setdefault('AWS_REGION', environ.get('AWS_REGION', Dynamo.DEFAULT_REGION))

    @staticmethod
    def _check_settings(app):
        """
        Check all user-specified settings to ensure they're correct.

        We'll raise an error if something isn't configured properly.

        :raises: ConfigurationError
        """
        if app.config['AWS_ACCESS_KEY_ID'] and not app.config['AWS_SECRET_ACCESS_KEY']:
            raise ConfigurationError('You must specify AWS_SECRET_ACCESS_KEY if you are specifying AWS_ACCESS_KEY_ID.')

        if app.config['AWS_SECRET_ACCESS_KEY'] and not app.config['AWS_ACCESS_KEY_ID']:
            raise ConfigurationError('You must specify AWS_ACCESS_KEY_ID if you are specifying AWS_SECRET_ACCESS_KEY.')

        if app.config['DYNAMO_ENABLE_LOCAL'] and not (app.config['DYNAMO_LOCAL_HOST'] and app.config['DYNAMO_LOCAL_PORT']):
            raise ConfigurationError('If you have enabled Dynamo local, you must specify the host and port.')

    def _get_app(self):
        """
        Helper method that implements the logic to look up an application.
        pass
        """
        if current_app:
            return current_app

        if self.app is not None:
            return self.app

        raise RuntimeError(
            'application not registered on dynamo instance and no application'
            'bound to current context'
        )

    @staticmethod
    def _get_ctx(app):
        """
        Gets the dyanmo app context state.
        """

        try:
            return app.extensions['dynamo']
        except KeyError:
            raise RuntimeError(
                'flask-dynamo extension not registered on flask app'
            )

    @staticmethod
    def _init_session(app):
        session_kwargs = {}
        # Only apply if manually specified: otherwise, we'll let boto
        # figure it out (boto will sniff for ec2 instance profile
        # credentials).
        if app.config['AWS_ACCESS_KEY_ID']:
            session_kwargs['aws_access_key_id'] = app.config['AWS_ACCESS_KEY_ID']
        if app.config['AWS_SECRET_ACCESS_KEY']:
            session_kwargs['aws_secret_access_key'] = app.config['AWS_SECRET_ACCESS_KEY']
        if app.config['AWS_SESSION_TOKEN']:
            session_kwargs['aws_session_token'] = app.config['AWS_SESSION_TOKEN']
        if app.config['AWS_REGION']:
            session_kwargs['region_name'] = app.config['AWS_REGION']
        return Session(**session_kwargs)

    def _session(self, app=None):
        if not app:
            app = self._get_app()
        ctx = self._get_ctx(app)
        try:
            return ctx._session_instance
        except AttributeError:
            ctx._session_instance = app.config['DYNAMO_SESSION'] or self._init_session(app)
            return ctx._session_instance

    @property
    def session(self):
        """
        Our DynamoDB session.

        This will be lazily created if this is the first time this is being
        accessed.  This session is reused for performance.
        """
        return self._session()

    def _connection(self, app=None):
        if not app:
            app = self._get_app()

        ctx = self._get_ctx(app)
        try:
            return ctx._connection_instance
        except AttributeError:
            client_kwargs = {}
            local = True if app.config['DYNAMO_ENABLE_LOCAL'] else False
            if local:
                client_kwargs['endpoint_url'] = 'http://{}:{}'.format(
                    app.config['DYNAMO_LOCAL_HOST'],
                    app.config['DYNAMO_LOCAL_PORT'],
                )

            ctx._connection_instance = self._session(app=app).resource('dynamodb', **client_kwargs)

            return ctx._connection_instance

    @property
    def connection(self):
        """
        Our DynamoDB connection.

        This will be lazily created if this is the first time this is being
        accessed.  This connection is reused for performance.
        """
        return self._connection()

    def get_table(self, table_name):
        return self.tables[table_name]

    def create_all(self, wait=False):
        """
        Create all user-specified DynamoDB tables.

        We'll ignore table(s) that already exists.
        We'll error out if the tables can't be created for some reason.
        """
        self.tables.create_all(wait=wait)

    def destroy_all(self, wait=False):
        """
        Destroy all user-specified DynamoDB tables.

        We'll error out if the tables can't be destroyed for some reason.
        """
        self.tables.destroy_all(wait=wait)
