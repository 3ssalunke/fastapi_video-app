from fastapi import HTTPException


class LoginRequiredException(HTTPException):
    pass


class InvalidUserIdException(HTTPException):
    pass
