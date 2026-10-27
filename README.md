# Learning Pathway Service

Microservicio FastAPI responsable de las rutas de aprendizaje de PathBridge. Genera recursos de YouTube a partir de brechas técnicas, registra el avance manual de videos y valida certificados por OCR.

Al aprobar un certificado, agrega de forma idempotente la habilidad como `hard_skill` en Identity Service y solicita a Gap Analysis el recálculo para el empleo de la ruta. No asigna un nivel no demostrado. La respuesta del certificado incluye el estado de ambas sincronizaciones para permitir seguimiento y reintentos seguros.

## Configuración local

1. Crea una base PostgreSQL, por ejemplo `learning_pathway_db`.
2. Define las variables `DATABASE_URL`, `IDENTITY_SERVICE_URL`, `GAP_ANALYSIS_SERVICE_URL`, `YOUTUBE_DATA_API_KEY` y `GATEWAY_USER_ID_HEADER`.
3. Instala las dependencias, aplica la migración y ejecuta el servicio:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8003
```

## Endpoints disponibles

- `GET /health`
- `POST /api/v1/learning-paths`
- `GET /api/v1/learning-paths/{job_id}`
- `PATCH /api/v1/learning-paths/{learning_path_id}/items/{item_id}`
- `GET /api/v1/learning-paths/{learning_path_id}/progress`
- `POST /api/v1/certificates` (multipart: `learning_path_id`, `skill_name`, `provider` opcional y `file`)
- `GET /api/v1/certificates/{certificate_id}`
- `POST /api/v1/certificates/{certificate_id}/synchronization` para reintentar una sincronización fallida.
