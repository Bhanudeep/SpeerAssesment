import unittest
from flask import Flask
from server import app  

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_home(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    

if __name__ == '__main__':
    unittest.main()
