class GameException(Exception):

    def __init__(self, action, message, code='UNEXPECTED'):
        self.action = action
        self.message = message
        self.code = code
        super(GameException, self).__init__(message)