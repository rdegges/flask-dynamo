.. _quickstart:
.. module:: flask.ext.dynamo


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

There is also an optional variable you can set:

- ``AWS_REGION`` (*defaults to us-east-1*)

These credentials can be grabbed from your `AWS Console`_.

.. note::
    A full list of Amazon regions can be found here:
    http://docs.aws.amazon.com/general/latest/gr/rande.html#ddb_region

If you're unsure of how to set environment variables, I recommend you check out
this `StackOverflow question`_.


Specify Your Tables
-------------------

The next thing you need to do is tell flask-dynamo which tables you'll be using.

If you're not sure how tables work with DynamoDB, you should read through the
`boto DynamoDB tutorial`_ before continuing.

The way you can specify your tables is by creating an array called
``DYNAMO_TABLES`` (*this is what flask-dynamo uses to set everything up*).

Below is an example::

    # app.py


    from boto.dynamodb2.fields import HashKey
    from boto.dynamodb2.table import Table

    from flask import Flask
    from flask.ext.dynamo import Dynamo

    app = Flask(__name__)
    app.config['DYNAMO_TABLES'] = [
        Table('users', schema=[HashKey('username')]),
        Table('groups', schema=[HashKey('name')]),
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


    from boto.dynamodb2.fields import HashKey
    from boto.dynamodb2.table import Table

    from flask import Flask
    from flask.ext.dynamo import Dynamo

    app = Flask(__name__)
    app.config['DYNAMO_TABLES'] = [
        Table('users', schema=[HashKey('username')]),
        Table('groups', schema=[HashKey('name')]),
    ]

    dynamo = Dynamo(app)

From this point on, you can interact with DynamoDB through the global ``dynamo``
object.


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

Now that you've got everything setup, you can easily access your tables in one
of two ways: you can either access the table directly from the ``dynamo``
global, or you can access the table in a dictionary-like format through
``dynamo.tables``.

Below is an example view which creates a new user account::

    # app.py

    @app.route('/create_user')
    def create_user():
        dynamo.users.put_item(data={
            'username': 'rdegges',
            'first_name': 'Randall',
            'last_name': 'Degges',
            'email': 'r@rdegges.com',
        })

        # or ...

        dynamo.tables['users'].put_item(data={
            'username': 'rdegges',
            'first_name': 'Randall',
            'last_name': 'Degges',
            'email': 'r@rdegges.com',
        })

Either of the above will work the same.

On a related note, you can also use the ``dynamo.tables`` dictionary to iterate
through all of your tables (*this is sometimes useful*).  Here's how you could
iterate over your existing DynamoDB tables::

    # app.py

    with app.app_context():
        for table_name, table in dynamo.tables.iteritems():
            print table_name, table


Deleting Tables
---------------

If, for some reason, you'd like to destroy all of your predefined DynamoDB
tables, flask-dynamo can also help you with that.

The below code snippet will destroy all of your predefined DynamoDB tables::

    # app.py

    with app.app_context():
        dynamo.destroy_all()

.. note::
    Please be *extremely* careful when running this -- it has the potential to
    completely destroy your application's data!


.. _pip: http://pip.readthedocs.org/en/latest/
.. _AWS Console: https://console.aws.amazon.com/iam/home?#security_credential
.. _StackOverflow question: http://stackoverflow.com/questions/5971312/how-to-set-environment-variables-in-python
.. _boto DynamoDB tutorial: http://boto.readthedocs.org/en/latest/dynamodb2_tut.html
