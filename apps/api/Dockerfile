FROM python:3.12.3

# Crear usuario no-root
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

WORKDIR /app

# Copiar requirements
COPY apps/api/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY apps/api .

# Dar permisos al usuario no-root
RUN chown -R appuser:appgroup /app

# Cambiar a usuario seguro
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]