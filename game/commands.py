import re

from game import models


class ValidationException(Exception):
    pass


class Command:
    AVAILABLE_ACTIONS = ["new", "start", "reinforce", "attack", "move", "state", "help"]

    def __init__(self, data):
        self.user_id = data["user_id"]
        self.user_name = data["user_name"]
        self.text = data["text"]

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
            raise ValidationException("Empty command")
        text = text.split(" ", 1)
        action = text[0].lower()
        arguments = text[1].strip() if len(text) > 1 else ""

        return action, arguments

    def validate(action, arguments):
        if action not in Command.AVAILABLE_ACTIONS:
            raise ValidationException("Unknown Command")
        for command in Command.AVAILABLE_ACTIONS:
            if command not in ["start", "help", "state"] and len(arguments) == 0:
                raise ValidationException("No arguments provided")


class GameCommand:

    def __init__(self, user_id, user_name, action, arguments):
        self.user_id = user_id
        self.user_name = user_name
        self.action = action
        self.arguments = arguments
        self.player = None
        self.game = None
        self.player_game = None

    def get_player(user_id=None, user_name=None):
        player, _ = models.Player.objects.update_or_create(
            slack_id=user_id, defaults={"name": user_name})
        return player

    def get_player_game(player):
        for player_game in player.playergame_set.all():
            if player_game.game.is_active():
                return player_game

    def parse_players(arguments):
        pattern = r"<@([^)]+?)>"
        matches = re.findall(pattern, arguments)
        for match in matches:
            user_id, user_name = match.split("|")
            yield GameCommand.get_player(user_id, user_name)

    def execute(self):
        self.player = GameCommand.get_player(self.user_id, self.user_name)
        self.player_game = GameCommand.get_player_game(self.player)
        self.game = self.player_game.game
        if self.action == "new":
            return self.new()

    def new(self):
        players = list(GameCommand.parse_players(self.arguments)) + [self.player]

        # Check players length
        if len(players) < 3:
            raise ValidationException("Not enough players")

        # Check if players are already in a game
        for player in players:
            if player.is_in_game():
                raise ValidationException(f"{str(player)} is already in game")

        game = models.Game.objects.create()
        game.init(players)
        game.save()
        return "Game initialized"

    def start(self):
        # Checking state
        if self.game.state != "waiting_for_reinforcements":
            raise ValidationException(f"Game cannot be started. In state: {self.game.state}")

        # Check if all players are ready
