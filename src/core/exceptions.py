
class AppException(Exception):

    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        # content
        self.message = message
        # status code
        self.code = code


class AuthenticationFailedException(AppException):

    def __init__(self, message: str = ""):
        super().__init__(message, 401)


class AlreadyExistsException(AppException):

    def __init__(self, message: str):
        super().__init__(message, 409)


class UserAlreadyExistsException(AlreadyExistsException):

    def __init__(self, message: str = "User Already Exists."):
        super().__init__(message)


class UserNameAlreadyExistsException(AlreadyExistsException):

    def __init__(self, message: str = "User Name Already Exists."):
        super().__init__(message)


class PodcastTitleAlreadyExistsException(AlreadyExistsException):

    def __init__(self, message: str = "Podcast Title Already Exists."):
        super().__init__(message)


class EpisodeTitleAlreadyExistsException(AlreadyExistsException):

    def __init__(self, message: str = "Episode Title Already Exists."):
        super().__init__(message)


class NotFoundException(AppException):

    def __init__(self, message: str):
        super().__init__(message, 404)


class UserNotFoundException(AlreadyExistsException):

    def __init__(self, message: str = "User Not Found."):
        super().__init__(message)


class UserAvatarNotFoundException(NotFoundException):

    def __init__(self, message: str = "User Avatar Not Found."):
        super().__init__(message)


class PodcastNotFoundException(NotFoundException):

    def __init__(self, message: str = "Podcast Not Found."):
        super().__init__(message)


class PodcastCoverNotFoundException(NotFoundException):

    def __init__(self, message: str = "Cover Not Found."):
        super().__init__(message)


class EpisodeCoverNotFoundException(NotFoundException):

    def __init__(self, message: str = "Cover Not Found."):
        super().__init__(message)


class EpisodeAudioNotFoundException(NotFoundException):

    def __init__(self, message: str = "Episode Audio Not Found."):
        super().__init__(message)


class EpisodeNotFoundException(NotFoundException):

    def __init__(self, message: str = "Episode Not Found."):
        super().__init__(message)


class NoPermissionException(AppException):

    def __init__(self, message: str = "Current User Have No Permission."):
        super().__init__(message, 403)
