from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)


# Implement REST Resource
class Users(Resource):

    def post(self):
        new_user = request.json

        user_collection = app.db.users

        result = user_collection.insert_one(new_user)

        user = user_collection.find_one({"_id": ObjectId(result.inserted_id)})

        return user

    def get(self, user_id):
        user_collection = app.db.users
        user = user_collection.find_one({"_id": ObjectId(user_id)})

        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return user

    def delte(self, user_id):
        ...

    def put(self, user_id):
        ...

# Add REST resource to API
api.add_resource(Users, '/users/', '/users/<string:user_id>')


# Implement REST Resource
class Trips(Resource):

    def post(self):
        new_trip = request.json

        trip_collection = app.db.trips

        result = trip_collection.insert_one(new_trip)

        trip = trip_collection.find_one({"_id": ObjectId(result.inserted_id)})

        return trip

    def get(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})

        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip

    def delte(self, trip_id):
        trip = self.get(trip_id)
        trip_collection = app.db.trips
        trip_collection.remove({trip})

        return trip.trip_id

    def put(self, trip_id):
        ...

# Add REST resource to API
api.add_resource(Trips, '/trips/', '/trips/<string:trip_id>')


# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
