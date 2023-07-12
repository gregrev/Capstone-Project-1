import os
from unittest import TestCase

from database import fill_database
from sqlalchemy import exc
from models import db, User


os.environ['DATABASE_URL'] = 'postgresql:///capstone_1-test'

from app import app

class UserModelTestCase(TestCase):
    """Test User model"""

    def setUp(self):
        """Create a test user and add data to db"""
        fill_database()

        user = User.signup(
            'test1', 'test1111', 'https://www.ikea.com/us/en/images/products/sparka-soft-toy-soccer-ball-black-white__0981434_pe815368_s5.jpg')
        user_id = 7
        user.id = user_id
        
        db.session.add(user)
        db.session.commit()

        user = db.session.get(User, user_id)

        self.user = user
        self.user_id = user_id

        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
    
    #TEST USER MODEL

    def test_user_model(self):
        """Test if User model is working"""

        u = User(
            username="testtest",
            password="HASHED_PW",
            image_url="https://www.ikea.com/us/en/images/products/sparka-soft-toy-soccer-ball-black-white__0981434_pe815368_s5.jpg"
        )

        db.session.add(u)
        db.session.commit()
        
        # once created user should have favorites
        self.assertEqual(len(u.favorites), 0)

    #TEST SIGNUP

    def test_valid_signup(self):
        """Test if signup is working"""
        with self.client:
            response = self.client.post('/signup', data={
                'username': 'testtest',
                'password': 'testtestpass',
                'image_url': 'https://www.ikea.com/us/en/images/products/sparka-soft-toy-soccer-ball-black-white__0981434_pe815368_s5.jpg'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            # check for user in database
            u_test = User.query.filter_by(username='testtest').first()
            self.assertIsNotNone(u_test)
            self.assertEqual(u_test.username, "testtest")
            # password should now be encrypted
            self.assertNotEqual(u_test.password, "testtestpass")
            self.assertEqual(
                u_test.image_url, "https://www.ikea.com/us/en/images/products/sparka-soft-toy-soccer-ball-black-white__0981434_pe815368_s5.jpg")
            self.assertTrue(u_test.password.startswith("$2b$"))

    #TEST AUTHENTICATION

    def test_authentication(self):
        """Test login authentication"""
        u = User.authenticate(self.user.username, "test1111")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.user_id)

    def test_invalid_username(self):
        """Test invalid username during login"""
        self.assertFalse(User.authenticate("invalidusername", "test1111"))

    def test_bad_password(self):
        """Test invalid password during login"""
        self.assertFalse(User.authenticate(self.user.username, "badpassword"))

    


