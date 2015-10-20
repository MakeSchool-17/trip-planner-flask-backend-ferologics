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

    # TRIPS TESTS
    def test_posting_trip(self):
        response = self.app.post('/trips/',
                                data=json.dumps(
                                    dict(
                                        name="A trip",
                                        data=[])),
                                        headers=self.auth,
                                content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A trip' in responseJSON["name"]

    def test_updating_trip(self):
        response = self.app.post("/trips/",
                                data=json.dumps(
                                    dict(
                                        name="A trip",
                                        data=[])),
                                        headers=self.auth,
                                content_type="application/json")

        postedResponseJSON = json.loads(response.data.decode())
        postedObjectID = postedResponseJSON["_id"]

        response = self.app.put("/trips/" + postedObjectID, headers=self.auth)
        self.assertEqual(response.status_code, 200)

    def test_getting_trip(self):
        response = self.app.post('/trips/', data=json.dumps(dict(name="Another trip")),
        headers=self.auth, content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/' + postedObjectID, headers=self.auth)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another trip' in responseJSON["name"]

    def test_deleting_trip(self):
        response = self.app.post('/trips/', data=json.dumps(dict(name="Another trip")),
        headers=self.auth, content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trips/' + postedObjectID, headers=self.auth)

        self.assertEqual(response.status_code, 200)

    def test_getting_non_existent_trip(self):
        response = self.app.get('/trips/55f0cbb4236f44b7f0e3cb23', headers=self.auth)
        self.assertEqual(response.status_code, 404)

# =====================================================================================================================
# =====================================================================================================================
    # USER TESTS
    def test_posting_user(self):
        response = self.app.post('/users/', data=json.dumps(dict(username="A user", password="fukayoo")),
        headers=self.auth, content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        assert 'application/json' in response.content_type
        assert 'A user' in responseJSON["username"]
        assert 'fukayoo' in responseJSON["password"]

    def test_updating_user(self):
        response = self.app.post("/users/", data=json.dumps(dict(username="A user", password="fukayoo")),
        headers=self.auth, content_type="application/json")

        postedResponseJSON = json.loads(response.data.decode())
        postedObjectID = postedResponseJSON["_id"]

        response = self.app.put("/users/" + postedObjectID,
                                data=json.dumps(
                                    dict(
                                        username="A different user",
                                        password="fukayoo")),
                                headers=self.auth,
                                content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_getting_user(self):
        response = self.app.post('/users/', data=json.dumps(dict(username="A user", password="fukayoo")),
        headers=self.auth, content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/users/' + postedObjectID, headers=self.auth)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'A user' in responseJSON["username"]

    def test_getting_non_existent_user(self):
        response = self.app.get('/users/55f0cbb4236f44b7f0e3cb23', headers=self.auth,)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
