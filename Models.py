from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    games_played = models.IntegerField(default=0)


class Match(models.Model):
    date = models.DateTimeField()
    home_team = models.ForeignKey(
        Team, related_name="home_team", on_delete=models.CASCADE)
    away_team = models.ForeignKey(
        Team, related_name="away_team", on_delete=models.CASCADE)
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
