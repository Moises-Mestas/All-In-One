FROM python:3.12.3

# Crear usuario no-root
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

WORKDIR /app

# Copiar requirements primero
COPY apps/api/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY apps/api .

# Cambiar permisos
RUN chown -R appuser:appgroup /app

# Usar usuario seguro
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]