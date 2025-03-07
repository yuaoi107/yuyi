
class AppException(Exception):

    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code


class UserAlreadyExistsException(AppException):

    def __init__(self, message: str = "用户已存在"):
        super().__init__(message, 409)


class NameAlreadyExistsException(AppException):

    def __init__(self, message: str = "名称已存在"):
        super().__init__(message, 409)


class UserNotFoundException(AppException):

    def __init__(self, message: str = "用户不存在"):
        super().__init__(message, 404)


class AvatarNotFoundException(AppException):

    def __init__(self, message: str = "头像不存在"):
        super().__init__(message, 404)
