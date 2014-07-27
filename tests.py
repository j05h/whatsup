#!.env/bin/python
import os

os.environ['FLASK_ENV'] = 'test'

import app
import unittest
import tempfile
#### REMOVE THIS AND ITS EVIL KIN import testing.cassandra
import uuid
import base64
from migrator import Migrator
from werkzeug.datastructures import Headers
from werkzeug.test import Client
from flask import json, jsonify

class FlaskrTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    app.env.from_object('config')
    cls.migrator = Migrator(app.app.config)
    cls.migrator.create_keyspace()
    cls.app = app.app.test_client()

  def setUp(self):
    self.migrator.create_tables()
    basic = ('Basic %s' % base64.b64encode('admin:testing'))
    self.headers = dict(Authorization = basic)

  @classmethod
  def tearDownClass(cls):
    cls.migrator.destroy_all_the_things()

  def tearDown(self):
    self.migrator.destroy_the_tables()

  def test_404(self):
    rv = self.app.get('/api/not/here')
    assert 404 == rv.status_code

  def test_unauthorized(self):
    rv = self.app.get('/api/v1.0/status')
    assert 403 == rv.status_code
    assert 'Unauthorized access' in rv.data

  def test_empty_db(self):
    rv = self.app.open('/api/v1.0/status', headers = self.headers)
    data = json.loads(rv.data)
    assert [] == data['status']

if __name__ == '__main__':
  unittest.main()
