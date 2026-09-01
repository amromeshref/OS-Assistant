from oshope.interfaces.voice_input.google_speech_recognition_service import (
    GoogleSpeechRecognitionService,
)
from oshope.config.config import (
    AVAILABLE_VOICE_PLATFORMS,
    DEFAULT_VOICE_PLATFORM,
)
from oshope.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceInputInterface:
    def __init__(self, platform: str = None):
        if platform is None:
            platform = DEFAULT_VOICE_PLATFORM
        self.platform = platform

        logger.info(f"Initializing VoiceInputInterface with platform: {self.platform}")

        if self.platform == "google":
            self.service = GoogleSpeechRecognitionService()
        else:
            logger.error(
                f"Unsupported voice input platform: {self.platform}. Available platforms are: {AVAILABLE_VOICE_PLATFORMS}"
            )
            raise ValueError(
                f"Unsupported voice input platform: {self.platform}. Available platforms are: {AVAILABLE_VOICE_PLATFORMS}"
            )
