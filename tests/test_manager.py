"""Tests for our manager."""
from __future__ import print_function


from os import environ
from uuid import uuid4

import pytest
from flask import Flask, current_app
from flask_dynamo import Dynamo, ConfigurationError

def make_table(table_name, name, _type):
    return dict(
        TableName=table_name,
        KeySchema=[dict(AttributeName=name, KeyType='HASH')],
        AttributeDefinitions=[dict(AttributeName=name, AttributeType=_type)],
        ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5),
    )

@pytest.fixture
def app(request):
    app = Flask(__name__)
    prefix = uuid4().hex
    app.config['DEBUG'] = True
    app.config['DYNAMO_TABLES'] = [
        make_table('%s-phones' % prefix, 'number', 'N'),
        make_table('%s-users' % prefix, 'username', 'S'),
    ]
    return app

@pytest.fixture
def local_app(app):
    app.config['DYNAMO_ENABLE_LOCAL'] = True
    return app

@pytest.fixture
def dynamo(app, request):
    dynamo = Dynamo(app)
    return dynamo

@pytest.yield_fixture
def active_dynamo(dynamo, app):
    with app.app_context():
        try:
            dynamo.create_all(wait=True)
            yield dynamo
        finally:
            try:
                dynamo.destroy_all()
            except Exception as e:
                print("Unable to clean up: {}".format(e))

def test_extension_classes():
    import flask_dynamo.errors
    import flask_dynamo.manager

    assert flask_dynamo.manager.Dynamo == Dynamo
    assert flask_dynamo.errors.ConfigurationError == ConfigurationError

def test_settings(app, dynamo):
    assert len(app.config['DYNAMO_TABLES']) == 2
    assert app.config['AWS_ACCESS_KEY_ID'] == environ.get('AWS_ACCESS_KEY_ID')
    assert app.config['AWS_SECRET_ACCESS_KEY'] == environ.get('AWS_SECRET_ACCESS_KEY')
    assert app.config['AWS_REGION'] == environ.get('AWS_REGION') if environ.get('AWS_REGION') else Dynamo.DEFAULT_REGION

def test_local_settings_missing_local_configs(local_app):
    with pytest.raises(ConfigurationError):
        Dynamo(local_app)

def test_local_settings_missing_local_port(local_app):
    local_app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
    with pytest.raises(ConfigurationError):
        Dynamo(local_app)

def test_local_settings_missing_local_host(local_app):
    local_app.config['DYNAMO_LOCAL_PORT'] = 8000
    with pytest.raises(ConfigurationError):
        Dynamo(local_app)

def test_valid_local_settings(local_app):
    local_app.config['DYNAMO_LOCAL_PORT'] = 8000
    local_app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
    Dynamo(local_app)

def test_connection(app, dynamo):
    with app.app_context():
        assert hasattr(dynamo.connection, 'meta')
        assert hasattr(dynamo.connection.meta, 'client')

def test_table_access(active_dynamo, app):
    with app.app_context():
        assert len(active_dynamo.tables.keys()) == 2
        for table_name, table in active_dynamo.tables.items():
            assert active_dynamo.tables[table_name].name == table_name
            assert current_app.extensions['dynamo'].tables[table_name].name == table_name
