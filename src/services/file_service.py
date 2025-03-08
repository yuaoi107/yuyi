

from src.config.settings import settings


class FileService:

    def __init__(self, contents_dir=settings.CONTENTS_DIR):
        self.contents_dir = contents_dir
