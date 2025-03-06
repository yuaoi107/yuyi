

from sqlmodel import Session

from src.models.podcast import PodcastPublic, PodcastUpload
from src.models.user import User


class PodcastService:
    @staticmethod
    def create_podcast(user_login: User, session: Session, podcast: PodcastUpload) -> PodcastPublic:
        pass
