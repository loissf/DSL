class Error(BaseException):
    def __init__(self, error_name, details, position):
        self.error_name = error_name
        self.details = details
        self.position = position

    def __str__(self):
        return f'{self.error_name}: {self.details}'

class IllegalCharError(Error):
    def __init__(self, details, position):
        super().__init__('IllegalCharError', details, position)

class SyntaxError(Error):
    def __init__(self, details, position):
        super().__init__('SyntaxError', details, position)

class TypeError(Error):
    def __init__(self, details, position):
        super().__init__('TypeError', details, position)

class ZeroDivisionError(Error):
    def __init__(self, details, position):
        super().__init__('ZeroDivisionError', details, position)
