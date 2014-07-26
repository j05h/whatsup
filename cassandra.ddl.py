#!.env/bin/python
import sys
import cassandra
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

CLUSTER_NODES = ['192.168.1.114']
KEYSPACE = 'status'

print "connecting to cluster %s" % CLUSTER_NODES
cluster = Cluster(CLUSTER_NODES)
session = cluster.connect()

print "creating keyspace %s" % KEYSPACE
try:
  session.execute(
      """
      CREATE KEYSPACE %s
      WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
      """ % KEYSPACE
  )
except cassandra.AlreadyExists as e:
  print "    %s" % e.message

session = cluster.connect('status')

print "creating tables in %s" % KEYSPACE
try:

  session.execute(
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

def create_index(session, name):
  print "creating index %s_key" % name
  try:
    session.execute("CREATE INDEX %s_key on stats (%s);" % (name, name))
  except cassandra.InvalidRequest as e:
    print "    %s" % e.message

create_index(session, "created_at")
create_index(session, "site")
create_index(session, "service")

print "done."
