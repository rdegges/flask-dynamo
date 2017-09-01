"""Flask integration for DynamoDB."""


__version__ = '0.1.2'
__author__ = 'Randall Degges'
__email__ = 'r@rdegges.com'


from .manager import Dynamo
from .errors import ConfigurationError
