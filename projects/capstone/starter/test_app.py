import unittest
import json

from app import create_app
from models import db_drop_and_create_all, setup_db

CASTING_ASSISTANT_TOKEN = {
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InJuZmdSdDAySk5MeVo3MklPaVhKMyJ9.eyJpc3MiOiJodHRwczovL2Rldi1hazVwMGl1YS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEzYjAwZWE4ZjQ3MTQwMDcwZWY3NzJiIiwiYXVkIjoiY2Fwc3RvbmUiLCJpYXQiOjE2MzU0NTU5NTMsImV4cCI6MTYzNTU0MjM1MiwiYXpwIjoiUk5JY08yMHNsTDRIV1ZMWDhRek0zYmpkd2pDd3VVbHgiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIl19.0wxLl_iU4xnUf1BMYdTBBRJjmNH5V5sJqMAHDP-myXyBviEKc3Nu3lVPCR0YknSZ9T4yIcmDkdcM7KOb5rtVq_hmTT-k6IYetyZaF9F_ig7OXs6UuqBiV6M6wHgtTJ_hT_jF7zn0_hUZoKA26U2ZpP3L5Dur3eKeo9unLK33er-3Xl6XqeYy5IL02csA_Yh_FKHHAXPVqANc-BHbgb8Tx-rKuU3UupsKadzfXl3i6UfMf-jN3zKfjzOtxxF0VHoZcy2PNMNkM_SUOZQNRdUXdrp5nu-UA6v4daI9oafeE4UDatuMPqQF90JZWwx5vOFAhztdRVHJRWj3arpmpve3LA'
}

CASTING_DIRECTOR_TOKEN = {
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InJuZmdSdDAySk5MeVo3MklPaVhKMyJ9.eyJpc3MiOiJodHRwczovL2Rldi1hazVwMGl1YS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEzYjAwZWE4ZjQ3MTQwMDcwZWY3NzJiIiwiYXVkIjoiY2Fwc3RvbmUiLCJpYXQiOjE2MzU0NTY4NjgsImV4cCI6MTYzNTU0MzI2NywiYXpwIjoiUk5JY08yMHNsTDRIV1ZMWDhRek0zYmpkd2pDd3VVbHgiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllIiwicG9zdDphY3RvcnMiXX0.P-lVnd8po-HD5oTYQwrdrYfH2TptyNhSGWDTarLPe4v3NdZUbF8JDLN1KeE3P7w-J9pyJqdnFHZlidBXeyX69gsXa7EB9EkqhsAbnKXwmWwpt31qVYdD_GngHOJCRXnctqi2xTKwsYoFpiijDx41nWC2VQ6qB1I9FpYMZuV7gZ5qp_WrGmxs0YpW3EhSks8wvc5cH5Nao4F7421OAii-i7tsTFeixy5xwM2TmRDH35fS1Jm1_lrr19qd9bdqXznr2AQerrgl1TSZoUgXvJsfs4Xo-3QR3-Nj7yuQ3pJh_XMC1nIfYSm_9hSQJobt0P90VhY9gupp-_ZLpsbmFiXzTw'
}

EXECUTIVE_PRODUCER_TOKEN = {
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InJuZmdSdDAySk5MeVo3MklPaVhKMyJ9.eyJpc3MiOiJodHRwczovL2Rldi1hazVwMGl1YS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEzYjAwZWE4ZjQ3MTQwMDcwZWY3NzJiIiwiYXVkIjoiY2Fwc3RvbmUiLCJpYXQiOjE2MzU0NjI3NjIsImV4cCI6MTYzNTU0OTE2MSwiYXpwIjoiUk5JY08yMHNsTDRIV1ZMWDhRek0zYmpkd2pDd3VVbHgiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJkZWxldGU6bW92aWVzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6bW92aWVzIl19.AjTMhaK2Yrf9JAczv88ffNESyq9BKXTFg9MrmvRm2D6YLojdGpWuOuL0vMY8T9P2kc5y4x8O7Y7oxRkar8TRgm3ZbLO-v_2pXezLjRyT7k2eEbbhqAd3UHR-4fK5m0y9ePUYT82NFBfnT8vF4iONc1fNdZIYFGcd4Q4xlR5aPK4ACWNFRknWXiAqKRc4SkrBpdB4ZfmC_O9SQ_PAlWXF1FFISE2q6Z5RmxEpjAQ0rVRkNHfmLvoxdw2T6B8zEufV61BrFCm4YogXTn3KRWc7iyuQWXE4z2L9VL4oForzCKdc9qe8wa_mUINGOIH7qLS5qbACBjqRUDlQ8sOX3A-G4w'
}


class CapstoneTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db_drop_and_create_all()

    def tearDown(self):
        pass

    '''
    Testing each end point for success and failure behaviours
    Using executive producer role for these tests
    '''

    def test_get_actors(self):
        res = self.client().get('/actors', headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']), 2)

    def test_fail_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_get_movies(self):
        res = self.client().get('/movies', headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['movies']), 2)

    def test_fail_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_delete_actor(self):
        res = self.client().delete('/actors/1', headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_fail_delete_actor(self):
        res = self.client().delete('/actors/10', headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_movie(self):
        res = self.client().delete('/movies/2', headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)

    def test_fail_delete_movie(self):
        res = self.client().delete('/movies/10', headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_actor(self):
        res = self.client().post('/actors',
                                 json={'name': 'Zendaya',
                                       'age': 25, 'gender': 'female'},
                                 headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['actor'], {'id': 3, 'name': 'Zendaya', 'age': 25, 'gender': 'FEMALE'})

    def test_fail_create_actor(self):
        res = self.client().post('/actors',
                                 json={'age': 21},
                                 headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_create_movie(self):
        res = self.client().post('/movies',
                                 json={'title': 'Dune',
                                       'release_date': '2021-09-23'},
                                 headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['movie'], {'id': 3, 'title': 'Dune', 'release_date': '2021-09-23'})

    def test_fail_create_movie(self):
        res = self.client().post('/movies',
                                 json={'age': 21},
                                 headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_update_actor(self):
        res = self.client().patch('/actors/1',
                                  json={'name': 'Rebecca', 'age': 17, 'gender': 'female'}, headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['actor'], {'id': 1, 'name': 'Rebecca', 'age': 17, 'gender': 'FEMALE'})

    def test_fail_update_actor(self):
        res = self.client().patch(
            '/actors/10', json={'gender': 'male'}, headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_movie(self):
        res = self.client().patch('/movies/2',
                                  json={'title': 'Jumanji', 'release_date': '2017-12-20'}, headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['movie'], {'id': 2, 'title': 'Jumanji', 'release_date': '2017-12-20'})

    def test_fail_update_movie(self):
        res = self.client().patch('/movies/500',
                                  json={'release_date': '2017-12-20'}, headers=EXECUTIVE_PRODUCER_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    '''
    Testing different roles
    '''

    def test_casting_assistant_update_movie(self):
        res = self.client().patch('/movies/2',
                                  json={'title': 'Jumanji', 'release_date': '2017-12-20'}, headers=CASTING_ASSISTANT_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    def test_casting_assistant_get_actors(self):
        res = self.client().get('/actors', headers=CASTING_ASSISTANT_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']) > 0, True)

    def test_casting_director_update_actor(self):
        res = self.client().patch('/actors/2',
                                  json={'name': 'James', 'age': 29, 'gender': 'male'}, headers=CASTING_DIRECTOR_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['actor'], {'id': 2, 'name': 'James', 'age': 29, 'gender': 'MALE'})

    def test_casting_director_delete_movie(self):
        res = self.client().delete('/movies/2', headers=CASTING_DIRECTOR_TOKEN)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)


if __name__ == "__main__":
    unittest.main()
