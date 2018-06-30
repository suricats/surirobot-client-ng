class ManagerException(Exception):
    def __init__(self, code=None, msg=None):
        super().__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        if self.code is None:
            self.code = 'unknown-error'
        if self.msg is None:
            self.msg = '{}: Unexpected error in manager.\nCode: {}'.format(type(self).__code__, self.code)
        return self.msg

    def __iter__(self):
        yield 'code', self.code
        yield 'msg', self.msg


class InitialisationManagerException(ManagerException):
    def __init__(self, code=None):
        super().__init__(
            code,
            'Unexpected error during initialisation of manager.\nCode: {}'.format(code)
        )


class BadEncodingScenarioFileException(ManagerException):
    def __init__(self):
        super().__init__(
            'bad_encoding_file',
            'Scenario file is invalid or corrupted.'
        )


class BadParameterException(ManagerException):
    def __init__(self, parameter, valid_values=None):
        msg = '{} is not correct.'.format(parameter)
        if valid_values:
            msg = msg + ' Valid values are {}'.format(', '.join(valid_values))
        super().__init__(
            'bad_parameter',
            msg
        )
