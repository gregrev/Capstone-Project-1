from app import app
import os
from unittest import TestCase

from database import fill_database
from sqlalchemy import exc
from models import db, User, Favorites


os.environ['DATABASE_URL'] = 'postgresql:///capstone_1-test'


class FavoritesModelTestCase(TestCase):
    """Test Favorites model"""

    def setUp(self):
        """Create a test user and add data to db"""
        fill_database()

        user = User.signup(
            'test8', 'test888', 'https://www.ikea.com/us/en/images/products/sparka-soft-toy-soccer-ball-black-white__0981434_pe815368_s5.jpg')
        db.session.add(user)
        db.session.commit()

        self.user = user
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()

    def test_add_favorite_repo(self):
        """Check when user adds a repo to favorites"""
        with self.client:
            # simulate login with test user
            self.client.post('/login', data={
                'username': 'test8',
                'password': 'test888'
            }, follow_redirects=True)

            # add repo to favorites
            response = self.client.post(
                '/repos/1/favorite', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(self.user.favorites), 1)
            self.assertEqual(self.user.favorites[0].repo_id, 1)

    def test_remove_favorite_repo(self):
        """Check when user removes a repo from favorites"""
        # add a favorite repo to user
        favorite_repo = Favorites(user_id=self.user.id, repo_id=1)
        db.session.add(favorite_repo)
        db.session.commit()

        with self.client:
            self.client.post('/login', data={
                'username': 'test8',
                'password': 'test888'
            }, follow_redirects=True)

            # delete repo
            response = self.client.post(
                '/repos/1/favorite', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(self.user.favorites), 0)

    def test_add_favorite_dev(self):
        """Check when user adds a dev to favorites"""
        with self.client:
            # simulate login with test user
            self.client.post('/login', data={
                'username': 'test8',
                'password': 'test888'
            }, follow_redirects=True)

            # add dev to favorites
            response = self.client.post(
                '/devs/1/favorite', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(self.user.favorites), 1)
            self.assertEqual(self.user.favorites[0].dev_id, 1)

    def test_remove_favorite_dev(self):
        """Check when user removes a dev from favorites"""
        # add fav dev to user
        favorite_dev = Favorites(user_id=self.user.id, dev_id=1)
        db.session.add(favorite_dev)
        db.session.commit()

        with self.client:
            self.client.post('/login', data={
                'username': 'test8',
                'password': 'test888'
            }, follow_redirects=True)

            # delete dev from favorites
            response = self.client.post(
                '/devs/1/favorite', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(self.user.favorites), 0)
