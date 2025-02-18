import unittest
from unittest.mock import MagicMock, patch, create_autospec
from sqlalchemy.orm import Session
from app.service.group_service import GroupService
from app.model import Group


class TestGroupService(unittest.TestCase):

    db: Session

    @patch("app.service.group_service.GroupRepository")
    def setUp(self, MockGroupRepository):
        self.db = create_autospec(Session)
        self.mock_group_repository = MockGroupRepository.return_value
        self.group_service = GroupService()
        self.group_service.group_repository = self.mock_group_repository

        self.mock_group1 = MagicMock(spec=Group)
        self.mock_group1.uuid = "be2a91c4-df99-490d-9061-bc12f50a80b7"
        self.mock_group1.name = "regular"

        self.mock_group2 = MagicMock(spec=Group)
        self.mock_group2.uuid = "b34d63a3-12fd-456e-b6d7-27c8ab69a6e3"
        self.mock_group2.name = "admin"

    def test_get_group_by_id(self):
        self.mock_group_repository.get_group_by_id.return_value = self.mock_group1

        response = self.group_service.get_group_by_id(self.db, self.mock_group1.uuid)

        self.mock_group_repository.get_group_by_id.assert_called_once_with(
            self.db, self.mock_group1.uuid
        )
        self.assertEqual(response, self.mock_group1)

    def test_get_group_by_id_not_found(self):
        self.mock_group_repository.get_group_by_id.return_value = None
        non_existing_group_id = "non-existing-uuid"

        with self.assertRaises(KeyError) as context:
            self.group_service.get_group_by_id(self.db, non_existing_group_id)

        self.mock_group_repository.get_group_by_id.assert_called_once_with(
            self.db, non_existing_group_id
        )

        expected_error_message = f"Group with id {non_existing_group_id} does not exist"
        self.assertEqual(str(context.exception.args[0]), expected_error_message)

    def test_get_all_groups(self):
        self.mock_group_repository.get_all_groups.return_value = [
            self.mock_group1,
            self.mock_group2,
        ]

        response = self.group_service.get_all_groups(self.db)

        self.mock_group_repository.get_all_groups.assert_called_once_with(self.db)

        expected_response = [
            {"uuid": self.mock_group1.uuid, "name": self.mock_group1.name},
            {"uuid": self.mock_group2.uuid, "name": self.mock_group2.name},
        ]

        actual_response = [
            {"uuid": group.uuid, "name": group.name} for group in response
        ]

        self.assertEqual(actual_response, expected_response)

    def test_get_all_groups_no_groups(self):
        self.mock_group_repository.get_all_groups.return_value = []

        with self.assertRaises(ValueError) as context:
            self.group_service.get_all_groups(self.db)

        self.assertEqual(str(context.exception), "No group in the database")
        self.mock_group_repository.get_all_groups.assert_called_once_with(self.db)

    def test_check_existing_group_name_success(self):
        self.mock_group_repository.check_exist_group_name.return_value = False

        self.group_service.check_existing_group_name(self.db, "admin")

        self.mock_group_repository.check_exist_group_name.assert_called_once_with(
            self.db, "admin"
        )

    def test_check_existing_group_name_fail(self):
        self.mock_group_repository.check_exist_group_name.return_value = True

        with self.assertRaises(KeyError) as context:
            self.group_service.check_existing_group_name(self.db, "regular")

        self.assertEqual(
            str(context.exception.args[0]), "Group with the name: regular already exist"
        )
        self.mock_group_repository.check_exist_group_name.assert_called_once_with(
            self.db, "regular"
        )

    def test_add_new_group_success(self):
        self.mock_group_repository.create_group.return_value = self.mock_group1

        response = self.group_service.add_new_group(self.db, "regular")

        self.mock_group_repository.create_group.assert_called_once_with(
            self.db, "regular"
        )
        self.assertEqual(response, self.mock_group1)

    def test_add_new_group_invalid_name(self):
        with self.assertRaises(ValueError) as context:
            self.group_service.add_new_group(self.db, "invalid_group_name")

        self.assertEqual(
            str(context.exception),
            f"Group name must be {self.mock_group1.name} or {self.mock_group2.name}",
        )

    def test_update_group(self):
        self.mock_group_repository.update_group.return_value = self.mock_group1

        response = self.group_service.update_group(
            self.db, self.mock_group1.uuid, "regular"
        )

        self.mock_group_repository.update_group.assert_called_once_with(
            self.db, self.mock_group1.uuid, "regular"
        )
        self.assertEqual(response, self.mock_group1)

    def test_update_group_invalid_name(self):
        invalid_group_name = "updated-name"

        with self.assertRaises(ValueError) as context:
            self.group_service.update_group(
                self.db, self.mock_group1.uuid, invalid_group_name
            )

        self.assertEqual(
            str(context.exception),
            "Group with name: updated-name must be regular or admin",
        )

    def test_delete_group(self):
        self.mock_group_repository.delete_group_by_id.return_value = None

        result = self.group_service.delete_group_by_id(self.db, self.mock_group1.uuid)

        self.mock_group_repository.delete_group_by_id.assert_called_once_with(
            self.db, self.mock_group1.uuid
        )
        self.assertIsNone(result)
