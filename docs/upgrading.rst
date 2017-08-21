.. _upgrading:


Upgrade Guide
=============

This page contains specific upgrading instructions to help you migrate between
flask-dynamo releases.

Version 0.0.8 -> Version 0.1.0
------------------------------

**Changes required!**
* The app.config['DYNAMO_TABLES'] schema needs to be updated to boto3 style. See
  :ref:`quickstart` for examples of how to do this.
* **Note** boto3 is a new requirement.
* **Optional** Use the app factory pattern, and access dynamo via
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
