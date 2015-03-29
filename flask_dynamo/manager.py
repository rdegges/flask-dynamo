"""Main Flask integration."""


from os import environ

from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.table import Table
from flask import (
    _app_ctx_stack as stack,
)

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
        self.init_settings()
        self.check_settings()

    def init_settings(self):
        """Initialize all of the extension settings."""
        self.app.config.setdefault('DYNAMO_TABLES', [])
        self.app.config.setdefault('DYNAMO_ENABLE_LOCAL', environ.get('DYNAMO_ENABLE_LOCAL', False))
        self.app.config.setdefault('DYNAMO_LOCAL_HOST', environ.get('DYNAMO_LOCAL_HOST'))
        self.app.config.setdefault('DYNAMO_LOCAL_PORT', environ.get('DYNAMO_LOCAL_PORT'))
        self.app.config.setdefault('AWS_ACCESS_KEY_ID', environ.get('AWS_ACCESS_KEY_ID'))
        self.app.config.setdefault('AWS_SECRET_ACCESS_KEY', environ.get('AWS_SECRET_ACCESS_KEY'))
        self.app.config.setdefault('AWS_REGION', environ.get('AWS_REGION', self.DEFAULT_REGION))

    def check_settings(self):
        """
        Check all user-specified settings to ensure they're correct.

        We'll raise an error if something isn't configured properly.

        :raises: ConfigurationError
        """
        if self.app.config['AWS_ACCESS_KEY_ID'] and not self.app.config['AWS_SECRET_ACCESS_KEY']:
            raise ConfigurationError('You must specify AWS_SECRET_ACCESS_KEY if you are specifying AWS_ACCESS_KEY_ID.')

        if self.app.config['AWS_SECRET_ACCESS_KEY'] and not self.app.config['AWS_ACCESS_KEY_ID']:
            raise ConfigurationError('You must specify AWS_ACCESS_KEY_ID if you are specifying AWS_SECRET_ACCESS_KEY.')

        if self.app.config['DYNAMO_ENABLE_LOCAL'] and not (self.app.config['DYNAMO_LOCAL_HOST'] and self.app.config['DYNAMO_LOCAL_PORT']):
            raise ConfigurationError('If you have enabled Dynamo local, you must specify the host and port.')

    @property
    def connection(self):
        """
        Our DynamoDB connection.

        This will be lazily created if this is the first time this is being
        accessed.  This connection is reused for performance.
        """
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'dynamo_connection'):
                kwargs = {
                    'host': self.app.config['DYNAMO_LOCAL_HOST'] if self.app.config['DYNAMO_ENABLE_LOCAL'] else None,
                    'port': int(self.app.config['DYNAMO_LOCAL_PORT']) if self.app.config['DYNAMO_ENABLE_LOCAL'] else None,
                    'is_secure': False if self.app.config['DYNAMO_ENABLE_LOCAL'] else True,
                }

                # Only apply if manually specified: otherwise, we'll let boto
                # figure it out (boto will sniff for ec2 instance profile
                # credentials).
                if self.app.config['AWS_ACCESS_KEY_ID']:
                  kwargs['aws_access_key_id'] = self.app.config['AWS_ACCESS_KEY_ID']
                if self.app.config['AWS_SECRET_ACCESS_KEY']:
                  kwargs['aws_secret_access_key'] = self.app.config['AWS_SECRET_ACCESS_KEY']

                # If DynamoDB local is disabled, we'll remove these settings.
                if not kwargs['host']:
                    del kwargs['host']
                if not kwargs['port']:
                    del kwargs['port']

                ctx.dynamo_connection = connect_to_region(self.app.config['AWS_REGION'], **kwargs)

            return ctx.dynamo_connection

    @property
    def tables(self):
        """
        Our DynamoDB tables.

        These will be lazily initializes if this is the first time the tables
        are being accessed.
        """
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'dynamo_tables'):
                ctx.dynamo_tables = {}
                for table in self.app.config['DYNAMO_TABLES']:
                    table.connection = self.connection
                    ctx.dynamo_tables[table.table_name] = table

                    if not hasattr(ctx, 'dynamo_table_%s' % table.table_name):
                        setattr(ctx, 'dynamo_table_%s' % table.table_name, table)

            return ctx.dynamo_tables

    def __getattr__(self, name):
        """
        Override the get attribute built-in method.

        This will allow us to provide a simple table API.  Let's say a user
        defines two tables: `users` and `groups`.  In this case, our
        customization here will allow the user to access these tables by calling
        `dynamo.users` and `dynamo.groups`, respectively.

        :param str name: The DynamoDB table name.
        :rtype: object
        :returns: A Table object if the table was found.
        :raises: AttributeError on error.
        """
        if name in self.tables:
            return self.tables[name]

        raise AttributeError('No table named %s found.' % name)

    def create_all(self):
        """
        Create all user-specified DynamoDB tables.

        We'll error out if the tables can't be created for some reason.
        """
        for table_name, table in self.tables.iteritems():
            Table.create(
                table_name = table.table_name,
                schema = table.schema,
                throughput = table.throughput,
                indexes = table.indexes,
                global_indexes = table.global_indexes,
                connection = self.connection,
            )

    def destroy_all(self):
        """
        Destroy all user-specified DynamoDB tables.

        We'll error out if the tables can't be destroyed for some reason.
        """
        for table_name, table in self.tables.iteritems():
            table.delete()
