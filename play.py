import math

from entertainment.football_for_db.game import Game
from entertainment.football_for_db.team import Team
from entertainment.football_for_db.setting import *
import random
from entertainment import models as en_models

def set_db_data(team1, team2):

    game_team1 = Team(formation = team1.formation_name)
    game_team2 = Team(formation = team2.formation_name)

    game_team1.init(team1.id, dir='L', is_user= True)
    game_team2.init(team2.id, dir='R', is_user= False)

    game = Game(game_team1, game_team2)
    i = 0
    game_history = []
    while not game.end:
        i += 1
        game.next()
        game_history.append(game.get_state_test())
        if i > 2700 * 2:
            break
    return [game_history,game.stats]


def play(team1, team2):
    team1.init(id=1, dir='L',is_user=True)
    team2.init(id=2, dir='R',is_user=False)
    game = Game(team1, team2)
    i = 0
    game_history = []
    while not game.end:
        i += 1

        game.next()

        game_history.append(game.get_state_test())
        if i > 2700 * 2:


            break
    return game_history

