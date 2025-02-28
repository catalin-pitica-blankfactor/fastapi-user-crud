import unittest

from app.core.config import get_sqlalchemy_db_url


class TestDatabaseConfig(unittest.TestCase):

    def test_get_sqlalchemy_db_url_default(self):
        expected_url = "sqlite:///./users.db"
        self.assertEqual(get_sqlalchemy_db_url(), expected_url)
