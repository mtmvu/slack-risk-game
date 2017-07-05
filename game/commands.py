from game import models


class ValidationException(Exception):
    pass


class Command:

    def __init__(self, data):
        self.user_id = data['user_id']
        self.user_name = data['user_name']
        self.text = data['text']

    def read(self):
        pass

    def validate(self):
        try:
            action = Command.parse_action(self.text)
        except ValidationException as e:
            return str(e)

    def parse_action(text):
        pass
