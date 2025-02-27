from unittest import TestCase
from unittest.mock import MagicMock, create_autospec, patch

from sqlalchemy.orm import Session

from app.model.group_model import Group
from app.model.user_model import User
from app.repository.user_repository import UserRepository


class TestUserRepository(TestCase):

    def setUp(self):

        self.db = create_autospec(Session)
        self.User = User
        self.Group = Group
        self.userRepository = UserRepository(self.db)

        self.mock_user1 = MagicMock()
        self.mock_user1.uuid = "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3"
        self.mock_user1.name = "catalin"
        self.mock_user1.url = {
            "current_user_url": "https://api.github.com/user",
            "hub_url": "https://api.github.com/hub",
        }
        self.mock_user1.group = "be2a91c4-df99-490d-9061-bc12f50a80b7"

        self.mock_user2 = MagicMock()
        self.mock_user2.uuid = "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        self.mock_user2.name = "iulia"
        self.mock_user2.url = {
            "current_user_url": "https://api.github.com/user",
            "hub_url": "https://api.github.com/hub",
        }
        self.mock_user2.group = "be2a91c4-df99-490d-9061-bc12f50a80b7"

        self.mock_group = MagicMock()
        self.mock_group.uuid = "be2a91c4-df99-490d-9061-bc12f50a80b7"
        self.mock_group.name = "regular"

    def test_get_user_by_id(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_user1

        retrieved_user = self.userRepository.get_user_by_id(
            "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3"
        )

        self.db.query.assert_called_once_with(self.User)
        self.assertEqual(retrieved_user, self.mock_user1)

    def test_get_user_by_name(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_user1

        retrieved_user = self.userRepository.get_user_by_name("catalin")

        self.db.query.assert_called_once_with(self.User)
        self.assertEqual(retrieved_user, self.mock_user1)

    def test_get_all_users(self):

        mock_users = [self.mock_user1, self.mock_user2]

        mock_query = self.db.query.return_value
        mock_query.options.return_value.all.return_value = mock_users

        retrieved_users = self.userRepository.get_all_users()

        for i in range(len(mock_users)):
            self.assertEqual(retrieved_users[i].uuid, mock_users[i].uuid)
            self.assertEqual(retrieved_users[i].name, mock_users[i].name)
            self.assertEqual(retrieved_users[i].url, mock_users[i].url)
            self.assertEqual(
                retrieved_users[i].group, "be2a91c4-df99-490d-9061-bc12f50a80b7"
            )

    @patch("uuid.uuid4", return_value="510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3")
    def test_create_user(self, mock_uuid):

        mock_group = MagicMock(uuid=self.mock_group.uuid, name=self.mock_group.name)
        self.db.query.return_value.filter.return_value.first.return_value = mock_group

        created_user = self.userRepository.create_user(
            "catalin", "be2a91c4-df99-490d-9061-bc12f50a80b7"
        )

        self.db.query.assert_called_once_with(self.Group)

        filter_call_args = self.db.query.return_value.filter.call_args[0]
        self.assertEqual(
            str(filter_call_args[0]), str(self.Group.uuid == mock_group.uuid)
        )

        self.assertEqual(created_user.uuid, self.mock_user1.uuid)
        self.assertEqual(created_user.name, self.mock_user1.name)
        self.assertIn(mock_group, created_user.group)

        self.db.add.assert_called_once_with(created_user)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(created_user)

    @patch("app.model.user_model.User")
    def test_update_user_url(self, mock_user):

        updated_content = {"current_user_url": "https://api.github.com/user"}

        self.db.query.return_value.filter.return_value.first.return_value = (
            self.mock_user1
        )

        self.userRepository.update_user_url(self.mock_user1.uuid, updated_content)

        self.db.query.assert_called_once_with(self.User)

        filter_call_args = self.db.query.return_value.filter.call_args[0]

        self.assertEqual(
            str(filter_call_args[0]), str(self.User.uuid == self.mock_user1.uuid)
        )

        self.assertEqual(self.mock_user1.urls, updated_content)

        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(self.mock_user1)

    def test_update_user(self):

        new_user_name = "updated name"

        self.db.query.return_value.filter.return_value.first.return_value = (
            self.mock_user1
        )

        updated_user = self.userRepository.update_user(
            self.mock_user1.uuid, new_user_name
        )

        self.mock_user1.name = new_user_name
        self.db.query.return_value.filter.return_value.update.assert_called_once_with(
            {self.User.name: new_user_name}
        )

        self.db.commit.assert_called_once()
        self.db.query.return_value.filter.return_value.first.assert_called_once()

        self.assertEqual(updated_user.name, new_user_name)

    def test_delete_user(self):

        self.db.query.return_value.filter.return_value.first.return_value = (
            self.mock_user1
        )

        self.userRepository.delete_user(self.mock_user1.uuid)

        filter_call_args = self.db.query.return_value.filter.call_args[0]

        self.assertEqual(
            str(filter_call_args[0]), str(self.User.uuid == self.mock_user1.uuid)
        )

        self.db.delete.assert_called_once_with(self.mock_user1)
        self.db.commit.assert_called_once()
