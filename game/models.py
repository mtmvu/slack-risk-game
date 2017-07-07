from random import shuffle

from django.db import models
from django_fsm import FSMField, transition, GET_STATE


class Player(models.Model):
    name = models.CharField(max_length=50)
    slack_id = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"<@{self.slack_id}|{self.name}>"


class Territory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    continent = models.ForeignKey("Continent")
    x = models.FloatField()
    y = models.FloatField()
    adjacents = models.ManyToManyField("self")


class Continent(models.Model):
    name = models.CharField(max_length=50, unique=True)
    bonus = models.IntegerField(default=0)


class Game(models.Model):
    state = FSMField(default='new')

    def is_active(self):
        return self.state != 'finished'

    @transition(field=state, source='new', target='waiting_for_reinforcements')
    def init(self, players):
        self._set_players(players)
        self._distribute_territories()
        self._distribute_reinforcements()

    @transition(field=state, source='waiting_for_reinforcements', target='started')
    def start(self, players):
        pass

    def _set_players(self, players):
        for player in players:
            p, _ = Player.objects.get_or_create(slack_id=player)
            PlayerGame.objects.create(game=self, player=p, color='black')

    def _distribute_territories(self):
        players = self.playergame_set.all()
        n_players = len(players)
        territories = list(Territory.objects.all())
        shuffle(territories)
        for i, territory in enumerate(territories):
            TerritoryGame.object.create(
                game=self, territory=territory, owner=players[i % n_players])

    def _distribute_reinforcements(self):
        players = self.playergame_set.all()
        n_players = len(players)
        reinforcements = 35

        if n_players == 4:
            reinforcements = 30
        elif n_players == 5:
            reinforcements = 25
        elif n_players == 6:
            reinforcements = 20

        for player in players:
            player.set_initial_reinforcements(reinforcements)
            player.save()


class PlayerGame(models.Model):
    game = models.ForeignKey("Game")
    player = models.ForeignKey("Player")
    color = models.CharField(max_length=50)
    turn_order = models.IntegerField(default=0)
    reinforcements = models.IntegerField(default=0)
    state = FSMField(default='waiting_for_turn')

    def continents(self):
        for continent in Continent.objects.all():
            continent_territories = continent.territory_set.count()
            player_territories = self.territorygame_set.filter(
                territory__continent=continent).count()
            if continent_territories == player_territories:
                yield continent

    @transition(field=state, source='waiting_for_turn', target='reinforcement_phase')
    def new_turn(self):
        self.set_reinforcements()

    @transition(field=state, source=['attack_phase', 'move_phase'], target='waiting_for_turn')
    def end_turn(self):
        pass

    @transition(field=state, source='waiting_for_turn', target='initial_reinforcement_phase')
    def set_initial_reinforcements(self, n):
        self.reinforcements += n

    def set_reinforcements(self):
        territory_bonus = min(3, int(self.territorygame_set.count() / 3))
        continent_bonus = 0
        for continent in self.continents():
            continent_bonus += continent.bonus

        self.reinforcements += territory_bonus + continent_bonus

    def can_reinforce(self):
        return self.reinforcements > 0

    def reinforce_state(self):
        if self.can_reinforce():
            return self.state

        if self.state == 'reinforcement_phase':
            return 'attack_phase'
        elif self.state == 'initial_reinforcement_phase':
            return 'waiting_for_turn'

    @transition(field=state,
                source=['initial_reinforcement_phase', 'reinforcement_phase'],
                target=GET_STATE(
                    lambda self: self.reinforce_state(),
                    states=['initial_reinforcement_phase',
                            'reinforcement_phase', 'attack_phase']
                ),
                conditions=[can_reinforce])
    def reinforce(self, n, territory):
        if n > self.reinforcements:
            raise

        try:
            territory = self.territorygame_set.get(territory__name=territory)
        except Exception:
            raise

        territory.army += n
        territory.save()


class TerritoryGame(models.Model):
    game = models.ForeignKey("Game")
    territory = models.ForeignKey("Territory")
    owner = models.ForeignKey("PlayerGame")
    army = models.IntegerField(default=1)
    new_army = models.IntegerField(default=0)
