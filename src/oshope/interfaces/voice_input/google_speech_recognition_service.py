from oshope.utils.logger import get_logger
import speech_recognition as sr
from pynput import keyboard

logger = get_logger(__name__)


class GoogleSpeechRecognitionService:
    def __init__(self):
        logger.info("Initializing Google Speech Recognition Service")
        self.start_key_listener()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = True
        self.audio_data = []

    def on_press(self, key):
        if key == keyboard.Key.esc:
            logger.info("Escape key pressed. Stopping listener.")
            self.is_listening = False

    def start_key_listener(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        logger.info("Started key listener for Escape key to stop recording.")

    def start_listening(self):
        print("Please speak now. Press Escape when you're done.")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening...")

            while self.is_listening:
                try:
                    # phrase_time_limit captures a chunk of speech (5 seconds max here)
                    audio_chunk = self.recognizer.listen(
                        source, timeout=1, phrase_time_limit=5
                    )
                    self.audio_data.append(audio_chunk)
                    # print("Captured a chunk...")
                except sr.WaitTimeoutError:
                    # No speech detected in timeout, keep listening
                    pass

    def transcribe_audio(self):
        full_transcription = ""
        for audio_chunk in self.audio_data:
            try:
                transcription = self.recognizer.recognize_google(audio_chunk)
                full_transcription += transcription + " "
            except sr.UnknownValueError:
                logger.warning(
                    "Google Speech Recognition could not understand audio chunk."
                )
            except sr.RequestError as e:
                logger.error(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )
        return full_transcription.strip()

    def reset(self):
        self.is_listening = True
        self.audio_data = []
        logger.info(
            "Google Speech Recognition Service has been reset for a new session."
        )
