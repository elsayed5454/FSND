#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
import sys
from flask import (
    Flask, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from models import db
import logging
from logging import Formatter, FileHandler
from sqlalchemy import func
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  areas = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  
  for area in areas:
    venues_in_area = Venue.query.filter_by(city=area.city, state=area.state).all()
    venue_dict = []
    for venue in venues_in_area:
      venue_dict.append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
      })
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venue_dict
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  data = []
  for record in result:
    data.append({
      "id": record.id,
      "name": record.name,
      "num_upcoming_shows": Show.query.filter_by(venue_id=record.id).filter(Show.start_time > datetime.now()).count()
    })
  
  response = {"count": len(result), "data": data}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
    return render_template('errors/404.html')

  past_shows_set = Show.query.join(Artist).filter(
    Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []
  for show in past_shows_set:
    artistData = Artist.query.get(show.artist_id)
    past_shows.append({
      "artist_id": artistData.id,
      "artist_name": artistData.name,
      "artist_image_link": artistData.image_link,
      "start_time": format_datetime(str(show.start_time))
      })

  upcoming_shows_set = Show.query.join(Artist).filter(
    Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_set:
    artistData = Artist.query.get(show.artist_id)
    upcoming_shows.append({
      "artist_id": artistData.id,
      "artist_name": artistData.name,
      "artist_image_link": artistData.image_link,
      "start_time": format_datetime(str(show.start_time))
      })

  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be listed.')
  else: # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue + ' + name + ' could not by deleted')
  else:
    flash('Venue ' + name + ' was successfully deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name).order_by(Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  data = []
  for record in result:
    data.append({
      "id": record.id,
      "name": record.name,
      "num_upcoming_shows": Show.query.filter_by(artist_id=record.id).filter(Show.start_time > datetime.now()).count()
    })
  
  response = {"count": len(result), "data": data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  if not artist:
    return render_template('errors/404.html')

  past_shows_set = Show.query.join(Artist).filter(
    Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []
  for show in past_shows_set:
    venueData = Venue.query.get(show.venue_id)
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": venueData.name,
      "venue_image_link": venueData.image_link,
      "start_time": format_datetime(str(show.start_time))
      })

  upcoming_shows_set = Show.query.filter(
    Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_set:
    venueData = Venue.query.get(show.venue_id)
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": venueData.name,
      "venue_image_link": venueData.image_link,
      "start_time": format_datetime(str(show.start_time))
      })

  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.genres.data = [genre.name for genre in artist.genres]
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  error = False
  try: 
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.genres = form.genres.data
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occured. The artist could not be edited.')
  else:
    flash('Edit completed successfully.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  error = False
  try: 
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.address = form.address.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occured. The venue could not be edited.')
  else:
    flash('Edit completed successfully.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  error = False
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be listed.')
  else: # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  results = db.session.query(Show, Venue, Artist) \
      .join(Venue, Show.venue_id == Venue.id) \
      .join(Artist, Show.artist_id == Artist.id) \
      .order_by(Show.start_time.desc()) \
      .all()

  for show, venue, artist in results:  # 3 objects here!
    data.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:
    form = ShowForm()
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: # on successful db insert, flash success
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
    
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
