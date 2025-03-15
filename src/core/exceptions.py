
class AppError(Exception):

    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        # content
        self.message = message
        # status code
        self.code = code


class AuthenticationFailedError(AppError):

    def __init__(self, message: str = ""):
        super().__init__(message, 401)


class AlreadyExistsError(AppError):

    def __init__(self, message: str):
        super().__init__(message, 409)


class UserAlreadyExistsError(AlreadyExistsError):

    def __init__(self, message: str = "User Already Exists."):
        super().__init__(message)


class UserNameAlreadyExistsError(AlreadyExistsError):

    def __init__(self, message: str = "User Name Already Exists."):
        super().__init__(message)


class PodcastTitleAlreadyExistsError(AlreadyExistsError):

    def __init__(self, message: str = "Podcast Title Already Exists."):
        super().__init__(message)


class EpisodeTitleAlreadyExistsError(AlreadyExistsError):

    def __init__(self, message: str = "Episode Title Already Exists."):
        super().__init__(message)


class NotFoundError(AppError):

    def __init__(self, message: str):
        super().__init__(message, 404)


class UserNotFoundError(AlreadyExistsError):

    def __init__(self, message: str = "User Not Found."):
        super().__init__(message)


class UserAvatarNotFoundError(NotFoundError):

    def __init__(self, message: str = "User Avatar Not Found."):
        super().__init__(message)


class PodcastNotFoundError(NotFoundError):

    def __init__(self, message: str = "Podcast Not Found."):
        super().__init__(message)


class PodcastCoverNotFoundError(NotFoundError):

    def __init__(self, message: str = "Cover Not Found."):
        super().__init__(message)


class PodcastFeedNotFoundError(NotFoundError):

    def __init__(self, message: str = "Podcast Feed Not Found."):
        super().__init__(message)


class EpisodeCoverNotFoundError(NotFoundError):

    def __init__(self, message: str = "Cover Not Found."):
        super().__init__(message)


class EpisodeAudioNotFoundError(NotFoundError):

    def __init__(self, message: str = "Episode Audio Not Found."):
        super().__init__(message)


class EpisodeNotFoundError(NotFoundError):

    def __init__(self, message: str = "Episode Not Found."):
        super().__init__(message)


class NoPermissionError(AppError):

    def __init__(self, message: str = "Current User Have No Permission."):
        super().__init__(message, 403)


class CosError(AppError):

    def __init__(self, message: str = "Cos Error."):
        super().__init__(message, 500)
