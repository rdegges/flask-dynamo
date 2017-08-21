.. _upgrading:


Upgrade Guide
=============

This page contains specific upgrading instructions to help you migrate between
flask-dynamo releases.


Version 0.1.0 -> Version 0.1.1
------------------------------

**No changes needed!**


Version 0.0.8 -> Version 0.1.0
------------------------------

**Changes required.**

* The ``app.config['DYNAMO_TABLES']`` schema needs to be updated to `boto3
  <https://boto3.readthedocs.io/en/latest/guide/dynamodb.html#creating-a-new-table>`_
  style. See :ref:`Specify Your Tables <specify-your-tables>` for examples of
  how to do this.
* **OPTIONAL**: Use the app factory pattern, and access Dynamo via
  ``Flask.current_app.extensions['dynamodb']``


Version 0.0.7 -> Version 0.0.8
------------------------------

**No changes needed!**


Version 0.0.6 -> Version 0.0.7
------------------------------

**No changes needed!**


Version 0.0.5 -> Version 0.0.6
------------------------------

**No changes needed!**


Version 0.0.4 -> Version 0.0.5
------------------------------

**No changes needed!**


Version 0.0.3 -> Version 0.0.4
------------------------------

**No changes needed!**


Version 0.0.2 -> Version 0.0.3
------------------------------

**No changes needed!**


Version 0.0.1 -> Version 0.0.2
------------------------------

**No changes needed!**
