# FSND: Capstone Project

## Introduction
The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies. You are an Executive Producer within the company and are creating a system to simplify and streamline your process. 

## Motivation

This is the last project of the `Udacity-Full-Stack-Nanodegree` Course.
It covers following technical topics:

1. Coding in Python 3
2. Relational Database Architecture
3. Modeling Data Objects with SQLAlchemy
4. Internet Protocols and Communication
5. Developing a Flask API
6. Authentication and Access
7. Authentication with Auth0
8. Authentication in Flask
9. Role-Based Access Control (RBAC)
10. Testing Flask Applications
11. Deploying Applications

## Heroku Deployment

The app is hosted live on heroku at the URL:  
**https://capstone78.herokuapp.com/**  
However, there is no frontend for this app yet, and it can only be presently used to authenticate using Auth0 by entering
credentials and retrieving a fresh token to use with curl or postman.

## Start Project locally

1. Initialize and activate the virtualenv:
  ```bash
  $ python -m venv venv
  $ source venv/bin/activate
  ```

2. Install the dependencies:
```bash
$ pip3 install -r requirements.txt
```

3. Change database configuration in `models.py` so it can connect to your local postgres database.

4. All necessary credential to run the project are provided in the `setup.sh` file. The credentials can be enabled by running the following command: 
```
source setup.sh
```

5. Run the development server:
  ```bash 
  $ python app.py
  ```

6. To execute tests, run
```bash 
$ python test_app.py
```

We can now also open the application via Heroku using the URL:  
**https://capstone78.herokuapp.com/**  
The live application can only be used to generate tokens via Auth0, the endpoints have to be tested using curl or Postman 
using the token since I did not build a frontend for the application.


## API Documentation

### Available Endpoints

1. Actors
   1. GET /actors
   2. POST /actors
   3. DELETE /actors/actor-id
   4. PATCH /actors/actor-id
2. Movies
   1. GET /movies
   2. POST /movies
   3. DELETE /movies/movie-id
   4. PATCH /movies/movie-id

### 1. GET /actors

Query actors.

- Gets a list of all actors from the database.
- Request Headers: **None**
- Requires permission: `get:actors`
- Returns: 
  1. List of dict of actors with following fields:
      - **integer** `id`
      - **string** `name`
      - **string** `gender` (male or female)
      - **integer** `age`
  2. **boolean** `success`

### 2. POST /actors

Create new actor.
- Request Headers (all required):  
       1. **string** `name`  
       2. **integer** `age`  
       3. **string** `gender` (male or female)
- Requires permission: `post:actors`
- Returns: 
  1. **string** `actor` (returns all its data in json format)
  2. **boolean** `success`


### 3. PATCH /actors/actor-id

Update an existing Actor.

- Request Headers:  
       1. **string** `name`  
       2. **integer** `age`  
       3. **string** `gender` (male or female) 
- Requires permission: `patch:actors` 
- Returns: 
  1. **string** `actor` (returns all its data in json format)
  2. **boolean** `success`


### 4. DELETE /actors/actor-id

Delete an Actor.

- Request Headers: `None`
- Requires permission: `delete:actors`
- Returns: 
  1. **integer** `deleted actor id`
  2. **boolean** `success`


### 5. GET /movies

Query movies.

- Gets a list of all movies from the database.
- Request Headers: **None**
- Requires permission: `get:movies`
- Returns: 
  1. List of dict of movies with following fields:
      - **integer** `id`
      - **string** `title`
      - **date** `release_date`
  2. **boolean** `success`

### 6. POST /movies

Create new movie.
- Request Headers (all required):  
       1. **string** `title`  
       2. **string** `release_date` (isoformat ex: 2021-07-12)  
- Requires permission: `post:movies`
- Returns: 
  1. **string** `movie` (returns all its data in json format)
  2. **boolean** `success`


### 7. PATCH /movies/movie-id

Update an existing movie.

- Request Headers:  
       1. **string** `title`  
       2. **string** `release_date` (isoformat ex: 2021-07-12)   
- Requires permission: `patch:movies` 
- Returns: 
  1. **string** `movie` (returns all its data in json format)
  2. **boolean** `success`


### 8. DELETE /movies/movie-id

Delete a movie.

- Request Headers: `None`
- Requires permission: `delete:movies`
- Returns: 
  1. **integer** `deleted movie id`
  2. **boolean** `success`


## Authentication

All API Endpoints are decorated with Auth0 permissions.

### Local Use
#### Create an App & API

1. Login to https://manage.auth0.com/ 
2. Click on Applications Tab
3. Create Application
4. Give it a name like `Studio` and select "Regular Web Application"
5. Go to Settings and find `domain`. Copy & paste it into `auth.py` -> `AUTH0_DOMAIN`
6. Click on API Tab 
7. Create a new API:
   1. Name: `Studio`
   2. Identifier `Studio`
8. Go to Settings and find `Identifier`. Copy & paste it into `auth.py` -> `API_AUDIENCE`

#### Create Roles & Permissions

1. `Enable RBAC & Add Permissions in the Access Token` in your API (API -> Click on your API Name -> Settings -> Enable RBAC & Add Permissions in the Access Token -> Save)
2. Create a new Role under `Users and Roles` -> `Roles` -> `Create Roles`
3. Give it a name like `Casting Producer`.
4. Go back to the API Tab and find your newly created API. Click on Permissions.
5. Create & assign the needed permissions accordingly 
6. Go back to `Users and Roles` -> `Roles` and select the role you recently created.
6. Under `Permissions`, assign all permissions you want this role to have. 


### Auth0 to use existing API
If you want to access the temporary API, access tokens for 3 roles are included in the `setup.sh` file.

## Existing Roles

* Casting Assistant
  - Can view actors and movies (get:actors & get:movies)
* Casting Director
  - All permissions a Casting Assistant has and 
  - Add or delete an actor from the database (post:actors & delete:actors)
  - Modify actors or movies (patch:movies & patch:actors)
* Exectutive Dircector
  - All permissions a Casting Director has and
  - Add or delete a movie from the database (post:movies & delete:movies)