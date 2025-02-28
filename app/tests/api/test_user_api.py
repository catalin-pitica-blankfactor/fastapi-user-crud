from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.user_schema import UserResponseForGet
from app.service.group_service import GroupService
from app.service.user_service import UserService

client = TestClient(app)


class TestUserApi(TestCase):

    def setUp(self):

        self.user1 = {
            "uuid": "e1e2e3e4-5678-1234-abcd-5678e1234567",
            "name": "catalin",
            "group_name": ["regular"],
            "url": {"current_user_url": "https://api.github.com/user"},
        }

    @patch.object(GroupService, "get_group_by_id")
    @patch.object(UserService, "add_new_user")
    def test_create_user_success(self, mock_add_new_user, mock_get_group_by_id):

        mock_get_group_by_id.return_value = {
            "uuid": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
            "group_name": "regular",
        }
        mock_add_new_user.return_value = {"uuid": self.user1["uuid"]}

        response = client.post(
            "/user",
            json={
                "user_name": "catalin",
                "user_group": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"uuid": self.user1["uuid"]})

        mock_get_group_by_id.assert_called_once_with(
            "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        )
        mock_add_new_user.assert_called_once()

    @patch.object(GroupService, "get_group_by_id")
    @patch.object(UserService, "add_new_user")
    def test_create_user_when_group_does_not_exist(
        self, mock_add_new_group, mock_get_group_by_id
    ):
        mock_get_group_by_id.side_effect = KeyError("Group with id does not exist")

        response = client.post(
            "/user",
            json={
                "user_name": "catalin",
                "user_group": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group with id does not exist"})

        mock_get_group_by_id.assert_called_once()
        mock_add_new_group.assert_not_called()

    @patch.object(GroupService, "get_group_by_id")
    @patch.object(UserService, "add_new_user")
    def test_create_user_when_user_already_exist(
        self, mock_add_new_group, mock_get_group_by_id
    ):

        mock_add_new_group.side_effect = ValueError(
            "User with name already exist in the database"
        )
        mock_get_group_by_id.return_valeu = {
            "uuid": "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        }

        response = client.post(
            "/user",
            json={
                "user_name": "catalin",
                "user_group": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"detail": "User with name already exist in the database"}
        )

        mock_get_group_by_id.assert_called_once_with(
            "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        )
        mock_add_new_group.assert_called_once()

    @patch.object(UserService, "get_all_users")
    def test_get_all_users_success(self, mock_get_all_users):

        mock_get_all_users.return_value = [self.user1]

        response = client.get("/user")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.user1])

        mock_get_all_users.assert_called_once_with()

    @patch.object(UserService, "get_all_users")
    def test_get_all_users_value_error(self, mock_get_all_users):

        mock_get_all_users.side_effect = ValueError("No users found")

        response = client.get(f"/user/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "No users found"})

        mock_get_all_users.assert_called_once_with()

    @patch.object(UserService, "get_all_users")
    def test_get_all_users_validation_error(self, mock_get_all_users):

        try:

            UserResponseForGet(uuid="e1e2e3e4-5678-1234-abcd-5678e1234567")
        except ValidationError as validation_error_instance:
            mock_get_all_users.side_effect = validation_error_instance

        response = client.get("/user")

        self.assertEqual(response.status_code, 400)

        error_details = response.json()["detail"]

        self.assertIn("group_name", str(error_details))
        mock_get_all_users.assert_called_once_with()

    @patch.object(UserService, "get_user_by_id")
    def test_get_user_by_id_success(self, mock_get_user_by_id):

        mock_get_user_by_id.return_value = self.user1

        response = client.get(f"/user/{self.user1['uuid']}")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), self.user1)

        mock_get_user_by_id.assert_called_once_with(self.user1["uuid"])

    @patch.object(UserService, "get_user_by_id")
    def test_get_user_by_id_not_found(self, mock_get_user_by_id):

        mock_get_user_by_id.side_effect = KeyError("No user found")

        response = client.get(f"/user/{self.user1['uuid']}")

        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.json(), {"detail": "No user found"})

        mock_get_user_by_id.assert_called_once_with(self.user1["uuid"])

    @patch.object(UserService, "check_user_validation")
    @patch.object(UserService, "check_group_in_user")
    @patch.object(UserService, "update_user")
    def test_update_user_success(
        self, mock_update_user, mock_check_group_in_user, mock_check_user_validation
    ):

        mock_check_user_validation.return_value = None
        mock_check_group_in_user.return_value = None
        mock_update_user.return_value = self.user1

        response = client.put(
            f"/user/{self.user1['uuid']}",
            json={"group_name": "regular", "user_name": "updated_name"},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), self.user1)

        mock_update_user.assert_called_once()
        mock_check_group_in_user.assert_called_once()
        mock_check_user_validation.assert_called_once()

    @patch.object(UserService, "check_user_validation")
    def test_update_user_not_found(self, mock_check_user_validation):

        mock_check_user_validation.side_effect = KeyError("User does not exist")

        response = client.put(
            f"/user/{self.user1['uuid']}",
            json={"group_name": "regular", "user_name": "diana"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User does not exist"})

        mock_check_user_validation.assert_called_once_with(self.user1["uuid"])

    @patch.object(UserService, "check_group_in_user")
    @patch.object(UserService, "check_user_validation")
    def test_update_user_group_not_part_of_user(
        self, mock_check_user_validation, mock_check_group_in_user
    ):

        mock_check_user_validation.return_value = self.user1
        mock_check_group_in_user.side_effect = ValueError(
            "Group does not part of the user"
        )

        response = client.put(
            f"/user/{self.user1['uuid']}",
            json={"group_name": "admin", "user_name": "diana"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Group does not part of the user"})

        mock_check_user_validation.assert_called_once()
        mock_check_group_in_user.assert_called_once_with(self.user1, "admin")

    @patch.object(UserService, "delete_user_by_id")
    @patch.object(UserService, "get_user_by_id")
    def test_delete_user_by_id_success(
        self, mock_get_user_by_id, mock_delete_user_by_id
    ):

        mock_get_user_by_id.return_value = self.user1
        mock_delete_user_by_id.return_value = None

        response = client.delete(f"/user/{self.user1['uuid']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)

        mock_get_user_by_id.assert_called_once_with(self.user1["uuid"])
        mock_delete_user_by_id.assert_called_once()

    @patch.object(UserService, "delete_user_by_id")
    @patch.object(UserService, "get_user_by_id")
    def test_delete_user_not_found(self, mock_get_user_by_id, mock_delete_user_by_id):

        mock_get_user_by_id.side_effect = KeyError("User with id does not exist")

        response = client.delete(f"/user/{self.user1['uuid']}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User with id does not exist"})

        mock_get_user_by_id.assert_called_once()
        mock_delete_user_by_id.assert_not_called()
