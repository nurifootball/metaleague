from abc import abstractmethod

from entertainment.football_for_db.formation import Formation
from entertainment.football_for_db.player import Player
from entertainment.football_for_db.setting import *
from entertainment.football_for_db.const import FORM
from entertainment import models as ent_models
import random
import math

class Team:
    def __init__(self, ids=None, formation='4-4-2'):
        if ids is None:
            ids = list(range(NUM_TEAM))
        self.team_name: str
        self.team_type: str
        self.formation = formation
        self.ids = ids
        self.is_user : bool


    def init(self, id, dir,is_user):
        """
        Set the teams id, direction and difficulty (only for AI teams)
        Also recolor the sprites based on the team's chosen color

        Attributes:
            id (int): The team's id (must be either 1 or 2)
            dir (str): The team's direction (must be either 'L' or 'R')
            diff (float): The game difficult (between 0-1)

        Calls ```set_players()``` and ```set_color()```
        """

        self.dir = dir
        self.is_user = is_user

        if self.dir == 'L':
            self.goal_x = 0
        else:
            self.goal_x = W
        if is_user:
            players = ent_models.ForPlayer.objects.filter(
                user_formation__id = id
            ).order_by('for_number')
            self.id = 1
        else:
            players = ent_models.AIPlayer.objects.filter(
                AI_formation__id = id
            ).order_by('for_number')
            self.id = 2

        self.set_players(players)


    def set_players(self, players):
        self.players = []

        for player in players:
            self.players.append(Player(player = player, team_id=self.id, pos=FORM[self.formation]["st_"+self.dir][player.get_for_number()]['coord']
                , dir=self.dir,is_user = self.is_user)
            )


        self.selected = NUM_TEAM//2
        self.next_selected = []

    def get_players(self, position = None):
        players = []
        if position:
            for player in self.players:
                if player.position == position:
                    players.append(player)
            return players
        else:
            return self.players


    def reset_position(self):
        for player in self.players:
            player.pos = FORM[self.formation]["st_"+self.dir][player.id]['coord']


    def __str__(self):
        s = f'Team {self.id}:'
        for player in self.players:
            s += player.__str__()
        return s

    def update(self, action, ball):
        """
        Update the team's state

        Basically calls each players' ```update()``` method
        """

        for i, player in enumerate(self.players):
            player.update(action[i], self.players)

    def formation_dir(self, id, catch = ""):

        player = self.players[id]
        min_dist = 2

        if abs(player.pos.x - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].x) <= min_dist and abs(
                player.pos.y - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].y) <= min_dist:
            player.walk_count = 0
            return 'NOTHING'
        elif abs(player.pos.x - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].x) <= min_dist:
            if (player.pos.y - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].y) > min_dist:
                return 'MOVE_U'
            else:
                return 'MOVE_D'
        elif abs(player.pos.y - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].y) <= min_dist:
            if (player.pos.x - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].x) > min_dist:
                return 'MOVE_L'
            else:
                return 'MOVE_R'
        elif (player.pos.x - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].x) > min_dist:
            if (player.pos.y - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].y) > min_dist:
                return random.choices(['MOVE_L', 'MOVE_U'])[0]
            else:
                return random.choices(['MOVE_L', 'MOVE_D'])[0]
        elif (player.pos.x - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].x) < - min_dist:
            if (player.pos.y - FORM[self.formation][f'{catch}{self.dir}'][id]['coord'].y) > min_dist:
                return random.choices(['MOVE_R', 'MOVE_U'])[0]
            else:
                return random.choices(['MOVE_R', 'MOVE_D'])[0]
        else:
            return 'NOTHING'

    def select_player(self, ball):
        """
        Select a player based on the balls position

        **Working**:

        - If ball is near the D-area, keeper gets automatic control
        - Otherwise the player nearest to the ball has control (ties are broken randomly)
        """

        dists = [player.pos.dist(ball.pos) +
                 player.rnd for player in self.players]
        # Default - Ball goes to nearest player
        self.selected = dists.index(min(dists))

        if min(dists) > MAX_PLAYER_RADIUS + BALL_RADIUS and abs(ball.pos.x - self.goal_x) < W // 5:
            # If the ball is within the D and is not very near to any other player, give control to the keeper
            self.selected = 0

    def move(self, state_prev, state, reward):
        """
        Move each player in the team. Call this method to move the team
        """
        actions = []
        for i, player in enumerate(self.players):

            move = player.move(state_prev, state, reward)
            if (state and state['ball'].ball_stats['catch']):
                # print(state['ball'].ball_stats['catch'])
                actions = [self.formation_dir(j, 'catch_') for j, pl in enumerate(self.players)]
                if i == 0:
                    if move != 'FORM':
                        actions[0] = move
                    else:
                        actions[0] = self.formation_dir(i)
                break
            if move != 'FORM':
                actions.append(move)
            else:
                actions.append(self.formation_dir(i))
        return actions
