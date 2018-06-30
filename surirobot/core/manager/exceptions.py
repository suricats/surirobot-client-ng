class ManagerException(Exception):
    def __init__(self, code=None, msg=None):
        super().__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        if self.code is None:
            self.code = 'unknown-error'
        if self.msg is None:
            self.msg = '{}: Unexpected error in manager.\nCode: {}'.format(type(self).__name__, self.code)
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


class TypeNotAllowedInDataRetrieverException(ManagerException):
    def __init__(self, action_name=None, list=None, dic=None, element_name=None, element_value=None):
        super().__init__(
            'type_not_allowed',
            'This type of variable is not allowed in the data retriever.\nName of parameter: {}\nParent list: {}\nParent dictionnary: {}\nElement[{}]: {}\n'.format(action_name, list, dic, element_name, element_value)
        )


class BadEncodingScenarioFileException(ManagerException):
    def __init__(self):
        super().__init__(
            'bad_encoding_file',
            'Scenario file is invalid or corrupted.'
        )
