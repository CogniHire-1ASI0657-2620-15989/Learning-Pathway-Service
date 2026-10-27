from io import BytesIO

import fitz
import pytesseract
from PIL import Image

from app.application.ports.certificate_text_extractor import CertificateTextExtractor


class TesseractCertificateTextExtractor(CertificateTextExtractor):
    async def extract_text(self, content: bytes, content_type: str) -> str:
        if content_type == "application/pdf":
            return self._extract_pdf_text(content)
        return self._extract_image_text(content)

    def _extract_pdf_text(self, content: bytes) -> str:
        document = fitz.open(stream=content, filetype="pdf")
        try:
            text = "\n".join(page.get_text() for page in document)
            if text.strip():
                return text
            if document.page_count == 0:
                return ""
            pixmap = document[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            return pytesseract.image_to_string(image, lang="spa+eng")
        finally:
            document.close()

    @staticmethod
    def _extract_image_text(content: bytes) -> str:
        with Image.open(BytesIO(content)) as image:
            return pytesseract.image_to_string(image, lang="spa+eng")
