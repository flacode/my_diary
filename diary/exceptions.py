from rest_framework.exceptions import APIException


class EmailNotSentException(APIException):
    """ Exception thrown when the confirmation email can not be sent """
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'not_registered'


class AccountNotFoundException(APIException):
    status_code = 404
    default_detail = 'User account not found, please first register'
    default_code = 'not found'


class InvalidCredentialsException(APIException):
    status_code = 401
    default_detail = 'Invalid uder credentials'
    default_code = 'unauthorised'
