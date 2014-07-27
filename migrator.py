#!.env/bin/python
import sys
import cassandra
from cassandra.cluster import Cluster

DEFAULT_SETTINGS = dict(nodes = ['192.168.1.114'],
                        keyspace = 'status')

class Migrator(object):
  def __init__(self, **kwargs):
    self.settings = dict(DEFAULT_SETTINGS)
    self.settings.update(kwargs)
    self.cluster = Cluster(self.settings['nodes'])

  def get_session(self):
    return self.cluster.connect(self.keyspace())

  def keyspace(self):
    return self.settings['keyspace']

  def create_keyspace(self):
    try:
      self.cluster.connect().execute(
          """
          CREATE KEYSPACE %s
          WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
          """ % self.keyspace()
      )
    except cassandra.AlreadyExists as e:
      print "    %s" % e.message


  def create_tables(self):
    try:

      self.get_session().execute(
        """
        CREATE TABLE stats (
          id uuid,
          created_at timestamp,
          site text,
          service text,
          message text,
          description text,
          state int,
          PRIMARY KEY (id)
        );
        """
      )
    except cassandra.AlreadyExists as e:
      print "    %s" % e.message

  def create_indicies(self):
    self.create_index("created_at")
    self.create_index("site")
    self.create_index("service")


  def create_index(self, name):
    try:
      self.get_session().execute("CREATE INDEX %s_key on stats (%s);" % (name, name))
    except cassandra.InvalidRequest as e:
      print "    %s" % e.message

  def destroy_all_the_things(self):
    # do we REALLY want this method here? or just in the tests?
    self.get_session().execute("DROP KEYSPACE %s" % self.keyspace())

  def destroy_the_tables(self):
    self.get_session().execute("DROP TABLE stats")

  def migrate(self):
    print "initializing cluster %s" % self.settings['nodes']
    self.create_keyspace()
    self.create_tables()
    self.create_indicies()
    print "done."
