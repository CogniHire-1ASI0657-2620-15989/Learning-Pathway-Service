from io import BytesIO

from PIL import Image, UnidentifiedImageError


class CertificateContentValidator:
    MAX_FILE_SIZE_BYTES = 5_000_000
    ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}

    @classmethod
    def validate(cls, content: bytes, content_type: str) -> None:
        if not content:
            raise ValueError("El archivo del certificado está vacío.")
        if len(content) > cls.MAX_FILE_SIZE_BYTES:
            raise ValueError("El archivo del certificado no puede superar 5 MB.")
        if content_type not in cls.ALLOWED_CONTENT_TYPES:
            raise ValueError("Solo se aceptan certificados PDF, JPG o PNG.")
        if content_type == "application/pdf":
            if not content.startswith(b"%PDF-"):
                raise ValueError("El archivo no contiene un PDF válido.")
            return
        try:
            with Image.open(BytesIO(content)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("El archivo no contiene una imagen válida.") from exc
