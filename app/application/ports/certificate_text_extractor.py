from abc import ABC, abstractmethod


class CertificateTextExtractor(ABC):
    @abstractmethod
    async def extract_text(self, content: bytes, content_type: str) -> str: ...
