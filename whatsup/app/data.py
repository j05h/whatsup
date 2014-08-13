from cassandra.cluster import Cluster
from cassandra.query import dict_factory

from whatsup.app import app


class Data(object):
    def __init__(self):
        self.cluster = Cluster(app.config['NODES'])

    def get_session(self):
        session = self.cluster.connect(app.config['KEYSPACE'])
        session.row_factory = dict_factory
        return session
