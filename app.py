import os

from flask import Flask, jsonify, render_template, session, redirect, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS

from models import db, connect_db, User, Favorites, TrendingDevs, TrendingRepos
from forms import UserAddForm, LoginForm, EditForm
from bs4 import BeautifulSoup
import requests


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
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# toolbar = DebugToolbarExtension(app)

connect_db(app)

def scrape_trending_repos():
    url = 'https://github.com/trending'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    repo_titles = soup.find_all('h2', class_='h3 lh-condensed')

    repos = []
    for repo in repo_titles:
        title = repo.text.strip()
        # split up the title in the h2 to use values seperately
        title_parts = title.split('/', 1)
        developer = title_parts[0].strip()
        repo_name = title_parts[1].strip()

        # the parent element of the h2 tag
        parent_element = repo.find_parent('article')

        # the p element with the specified class within the parent element
        description_element = parent_element.find(
            'p', class_='col-9 color-fg-muted my-1 pr-4')

        # get the description text
        description = description_element.text.strip() if description_element else ""

        language = repo.find_next(
            'span', class_='d-inline-block ml-0 mr-3').text.strip()
        stargazers = repo.find_next(
            'a', class_='Link--muted d-inline-block mr-3').text.strip()
        stars_today = repo.find_next(
            'span', class_='d-inline-block float-sm-right').text.strip()
        href = repo.find_next('a')['href']

        repo_data = {
            'developer': developer,
            'repo_name': repo_name,
            'description': description,
            'language': language,
            'stargazers': stargazers,
            'stars_today': stars_today,
            'repo_link': f"https://github.com{href}"
        }
        repos.append(repo_data)

    return repos


def scrape_trending_devs():
    url = 'https://github.com/trending/developers'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    devs = soup.find_all('article', class_='Box-row')

    trending_devs = []
    for dev in devs:
        dev_name = dev.find('h1', class_='h3 lh-condensed').text.strip()

        dev_username = dev.find('p', class_='f4 text-normal mb-1')
        if dev_username:
            dev_username = dev_username.find(
                'a', class_='Link--secondary').text.strip()
        else:
            dev_username = 'N/A'

        dev_avatar = dev.find('img', class_='avatar-user')
        if dev_avatar:
            dev_avatar = dev_avatar['src']
        else:
            dev_avatar = 'N/A'

        dev_pop_proj_name_elem = dev.find('h1', class_='h4 lh-condensed')
        if dev_pop_proj_name_elem:
            dev_pop_proj_name = dev_pop_proj_name_elem.find(
                'a', class_='css-truncate-target').text.strip()
        else:
            dev_pop_proj_name = 'N/A'

        dev_proj_desc_elem = dev.find('div', class_='f6 color-fg-muted mt-1')
        if dev_proj_desc_elem:
            dev_proj_desc = dev_proj_desc_elem.text.strip()
        else:
            dev_proj_desc = 'N/A'

        dev_data = {
            'dev_name': dev_name,
            'dev_username': dev_username,
            'dev_avatar': dev_avatar,
            'dev_pop_proj_name': dev_pop_proj_name,
            'dev_proj_desc': dev_proj_desc
        }
        trending_devs.append(dev_data)

    return trending_devs


@app.cli.command("fill_database")
def fill_database_command():
    with app.app_context():
        db.drop_all()
        db.create_all()

        trending_repos = scrape_trending_repos()
        trending_devs = scrape_trending_devs()

        for repo_data in trending_repos:
            new_repo = TrendingRepos(
                developer=repo_data['developer'],
                repo_name=repo_data['repo_name'],
                description=repo_data['description'],
                language=repo_data['language'],
                repo_link=repo_data['repo_link'],
                stargazers=repo_data['stargazers'],
                stars_today=repo_data['stars_today']
            )
            db.session.add(new_repo)

        for dev_data in trending_devs:
            dev_username = dev_data['dev_username']
            profile_link = f"https://www.github.com/{dev_username}"
            new_dev = TrendingDevs(
                dev_name=dev_data['dev_name'],
                dev_username=dev_data['dev_username'],
                dev_avatar=dev_data['dev_avatar'],
                profile_link=profile_link,
                dev_pop_proj_name=dev_data['dev_pop_proj_name'],
                dev_proj_desc=dev_data['dev_proj_desc']
            )
            db.session.add(new_dev)

        db.session.commit()


def serialized_repos():
    repos = TrendingRepos.query.all()
    # devs = TrendingDevs.query.all()

    repos_data = [
        {
            'developer': repo.developer,
            'repo_name': repo.repo_name,
            'description': repo.description,
            'language': repo.language,
            'repo_link': repo.repo_link,
            'stargazers': repo.stargazers,
            'stars_today': repo.stars_today
        }
        for repo in repos
    ]

    return repos_data


def serialized_devs():
    devs = TrendingDevs.query.all()

    devs_data = [
        {
            'dev_name': dev.dev_name,
            'dev_username': dev.dev_username,
            'dev_avatar': dev.dev_avatar,
            'profile_link': dev.profile_link,
            'dev_pop_proj_name': dev.dev_pop_proj_name,
            'dev_proj_desc': dev.dev_proj_desc
        }
        for dev in devs
    ]

    return devs_data

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
        username = form.username.data
        password = form.password.data
        image_url = form.image_url.data or User.image_url.default.arg

        new_user = User.signup(username, password, image_url)
        db.session.add(new_user)
        db.session.commit()
        # update the session with the user's ID
        session[CURR_USER_KEY] = new_user.id
        flash('Successfully Created Your Account!')
        return redirect("/")

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