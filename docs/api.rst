.. _api:


API
===

.. module:: flask_dynamo.manager

This part of the documentation documents all the public classes, functions, and
API details in flask-dynamo.  This documentation is auto generated, and is
always a good up-to-date reference.


Configuration
-------------

.. autoclass:: Dynamo

    .. automethod:: init_app
    .. autoattribute:: connection
    .. autoinstanceattribute:: DynamoLazyTables
    .. automethod:: get_table
    .. automethod:: create_all
    .. automethod:: destroy_all

.. autoclass:: DynamoLazyTables

    .. automethod:: keys
    .. automethod:: len
    .. automethod:: items
    .. automethod:: wait_exists
    .. automethod:: wait_not_exists
    .. automethod:: create_all
    .. automethod:: destroy_all


Errors
------

.. module:: flask_dynamo.errors

.. autoclass:: ConfigurationError
