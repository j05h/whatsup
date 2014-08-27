#!.env/bin/python
import base64
import os
import unittest

from flask import json
from freezegun import freeze_time

from migrator import Migrator

os.environ['FLASK_ENV'] = 'Test'
# should be AFTER FLASK_ENV is set to Test
import whatsup.app as app

class FlaskrTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.env.from_object('whatsup.config')
        print "Testing in %s" % app.app.config['KEYSPACE']
        cls.migrator = Migrator(app.app.config)
        cls.migrator.create_keyspace()
        cls.app = app.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.migrator.destroy_all_the_things()

    def setUp(self):
        self.migrator.create_tables()
        self.migrator.create_indicies()
        basic = ('Basic %s' % base64.b64encode('admin:testing'))
        self.headers = [('Authorization', basic),
                        ('Content-Type', 'application/json')]

    def tearDown(self):
        self.migrator.destroy_the_tables()

    def test_404(self):
        rv = self.app.get('/api/not/here')
        self.assertEqual(404, rv.status_code)

    def test_unauthorized(self):
        rv = self.app.get('/api/v1.0/status')
        self.assertEqual(403, rv.status_code)
        assert 'Unauthorized access' in rv.data

    def test_empty_db(self):
        rv = self.app.get('/api/v1.0/status', headers=self.headers)
        data = json.loads(rv.data)
        assert [] == data['status']

    def json_data(self, **kwargs):
        default = {'site': 'local',
                   'service': 'testing',
                   'message': 'nominal',
                   'state': 1}
        default.update(kwargs)
        return default

    def json_string(self, **kwargs):
        return json.dumps(self.json_data(**kwargs))

    def post_stat(self, **kwargs):
        j = self.json_string(**kwargs)
        h = self.headers + [('Content-Length', len(j))]
        return self.app.post('/api/v1.0/status', data=j, headers=h)

    def test_post_stat(self):
        rv = self.post_stat()
        self.assertEqual(201, rv.status_code)
        data = json.loads(rv.data)
        self.assertEqual('success', data['status'])

    def test_get_current(self):
        with freeze_time("2014-01-02 12:00:01"):
            self.post_stat()
        # populate 4 states on the different services
        self.post_stat(service='foo')
        self.post_stat(service='bar', state=0)
        self.post_stat(service='baz', state=-1)
        self.post_stat(service='qux')

        rv = self.app.get('/api/v1.0/status/current', headers=self.headers)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)
        status = data['status'][0]

        self.assertEqual(4, len(data['status']))
        self.assertEqual(self.json_data()['message'],
                         status['states'][0]['message'])

    def test_get_rolled_up_current(self):
        # populate 4 states across different times
        with freeze_time("2014-01-02 12:00:01"):
            self.post_stat()
        with freeze_time("2014-01-02 12:00:02"):
            self.post_stat(state=0)
        with freeze_time("2014-01-02 12:00:03"):
            self.post_stat(state=-1)
        with freeze_time("2014-01-02 12:00:04"):
            self.post_stat()

        with freeze_time("2014-01-02 13:14:15"):
            rv = self.app.get('/api/v1.0/status/current', headers=self.headers)

        self.assertEqual(200, rv.status_code)

        data = json.loads(rv.data)

        status = data['status'][0]

        self.assertEqual(1, len(data['status']))
        self.assertEqual(4, len(status['states']))
        self.assertEqual(self.json_data()['message'],
                         status['states'][0]['message'])
        self.assertEqual(1, status['current_state'])
        self.assertEqual(-1, status['worst_state'])

if __name__ == '__main__':
    unittest.main()
