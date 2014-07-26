#!.env/bin/python
import sys
import cassandra
from cassandra.cluster import Cluster

CLUSTER_NODES = ['192.168.1.114']
KEYSPACE = 'status'

cluster = Cluster(CLUSTER_NODES)

def get_session():
  return cluster.connect(KEYSPACE)

def create_keyspace():

  print "creating keyspace %s" % KEYSPACE
  try:
    cluster.connect().execute(
        """
        CREATE KEYSPACE %s
        WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
        """ % KEYSPACE
    )
  except cassandra.AlreadyExists as e:
    print "    %s" % e.message


def create_tables():
  print "creating tables in %s" % KEYSPACE
  try:

    get_session().execute(
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

def create_indicies():
  create_index("created_at")
  create_index("site")
  create_index("service")


def create_index(name):
  print "creating index %s_key" % name
  try:
    get_session().execute("CREATE INDEX %s_key on stats (%s);" % (name, name))
  except cassandra.InvalidRequest as e:
    print "    %s" % e.message


print "initializing cluster %s" % CLUSTER_NODES
create_keyspace()
create_tables()
create_indicies()
print "done."
