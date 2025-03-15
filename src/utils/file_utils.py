import uuid
from mutagen.mp3 import MP3


def get_unique_filename(filename: str) -> str:
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


def get_audio_duration_from_binaryio(binary_io):
    audio = MP3(binary_io)
    return audio.info.length
