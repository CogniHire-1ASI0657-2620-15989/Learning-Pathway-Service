# Learning Pathway Service

Microservicio FastAPI responsable de las rutas de aprendizaje de PathBridge.

Esta primera entrega solo prepara el esqueleto técnico: servicio aislado, configuración, acceso a su futura base PostgreSQL, Alembic y health check. Las rutas de aprendizaje, las integraciones y los modelos de negocio se incorporarán en los siguientes incrementos.

## Configuración local

1. Crea una base PostgreSQL, por ejemplo `learning_pathway_db`.
2. Define la variable `DATABASE_URL`.
3. Instala las dependencias, aplica la migración y ejecuta el servicio:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8003
```

## Endpoint disponible

- `GET /health`
