"""SQLAlchemy Models for Capstone"""

# from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from api import get_trending_repos  # get_trending_devs

bcrypt = Bcrypt()

db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)
    app.app_context().push()
    db.create_all()

# CREATE tables for trending repo and devs


class TrendingRepos(db.Model):
    """Trending Repos Model"""

    __tablename__ = "trending_repos"

    id = db.Column(db.Integer, primary_key=True)
    developer = db.Column(db.String(100))
    repo_name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    language = db.Column(db.String(50))
    repo_link = db.Column(db.String(200))
    stargazers = db.Column(db.String(50))
    stars_today = db.Column(db.String(50))


class TrendingDevs(db.Model):
    """Trending Devs Model"""

    __tablename__ = "trending_devs"

    id = db.Column(db.Integer, primary_key=True)
    dev_name = db.Column(db.String(100))
    dev_username = db.Column(db.String(100))
    dev_avatar = db.Column(db.String(100))
    profile_link = db.Column(db.String(100))
    dev_pop_proj_name = db.Column(db.String(100))
    dev_proj_desc = db.Column(db.String(300))


class Favorites(db.Model):
    """Connect users to their favorites"""

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    repo_id = db.Column(
        db.Integer,
        db.ForeignKey('trending_repos.id', ondelete='cascade')
    )

    dev_id = db.Column(
        db.Integer,
        db.ForeignKey('trending_devs.id', ondelete='cascade')
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True, autoincrement=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-logo.png",
    )

    favorites = db.relationship(
        'Favorites',
        backref='user',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password, image_url):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            image_url=image_url
        )

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

