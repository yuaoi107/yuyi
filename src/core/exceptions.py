
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


class NoPermissionException(AppException):

    def __init__(self, message: str = "当前用户没有权限"):
        super().__init__(message, 403)


class PodcastNotFoundException(AppException):

    def __init__(self, message: str = "播客不存在"):
        super().__init__(message, 404)


class CoverNotFoundException(AppException):

    def __init__(self, message: str = "封面不存在"):
        super().__init__(message, 404)


class AudioNotFoundException(AppException):

    def __init__(self, message: str = "音频不存在"):
        super().__init__(message, 404)


class EpisodeNotFoundException(AppException):

    def __init__(self, message: str = "单集不存在"):
        super().__init__(message, 404)
