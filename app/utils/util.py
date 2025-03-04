from passlib.context import CryptContext
from pydantic import BaseModel


class Message(BaseModel):
    detail: str


def add_responses(*status_codes: int) -> dict[int, dict[str, Message]]:
    error_message = {"model": Message}
    responses = {}
    for code in status_codes:
        responses[code] = error_message
    return responses


def hash_password(password: str) -> str:
    encrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return encrypt_context.hash(password)
