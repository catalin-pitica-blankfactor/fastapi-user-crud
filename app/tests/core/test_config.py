import unittest

from app.core.config import get_sqlalchemy_db_url


class TestDatabaseConfig(unittest.TestCase):

    def test_get_sqlalchemy_db_url_default(self):
        expected_url = "postgresql+psycopg2://admin:securepassword@localhost:5432/users"
        self.assertEqual(get_sqlalchemy_db_url(), expected_url)
