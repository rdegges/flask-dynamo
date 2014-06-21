# flask-dynamo

DynamoDB integration for Flask.


![Dragon Sketch][]


## Meta

- Author: Randall Degges
- Email: r@rdegges.com
- Site: http://www.rdegges.com
- Status: maintained, active


## Purpose

I love using Amazon's [DynamoDB][] database -- it's incredibly fast, infinitely
scalable, and has a beautifully simple API.

Of all the NoSQL databases that exist, Dynamo is the simplest to deploy and run
in high-traffic production environments, and incredibly simple to get started
with / grow into.

I've been using it for several years now, and couldn't be happier.

The only problem I had using Dynamo with Flask is lack of an official extension
-- so I created one!

This extension makes working with Dynamo in Flask projects simple and painless
-- and doesn't get in your way at all (*no need to compromise!*).


## Installation

To install `flask-dynamo`, you need to use [pip][]:

```console
$ pip install flask-dynamo
```

If you'd like to upgrade your existing `flask-dynamo` installation, you can do
so by running:

```console
$ pip install -U flask-dynamo
```


## Configuration

Configuring `flask-dynamo` is easy.  Firstly, you need to specify your AWS
credentials as environment variables.  You can do this in various ways -- if
you aren't sure how, see [this thread][].

The variables you need to set are:

- `AWS_ACCESS_KEY_ID` (*your AWS access key ID*)
- `AWS_SECRET_ACCESS_KEY` (*your AWS secret access key*)

You can also optionally set:

- `AWS_REGION` (*the AWS region you'd like to use, defaults to us-east-1*)

Next, you'll need to define your DynamoDB tables using the standard [boto][]
interface.  You're expected to define every table your application will need to
use, and put these tables into a big array called `DYNAMO_TABLES`, like so:

```python
# app.py

from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
from flask import Flask

# create your flask app
app = Flask(__name__)

# ...

app.config['DYNAMO_TABLES'] = [
    Table('users', schema=[HashKey('username')]),
    Table('groups', schema=[HashKey('name')]),
    # ...
]
```

By specifying your tables manually, `flask-dynamo` is able to efficiently handle
table retrieval, creation, and deletion on your behalf.

Next, you need to import `flask-dynamo` and initialize the extension:

```python
# app.py

from flask.ext.dynamo import Dynamo

# ...

dynamo = Dynamo(app)
```

Now you should be ready to go!

Below is a full Flask app as an example (*just to be explicit*):

```python
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


# Define your Flask code here.


if __name__ == '__main__':
    app.run()
```

**NOTE**: The above example assumes you've already set the proper environment
variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.


## Usage

Now that you've gotten `flask-dynamo` configured, let's take a look at what it
offers you.


### Create all Tables

The first thing you might want to do is create all of your DynamoDB tables at
once.  Instead of doing this manually, `flask-dynamo` ships with a helpful tool
to make the process easier.

After defining your `DYNAMO_TABLES` configuration value, you can automatically
create all your tables by using the following code snippet anywhere in your
code base:

```python
with app.app_context():
    dynamo.create_all()
```

The above code will create all tables you've defined in `DYNAMO_TABLES`,
respecting all configuration options you pass (*including throughput, etc.*)
when specifying the tables.


### Destroy all Tables

In a similar fashion to the above, you can also easily *destroy* all of your
DynamoDB tables.

You can destroy all tables with the following code snippet:

```python
with app.app_context():
    dynamo.destroy_all()
```

**NOTE**: Please be *extremely* careful when running this -- it has the
potential to completely destroy your application's data.


### Access Tables

The nicest features of `flask-dynamo` is simple table access.

From inside a view, you can easily reference your tables directly off the
`dynamo` object, as well as through the `dynamo.tables` dictionary.  For
instance:

```python
@app.route('/create_user')
def create_user():
    dynamo.users.put_item(data={
        'username': 'rdegges',
        'first_name': 'Randall',
        'last_name': 'Degges',
        'email': 'r@rdegges.com',
    })
    return 'OK!'

# or ...

@app.route('/create_user')
def create_user():
    dynamo.tables['users'].put_item(data={
        'username': 'rdegges',
        'first_name': 'Randall',
        'last_name': 'Degges',
        'email': 'r@rdegges.com',
    })
    return 'OK!'
```

Both of the above examples are equivalent.


## Questions?

Got any questions, comments, or feedback?  If so, please [drop me a line][].  If
you found a bug or have a feature request, please use the [issue tracker][].

Thanks!  &lt;3333


## Changes

This section covers all library changes and release notes.


### Version 0.0.1

*Released June 21, 2014.*

- First release ever, woo!


  [Dragon Sketch]: https://github.com/rdegges/flask-dynamo/raw/master/assets/dragon-sketch.jpg "Dragon Sketch"
  [DynamoDB]: http://aws.amazon.com/dynamodb/ "DynamoDB"
  [pip]: http://pip.readthedocs.org/en/latest/ "pip"
  [this thread]: http://stackoverflow.com/questions/5971312/how-to-set-environment-variables-in-python "How to Set Environment Variables in Python"
  [boto]: http://boto.readthedocs.org/en/latest/dynamodb2_tut.html "Boto DynamoDB"
  [drop me a line]: mailto:r@rdegges.com
  [issue tracker]: https://github.com/rdegges/flask-dynamo/issues "Flask-Dynamo Issue Tracker"
