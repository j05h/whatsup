CREATE KEYSPACE status WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

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

CREATE INDEX  created_at_key on stats (created_at);
CREATE INDEX  site_key       on stats (site);
CREATE INDEX  service_key    on stats (service);

