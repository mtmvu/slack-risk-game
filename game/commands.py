from game import models


class ValidationException(Exception):
    pass


class Command:
    AVAILABLE_ACTIONS = ['new', 'start', 'reinforce', 'attack', 'move']

    def __init__(self, data):
        self.user_id = data['user_id']
        self.user_name = data['user_name']
        self.text = data['text']

    def execute(self):
        try:
            action, arguments = Command.parse_command(self.text)
            Command.validate(action, arguments)
            return GameCommand(self.user_id, self.user_name, action, arguments).execute()
        except ValidationException as e:
            return e

    def parse_command(text):
        text = text.strip()
        if len(text) == 0:
            raise ValidationException('Empty command')
        text = text.split(' ', 1)
        action = text[0].lower()
        arguments = text[1].strip() if len(text) > 1 else ''

        return action, arguments

    def validate(action, arguments):
        if action not in Command.AVAILABLE_ACTIONS:
            raise ValidationException('Unknown Command')
        for command in Command.AVAILABLE_ACTIONS:
            if command != 'start' and len(arguments) == 0:
                raise ValidationException('No arguments provided')


class GameCommand:

    def __init__(self, user_id, user_name, action, arguments):
        self.user_id = user_id
        self.user_name = user_name
        self.action = action
        self.arguments = arguments
        self.player = None
        self.game = None
        self.player_game = None

    def execute(self):
        self.player = GameCommand.get_player()
        if self.action == "new":
            self.new_game()

    def get_player(user_id, user_name):
        player, _ = models.Player.objects.update_or_create(
            slack_id=user_id, defaults={"name": user_name})
        return player

    def new_game(self):
        for player_game in self.player.playergame_set.all():
            if player_game.game.is_active():
                raise ValidationException('Already in a game')
