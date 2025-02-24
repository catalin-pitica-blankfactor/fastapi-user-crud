from unittest import TestCase
from unittest.mock import MagicMock, create_autospec, patch
from sqlalchemy.orm import Session
from app.repository.group_repository import GroupRepository
from app.model.group_model import Group


class TestGroupRepository(TestCase):

    def setUp(self):

        self.db = create_autospec(Session)

        self.group_repository = GroupRepository(self.db)

        self.mock_group1 = Group(
            uuid="be2a91c4-df99-490d-9061-bc12f50a80b7", name="regular"
        )

        self.mock_group2 = Group(
            uuid="b34d63a3-12fd-456e-b6d7-27c8ab69a6e3", name="admin"
        )

    def test_get_group_by_id(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_group1

        retrieved_group = self.group_repository.get_group_by_id(self.mock_group1.uuid)

        self.db.query.assert_called_once_with(Group)
        self.assertEqual(retrieved_group, self.mock_group1)

    def test_get_all_groups(self):

        mock_group = [self.mock_group1, self.mock_group2]
        mock_query = self.db.query.return_value
        mock_query.all.return_value = mock_group

        retrieved_groups = self.group_repository.get_all_groups()

        self.db.query.assert_called_once_with(Group)
        self.assertEqual(len(retrieved_groups), len(mock_group))
        self.assertEqual(retrieved_groups[0].uuid, self.mock_group1.uuid)
        self.assertEqual(retrieved_groups[1].uuid, self.mock_group2.uuid)

    def test_check_exist_group_name(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_group1

        retrieved_group = self.group_repository.check_exist_group_name(
            self.mock_group1.name
        )

        self.db.query.assert_called_once_with(Group)
        self.assertEqual(retrieved_group, self.mock_group1)

    @patch("uuid.uuid4", return_value="be2a91c4-df99-490d-9061-bc12f50a80b7")
    def test_create_group(self, mock_uuid):

        new_group_name = "regular"

        created_group = self.group_repository.create_group(new_group_name)

        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(created_group)

        self.assertEqual(created_group.uuid, self.mock_group1.uuid)
        self.assertEqual(created_group.name, new_group_name)

    def test_update_group(self):

        updated_group_name = "updated_name"

        self.db.query.return_value.filter.return_value.first.return_value = (
            self.mock_group1
        )

        updated_group = self.group_repository.update_group(
            self.mock_group1.uuid, updated_group_name
        )

        self.mock_group1.name = updated_group_name
        self.db.query.return_value.filter.return_value.update.assert_called_once_with(
            {Group.name: updated_group_name}
        )

        self.db.commit.assert_called_once()
        self.db.query.return_value.filter.return_value.first.assert_called_once()

        self.assertEqual(updated_group.name, updated_group_name)

    def test_delete_group_by_id(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_group1

        self.group_repository.delete_group_by_id(self.mock_group1.uuid)

        self.db.query.assert_called_once_with(Group)
        self.db.delete.assert_called_once_with(self.mock_group1)
        self.db.commit.assert_called_once()
