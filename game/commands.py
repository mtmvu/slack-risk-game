from game import models


class ValidationException(Exception):
    pass


class Command:
    AVAILABLE_COMMANDS = ['new', 'start', 'reinforce', 'attack', 'move']

    def __init__(self, data):
        self.user_id = data['user_id']
        self.user_name = data['user_name']
        self.text = data['text']

    def execute(self):
        try:
            action, arguments = Command.parse_command(self.text)
        except ValidationException as e:
            return e

    def validate(self):
        pass

    def parse_command(text):
        text = text.strip()
        if len(text) == 0:
            raise ValidationException('Empty command')
        text = text.split(' ', 1)
        action = text[0].lower()
        arguments = text[1].strip() if len(text) > 1 else ''

        return action, arguments

    def validate_command(action, arguments):
        if action not in Command.AVAILABLE_COMMANDS:
            raise ValidationException('Unknown Command')


class GameCommand:
    pass
