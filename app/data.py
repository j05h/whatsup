from app import app
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


# TODO: should be configured
DEFAULT_SETTINGS = dict(nodes = ['192.168.1.114'],
                        keyspace = 'status')

class Data(object):
  def __init__(self, **kwargs):
    self.settings = dict(DEFAULT_SETTINGS)
    self.settings.update(kwargs)
    self.settings['keyspace'] = app.config['keyspace']
    self.cluster = Cluster(self.settings['nodes'])

  def get_session(self):
    session = self.cluster.connect(self.settings['keyspace'])
    session.row_factory = dict_factory
    return session

  def today(self):
    return self.get_session().execute('SELECT * from stats');
