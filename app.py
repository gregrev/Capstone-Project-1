import os

from flask import Flask, jsonify, render_template, session, redirect, flash, g, request

from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Favorites, TrendingDevs, TrendingRepos
from database import fill_database, serialized_devs, serialized_repos
from forms import UserAddForm, LoginForm, EditForm


app = Flask(__name__)
CORS(app, supports_credentials=True)

CURR_USER_KEY = "user_id"

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///capstone_1'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "oh so secret")

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'


connect_db(app)

fill_database()

@app.before_request
def load_user():
    """Load the current user before each request"""
    user_id = session.get(
        CURR_USER_KEY)
    if user_id:
        g.user = User.query.get(user_id)
    else:
        g.user = None


@app.route("/", methods=['GET'])
def homepage():
    """Display Homepage"""
    return redirect('/repos')

#  ***SIGNUP***


@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    form = UserAddForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            image_url = form.image_url.data or User.image_url.default.arg

            new_user = User.signup(username, password, image_url)
            db.session.add(new_user)
            db.session.commit()

            session[CURR_USER_KEY] = new_user.id
            flash('Successfully Created Your Account!')
            return redirect("/")
        except IntegrityError:    
        # update the session with the user's ID
            flash("Username already taken", 'danger')
            return redirect('/signup')

    return render_template('/users/signup.html', form=form)

#  ***LOGIN***


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back, {username}!')
            # update the session with the user's ID
            session[CURR_USER_KEY] = user.id
            return redirect('/')
        else:
            flash('Invalid Login', 'error')
            form.username.errors = ['Invalid Login']

    return render_template('/users/login.html', form=form)

#  ***LOGOUT***


@app.route('/logout', methods=['POST'])
def logout_user():
    """Logout the current user"""

    # remove user id from session
    session.pop(CURR_USER_KEY, None)
    flash('You have been logged out')
    return redirect('/')

#  ***ADD FAVORITES***


@app.route("/repos/<int:repo_id>/favorite", methods=['POST'])
def add_favorite_repo(repo_id):
    """Add/remove a favorite for the current logged-in user"""
    if not g.user:
        flash("Please log in to add favorites.")
        return redirect("/login")

    # see if the repository is already a favorite for the user
    favorite = Favorites.query.filter_by(
        user_id=g.user.id, repo_id=repo_id).first()

    if favorite:
        # ifg already a favorite, remove it
        db.session.delete(favorite)
        db.session.commit()
        flash("Repository removed from favorites.")
    else:
        # if not add it
        favorite = Favorites(user_id=g.user.id, repo_id=repo_id)
        db.session.add(favorite)
        db.session.commit()
        flash("Repository added to favorites.")

    return redirect("/repos")


@app.route("/devs/<int:dev_id>/favorite", methods=['POST'])
def add_favorite_dev(dev_id):
    """Add/remove a favorite for the current logged-in user"""
    if not g.user:
        flash("Please log in to add favorites.")
        return redirect("/login")

    # check if dev is alreeady a favorite
    favorite = Favorites.query.filter_by(
        user_id=g.user.id, dev_id=dev_id).first()

    if favorite:
        # if yes remove
        db.session.delete(favorite)
        db.session.commit()
        flash("Developer removed from favorites.")
    else:
        # if not add
        favorite = Favorites(user_id=g.user.id, dev_id=dev_id)
        db.session.add(favorite)
        db.session.commit()
        flash("Developer added to favorites.")

    return redirect("/devs")

#  ***SHOW USER PROFILE***


@app.route('/users/<int:user_id>')
def show_profile(user_id):
    """Show user profile and user favorites"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    favorites = Favorites.query.filter_by(user_id=g.user.id).all()
    repos = []
    devs = []
    for fav in favorites:
        repo = TrendingRepos.query.get(fav.repo_id)
        dev = TrendingDevs.query.get(fav.dev_id)
        if repo:
            repos.append(repo)
        if dev:
            devs.append(dev)

    return render_template('/users/profile.html', repos=repos, devs=devs, favorites=favorites, user=user)

#  ***DAILY TRENDING REPOS ***


@app.route("/repos", methods=['GET'])
def display_repos():
    """Display trending repos"""
    if g.user:
        favorites = Favorites.query.filter_by(user_id=g.user.id).all()
        favorites_repo_ids = [fav.repo_id for fav in favorites]
    else:
        favorites = []
        favorites_repo_ids = []

    repos_data = TrendingRepos.query.all()

    # get languages from repos_data and put into list
    languages = list({repo.language for repo in repos_data})

    # language filtering
    # get value of the query param language to filter by that language
    selected_language = request.args.get('language')

    filtered_repos = []

    if selected_language and selected_language != 'all':
        for repo in repos_data:
            if repo.language == selected_language:
                filtered_repos.append(repo)
    else:
        filtered_repos = repos_data

    current_page = "repos"

    return render_template('repos.html', repos=filtered_repos, languages=languages, favorites=favorites, selected_language=selected_language, favorites_repo_ids=favorites_repo_ids, current_page=current_page)

#  ***DAILY TRENDING DEVS ***


@app.route("/devs", methods=['GET'])
def display_devs():
    """Display trending repos"""
    if g.user:
        favorites = Favorites.query.filter_by(user_id=g.user.id).all()
        devs = []
        for fav in favorites:
            dev = TrendingDevs.query.get(fav.dev_id)
            if dev:
                devs.append(dev)
    else:
        favorites = []
        devs = []

    devs_data = TrendingDevs.query.all()

    current_page = "devs"

    return render_template('devs.html', devs_data=devs_data, favorites=favorites, devs=devs, current_page=current_page)


#  *** API's ***
@app.route('/api/trending_repos', methods=['GET'])
def get_repos():
    """show api data of trending repos of the day"""
    repos_data = serialized_repos()
    return jsonify(repos_data)


@app.route('/api/trending_devs', methods=['GET'])
def get_devs():
    """show api data of trending repos of the day"""
    devs_data = serialized_devs()
    return jsonify(devs_data)


if __name__ == '__main__':
    app.run()

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req