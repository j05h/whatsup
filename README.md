### ABOUT

  This is (so far) a status API to keep track of upness or downness of services
  at various sites.  It is mostly a super thin layer on top of Cassandra.

  Architecturally, it is very simple.

```
    <nginx/apache> -> <flask app server> -> <cassandra cluster>
```

  Flask app is completely stateless, allowing for easy horizontal scalability.
  There are no complex authentication systems required. The Cassandra cluster
  (as well as the web front ends) should scale across multiple datacenters
  and regions to allow for the most resiliency with the service.

### TESTING

Requirements:

* Ansible >= 1.6
* Vagrant >= 1.6
* tox

```
    $ vagrant up
    $ tox
```

### USAGE:

```
    $ vagrant up
    $ ./newb
    $ ./run.py
```

####  Pull the latest status:

```
    curl -u admin:testing localhost:5000/api/v1.0/status/current
```

####  Update a service:

```
    curl -u admin:testing -i -H "Content-Type: application/json" -X POST -d \
      '{"site":"localhost","service":"testing","message":"nominal","state":1}' \
      localhost:5000/api/v1.0/status
```

```
    curl -u admin:testing -i -H "Content-Type: application/json" -X POST -d \
      '{"site":"remotehost","service":"verifying","message":"not quite right","state":0}' \
      localhost:5000/api/v1.0/status
```

```
    curl -u admin:testing -i -H "Content-Type: application/json" -X POST -d \
      '{"site":"localhost","service":"checking","message":"borked","state":-1}' \
      localhost:5000/api/v1.0/status
```

    'site' is the location in which the service runs
    'service' is the name of the service
    'messsage' is a detailed message
    'description' is a more detailed description of the error
    'state' is either 1 (UP); 0 (COMPROMISED); -1 (DOWN)
