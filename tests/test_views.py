import unittest
from apps.app import create_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()


class IndexPageTest(BaseTestCase):
    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class SigninPageTest(BaseTestCase):
    def test_signin_page(self):
        response = self.client.get('/signin')
        self.assertEqual(response.status_code, 200)


class SignupPageTest(BaseTestCase):
    def test_signup_page(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
