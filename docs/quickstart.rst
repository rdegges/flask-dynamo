.. _quickstart:
.. module:: flask_dynamo


Quickstart
==========

This section will guide you through everything you need to know to get up and
running with flask-dynamo!


Installation
------------

The first thing you need to do is install flask-dynamo.  Installation can be
done through `pip`_, the Python package manager.

To install flask-dynamo, run::

    $ pip install flask-dynamo

If you'd like to upgrade an existing installation of flask-dynamo to the latest
release, you can run::

    $ pip install -U flask-dynamo


Set Environment Variables
-------------------------

In order to run properly, flask-dynamo requires that you set several environment
variables.

The required environment variables are:

- ``AWS_ACCESS_KEY_ID`` (*your Amazon access key ID*)
- ``AWS_SECRET_ACCESS_KEY`` (*your Amazon secret access key*)

There are also optional variables you can set:

- ``AWS_REGION`` (*defaults to us-east-1*)
- ``DYNAMO_ENABLE_LOCAL`` (*defaults to False*)
- ``DYNAMO_LOCAL_HOST`` (*defaults to None*)
- ``DYNAMO_LOCAL_PORT`` (*defaults to None*)

These credentials can be grabbed from your `AWS Console`_.

.. note::
    A full list of Amazon regions can be found here:
    http://docs.aws.amazon.com/general/latest/gr/rande.html#ddb_region

If you're unsure of how to set environment variables, I recommend you check out
this `StackOverflow question`_.


.. _specify-your-tables:

Specify Your Tables
-------------------

The next thing you need to do is tell flask-dynamo which tables you'll be using.

If you're not sure how tables work with DynamoDB, you should read through the
`boto DynamoDB tutorial`_ before continuing.

The way you can specify your tables is by creating an array called
``DYNAMO_TABLES`` (*this is what flask-dynamo uses to set everything up*).

Below is an example::

    # app.py

    from flask import Flask
    from flask_dynamo import Dynamo

    app = Flask(__name__)
    app.config['DYNAMO_TABLES'] = [
        {
             TableName='users',
             KeySchema=[dict(AttributeName='username', KeyType='HASH')],
             AttributeDefinitions=[dict(AttributeName='username', AttributeType='S')],
             ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }, {
             TableName='groups',
             KeySchema=[dict(AttributeName='name', KeyType='HASH')],
             AttributeDefinitions=[dict(AttributeName='name', AttributeType='S')],
             ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }
     ]

In the above example, I'm defining two DynamoDB tables: ``users`` and
``groups``, along with their respective schemas.

flask-dynamo will respect *any* boto tables you define -- it will also respect
any of the other fields you specify on your tables.


Initialize Dynamo
-----------------

Now that you've defined your tables, you can initialize flask-dynamo in your
app.

All you need to do is pass your app to the ``Dynamo`` constructor::

    # app.py

    from flask import Flask
    from flask_dynamo import Dynamo

    app = Flask(__name__)
    app.config['DYNAMO_TABLES'] = [
        {
             TableName='users',
             KeySchema=[dict(AttributeName='username', KeyType='HASH')],
             AttributeDefinitions=[dict(AttributeName='username', AttributeType='S')],
             ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }, {
             TableName='groups',
             KeySchema=[dict(AttributeName='name', KeyType='HASH')],
             AttributeDefinitions=[dict(AttributeName='name', AttributeType='S')],
             ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }
    ]

    dynamo = Dynamo(app)

If you use the app factory pattern then use::

    # app.py

    from flask import Flask
    from flask_dynamo import Dynamo

    def create_app():
        app = Flask(__name__)
        app.config['DYNAMO_TABLES'] = [
            {
                 TableName='users',
                 KeySchema=[dict(AttributeName='username', KeyType='HASH')],
                 AttributeDefinitions=[dict(AttributeName='username', AttributeType='S')],
                 ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
            }, {
                 TableName='groups',
                 KeySchema=[dict(AttributeName='name', KeyType='HASH')],
                 AttributeDefinitions=[dict(AttributeName='name', AttributeType='S')],
                 ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
            }
        ]
        dynamo = Dynamo()
        dynamo.init_app(app)
        return app

    app = create_app()


From this point on, you can interact with DynamoDB through the global ``dynamo``
object, or through ``Flask.current_app.extensions['dynamodb']`` if you are
using the Flask app factory pattern.


Create Your Tables
------------------

If you haven't already created your DynamoDB tables, flask-dynamo can help you
out!

After configuring flask-dynamo, you can use the following code snippet to create
all of your predefined DynamoDB tables::

    with app.app_context():
        dynamo.create_all()

This works great in bootstrap scripts.


Working with Tables
-------------------

Now that you've got everything setup, you can easily access your tables
in a dictionary-like format through ``dynamo.tables``.

Below is an example view which creates a new user account::

    # app.py

    @app.route('/create_user')
    def create_user():
        dynamo.tables['users'].put_item(data={
            'username': 'rdegges',
            'first_name': 'Randall',
            'last_name': 'Degges',
            'email': 'r@rdegges.com',
        })

On a related note, you can also use the ``dynamo.tables`` dictionary to iterate
through all of your tables (*this is sometimes useful*).  Here's how you could
iterate over your existing DynamoDB tables::

    # app.py

    for table_name, table in dynamo.tables.items():
        print(table_name, table)


Deleting Tables
---------------

If, for some reason, you'd like to destroy all of your predefined DynamoDB
tables, flask-dynamo can also help you with that.

The below code snippet will destroy all of your predefined DynamoDB tables::

    # app.py

    dynamo.destroy_all()

.. note::
    Please be *extremely* careful when running this -- it has the potential to
    completely destroy your application's data!


Using DynamoDB Local
--------------------

If you'd like to use a local DynamoDB instance, flask-dynamo can help you.  The
only change you need to make is to your configuration.  By specifying a few
extra configuration variables, you'll be able to connect to your local DynamoDB
instance as opposed to the 'real' AWS cloud service -- this is great for testing
things out.

For more information about DynamoDB local, read the official `DynamoDB Local
documentation`_.

The settings you need to set are:

- ``DYNAMO_ENABLE_LOCAL`` - Set this to ``True``.
- ``DYNAMO_LOCAL_HOST`` - Set this to your local DB hostname -- usually
  ``'localhost'``.
- ``DYNAMO_LOCAL_PORT`` - Set this to your local DB port -- usually ``8000``.

The settings above can be specified in one of two ways, either via environment
variables, or via application configuration options directly, eg::

    app.config['DYNAMO_ENABLE_LOCAL'] = True
    app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
    app.config['DYNAMO_LOCAL_PORT'] = 8000

No other code needs to be changed in order to use DynamoDB Local.


.. _pip: http://pip.readthedocs.org/en/latest/
.. _AWS Console: https://console.aws.amazon.com/iam/home?#security_credential
.. _StackOverflow question: http://stackoverflow.com/questions/5971312/how-to-set-environment-variables-in-python
.. _boto DynamoDB tutorial: http://boto3.readthedocs.io/en/latest/guide/dynamodb.html
.. _DynamoDB Local documentation: http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.DynamoDBLocal.html
