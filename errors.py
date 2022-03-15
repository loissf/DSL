class Error(Exception):
    def __init__(self, error_name, details, position = None):
        super().__init__()
        self.error_name = error_name
        self.details = details
        self.position = position

    def __str__(self):
        return f'{self.error_name}: {self.details}'

class IllegalCharErrorDsl(Error):
    def __init__(self, details, position):
        super().__init__('IllegalCharError', details, position)

class SyntaxErrorDsl(Error):
    def __init__(self, details, position):
        super().__init__('SyntaxError', details, position)

class TypeErrorDsl(Error):
    def __init__(self, details, position):
        super().__init__('TypeError', details, position)

class ZeroDivisionErrorDsl(Error):
    def __init__(self, details, position):
        super().__init__('ZeroDivisionError', details, position)

class IndexErrorDsl(Error):
    def __init__(self, details, position):
        super().__init__('IndexError', details, position)
