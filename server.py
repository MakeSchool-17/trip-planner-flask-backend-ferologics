from flask import Flask, request, Response, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
from functools import wraps
import bcrypt

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)
app.bcrypt_rounds = 8


def check_auth(username, password):

    user_collection = app.db.users

    # look for the password in the database
    user = user_collection.find_one({"username": username})
    if user is None:
        return False

    pwd = user["password"]
    # encode password for camparision
    encoded_password = pwd.encode("utf-8")

    usernames_match = username == user["username"]
    passwords_match = bcrypt.hashpw(password.encode("utf-8"), encoded_password) == encoded_password
    # return if matching usernames and passwords
    return  usernames_match and passwords_match

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {"error": "Basic Auth Required."}
            response = jsonify(message)
            response.status_code = 401
            return response
        return f(*args, **kwargs)
    return decorated

# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
                                                # USER
# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
class Users(Resource):

    def post(self):
        # new user JSON request in form [username:str, password:str]
        new_user = request.json
        user_collection = app.db.users

        # encode the password
        password = new_user["password"].encode("utf-8")

        # hash pw
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(app.bcrypt_rounds))
        dec_hashed = hashed.decode("utf-8")  # without the b'

        # store along with the user name
        result = user_collection.insert_one({"username": new_user["username"], "password": dec_hashed})

        user = user_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return user

    @requires_auth
    def get(self, user_id): # TODO - update this to not use the user ID
        user_collection = app.db.users
        user = user_collection.find_one({"_id": ObjectId(user_id)})

        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return user

    @requires_auth
    def put(self, user_id): # TODO - update this to not use the user ID
        new_data = request.json

        user_collection = app.db.users
        result = user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": new_data})

        response = jsonify(data=[])
        if result.modified_count == 0:
            response.status_code = 404
            return response
        else:
            response.status_code = 200
            return response

# Add REST resource to API
api.add_resource(Users, '/users/', '/users/<string:user_id>')

# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
                                                # TRIP
# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
class Trips(Resource):

    @requires_auth
    def post(self):
        new_trip = request.json
        trip_collection = app.db.trips

        result = trip_collection.insert_one(new_trip)
        trip = trip_collection.find_one({"_id": ObjectId(result.inserted_id)})

        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip

    @requires_auth
    def get(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})

        response = jsonify(data=[])
        if trip is None:
            response.status_code = 404
            return response

        elif trip["user"] != request.authorization["username"]:
            response.status_code = 401
            return response
        else:
            return trip

    @requires_auth
    def delete(self, trip_id): # TODO - update this to not use the ID
        trip_collection = app.db.trips
        result = trip_collection.delete_one({"_id": ObjectId(trip_id)})

        response = jsonify(data=[])
        if result.deleted_count == 0:
            response.status_code = 404
            return response
        else:
            response.status_code = 200
            return response

    @requires_auth
    def put(self, trip_id): # TODO - update this to not use the ID

        # setup
        new_data = request.json
        trip_collection = app.db.trips
        response = jsonify(data=[])

        # escape if the trip to be modified does not belong to the user
        trip_to_modify = trip_collection.find_one( {"_id": ObjectId( trip_id )} )

        if trip_to_modify["user"] != request.authorization["username"]:
            response.status_code = 401
            return response
        else:  # otherwise update the trip
            update_trip_result = trip_collection.update_one( {"_id": ObjectId( trip_id )}, {"$set": new_data} )

            response.status_code = 404 if ( update_trip_result.modified_count == 0 ) else 200

            return response

# Add REST resource to API
api.add_resource(Trips, '/trips/', '/trips/<string:trip_id>')


# provide a custom JSON serializer for flask_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
