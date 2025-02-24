from unittest import TestCase

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db


class TestGetDbFunction(TestCase):

    def test_get_db(self):

        db = None
        for db in get_db():

            self.assertIsInstance(db, Session)

            self.assertTrue(db.is_active)

            break

        self.assertIsNotNone(db)
        with self.assertRaises(Exception):
            db.execute(text("SELECT *"))
