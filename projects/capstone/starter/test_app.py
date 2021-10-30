import unittest
import json
import os

from app import create_app
from models import db_drop_and_create_all, setup_db

CASTING_ASSISTANT_HEADER = {
    'Authorization': 'Bearer {}'
    .format(os.environ.get('CASTING_ASSISTANT_TOKEN'))
}

CASTING_DIRECTOR_HEADER = {
    'Authorization': 'Bearer {}'
    .format(os.environ.get('CASTING_DIRECTOR_TOKEN'))
}

EXECUTIVE_PRODUCER_HEADER = {
    'Authorization': 'Bearer {}'
    .format(os.environ.get('EXECUTIVE_PRODUCER_TOKEN'))
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
        res = self.client().get('/actors', headers=EXECUTIVE_PRODUCER_HEADER)
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
        res = self.client().get('/movies', headers=EXECUTIVE_PRODUCER_HEADER)
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
        res = self.client().delete('/actors/1',
                                   headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_fail_delete_actor(self):
        res = self.client().delete('/actors/10',
                                   headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_movie(self):
        res = self.client().delete('/movies/2',
                                   headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)

    def test_fail_delete_movie(self):
        res = self.client().delete('/movies/10',
                                   headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_actor(self):
        res = self.client().post('/actors',
                                 json={'name': 'Zendaya',
                                       'age': 25, 'gender': 'female'},
                                 headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['actor'], {'id': 3, 'name': 'Zendaya',
                            'age': 25, 'gender': 'FEMALE'})

    def test_fail_create_actor(self):
        res = self.client().post('/actors',
                                 json={'age': 21},
                                 headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_create_movie(self):
        res = self.client().post('/movies',
                                 json={'title': 'Dune',
                                       'release_date': '2021-09-23'},
                                 headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['movie'], {'id': 3, 'title': 'Dune',
                            'release_date': '2021-09-23'})

    def test_fail_create_movie(self):
        res = self.client().post('/movies',
                                 json={'age': 21},
                                 headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_update_actor(self):
        res = self.client().patch('/actors/1',
                                  json={'name': 'Rebecca',
                                        'age': 17, 'gender': 'female'},
                                  headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['actor'], {'id': 1, 'name': 'Rebecca',
                            'age': 17, 'gender': 'FEMALE'})

    def test_fail_update_actor(self):
        res = self.client().patch(
            '/actors/10', json={'gender': 'male'},
            headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_movie(self):
        res = self.client().patch('/movies/2',
                                  json={'title': 'Jumanji',
                                        'release_date': '2017-12-20'},
                                  headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['movie'], {'id': 2, 'title': 'Jumanji',
                            'release_date': '2017-12-20'})

    def test_fail_update_movie(self):
        res = self.client().patch('/movies/500',
                                  json={'release_date': '2017-12-20'},
                                  headers=EXECUTIVE_PRODUCER_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    '''
    Testing different roles
    '''

    def test_casting_assistant_update_movie(self):
        res = self.client().patch('/movies/2',
                                  json={'title': 'Jumanji',
                                        'release_date': '2017-12-20'},
                                  headers=CASTING_ASSISTANT_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    def test_casting_assistant_get_actors(self):
        res = self.client().get('/actors', headers=CASTING_ASSISTANT_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']) > 0, True)

    def test_casting_director_update_actor(self):
        res = self.client().patch('/actors/2',
                                  json={'name': 'James',
                                        'age': 29, 'gender': 'male'},
                                  headers=CASTING_DIRECTOR_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['actor'], {'id': 2, 'name': 'James',
                            'age': 29, 'gender': 'MALE'})

    def test_casting_director_delete_movie(self):
        res = self.client().delete('/movies/2',
                                   headers=CASTING_DIRECTOR_HEADER)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)


if __name__ == "__main__":
    unittest.main()
