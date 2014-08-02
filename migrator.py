#!.env/bin/python
import sys
import cassandra
from cassandra.cluster import Cluster
from flask import Flask
from flask_environments import Environments

class Migrator(object):
  def __init__(self, config):
    self.config = config
    self.cluster = Cluster(self.config['NODES'])

  def get_session(self):
    return self.cluster.connect(self.keyspace())

  def keyspace(self):
    return self.config['KEYSPACE']

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
          updated_at timestamp,
          year int,
          month int,
          date int,
          site text,
          service text,
          current_state int,
          current_message text,
          worst_state int,
          worst_message text,
          states map <double, text>,
          PRIMARY KEY (service, site, year, month, date)
        );
        """
      )
    except cassandra.AlreadyExists as e:
      print "    %s" % e.message

  def create_indicies(self):
    return True

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
    print "initializing cluster %s in %s" % (self.config['NODES'], self.config['KEYSPACE'])
    self.create_keyspace()
    self.create_tables()
    self.create_indicies()
    print "done."

if __name__ == '__main__':
  app = Flask(__name__)
  env = Environments(app)
  env.from_object('config')

  migrator = Migrator(app.config)
  migrator.migrate()

