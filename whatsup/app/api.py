from whatsup.app import app
from whatsup.status import Status
from flask import Flask, json, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth

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
    return json.dumps({ 'status': Status().current() })

@app.route('/api/v1.0/status/current', methods = ['GET'])
@auth.login_required
def get_today():
    return json.dumps({ 'status': Status().current() })

@app.route('/api/v1.0/status/<string:status_id>', methods = ['GET'])
@auth.login_required
def get_status(status_id):
    row = Status().get(status_id)
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

    Status().add(request.json)

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
