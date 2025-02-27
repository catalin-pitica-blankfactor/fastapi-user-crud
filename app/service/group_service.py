from typing import Annotated, Any

from fastapi import Depends

from app.core.constants import GroupType
from app.repository.group_repository import GroupRepository


class GroupService:
    def __init__(self, r: Annotated[GroupRepository, Depends(GroupRepository)]):
        self.group_repository = r

    def add_new_group(self, name: str) -> Any:
        if name not in {group.value for group in GroupType}:
            raise ValueError(
                f"Group name must be {GroupType.REGULAR.value} or {GroupType.ADMIN.value}"
            )
        return self.group_repository.create_group(name)

    def check_existing_group_name(self, group_name: str):
        if self.group_repository.check_exist_group_name(group_name):
            raise KeyError(f"Group with the name: {group_name} already exist")

    def get_all_groups(self):
        all_groups = self.group_repository.get_all_groups()
        if not all_groups:
            raise ValueError(f"No group in the database")
        return all_groups

    def get_group_by_id(self, group_id: str):
        group = self.group_repository.get_group_by_id(group_id)
        if not group:
            raise KeyError(f"Group with id {group_id} does not exist")
        return group

    def update_group(self, id: str, name: str):
        if name not in {group.value for group in GroupType}:
            raise ValueError(
                f"Group with name: {name} must be {GroupType.REGULAR.value} or {GroupType.ADMIN.value}"
            )
        return self.group_repository.update_group(id, name)

    def delete_group_by_id(self, group_id: str):
        return self.group_repository.delete_group_by_id(group_id)
