class ServiceError(Exception):
    pass


class AlreadyExists(ServiceError):
    pass


class NotFound(ServiceError):
    pass


class InvalidCredentials(ServiceError):
    pass


class Forbidden(ServiceError):
    pass
