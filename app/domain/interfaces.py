from abc import ABC, abstractmethod


class OCRService(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        pass

class EmailService(ABC):
    @abstractmethod
    def send_notification(
            self,
            recipient: str,
            image_path: str,
            extracted_text: str
    ) -> bool:
        pass