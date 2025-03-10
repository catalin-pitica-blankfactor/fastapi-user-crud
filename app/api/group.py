from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from app.schemas.group_schema import (GroupCreate, GroupResponseForCreate,
                                      GroupResponseForGet)
from app.service.group_service import GroupService

router = APIRouter()


@router.post("/group", response_model=GroupResponseForCreate)
async def create_group(
    group: GroupCreate,
    group_service: GroupService = Depends(),
):
    try:
        group_service.check_existing_group_name(group.name)
        return group_service.add_new_group(group.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@router.get("/group", response_model=list[GroupResponseForGet])
async def get_all_groups(group_service: GroupService = Depends()):
    try:
        return group_service.get_all_groups()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])


@router.get("/group/{group_id}", response_model=GroupResponseForGet)
async def get_group_by_id(
    group_id: str,
    group_service: GroupService = Depends(),
):
    try:
        return group_service.get_group_by_id(group_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@router.put("/group/{group_id}", response_model=GroupResponseForCreate)
async def update_group(
    group_id: str,
    group_name: GroupCreate,
    group_service: GroupService = Depends(),
):
    try:
        group_service.get_group_by_id(group_id)
        group_service.check_existing_group_name(group_name.name)
        return group_service.update_group(group_id, group_name.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@router.delete("/group/{group_id}")
async def delete_group_by_id(
    group_id: str,
    group_service: GroupService = Depends(),
):
    try:
        group_service.get_group_by_id(group_id)
        return group_service.delete_group_by_id(group_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])
