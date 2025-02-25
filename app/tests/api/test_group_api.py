from unittest import TestCase
from unittest.mock import patch
from app.main import app
from fastapi.testclient import TestClient
from app.service.group_service import GroupService


client = TestClient(app)


class TestGroupAPI(TestCase):

    def setUp(self):

        self.group1 = {
            "uuid": "be2a91c4-df99-490d-9061-bc12f50a80b7",
            "name": "regular",
        }

        self.group2 = {
            "uuid": "b34d63a3-12fd-456e-b6d7-27c8ab69a6e3",
            "name": "admin",
        }

    @patch.object(GroupService, "check_existing_group_name")
    @patch.object(GroupService, "add_new_group")
    def test_create_group(self, mock_add_new_group, mock_check_existing_group_name):

        mock_check_existing_group_name.return_value = None
        mock_add_new_group.return_value = self.group1

        response = client.post("/group", json={"name": "regular"})

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), {"uuid": self.group1["uuid"]})

        mock_check_existing_group_name.assert_called_once_with("regular")
        mock_add_new_group.assert_called_once_with("regular")

    @patch.object(GroupService, "check_existing_group_name")
    @patch.object(GroupService, "add_new_group")
    def test_create_group_already_exist(
        self, mock_add_new_group, mock_check_existing_group_name
    ):

        mock_check_existing_group_name.side_effect = KeyError(
            "Group name already exist"
        )

        response = client.post("/group", json={"name": "duplicate-group"})

        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.json(), {"detail": "Group name already exist"})

        mock_check_existing_group_name.assert_called_once_with("duplicate-group")
        mock_add_new_group.assert_not_called()

    @patch.object(GroupService, "check_existing_group_name")
    @patch.object(GroupService, "add_new_group")
    def test_create_group_value_error_when_add_wrong_group_name(
        self, mock_add_new_group, mock_check_existing_group_name
    ):

        mock_add_new_group.side_effect = ValueError(
            "Group name must be regular or admin"
        )

        response = client.post("/group", json={"name": "test"})

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json(), {"detail": "Group name must be regular or admin"}
        )

        mock_add_new_group.assert_called_once_with("test")
        mock_check_existing_group_name.assert_called_once_with("test")

    @patch.object(GroupService, "get_all_groups")
    def test_get_all_groups_success(self, mock_get_all_groups):

        mock_get_all_groups.return_value = [
            {"uuid": "be2a91c4-df99-490d-9061-bc12f50a80b7", "name": "regular"},
            {"uuid": "b34d63a3-12fd-456e-b6d7-27c8ab69a6e3", "name": "admin"},
        ]

        response = client.get("/group")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), [self.group1, self.group2])

        mock_get_all_groups.assert_called_once()

    @patch.object(
        GroupService,
        "get_all_groups",
    )
    def test_get_all_groups_no_groups(self, mock_get_all_groups):

        mock_get_all_groups.side_effect = ValueError("No group found")

        response = client.get("/group")

        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.json(), {"detail": "No group found"})

        mock_get_all_groups.assert_called_once()

    @patch.object(GroupService, "get_group_by_id")
    def test_get_group_by_id(self, mock_get_group_by_id):

        mock_get_group_by_id.return_value = self.group1

        response = client.get(f"/group/{self.group1['uuid']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.group1)
        mock_get_group_by_id.assert_called_once_with(self.group1["uuid"])

    @patch.object(GroupService, "get_group_by_id")
    def test_get_group_by_id_not_found(self, mock_get_group_by_id):

        mock_get_group_by_id.side_effect = KeyError("Group not found")

        response = client.get("/group/non-existing-id")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group not found"})

        mock_get_group_by_id.assert_called_once_with("non-existing-id")

    @patch.object(GroupService, "update_group")
    @patch.object(GroupService, "get_group_by_id")
    @patch.object(GroupService, "check_existing_group_name")
    def test_update_group(
        self, mock_check_existing_group_name, mock_get_group_by_id, mock_update_group
    ):

        updated_group = {"uuid": self.group1["uuid"], "name": "updated-regular"}
        mock_get_group_by_id.return_value = self.group1
        mock_update_group.return_value = updated_group
        mock_check_existing_group_name.return_value = None
        response = client.put(
            f"/group/{self.group1['uuid']}", json={"name": "updated-regular"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"uuid": updated_group["uuid"]})
        mock_get_group_by_id.assert_called_once_with(self.group1["uuid"])
        mock_check_existing_group_name.assert_called_once_with(updated_group["name"])
        mock_update_group.assert_called_once_with(
            self.group1["uuid"], "updated-regular"
        )

    @patch.object(GroupService, "update_group")
    @patch.object(GroupService, "get_group_by_id")
    @patch.object(GroupService, "check_existing_group_name")
    def test_update_group_raises_value_error_when_group_name_already_exists(
        self, mock_check_existing_group_name, mock_get_group_by_id, mock_update_group
    ):

        updated_group = {"uuid": self.group1["uuid"], "name": "updated-regular"}
        mock_get_group_by_id.return_value = updated_group
        mock_check_existing_group_name.side_effect = KeyError(
            "Group name already exist"
        )

        response = client.put(
            f"/group/{updated_group['uuid']}", json={"name": "updated-regular"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group name already exist"})
        mock_get_group_by_id.assert_called_once_with(self.group1["uuid"])
        mock_check_existing_group_name.assert_called_once_with(updated_group["name"])
        mock_update_group.assert_not_called()

    @patch.object(GroupService, "update_group")
    @patch.object(GroupService, "get_group_by_id")
    @patch.object(GroupService, "check_existing_group_name")
    def test_update_group_not_found(
        self, mock_check_existing_group_name, mock_get_group_by_id, mock_update_group
    ):

        mock_get_group_by_id.side_effect = KeyError("group with id not found")

        response = client.put(
            f"/group/{self.group1['uuid']}", json={"name": "updated-regular"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "group with id not found"})
        mock_get_group_by_id.assert_called_once_with(self.group1["uuid"])
        mock_update_group.assert_not_called()
        mock_check_existing_group_name.assert_not_called()

    @patch.object(GroupService, "update_group")
    @patch.object(GroupService, "get_group_by_id")
    @patch.object(GroupService, "check_existing_group_name")
    def test_update_group_when_wring_group_name(
        self, mock_check_existing_group_name, mock_get_group_by_id, mock_update_group
    ):

        mock_check_existing_group_name.return_value = None
        mock_get_group_by_id.return_value = None
        mock_update_group.side_effect = ValueError(
            "Group name must be regular or admin"
        )

        response = client.put(
            f"/group/{self.group1['uuid']}", json={"name": "updated-test"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"detail": "Group name must be regular or admin"}
        )

        mock_check_existing_group_name.assert_called_once()
        mock_get_group_by_id.assert_called_once()
        mock_update_group.assert_called_once()

    @patch.object(GroupService, "get_group_by_id")
    @patch.object(GroupService, "delete_group_by_id")
    def test_delete_group_by_id(self, mock_delete_group_by_id, mock_get_group_by_id):

        mock_get_group_by_id.return_value = self.group1
        mock_delete_group_by_id.return_value = None

        response = client.delete(f"/group/{self.group1['uuid']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)
        mock_get_group_by_id.assert_called_once_with(self.group1["uuid"])
        mock_delete_group_by_id.assert_called_once_with(self.group1["uuid"])

    @patch.object(GroupService, "get_group_by_id")
    @patch.object(GroupService, "delete_group_by_id")
    def test_delete_group_by_id_not_found(
        self, mock_delete_group_by_id, mock_get_group_by_id
    ):

        mock_get_group_by_id.side_effect = KeyError("Group not found")

        response = client.delete(f"/group/{self.group1['uuid']}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group not found"})
        mock_get_group_by_id.assert_called_once_with(self.group1["uuid"])
        mock_delete_group_by_id.assert_not_called()
