from flask import json


class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'startswith') and obj.startswith('{'):
            return json.dumps(json.loads(obj))
        return json.JSONEncoder.default(self, obj)
