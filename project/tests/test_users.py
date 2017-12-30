# project/tests/test_users.py


import json

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase


def add_user(username, email):
    user_object = User(username=username, email=email)
    db.session.add(user_object)
    db.session.commit()
    return user_object


class TestUserService(BaseTestCase):
    """Tests for the User Service."""

    def test_user(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('Pong', data['message'])
        self.assertIn('success', data['status'])

    def test_main_no_user(self):
        """Ensure the main route behaves correctly when no users have been
    added to the database."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_user(self):
        """Ensure the main route behaves correctly when users have been
    added to the database."""
        add_user('Username-test-1', 'test1@gmail.com')
        add_user('Username-test-2', 'test2@gmail.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertNotIn(b'<p>No users!</p>', response.data)
        self.assertIn(b'<strong>Username-test-1</strong>', response.data)
        self.assertIn(b'<strong>Username-test-2</strong>', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='test', email='test@gmail.com'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<h1>All Users</h1>', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'<strong>test</strong>', response.data)

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='测试用户名',
                    email='ceshi@gmail.com',
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('success', data['status'])
            self.assertIn('User add success', data['message'])
            self.assertIn('user_id', data['data'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])
            self.assertIn('Invalid payload', data['message'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have a url key."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='测试User添加',
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])
            self.assertIn('Invalid payload', data['message'])

    def test_add_user_duplicate_user(self):
        """Ensure error is thrown if the user already exists."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='测试User添加',
                    email='user@gmail.com'
                )),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='测试User添加',
                    email='user@gmail.com',
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('fail', data['status'])
            self.assertIn('User already exists', data['message'])

    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user_object = add_user('测试User添加', 'ceshiyonghu@gmail.com')
        with self.client:
            response = self.client.get('/users/{user_id}'.format(user_id=user_object.id))
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Query success', data['message'])
            self.assertIn('测试User添加', data['data']['username'])
            self.assertIn('ceshiyonghu@gmail.com', data['data']['email'])
            self.assertTrue('create_time' in data['data'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/xxxxx')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user('测试1', 'test1@gmail.com')
        add_user('测试2', 'test2@gmail.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertEqual(len(data['data']['users']), 2)
            self.assertTrue('create_time' in data['data']['users'][0])
            self.assertTrue('create_time' in data['data']['users'][1])
            self.assertIn('测试1', data['data']['users'][0]['username'])
            self.assertIn(
                'test1@gmail.com', data['data']['users'][0]['email'])
            self.assertIn('测试2', data['data']['users'][1]['username'])
            self.assertIn(
                'test2@gmail.com', data['data']['users'][1]['email'])
