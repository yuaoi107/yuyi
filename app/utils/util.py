from passlib.context import CryptContext


def hash_password(password: str) -> str:
    encrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return encrypt_context.hash(password)
