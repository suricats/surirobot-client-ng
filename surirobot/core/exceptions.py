class ActionException(Exception):
    def __init__(self, service='Unknown', name='Unknown', msg='Unexpected error'):
        super().__init__(msg)
        self.service = service
        self.name = name
        self.msg = msg

    def __str__(self):
        return '{}: Unexpected error in {} action of {} service.'.format(type(self).__name__, self.name, self.service)

    def __iter__(self):
        yield 'service', self.service
        yield 'name', self.name
        yield 'msg', self.msg


class NotFoundActionException(ActionException):
    def __init__(self, service=None, name=None):
        super().__init__(
            service,
            name,
            '{}: {} action of {} service is not found.'.format(type(self).__name__, name, service)
        )


class BadParameterException(ActionException):
    def __init__(self, parameter, valid_values=None):
        msg = '{} is not correct.'.format(parameter)
        if valid_values:
            msg = msg + ' Valid values are {}'.format(', '.join(valid_values))
        super().__init__(
            'bad_parameter',
            msg
        )
