
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from src.core.exceptions import CosError
from src.config.settings import settings

try:
    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY
    )

    cos_client = CosS3Client(config)
except Exception as e:
    print(e)
    raise CosError()
