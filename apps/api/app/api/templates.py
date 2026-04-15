from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.database import get_db
from packages.core.models.template import Template
from packages.core.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])

@router.get("", response_model=List[TemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Template).where(Template.is_active == True))
    return result.scalars().all()

@router.post("", response_model=TemplateResponse)
async def create_template(template_in: TemplateCreate, db: AsyncSession = Depends(get_db)):
    # Verificar que el slug no exista
    existing = await db.execute(select(Template).where(Template.slug == template_in.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El slug ya está en uso")
    
    db_template = Template(**template_in.model_dump())
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: int, template_in: TemplateUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
        
    for key, value in template_in.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
        
    await db.commit()
    await db.refresh(template)
    return template

@router.delete("/{template_id}")
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
        
    await db.delete(template)
    await db.commit()
    return {"message": "Plantilla eliminada"}