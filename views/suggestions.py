from flask import Response, request
from flask_restful import Resource
from models import User
from . import get_authorized_user_ids
import json
import flask_jwt_extended

class SuggestionsListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        
    @flask_jwt_extended.jwt_required()
    def get(self):
        ids_for_friends = get_authorized_user_ids(self.current_user)
        suggestions = User.query.filter(~User.id.in_(ids_for_friends)).all()

        suggestions_dictionaries = [ 
            suggest.to_dict() for suggest in suggestions
        ]
        return Response(json.dumps(suggestions_dictionaries[0:7]), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        SuggestionsListEndpoint, 
        '/api/suggestions', 
        '/api/suggestions/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
