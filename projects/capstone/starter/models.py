import enum
import os
from sqlalchemy import Column, Integer, String, Date, Enum
from flask_sqlalchemy import SQLAlchemy
from datetime import date

database_name = "capstone"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.environ.get(
    'DATABASE_URL', "postgresql://postgres:123456@{}/{}"
    .format('localhost:5432', database_name))

if database_path.startswith("postgres://"):
    database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()


'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Gender(enum.Enum):
    MALE = 1
    FEMALE = 0


'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    # add one demo movie and actor which is helping in POSTMAN test
    movie = Movie(
        title='interstellar',
        release_date=date.fromisoformat('2014-11-07')
    )
    movie.insert()

    movie = Movie(
        title='Harry Potter and the Philosopher\'s Stone',
        release_date=date.fromisoformat('2002-01-16')
    )
    movie.insert()

    actor = Actor(
        name='Matthew McConaughey',
        age=51,
        gender=Gender.MALE
    )
    actor.insert()

    actor = Actor(
        name='Emma Charlotte Duerre Watson',
        age=31,
        gender=Gender.FEMALE
    )
    actor.insert()


class Movie(db.Model):
    id = Column(Integer(), primary_key=True)
    title = Column(String(80), unique=True)
    release_date = Column(Date(), nullable=False)

    '''
    insert()
        inserts a new model into a database
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''

    def update(self):
        db.session.commit()

    '''
    repr()
        form representation of the Movies model
    '''

    def repr(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.isoformat()
        }


class Actor(db.Model):
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), nullable=False)
    age = Column(Integer(), nullable=False)
    gender = Column(Enum(Gender), nullable=False)

    '''
    insert()
        inserts a new model into a database
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''

    def update(self):
        db.session.commit()

    '''
    repr()
        form representation of the actors model
    '''

    def repr(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': str(self.gender.name)
        }
