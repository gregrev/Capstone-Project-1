from app import app
from models import db, User, Favorites, TrendingDevs, TrendingRepos


db.drop_all()
db.create_all()

User1 = User(
    username="gregory",
    password="gregory",
    image_url='/static/images/default-logo.png',
)

User2 = User(
    username="stephanie",
    password="stephanie",
    image_url='/static/images/default-logo.png',
)

SeedRepo1 = TrendingRepos(
    developer = 'grerev',
    repo_name = 'ollover Luca',
    description = 'this is a test',
    language = 'english',
    repo_link = 'https://github.com/gregrev/Flask-Feedback',
    stargazers = '100',
    stars_today = '50 stars today'
)

SeedRepo2 = TrendingRepos(
    developer = 'jake-smith',
    repo_name = 'testing1123',
    description = 'this is a another test',
    language = 'spanish',
    repo_link = 'https://github.com/test',
    stargazers = '500',
    stars_today = '1 stars today'
)

SeedDev1 = TrendingDevs(
    dev_name = 'Peter Parker',
    dev_username = 'Spidey101',
    dev_avatar = 'www.google.com',
    profile_link = 'www.github.com',
    dev_pop_proj_name = 'WebSlinger',
    dev_proj_desc = 'How to make webs'
)

SeedDev2 = TrendingDevs(
    dev_name = 'Tony Stark',
    dev_username = 'IronMan1',
    dev_avatar = 'www.google.com',
    profile_link = 'www.github.com',
    dev_pop_proj_name = 'MKV Iron Suit',
    dev_proj_desc = 'How to use blasters'
)

SeedFav1 = Favorites(
    user_id = '1',
    repo_id = 2,
    dev_id = 2
)

SeedFav2 = Favorites(
    user_id = '2',
    repo_id = 1,
    dev_id = 1
)

db.session.add_all([User1, User2, SeedDev1, SeedDev2, SeedRepo1, SeedRepo2, SeedFav1, SeedFav2])
db.session.commit()
