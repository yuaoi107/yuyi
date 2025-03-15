
from typing import Annotated, BinaryIO
from fastapi import Depends, UploadFile

from src.core.exceptions import CosError
from src.config.settings import settings
from src.core.cos import cos_client


class CosService:

    def __init__(self):

        self._client = cos_client
        self._bucket = settings.COS_BUCKET

    def save_file(self, file: BinaryIO, filename: str):
        try:
            self._client.put_object(self._bucket, file, filename)
        except Exception as e:
            raise CosError

    def fetch_file(self, filename):
        try:
            response = self._client.get_object(self._bucket, filename)
            return response["Body"].get_raw_stream()
        except Exception as e:
            raise CosError

    def delete_file(self, filename):
        try:
            if self._client.object_exists(self._bucket, filename):
                self._client.delete_object(self._bucket, filename)
        except Exception as e:
            raise CosError


def get_cos_service():
    return CosService()


CosServiceDep = Annotated[CosService, Depends(get_cos_service)]
