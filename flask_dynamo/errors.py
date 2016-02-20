"""Custom errors."""


class ConfigurationError(Exception):
    """
    This exception is raised if the user hasn't properly configured
    Flask-Dynamo.
    """
    pass


class DynamodbTableError(Exception):
    """
    This exception is raised if tables already exists or can't be updated.
    """
    pass
