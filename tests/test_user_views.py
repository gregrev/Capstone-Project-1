import os
from unittest import TestCase

from models import db, connect_db, Favorites, User, TrendingRepos, TrendingDevs
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///capstone_1"

from app import app, CURR_USER_KEY