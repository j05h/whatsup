#!.env/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

app = Flask(__name__)

# TODO: should be configured
cluster = Cluster(['192.168.1.114'])

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'testing'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

@app.route('/api/v1.0/status', methods = ['GET'])
@auth.login_required
def get_stati():
    rows = get_session().execute('SELECT * from stats');
    return jsonify( { 'status': rows } )

@app.route('/api/v1.0/status/today', methods = ['GET'])
@auth.login_required
def get_today():
    rows = get_session().execute('SELECT * from stats');
    return jsonify( { 'status': rows } )

@app.route('/api/v1.0/status/<string:status_id>', methods = ['GET'])
@auth.login_required
def get_status(status_id):
    row = get_session().execute('SELECT * from stats WHERE id = '+status_id)
    if not row:
        abort(404, status_id)
    return jsonify( { 'status': row } )

def has_status_keys(json):
    return ('site' in json and
            'service' in json and
            'message' in json and
            'state' in json)

@app.route('/api/v1.0/status', methods = ['POST'])
@auth.login_required
def create_status():
    if not request.json or not has_status_keys(request.json):
        abort(400, "Missing JSON or keys in "+request.data)
    status = get_session().execute(
        """
        INSERT INTO stats (id, created_at, site, service, message, description, state)
        VALUES (uuid(), dateof(now()), %s, %s, %s, %s, %s)
        """,
        [
            request.json['site'],
            request.json['service'],
            request.json['message'],
            request.json.get('description', ''),
            int(request.json['state'])
        ]
    )

    return jsonify( { 'status': 'success' } ), 201

@app.route('/api/v1.0/status/<string:status_id>', methods = ['PUT'])
@auth.login_required
def update_status(status_id):
    status = filter(lambda t: t['id'] == status_id, status)
    if len(status) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'site' in request.json and type(request.json['site']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'state' in request.json and type(request.json['state']) is not int:
        abort(400)
    status[0]['site'] = request.json.get('site', status[0]['site'])
    status[0]['description'] = request.json.get('description', status[0]['description'])
    status[0]['state'] = request.json.get('state', status[0]['state'])
    return jsonify( { 'status': status[0] } )

@app.route('/api/v1.0/status/<int:status_id>', methods = ['DELETE'])
@auth.login_required
def delete_status(status_id):
    status = filter(lambda t: t['id'] == status_id, status)
    if len(status) == 0:
        abort(404)
    status.remove(status[0])
    return jsonify( { 'result': True } )

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def get_session():
    session = cluster.connect('status')
    session.row_factory = dict_factory
    return session

# TODO: Do we need this?
def make_public(status):
    new_status = {}
    for field in status:
        if field == 'id':
            new_status['uri'] = url_for('get_status', status_id = status['id'], _external = True)
            new_status['uuid'] = status['id']
        else:
            new_status[field] = status[field]
    return new_status

if __name__ == '__main__':
    app.run(debug = True)
