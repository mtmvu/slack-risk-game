from game import models


class ValidationException(Exception):
    pass


class Command:

    def __init__(self, data):
        self.user_id = data['user_id']
        self.user_name = data['user_name']
        self.text = data['text']

    def execute(self):
        action, arguments = Command.parse_command(self.text)

    def validate(self):
        pass

    def parse_command(text):
        text = text.strip()
        if len(text) == 0:
            raise ValidationException('Empty command')
        text = text.split(' ', 1)
        action = text[0]
        arguments = text[1].strip() if len(text) > 1 else ''

        return action, arguments
