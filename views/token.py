import mimetypes
from os import access
from telnetlib import STATUS
from models import User
import flask_jwt_extended
from flask import Response, request
from flask_restful import Resource
import json
from datetime import timezone, datetime, timedelta

class AccessTokenEndpoint(Resource):

    def post(self):
        body = request.get_json() or {}
        print(body)

        # check username and log in credentials. If valid, return tokens
        username = body.get('username')
        password = body.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None:
            return Response(json.dumps({
                "message": "Username not found"
            }), status=401)
        if user.check_password(password):
            access_token = flask_jwt_extended.create_access_token(identity=user.id)
            return Response(json.dumps({ 
                "access_token": access_token, 
                "refresh_token": flask_jwt_extended.create_refresh_token(identity= user.id)
            }), mimetype="application/json", status=200)
        else:
            return Response(json.dumps({
                "message": "Incorrect Password"
            }), status=401)

class RefreshTokenEndpoint(Resource):
    
    def post(self):

        body = request.get_json() or {}
        refresh_token = body.get('refresh_token')
        print(refresh_token)

        if refresh_token:
            try:
                decodedt = flask_jwt_extended.decode_token(refresh_token)
                exp_timestamp = decodedt.get("exp")
                user_id = decodedt.get("sub")
                curr_timestamp = datetime.timestamp(datetime.now(timezone.utc))
            except:
                return Response(json.dumps({
                    "Message": "Error"
                }), mimetype="application/json", status=400)
            if exp_timestamp < curr_timestamp:
                print('token has expired')
                return Response(json.dumps({
                    "Message": "Expired: refresh token has expired"
                }), mimetype="application/json", status=401)
            else:
                print('new access token issued')
                return Response(json.dumps({
                    "access_token": flask_jwt_extended.create_access_token(identity=user_id)
                }), mimetype="application/json", status=200)
        else:
            print('missing refresh token')
            return Response(json.dumps({
                "Message": "Missing: Need to include Refresh token"
            }), mimetype="application/json", status=401)


def initialize_routes(api):
    api.add_resource(
        AccessTokenEndpoint, 
        '/api/token', '/api/token/'
    )

    api.add_resource(
        RefreshTokenEndpoint, 
        '/api/token/refresh', '/api/token/refresh/'
    )