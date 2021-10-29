from datetime import date

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from auth import requires_auth, AuthError

from models import Actor, Movie, Gender, setup_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        all_actors = Actor.query.order_by(Actor.id).all()
        formatted_actors = [actor.repr() for actor in all_actors]
        # print(json.dumps(formatted_actors))

        if len(formatted_actors) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'actors': formatted_actors
        })

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        all_movies = Movie.query.order_by(Movie.id).all()
        formatted_movies = [movie.repr() for movie in all_movies]
        # print(json.dumps(formatted_movies))

        if len(formatted_movies) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'movies': formatted_movies
        })

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        try:
            deleted_actor = Actor.query.filter(
                Actor.id == actor_id).one_or_none()
            deleted_actor.delete()

            return jsonify({
                'success': True,
                'deleted': actor_id
            })
        except:
            abort(404)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        try:
            deleted_movie = Movie.query.filter(
                Movie.id == movie_id).one_or_none()
            deleted_movie.delete()

            return jsonify({
                'success': True,
                'deleted': movie_id
            })
        except:
            abort(404)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor(payload):
        body = request.get_json()

        if 'name' not in body or 'age' not in body or 'gender' not in body:
            abort(400)

        created_actor = Actor(name=body['name'], age=body['age'])
        if body['gender'].upper() in Gender.__members__:
            created_actor.gender = Gender[body['gender'].upper()]
        else:
            abort(400)

        created_actor.insert()

        return jsonify({
            'success': True,
            'actor': created_actor.repr()
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie(payload):
        body = request.get_json()

        if 'title' not in body or 'release_date' not in body:
            abort(400)

        created_movie = Movie(title=body['title'],
                              release_date=date.fromisoformat(body['release_date']))
        created_movie.insert()

        return jsonify({
            'success': True,
            'movie': created_movie.repr()
        })

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(payload, actor_id):
        body = request.get_json()
        if not body:
            abort(400)

        updated_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if not updated_actor:
            abort(404)

        updated_name = body.get('name', None)
        if updated_name:
            updated_actor.name = updated_name

        updated_age = body.get('age', None)
        if updated_age:
            updated_actor.age = updated_age

        updated_gender = body.get('gender', None)
        if updated_gender:
            if updated_gender.upper() == Gender.MALE.name:
                updated_actor.gender = Gender.MALE
            elif updated_gender.upper() == Gender.FEMALE.name:
                updated_actor.gender = Gender.FEMALE

        updated_actor.update()
        return jsonify({
            'success': True,
            'actor': updated_actor.repr()
        })

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        body = request.get_json()
        if not body:
            abort(400)

        updated_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if not updated_movie:
            abort(404)

        updated_title = body.get('title', None)
        if updated_title:
            updated_movie.title = updated_title

        updated_release_date = body.get('release_date', None)
        if updated_release_date:
            updated_movie.release_date = date.fromisoformat(updated_release_date)

        updated_movie.update()
        return jsonify({
            'success': True,
            'movie': updated_movie.repr()
        })

    # Error Handling

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(AuthError)
    def auth_failed(AuthError):
        return jsonify({
            "success": False,
            "error": AuthError.status_code,
            "message": AuthError.error
        }), AuthError.status_code

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
