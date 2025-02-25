import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.model.group_model import Group


class GroupRepository:

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_group_by_id(self, group_id: str):
        return self.db.query(Group).filter(Group.uuid == group_id).first()

    def get_all_groups(self):
        return self.db.query(Group).all()

    def check_exist_group_name(self, group_name):
        return self.db.query(Group).filter(Group.name == group_name).first()

    def create_group(self, name: str):
        new_id = str(uuid.uuid4())
        db_group = Group(uuid=new_id, name=name)
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def update_group(self, group_id: str, group_name: str):
        self.db.query(Group).filter(Group.uuid == group_id).update(
            {Group.name: group_name}
        )
        self.db.commit()
        db_group_update = self.db.query(Group).filter(Group.uuid == group_id).first()
        return db_group_update

    def delete_group_by_id(self, group_id: str):
        group = self.db.query(Group).filter(Group.uuid == group_id).first()
        self.db.delete(group)
        self.db.commit()
