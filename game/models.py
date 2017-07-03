from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=50)
    slack_id = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)


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
    is_active = models.BooleanField(default=True)


class PlayerGame(models.Model):
    game = models.ForeignKey("Game")
    player = models.ForeignKey("Player")
    color = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    turn_order = models.IntegerField(default=0)
    reinforcement = models.IntegerField(default=0)

    def owns_continents(self):
        for continent in Continent.objects.all():
            continent_territories = continent.territory_set.count()
            player_territories = self.territorygame_set.filter(
                territory__continent=continent).count()
            if continent_territories == player_territories:
                yield continent

    def get_reinforcements(self):
        pass


class TerritoryGame(models.Model):
    game = models.ForeignKey("Game")
    territory = models.ForeignKey("Territory")
    owner = models.ForeignKey("PlayerGame")
    army = models.IntegerField(default=0)
