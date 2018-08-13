from rest_framework.exceptions import APIException


class EmailNotSentException(APIException):
    """ Exception thrown when the confirmation email can not be sent """
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'not_registered'
