import server
import unittest
import json
from pymongo import MongoClient
import base64


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # setup authorization credentials
        credentials = "admin:secret"
        cred_encoded = base64.b64encode(credentials.encode('utf-8'))
        self.auth = {"Authorization" : "Basic " + cred_encoded.decode('utf-8')}

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('trips')
        db.drop_collection('users')

# =====================================================================================================================
                                            # USER TESTS
# =====================================================================================================================

    # POSTING
    def test_posting_user(self):
        response = self.app.post('/users/',
                                data=json.dumps(
                                    dict(
                                        username="A user",
                                        password="fukayoo"
                                        )),
                                headers=self.auth,
                                content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        assert 'application/json' in response.content_type
        assert 'A user' in responseJSON["username"]
        assert 'fukayoo' in responseJSON["password"]

    # UPDATING
    def test_updating_user(self):
        response = self.app.post("/users/",
                                data=json.dumps(
                                    dict(
                                        username="A user",
                                        password="fukayoo"
                                        )),
                                headers=self.auth,
                                content_type="application/json")

        postedResponseJSON = json.loads(response.data.decode())
        postedObjectID = postedResponseJSON["_id"]

        # update the posted user with a new name
        response = self.app.put("/users/" + postedObjectID,
                                data=json.dumps(
                                    dict(
                                        username="A different user",
                                        password="fukayoo"
                                        )),
                                headers=self.auth,
                                content_type="application/json")

        # run assertions to test status code
        self.assertEqual(response.status_code, 200)

    # GETTING
    def test_getting_user(self):
        # post user object with username and password --> get response
        response = self.app.post('/users/',
                                data=json.dumps(
                                    dict(
                                        username="A user",
                                        password="fukayoo"
                                        )),
                                headers=self.auth,
                                content_type='application/json')

        # process the response
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        # get the posted user
        response = self.app.get('/users/' + postedObjectID, headers=self.auth)
        responseJSON = json.loads(response.data.decode())

        # run assertions to test for validity
        self.assertEqual(response.status_code, 200)
        assert 'A user' in responseJSON["username"]

    # GETTING NON-EXISTENT
    def test_getting_non_existent_user(self):
        # test for an arbitrary user
        response = self.app.get('/users/55f0cbb4236f44b7f0e3cb23', headers=self.auth,)
        # run assertions to test status code
        self.assertEqual(response.status_code, 404)

# =====================================================================================================================
                                           # TRIP TESTS
# =====================================================================================================================

    # POSTING
    def test_posting_trip(self):
        response = self.app.post('/trips/',
                                data=json.dumps(
                                    dict(
                                        name="A trip",
                                        waypoints=[]
                                        )),
                                headers=self.auth,
                                content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A trip' in responseJSON["name"]

    # UPDATING
    def test_updating_trip(self):
        response = self.app.post("/trips/",
                                data=json.dumps(
                                    dict(
                                        name="A trip",
                                        waypoints=[]
                                        )),
                                headers=self.auth,
                                content_type="application/json")

        postedResponseJSON = json.loads(response.data.decode())
        postedObjectID = postedResponseJSON["_id"]

        response = self.app.put("/trips/" + postedObjectID, headers=self.auth)
        self.assertEqual(response.status_code, 200)

    # GETTING
    def test_getting_trip(self):
        response = self.app.post('/trips/',
                                data=json.dumps(
                                    dict(
                                        name="Another trip",
                                        waypoints=[]
                                        )),
                                headers=self.auth,
                                content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/' + postedObjectID, headers=self.auth)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another trip' in responseJSON["name"]

    # DELETING
    def test_deleting_trip(self):
        response = self.app.post('/trips/',
                                data=json.dumps(
                                    dict(
                                        name="Another trip",
                                        waypoints=[]
                                        )),
                                headers=self.auth,
                                content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trips/' + postedObjectID, headers=self.auth)

        self.assertEqual(response.status_code, 200)

    # GETTING NON-EXISTENT
    def test_getting_non_existent_trip(self):
        response = self.app.get('/trips/55f0cbb4236f44b7f0e3cb23', headers=self.auth)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
