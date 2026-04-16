import sys
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/packages")

from datetime import datetime, timezone
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from packages.core.models.user import User
from packages.core.models.site_module import SiteModule
from packages.core.models.site import Site
from packages.core.models.module import Module
from packages.core.schemas.site_module import SiteModuleCreate, SiteModuleUpdate, SiteModuleResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/site-modules", tags=["site-modules"])

def now_utc():
    return datetime.now(timezone.utc)

@router.get("", response_model=List[SiteModuleResponse])
async def list_site_modules(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(SiteModule)
        .join(Site)
        .where(Site.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/site/{site_id}", response_model=List[SiteModuleResponse])
async def get_site_modules(
    site_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result_site = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id)
    )

    if not result_site.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    result = await db.execute(
        select(SiteModule).where(SiteModule.site_id == site_id)
    )
    return result.scalars().all()

@router.post("", response_model=SiteModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_site_module(
    site_module_data: SiteModuleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result_site = await db.execute(
        select(Site).where(Site.id == site_module_data.site_id, Site.user_id == current_user.id)
    )
    if not result_site.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    result_module = await db.execute(
        select(Module).where(Module.id == site_module_data.module_id)
    )
    if not result_module.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    result_exists = await db.execute(
        select(SiteModule).where(
            SiteModule.site_id == site_module_data.site_id,
            SiteModule.module_id == site_module_data.module_id
        )
    )
    if result_exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Este módulo ya está asignado a este sitio")

    site_module = SiteModule(
        site_id=site_module_data.site_id,
        module_id=site_module_data.module_id,
        is_active=site_module_data.is_active,
        config=site_module_data.config,
        activated_at=now_utc() if site_module_data.is_active else None,
    )

    db.add(site_module)
    await db.commit()
    await db.refresh(site_module)
    return site_module

@router.post("/site/{site_id}/activate-module/{module_slug}", response_model=SiteModuleResponse)
async def activate_module_for_site(
    site_id: int,
    module_slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result_site = await db.execute(
        select(Site).where(Site.id == site_id, Site.user_id == current_user.id)
    )
    site = result_site.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    result_module = await db.execute(
        select(Module).where(Module.slug == module_slug)
    )
    module = result_module.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail=f"Módulo '{module_slug}' no encontrado")

    result_exists = await db.execute(
        select(SiteModule).where(
            SiteModule.site_id == site_id,
            SiteModule.module_id == module.id
        )
    )
    existing = result_exists.scalar_one_or_none()

    default_config = {
        "registration_fields": ["email", "password", "first_name", "last_name", "phone"],
        "custom_fields": [],
        "require_verification": False
    }

    if existing:
        existing.is_active = True
        existing.config = default_config
        existing.activated_at = now_utc()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        new_sm = SiteModule(
            site_id=site_id,
            module_id=module.id,
            is_active=True,
            config=default_config,
            activated_at=now_utc()
        )
        db.add(new_sm)
        await db.commit()
        await db.refresh(new_sm)
        return new_sm

@router.put("/{site_module_id}", response_model=SiteModuleResponse)
async def update_site_module(
    site_module_id: int,
    site_module_update: SiteModuleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(SiteModule)
        .join(Site)
        .where(SiteModule.id == site_module_id, Site.user_id == current_user.id)
    )
    site_module = result.scalar_one_or_none()

    if not site_module:
        raise HTTPException(status_code=404, detail="SiteModule no encontrado")

    if site_module_update.is_active is not None:
        site_module.is_active = site_module_update.is_active
        if site_module_update.is_active:
            site_module.activated_at = now_utc()
        else:
            site_module.deactivated_at = now_utc()

    if site_module_update.config is not None:
        site_module.config = site_module_update.config

    await db.commit()
    await db.refresh(site_module)
    return site_module

@router.delete("/{site_module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_module(
    site_module_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(SiteModule)
        .join(Site)
        .where(SiteModule.id == site_module_id, Site.user_id == current_user.id)
    )
    site_module = result.scalar_one_or_none()

    if not site_module:
        raise HTTPException(status_code=404, detail="SiteModule no encontrado")

    await db.delete(site_module)
    await db.commit()

@router.post("/{site_module_id}/toggle", response_model=SiteModuleResponse)
async def toggle_site_module(
    site_module_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(SiteModule)
        .join(Site)
        .where(SiteModule.id == site_module_id, Site.user_id == current_user.id)
    )
    site_module = result.scalar_one_or_none()

    if not site_module:
        raise HTTPException(status_code=404, detail="SiteModule no encontrado")

    site_module.is_active = not site_module.is_active

    if site_module.is_active:
        site_module.activated_at = now_utc()
    else:
        site_module.deactivated_at = now_utc()

    await db.commit()
    await db.refresh(site_module)
    return site_module