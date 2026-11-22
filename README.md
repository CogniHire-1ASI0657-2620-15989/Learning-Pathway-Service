# Learning Pathway Service

Microservicio FastAPI responsable de las rutas de aprendizaje de PathBridge. Genera recursos de YouTube a partir de brechas técnicas, registra el avance manual de videos y valida certificados por OCR (Tesseract, local, sin API externa).

Al aprobar un certificado, agrega de forma idempotente la habilidad como `hard_skill` en Identity Service y solicita a Gap Analysis el recálculo para el empleo de la ruta. No asigna un nivel no demostrado. La respuesta del certificado incluye el estado de ambas sincronizaciones para permitir seguimiento y reintentos seguros.

## Configuración local

1. Crea una base PostgreSQL, por ejemplo `learning_pathway_db`.
2. Define las variables obligatorias: `DATABASE_URL`, `IDENTITY_SERVICE_URL`, `GAP_ANALYSIS_SERVICE_URL`, `YOUTUBE_DATA_API_KEY`, `GATEWAY_USER_ID_HEADER` e **`INTERNAL_API_KEY`** (secreto compartido que debe enviar el Gateway en `X-Internal-Api-Key`; ver "Seguridad de red"). `DATABASE_SCHEMA` es opcional (por defecto `learning_pathway`).
3. Variables opcionales (no vienen en `.env.example`):
   - `REDIS_URL`: habilita el caché de recomendaciones de YouTube. Sin ella, el servicio sigue funcionando sin cachear.
   - `RABBITMQ_URL`: requerida solo para ejecutar el worker asíncrono (ver "Worker de eventos").
4. Instala las dependencias, aplica la migración y ejecuta el servicio:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8003
```

## Seguridad de red

El servicio **no valida JWT**: esa responsabilidad es del API Gateway, que reenvía el id del usuario autenticado en el header configurable `X-User-Id` (`GATEWAY_USER_ID_HEADER`) y el secreto compartido en `X-Internal-Api-Key`. Un middleware global exige `X-Internal-Api-Key` en **todas las rutas excepto `/health`**; sin ese header la respuesta es `401 Unauthorized` (`application/problem+json`).

## Endpoints disponibles

- `GET /health`
- `POST /api/v1/learning-paths`
- `GET /api/v1/learning-paths/{job_id}`
- `PATCH /api/v1/learning-paths/{learning_path_id}/items/{item_id}`
- `GET /api/v1/learning-paths/{learning_path_id}/progress`
- `POST /api/v1/certificates` (multipart: `learning_path_id`, `skill_name`, `provider` opcional y `file`; solo PDF, JPG o PNG, máx. 5 MB)
- `GET /api/v1/certificates?learning_path_id={id}` para listar certificados propios, opcionalmente filtrados por ruta.
- `GET /api/v1/certificates/{certificate_id}`
- `POST /api/v1/certificates/{certificate_id}/synchronization` para reintentar una sincronización fallida con Identity Service.

## Validación de certificados (OCR)

Tesseract extrae el texto del archivo y el servicio lo contrasta contra el nombre del candidato y la skill de la ruta. El certificado queda en uno de estos estados:

- `approved`: el texto menciona al candidato y a la skill correcta → se registra como `hard_skill` verificada y se recalcula el reporte de brechas.
- `name_mismatch`: el nombre del certificado no coincide con el perfil.
- `course_mismatch`: el certificado no menciona la skill de la ruta.
- `unreadable`: no se pudo extraer texto suficiente del archivo.

Si la sincronización con Identity Service o Gap Analysis falla tras una aprobación, el certificado conserva el estado de cada sincronización por separado y puede reintentarse con `POST /synchronization` sin repetir el OCR.

## Caché y resiliencia de recomendaciones

Las búsquedas de video en YouTube pasan por un `CircuitBreaker` y, si `REDIS_URL` está definido, por un caché best-effort (`RedisJsonCache`): una falla de Redis nunca bloquea la generación de la ruta, simplemente no se cachea.

## Worker de eventos (RabbitMQ)

`app/workers/gap_report_consumer.py` es un proceso independiente (no corre dentro de `uvicorn`) que escucha el evento `gap_report.generated` publicado por Gap Analysis Service en el exchange `pathbridge.events` y pre-calienta (busca y cachea) los videos de YouTube para hasta 10 de las `missing_hard_skills` del reporte, antes de que el candidato pida su ruta. Incluye cola de reintentos (TTL 30s, hasta 3 intentos) y dead-letter queue (`learning-pathway.gap-report.dlq`) para eventos que fallan repetidamente.

Requiere `RABBITMQ_URL`. Se ejecuta como proceso aparte:

```powershell
python -m app.workers.gap_report_consumer
```

## Observabilidad

- Cada request recibe/propaga un `X-Correlation-ID`, incluido en los logs (JSON estructurado) y en las respuestas de error.
- Los errores se devuelven como `application/problem+json` (RFC 7807): `type`, `title`, `status`, `detail`, `instance` y `correlation_id`.

## Pruebas

Incluye tests unitarios (`tests/`) y pruebas de aceptación en Gherkin con `pytest-bdd` (`tests/bdd/features/*.feature`). Identity Service, Gap Analysis, YouTube, Redis y el OCR se sustituyen por fakes en memoria, por lo que no se necesita infraestructura externa para correrlos.

Features cubiertas:
- `learning_pathway_generation.feature` — generación de la ruta (US14).
- `course_external_links.feature` — enlaces externos a cursos (US15).
- `certificate_upload.feature` — carga de certificados (US16).
- `certificate_automatic_validation.feature` — validación automática por OCR (US17).
- `certificate_validation_error_handling.feature` — manejo de errores y reintento de sincronización (US18).
- `learning_pathway_progress_tracking.feature` — barra de progreso (US19).

Ejecutar todo:

```powershell
pytest
```
