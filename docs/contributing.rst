.. _contributing:


Contributing
============

Want to contribute to flask-dynamo?  **AWESOME!**

There's only a few things you need to know to get started:

1. All development is done on the `Github repo`_.
2. When you send a pull request, please send it to the ``develop`` branch --
   this is where active development happens.
3. Please add tests if you can -- it'll make accepting your pull requests a lot
   easier!

That's about it!


Setup Your Environment
----------------------

To get started developing, you'll want to fork flask-dynamo on `Github`_.

After that, you'll need to check out the ``develop`` branch, as this is where
you should 'base' your development from::

    $ git clone git@github.com:yourusername/flask-dynamo.git
    $ cd flask-dynamo
    $ git fetch origin develop:develop
    $ git checkout develop

Next, create a new branch that describes the change you want to make::

    $ git checkout -b bug-fix

Next, you'll want to install all of the local dependencies with pip::

    $ pip install -r requirements.txt

After that, you'll want to install the flask-dynamo package in development
mode::

    $ python setup.py develop

Lastly, you'll want to configure your AWS access keys as environment variables
so you can run the tests::

    $ export AWS_ACCESS_KEY_ID=xxx
    $ export AWS_SECRET_ACCESS_KEY=xxx


Running Tests
-------------

After writing some code, you'll need to run the tests to ensure everything is
still working ok!  This can be done by running::

    $ python setup.py test

From the project's root directory.

.. note::
    The tests take a while to run -- this is on purpose, as Amazon rate limits
    your requests.


Submitting Your Pull Request
----------------------------

Now that you've added an awesome feature or fixed a bug, you probably want to
submit your pull request, so let's do it!

First, you'll want to push your topic branch to your Github fork::

    $ git push origin bug-fix

Then, go to Github on your fork, and submit a pull request from your topic
branch into the ``develop`` branch on the main flask-dynamo repository.

That's it!


Thanks!
-------

I'd also like to give you a big shout out for any contributions you make. You
are totally fucking awesome and I love you.

-Randall


.. _Github repo: https://github.com/rdegges/flask-dynamo
.. _Github: https://github.com/rdegges/flask-dynamo
