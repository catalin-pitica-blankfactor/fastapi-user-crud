from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import ValidationError

from app.schemas.user_schema import (UserCreate, UserResponse,
                                     UserResponseForGet, UserUpdate)
from app.service.group_service import GroupService
from app.service.user_service import UserService

router = APIRouter()


@router.post("/user", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    background_task: BackgroundTasks,
    user_service: UserService = Depends(),
    group_service: GroupService = Depends(),
):
    try:
        group_service.get_group_by_id(user.user_group)
        return user_service.add_new_user(
            user.user_name, user.user_group, background_task
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])


@router.get("/user", response_model=list[UserResponseForGet])
async def get_all_users(user_service: UserService = Depends()):
    try:
        users = user_service.get_all_users()
        return users
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.json())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])


@router.get("/user/{user_id}", response_model=UserResponseForGet)
async def get_user_by_id(user_id: str, user_service: UserService = Depends()):
    try:
        return user_service.get_user_by_id(user_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@router.put("/user/{user_id}", response_model=UserResponseForGet)
async def update_user(
    user_id: str,
    user_group: UserUpdate,
    user_service: UserService = Depends(),
):
    try:
        user = user_service.check_user_validation(user_id)
        user_service.check_group_in_user(user, user_group.group_name)
        return user_service.update_user(user_id, user_group.user_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@router.delete("/user/{user_id}")
async def delete_user_by_id(user_id: str, user_service: UserService = Depends()):
    try:
        user_service.get_user_by_id(user_id)
        return user_service.delete_user_by_id(user_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])
