from abc import abstractmethod

from entertainment.football_for_db.ball import Ball
from entertainment.football_for_db.setting import *
from entertainment.football_for_db.stats import Stats
import random

class Game:
    def __init__(self, team1, team2):

        self.team1 = team1
        self.team2 = team2

        self.ball = Ball(pos=(W//2, H//2))
        self.stats = Stats(team1,team2)

        self.end = False
        self.state_prev = None

        self.rewards = None
        self.state = None


    def same_team_collision(self, team, free):
        """
        같은 팀 끼리 충돌 여부 판단
        :param team:
        :param free:
        :return:
        """

        min_dist = P(2 * MAX_PLAYER_RADIUS, 2 * MAX_PLAYER_RADIUS)
        if not free:
            min_dist.x += BALL_RADIUS

        for player1 in team.players:
            for player2 in team.players:
                if player1 != player2 and abs(player1.pos.x - player2.pos.x) <= min_dist.x \
                        and abs(player1.pos.y - player2.pos.y) <= min_dist.y:
                    xincr = 1 + MAX_PLAYER_RADIUS - abs(player1.pos.x - player2.pos.x) // 2
                    xdir = (1, -1)
                    yincr = 1 + MAX_PLAYER_RADIUS - abs(player1.pos.y-player2.pos.y) // 2
                    ydir = (1, -1)


                    if player1.pos.x < player2.pos.x:
                        xdir = (-1, 1)
                    if player1.pos.y < player2.pos.y:
                        ydir = (-1, 1)

                    if abs(player1.pos.y - player2.pos.y) < abs(player1.pos.x - player2.pos.x):
                        ydir = (0, 0)
                    elif abs(player1.pos.y - player2.pos.y) > abs(player1.pos.x - player2.pos.x):
                        xdir = (0, 0)

                    player1.pos.x += xdir[0] * xincr
                    player2.pos.x += xdir[1] * xincr
                    player1.pos.y += ydir[0] * yincr
                    player2.pos.y += ydir[1] * yincr


    def diff_team_collision(self, team1, team2, free):
        '''
        Check if current player collides with any other players of the opposite team
        '''

        min_dist = P(2*MAX_PLAYER_RADIUS, 2*MAX_PLAYER_RADIUS)
        if not free:
            min_dist.x += BALL_RADIUS



        for player1 in team1.players:
            for player2 in team2.players:
                if (player1.action_delay == 0) and (player2.action_delay==0):
                    if abs(player1.pos.x - player2.pos.x) <= min_dist.x and abs(player1.pos.y - player2.pos.y) <= min_dist.y:


                        xincr = 1 + 2*MAX_PLAYER_RADIUS - \
                            abs(player1.pos.x-player2.pos.x)//2
                        xdir = (1, -1)
                        yincr = 1 + 2*MAX_PLAYER_RADIUS - \
                            abs(player1.pos.y-player2.pos.y)//2
                        ydir = (1, -1)

                        if player1.pos.x < player2.pos.x:
                            xdir = (-1, 1)
                        if player1.pos.y < player2.pos.y:
                            ydir = (-1, 1)

                        pl1_dri = random.randint(player1.st[2] - 30, player1.st[2] + 30)
                        pl2_dri = random.randint(player2.st[2] - 30, player2.st[2] + 30)
                        pl1_phy = random.randint(player1.st[4] - 30, player1.st[4] + 30)
                        pl2_phy = random.randint(player2.st[4] - 30, player2.st[4] + 30)
                        pl1_def = random.randint(player1.st[5] - 30, player1.st[5] + 30)
                        pl2_def = random.randint(player2.st[5] - 30, player2.st[5] + 30)

                        if self.ball.ball_stats['player'] == player1.id:
                            if pl1_dri > pl2_def:
                                player2.pos.x += xdir[1] * xincr
                                player2.pos.y += ydir[1] * yincr
                                player2.action_delay = 100
                                self.stats.tackle_acc[team2.id]['fail'] += 1
                            else:
                                player1.pos.x += xdir[0] * xincr
                                player1.pos.y += ydir[0] * yincr
                                player1.action_delay = 100
                                self.stats.tackle_acc[team2.id]['succ'] += 1
                        elif self.ball.ball_stats['player'] == player2.id:
                            if pl2_dri > pl1_def:
                                player1.pos.x += xdir[0] * xincr
                                player1.pos.y += ydir[0] * yincr
                                player1.action_delay = 100
                                self.stats.tackle_acc[team1.id]['fail'] += 1
                            else:
                                player2.pos.x += xdir[1] * xincr
                                player2.pos.y += ydir[1] * yincr
                                player2.action_delay = 100
                                self.stats.tackle_acc[team1.id]['succ'] += 1
                        else:
                            if pl1_phy > pl2_phy:
                                player2.pos.x += xdir[1] * xincr
                                player2.pos.y += ydir[1] * yincr
                                player2.action_delay = 100
                            else:
                                player1.pos.x += xdir[0] * xincr
                                player1.pos.y += ydir[0] * yincr
                                player1.action_delay = 100
                        if not free:
                            self.ball.reset(self.ball.pos)
                else:

                    pass
        for player1 in team1.players:
            if player1.action_delay > 0:
                player1.action_delay -= 1
        for player2 in team2.players:
            if player2.action_delay > 0:
                player2.action_delay -= 1


    def collision(self, team1, team2, ball):
        '''
        Handle collisions between all in-game players.
        '''

        self.same_team_collision(team1, self.ball.free)
        self.same_team_collision(team2, self.ball.free)
        self.diff_team_collision(team1, team2, self.ball.free)


    def get_state(self):
        '''
        Create a state object that summarizes the entire game

        ```
        state = {
            'team1': {
                'players' # list of the team player's coordinates
                'goal_x' # The x-coordinate of their goal post
            },
            'team2': {
                'players' # list of the team player's coordinates
                'goal_x' # The x-coordinate of their goal post
            },
            'ball' # Position of the ball
        }
        ```
        '''
        pos1 = [player.pos for player in self.team1.players]
        pos2 = [player.pos for player in self.team2.players]

        return {
            'team1': {
                'players': self.team1.players,
                'goal_x': self.team1.goal_x,
                'pos':pos1,
                'dir':self.team1.dir,
                'id':self.team1.id,
            },
            'team2': {
                'players': self.team2.players,
                'goal_x': self.team2.goal_x,
                'pos':pos2,
                'dir': self.team2.dir,
                'id': self.team2.id,
            },
            'ball': self.ball,
        }

    def get_state_test(self):
        '''
        Create a state object that summarizes the entire game

        ```
        state = {
            'team1': {
                'players' # list of the team player's coordinates
                'goal_x' # The x-coordinate of their goal post
            },
            'team2': {
                'players' # list of the team player's coordinates
                'goal_x' # The x-coordinate of their goal post
            },
            'ball' # Position of the ball
        }
        ```
        '''
        pos1 = [player.pos.val for player in self.team1.players]
        pos2 = [player.pos.val for player in self.team2.players]

        return {
            'team1': {
                "pos":pos1
            },
            'team2': {
                "pos":pos2
            },
            'goal': self.stats.get_goal(),
            'ball': self.ball.val,
        }


    def move_next(self, a1, a2):
        '''
        Update the players' and ball's internal state based on the teams' actions

        Attributes:
            a1 (list): list of actions (1 for each player) in team 1
            a2 (list): list of actions (1 for each player) in team 2

        Each action must be a key in either the ```ACT``` or the ```META_ACT``` dictionary found in ```const.py```
        '''

        state_prev = self.get_state()
        if self.ball.ball_stats['team'] != -1:
            self.stats.pos[self.ball.ball_stats['team']] += 1

        self.team1.update(a1, self.ball)  # Update team's state
        self.team2.update(a2, self.ball)

        # Check for collision between players
        self.collision(self.team1, self.team2, self.ball)

        self.ball.update(self.team1, self.team2, a1, a2,
                         self.stats)  # Update ball's state

        state = self.get_state()
        return state_prev, state, 0

    def next(self):
        '''
        Move the game forward by 1 frame

        Passes state objects to the teams and pass their actions to ```move_next()```

        Also checks for special keyboard buttons and sets internal flags to pause, quit
        the game or run it in debug mode
        '''
        if self.state:
            print(self.state['ball'].ball_stats['catch'])
        a1 = self.team1.move(self.state_prev, self.state, self.rewards)
        a2 = self.team2.move(self.state_prev, self.state, self.rewards)

        self.state_prev, self.state, self.rewards = self.move_next(a1, a2)


