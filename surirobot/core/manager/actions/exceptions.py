class ActionException(Exception):
    def __init__(self, name=None, msg=None):
        super().__init__(msg)
        self.name = name
        self.msg = msg

    def __str__(self):
        if self.name is None:
            self.name = 'Unknown'
        if self.msg is None:
            self.msg = '{}: Unexpected error in {} action.'.format(type(self).__name__, self.name)
        return self.msg

    def __iter__(self):
        yield 'name', self.name
        yield 'msg', self.msg


class NotFoundActionException(ActionException):
    def __init__(self, name=None):
        super().__init__(
            name,
            'Action "{}" is not found.'.format(name)
        )


class MissingParametersActionException(ActionException):
    def __init__(self, name, parameters=None):
        super().__init__(
            name,
            'Missing parameters "{}" on action "{}".'.format(parameters, name)
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
