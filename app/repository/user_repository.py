import json
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.model.group_model import Group
from app.model.user_model import User


class UserRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_user_by_id(self, user_id: str):
        return self.db.query(User).filter(User.uuid == user_id).first()

    def get_user_by_name(self, user_name: str):
        return self.db.query(User).filter(User.name == user_name).first()

    def get_all_users(self):
        return self.db.query(User).options(joinedload(User.group)).all()

    def create_user(self, user_name: str, user_group: str):
        group_for_user = self.db.query(Group).filter(Group.uuid == user_group).first()
        new_id = str(uuid.uuid4())
        db_user = User(uuid=new_id, name=user_name)
        db_user.group.append(group_for_user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user_url(self, user_id: str, updated_content: json):
        user = self.db.query(User).filter(User.uuid == user_id).first()
        user.urls = updated_content
        self.db.commit()
        self.db.refresh(user)

    def update_user(self, user_id: str, user_name: str):
        self.db.query(User).filter(User.uuid == user_id).update({User.name: user_name})
        self.db.commit()
        user_updated = self.db.query(User).filter(User.uuid == user_id).first()
        return user_updated

    def delete_user(self, user_id: str):
        user = self.db.query(User).filter(User.uuid == user_id).first()
        self.db.delete(user)
        self.db.commit()
