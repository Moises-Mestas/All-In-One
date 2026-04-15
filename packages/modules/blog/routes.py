from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import shutil
import uuid
import os

# Importamos tu configuracion de base de datos
from app.db.database import get_db
# Importamos nuestros schemas, servicios y modelos del blog
from packages.modules.blog import schemas, services
from packages.modules.blog.models import Post, Category, PostStatus

# 👇 CORRECCIÓN 1: Agregamos el /v1 para que coincida con React
router = APIRouter(prefix="/modules/blog", tags=["Module: Blog"])
# ==========================================
# RUTAS PARA CATEGORÍAS
# ==========================================
@router.post("/{site_id}/categories", response_model=schemas.CategoryResponse)
async def create_category_route(site_id: int, category_in: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_category(db, site_id, category_in)

# ==========================================
# RUTAS PARA ARTÍCULOS (POSTS)
# ==========================================

# 1. Crear un artículo (Borrador por defecto)
@router.post("/{site_id}/posts", response_model=schemas.PostResponse)
async def create_post_route(site_id: int, post_in: schemas.PostCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_post(db, site_id, post_in)

# 2. Listar todos los artículos de un sitio
@router.get("/{site_id}/posts", response_model=List[schemas.PostResponse])
async def list_posts_route(site_id: int, only_published: bool = False, db: AsyncSession = Depends(get_db)):
    return await services.get_posts_by_site(db, site_id, only_published)

# 3. Obtener un artículo específico
@router.get("/{site_id}/posts/{slug}", response_model=schemas.PostResponse)
async def get_post_route(site_id: int, slug: str, db: AsyncSession = Depends(get_db)):
    return await services.get_post_by_slug(db, site_id, slug)

# 4. Actualizar un artículo
@router.put("/{site_id}/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post_route(site_id: int, post_id: int, post_in: schemas.PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id, Post.site_id == site_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    update_data = post_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
        
    await db.commit()
    await db.refresh(post)
    return post

# 5. Borrar un artículo
@router.delete("/{site_id}/posts/{post_id}")
async def delete_post_route(site_id: int, post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id, Post.site_id == site_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    await db.delete(post)
    await db.commit()
    return {"message": "Artículo eliminado correctamente"}

# ==========================================
# 👇 CORRECCIÓN 2: RUTA ÚNICA Y CORRECTA PARA IMÁGENES
# ==========================================
@router.post("/{site_id}/upload-image")
async def upload_blog_image(site_id: int, file: UploadFile = File(...)):
    try:
        # Creamos la carpeta de subidas si no existe
        upload_dir = "/app/uploads/blog"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generamos un nombre único
        ext = file.filename.split('.')[-1]
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        save_path = f"{upload_dir}/{new_filename}"
        
        # Guardamos el archivo
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"url": f"/uploads/blog/{new_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando imagen: {str(e)}")