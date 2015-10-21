import server
import unittest
import json
from pymongo import MongoClient
import base64


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection("users")
        db.drop_collection("trips")

        # setup authorization credentials
        self.username = "A user"
        self.credentials = "A user:fukayoo"
        self.cred_encoded = base64.b64encode(self.credentials.encode('utf-8'))
        self.auth = {"Authorization" : "Basic " + self.cred_encoded.decode('utf-8')}

        # register user and get response to use in test functions
        self.post_user_response = self.app.post('/users/',
                                                data=json.dumps(
                                                    dict(
                                                        username="A user",
                                                        password="fukayoo"
                                                        )),
                                                content_type='application/json')

        # post a new trip to be used in test functions
        self.post_trip_response = self.app.post('/trips/',
                                            data=json.dumps(
                                                dict(
                                                    name="A trip",
                                                    waypoints=[],
                                                    user=self.username
                                                )),
                                            headers=self.auth,
                                            content_type='application/json')

        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        ...

# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
                                            # USER TESTS
# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»

    # POSTING
    def test_posting_user(self):
        self.post_user_response = self.app.post('/users/',
                                                data=json.dumps(
                                                    dict(
                                                        username="A user",
                                                        password="fukayoo"
                                                        )),
                                                content_type='application/json')

        responseJSON = json.loads(self.post_user_response.data.decode())

        assert 'application/json' in self.post_user_response.content_type
        assert 'A user' in responseJSON["username"]

    # UPDATING
    def test_updating_user(self):

        postedResponseJSON = json.loads(self.post_user_response.data.decode())
        postedObjectID = postedResponseJSON["_id"]

        # update the posted user with a new name
        put_response = self.app.put("/users/" + postedObjectID,
                                    data=json.dumps(
                                        dict(
                                            username="A different user",
                                            password="fukayoo"
                                            )),
                                    headers=self.auth,
                                    content_type="application/json")

        # run assertions to test status code
        self.assertEqual(put_response.status_code, 200)

    # GETTING
    def test_getting_user(self):
        # process the response
        postResponseJSON = json.loads(self.post_user_response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        # get the posted user
        get_user_response = self.app.get('/users/' + postedObjectID, headers=self.auth)
        responseJSON = json.loads(get_user_response.data.decode())

        # run assertions to test for validity
        self.assertEqual(get_user_response.status_code, 200)
        assert 'A user' in responseJSON["username"]

    # GETTING NON-EXISTENT
    def test_getting_non_existent_user(self):
        # test for an arbitrary user
        get_user_response = self.app.get('/users/55f0cbb4236f44b7f0e3cb23', headers=self.auth)
        # run assertions to test status code
        self.assertEqual(get_user_response.status_code, 404)

# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
                                           # TRIP TESTS
# «««««««««««««««««««««««««««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»

    # POSTING
    def test_posting_trip(self):
        self.post_trip_response = self.app.post('/trips/',
                                            data=json.dumps(
                                                dict(
                                                    name="A trip",
                                                    waypoints=[],
                                                    user=self.username
                                                )),
                                            headers=self.auth,
                                            content_type='application/json')

        responseJSON = json.loads(self.post_trip_response.data.decode())

        self.assertEqual(self.post_trip_response.status_code, 200)
        assert 'application/json' in self.post_trip_response.content_type
        assert 'A trip' in responseJSON["name"]

    # UPDATING
    def test_updating_trip(self):
        # import pdb; pdb.set_trace()

        postedResponseJSON = json.loads(self.post_trip_response.data.decode())
        postedObjectID = postedResponseJSON["_id"]

        put_trip_response = self.app.put("/trips/" + postedObjectID,
                                        data=json.dumps(
                                            dict(
                                                name="A different trip",
                                                waipoints=["new waipoint"],
                                                user=self.username
                                            )),
                                        headers=self.auth,
                                        content_type="application/json")

        self.assertEqual(put_trip_response.status_code, 200)

    # GETTING
    def test_getting_trip(self):
        postResponseJSON = json.loads(self.post_trip_response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        get_trip_response = self.app.get('/trips/' + postedObjectID, headers=self.auth)
        responseJSON = json.loads(get_trip_response.data.decode())

        self.assertEqual(get_trip_response.status_code, 200)
        assert 'A trip' in responseJSON["name"]

    # DELETING
    def test_deleting_trip(self):
        postResponseJSON = json.loads(self.post_trip_response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        delete_trip_response = self.app.delete('/trips/' + postedObjectID, headers=self.auth)

        self.assertEqual(delete_trip_response.status_code, 200)

    # GETTING NON-EXISTENT
    def test_getting_non_existent_trip(self):
        get_trip_response = self.app.get('/trips/55f0cbb4236f44b7f0e3cb23', headers=self.auth)
        self.assertEqual(get_trip_response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
