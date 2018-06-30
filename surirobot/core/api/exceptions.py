class BaseAPIException(Exception):
    status_code = 500

    def __init__(self, code='api_error', msg='Unexpected error', type='unknown'):
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.type = type

    def __str__(self):
        if self.code is None:
            self.code = 'unknown'
        if self.msg is None:
            self.msg = '{}: Unexpected error in {} api.\nCode: {}'.format(type(self).__name__, self.type, self.code)
        return self.msg

    def __iter__(self):
        yield 'code', self.code
        yield 'msg', self.msg


class URLNotDefinedAPIException(BaseAPIException):
    status_code = 500

    def __init__(self, type='unknown'):
        super().__init__(
            'url_not_defined',
            'Url is not defined for {} API\nPlease check your environment file.'.format(type)
        )


class ExternalAPIException(BaseAPIException):
    status_code = 503

    def __init__(self, api_name='External API'):
        super().__init__(
            'external_api_error',
            '{} is not working properly.'.format(api_name)
        )


class APIThrottlingException(BaseAPIException):
    status_code = 429

    def __init__(self, api_name='External API'):
        super().__init__(
            'api_throttling',
            '{} needs to cool down.'.format(api_name)
        )


class InvalidCredentialsException(BaseAPIException):
    status_code = 401

    def __init__(self, api_name='External API'):
        super().__init__(
            'invalid_credentials',
            '{} credentials are not valid.'.format(api_name)
        )


class OperationFailedException(BaseAPIException):
    status_code = 422

    def __init__(self):
        super().__init__(
            'operation_failed',
            'API failed to process your request.'
        )


class MissingParameterException(BaseAPIException):
    status_code = 400

    def __init__(self, parameter):
        super().__init__(
            'missing_parameter',
            '{} is missing.'.format(parameter)
        )


class BadParameterException(BaseAPIException):
    status_code = 400

    def __init__(self, parameter, valid_values=None):
        msg = '{} is not correct.'.format(parameter)
        if valid_values:
            msg = msg + ' Valid values are: {}'.format(', '.join(valid_values))
        super().__init__(
            'bad_parameter',
            msg
        )


class MissingHeaderException(BaseAPIException):
    status_code = 400

    def __init__(self, header):
        super().__init__(
            'missing_header',
            '{} is missing.'.format(header)
        )


class BadHeaderException(BaseAPIException):
    status_code = 400

    def __init__(self, header, valid_values=None):
        msg = '{} is not correct.'.format(header)
        if valid_values:
            msg = msg + ' Valid values are: {}'.format(', '.join(valid_values))
        super().__init__(
            'bad_header',
            msg
        )
