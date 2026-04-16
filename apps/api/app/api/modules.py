import sys
import os
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/packages")

from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from packages.core.models.user import User
from packages.core.models.module import Module
from packages.core.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/modules", tags=["modules"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=List[ModuleResponse])
async def list_modules(
    current_user: CurrentUser,
    db: DBSession
):
    result = await db.execute(select(Module))
    modules = result.scalars().all()
    return modules


@router.post("", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    current_user: CurrentUser,
    db: DBSession
):
    result = await db.execute(select(Module).where(Module.slug == module_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El slug del módulo ya existe"
        )

    module = Module(
        name=module_data.name,
        slug=module_data.slug,
        description=module_data.description,
        version=module_data.version,
        is_system=module_data.is_system,
        is_active=module_data.is_active,
        icon=module_data.icon,
        config_schema=module_data.config_schema,
        admin_url=module_data.admin_url,
    )

    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: int,
    current_user: CurrentUser,
    db: DBSession
):
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo no encontrado"
        )

    return module


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_update: ModuleUpdate,
    current_user: CurrentUser,
    db: DBSession
):
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo no encontrado"
        )

    update_data = module_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(module, key, value)

    await db.commit()
    await db.refresh(module)
    return module


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    current_user: CurrentUser,
    db: DBSession
):
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo no encontrado"
        )

    await db.delete(module)
    await db.commit()