"""Main Flask integration."""

from os import environ

from boto3.session import Session
from flask import current_app

from .errors import ConfigurationError


class Dynamo(object):
    """DynamoDB wrapper for Flask."""

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

        self.init_settings(app)
        self.check_settings(app)

        app.extensions['dynamo'] = self

    @staticmethod
    def init_settings(app):
        """Initialize all of the extension settings."""
        app.config.setdefault('DYNAMO_TABLES', [])
        app.config.setdefault('DYNAMO_ENABLE_LOCAL', environ.get('DYNAMO_ENABLE_LOCAL', False))
        app.config.setdefault('DYNAMO_LOCAL_HOST', environ.get('DYNAMO_LOCAL_HOST'))
        app.config.setdefault('DYNAMO_LOCAL_PORT', environ.get('DYNAMO_LOCAL_PORT'))
        app.config.setdefault('AWS_ACCESS_KEY_ID', environ.get('AWS_ACCESS_KEY_ID'))
        app.config.setdefault('AWS_SECRET_ACCESS_KEY', environ.get('AWS_SECRET_ACCESS_KEY'))
        app.config.setdefault('AWS_REGION', environ.get('AWS_REGION', Dynamo.DEFAULT_REGION))

    @staticmethod
    def check_settings(app):
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

    def get_app(self):
        """
        Helper method that implements the logic to look up an application.
        pass
        """
        if current_app:
            return current_app

        if self.app is not None:
            return self.app

        raise RuntimeError(
            'application not registered on db instance and no application'
            'bound to current context'
        )

    @staticmethod
    def get_state(app):
        """
        Gets the state for the application
        """

        try:
            return app.extensions['dynamo']
        except KeyError:
            raise RuntimeError(
                'flask-dynamo extension not registered on flask app'
            )

    @property
    def connection(self):
        """
        Our DynamoDB connection.

        This will be lazily created if this is the first time this is being
        accessed.  This connection is reused for performance.
        """
        app = self.get_app()
        ctx = self.get_state(app)
        if ctx is not None:
            if not hasattr(ctx, 'dynamo_connection'):
                session_kwargs = {}
                client_kwargs = {}
                local = True if app.config['DYNAMO_ENABLE_LOCAL'] else False
                if local:
                    client_kwargs['endpoint_url'] = 'http://{}:{}'.format(
                        app.config['DYNAMO_LOCAL_HOST'],
                        app.config['DYNAMO_LOCAL_PORT'],
                    )

                # Only apply if manually specified: otherwise, we'll let boto
                # figure it out (boto will sniff for ec2 instance profile
                # credentials).
                if app.config['AWS_ACCESS_KEY_ID']:
                    session_kwargs['aws_access_key_id'] = app.config['AWS_ACCESS_KEY_ID']
                if app.config['AWS_SECRET_ACCESS_KEY']:
                    session_kwargs['aws_secret_access_key'] = app.config['AWS_SECRET_ACCESS_KEY']
                if app.config.get('AWS_REGION', None):
                    session_kwargs['region_name'] = app.config['AWS_REGION']

                ctx.dynamo_session = Session(**session_kwargs)
                ctx.dynamo_connection = ctx.dynamo_session.resource('dynamodb', **client_kwargs)

            return ctx.dynamo_connection

    @property
    def tables(self):
        """
        Our DynamoDB tables.

        These will be lazily initializes if this is the first time the tables
        are being accessed.
        """
        app = self.get_app()
        ctx = self.get_state(app)
        if ctx is not None:
            if not hasattr(ctx, 'dynamo_tables'):
                ctx.dynamo_tables = {}
                for table in app.config['DYNAMO_TABLES']:
                    table_name = table['TableName']
                    ctx.dynamo_tables[table_name] = table

                    if not hasattr(ctx, 'dynamo_table_%s' % table_name):
                        setattr(ctx, 'dynamo_table_%s' % table_name, table)

            return ctx.dynamo_tables

    def __getattr__(self, name):
        """
        Override the get attribute built-in method.

        This will allow us to provide a simple table API.  Let's say a user
        defines two tables: `users` and `groups`.  In this case, our
        customization here will allow the user to access these tables by
        calling `dynamo.users` and `dynamo.groups`, respectively.

        :param str name: The DynamoDB table name.
        :rtype: object
        :returns: A Table object if the table was found.
        :raises: AttributeError on error.
        """
        try:
            return self.tables[name]
        except KeyError:
            raise AttributeError('No table named %s found.' % name)

    def get_table(self, table_name):
        return self.connection.Table(table_name)

    def create_all(self, wait=False):
        """
        Create all user-specified DynamoDB tables.

        We'll ignore table(s) that already exists.
        We'll error out if the tables can't be created for some reason.
        """
        for table_name in self.tables:
            table = self.tables[table_name]
            self.connection.create_table(**table)
            if wait:
                waiter = self.connection.meta.client.get_waiter('table_exists')
                waiter.wait(TableName=table['TableName'])

    def destroy_all(self, wait=False):
        """
        Destroy all user-specified DynamoDB tables.

        We'll error out if the tables can't be destroyed for some reason.
        """
        for table_name in self.tables:
            table = self.connection.Table(table_name)
            table.delete()
            if wait:
                waiter = self.connection.meta.client.get_waiter('table_not_exists')
                waiter.wait(TableName=table['TableName'])
