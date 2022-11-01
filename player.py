import random
import time

from entertainment.football_for_db.setting import *
from entertainment.football_for_db.const import ACT
import math


class Player:
    def __init__(self, player, team_id, pos, dir='L', is_user=None):
        self.player = player
        self.id = player.get_for_number()
        self.team_id = team_id
        self.team_dir = dir
        self.pos = pos
        self.pos_position = player.rep_po
        self.position = player.po
        self.st = []
        self.walk_dir = dir
        self.action_delay = 0
        self.catch_delay = 0
        self.walk_count = 0
        self.rnd = 0.01 * random.random()
        if is_user:
            for st in player.get_st_list():
                st_fix = st
                if self.pos_position != player.player.nft_info.position.r_po:
                    st_fix = st - (st // 3)
                elif player.player.nft_info.position.po not in self.position:
                    st_fix = st - (st // 10)
                if st_fix < 21:
                    st_fix = 20
                self.st.append(st_fix)
        else:
            for st in player.get_st_list():
                self.st.append(st)

    def __str__(self):
        return f'player {self.id} - {self.pos}'

    def dist_to_line(self, line, pt):
        return abs(line[0] * pt.x + line[1] * pt.y + line[2]) / math.sqrt(line[0] ** 2 + line[1] ** 2)

    def ai_move_with_ball(self, enemy_players, goal_x):
        player_vec = P(0, 0)
        for player in enemy_players:
            if self.pos.dist(player.pos) < AI_NEAR_RADIUS:
                dir = player.pos - self.pos
                mag = (AI_NEAR_RADIUS * MAX_PLAYER_RADIUS / dir.mag) ** 2
                player_vec -= P(mag / dir.mag, mag / dir.mag) * dir

        goal_vec = P(goal_x, H // 2) - self.pos
        goal_vec += P(1 / goal_vec.mag, 1 / goal_vec.mag)

        final_vec = goal_vec + player_vec

        dir_final = final_vec * P(1 / final_vec.mag, 1 / final_vec.mag)

        if goal_x >= 500:
            possible_dir = ['NOTHING', 'MOVE_U', 'MOVE_D', 'MOVE_R']
        else:
            possible_dir = ['NOTHING', 'MOVE_U', 'MOVE_D', 'MOVE_L', ]
        dist_to_dir = [dir_final.dist(ACT[dir]) for dir in possible_dir]
        prob_dist = [math.exp(1 / d) if d >= 0.1 else math.exp(10) for d in dist_to_dir]

        chosen_dir = random.choices(possible_dir, weights=[prob / sum(prob_dist) for prob in prob_dist])[0]

        return chosen_dir

    def ai_move_without_ball(self, ball):

        if self.action_delay != 0:
            return "NOTHING"
        if not (ball.ball_stats['team'] == self.team_id):

            if ball.ball_stats['player'] == 0:
                return "FORM"
            elif self.pos.dist(ball.pos) < AI_FAR_RADIUS - 100:

                vec = ball.pos - self.pos
                if abs(vec.x) > abs(vec.y):
                    if vec.x > 0:
                        return "MOVE_R"
                    else:
                        return "MOVE_L"
                else:
                    if vec.y > 0:
                        return "MOVE_D"
                    else:
                        return "MOVE_U"
            elif self.pos.dist(ball.pos) < AI_FAR_RADIUS:
                vec = ball.pos - self.pos
                vec_dir = P(1 / vec.mag, 1 / vec.mag) * vec

                possible_dir = ['NOTHING', 'MOVE_U', 'MOVE_D', 'MOVE_L', 'MOVE_R']
                dist_to_dir = [vec_dir.dist(ACT[dir]) for dir in possible_dir]

                prob_dist = [math.exp(1 / d) if d >= 0.1 else math.exp(10) for d in dist_to_dir]
                chosen_dir = random.choices(possible_dir, weights=[prob / sum(prob_dist) for prob in prob_dist])[0]

                return chosen_dir
            # else:
            #     if abs(self.pos_position.x - self.pos.x) < 100:
            #         if self.pos.x - ball.pos.x > 100:
            #             return "MOVE_L"
            #         elif self.pos.x - ball.pos.x < 100:
            #             return "MOVE_R"
            else:
                return "FORM"
        else:
            return "FORM"

    def ai_pass(self, team_players, enemy_team_players):
        team_pos = {player.id: P(player.pos.x, H - player.pos.y)
                    for player in team_players}
        enemy_team_pos = {player.id: P(player.pos.x, H - player.pos.y)
                          for player in enemy_team_players}

        self_pos = P(self.pos.x, H - self.pos.y)

        prefs = {
            'SHOOT_A': {'priority': {'L': 4, 'R': 1}, 'angle': math.pi, 'dir': P(-1, 0)},
            'SHOOT_Q': {'priority': {'L': 3, 'R': 1}, 'angle': math.pi * 3 / 4, 'dir': P(-1, 1)},
            'SHOOT_Z': {'priority': {'L': 3, 'R': 1}, 'angle': -math.pi * 3 / 4, 'dir': P(-1, -1)},
            'SHOOT_W': {'priority': {'L': 2, 'R': 2}, 'angle': math.pi / 2, 'dir': P(0, 1)},
            'SHOOT_X': {'priority': {'L': 2, 'R': 2}, 'angle': -math.pi / 2, 'dir': P(0, -1)},
            'SHOOT_E': {'priority': {'L': 1, 'R': 3}, 'angle': math.pi / 4, 'dir': P(1, 1)},
            'SHOOT_C': {'priority': {'L': 1, 'R': 3}, 'angle': -math.pi / 4, 'dir': P(1, -1)},
            'SHOOT_D': {'priority': {'L': 1, 'R': 4}, 'angle': 0, 'dir': P(1, 0)},
        }

        possible_passes = []

        for k, v in prefs.items():
            line = [
                math.sin(v['angle']),
                -math.cos(v['angle']),
                self_pos.y * math.cos(v['angle']) - self_pos.x * math.sin(v['angle']),
            ]

            for player in team_players:
                if player.id != self.id:
                    team_dist = self.dist_to_line(line, team_pos[player.id])
                    if (team_dist < AI_MIN_PASS_DIST and (self_pos.x - team_pos[player.id].x) * v['dir'].x <= 0 and
                            (self_pos.y - team_pos[player.id].y) * v['dir'].y <= 0):
                        enemy_dist = math.inf
                        enemy_min_pos = P(0, 0)
                        for enemy_player in enemy_team_players:
                            if self.dist_to_line(line, enemy_team_pos[enemy_player.id]) < enemy_dist:
                                enemy_dist = self.dist_to_line(
                                    line, enemy_team_pos[enemy_player.id]
                                )
                                enemy_min_pos = enemy_team_pos[enemy_player.id]
                        if (enemy_dist < team_dist and (self.pos.x - enemy_min_pos.x) * v['dir'].x < - 0 and
                                (self.pos.y - enemy_min_pos.y) * v['dir'].y <= 0):
                            continue
                        else:
                            possible_passes.append(
                                (v['priority'][self.team_dir],
                                 team_dist,
                                 k,
                                 enemy_dist)
                            )
        if possible_passes:
            ai_pass = sorted(possible_passes)[0][2]
        else:
            ai_pass = 'NOTHING'

        return ai_pass

    def ai_shoot(self, gk, goal_x):
        angles = {
            'L': {
                'SHOOT_E': math.pi / 4,
                'SHOOT_D': 0,
                'SHOOT_C': -math.pi / 4
            },
            'R': {  # For team 2
                'SHOOT_Q': math.pi * 3 / 4,
                'SHOOT_A': math.pi,
                'SHOOT_Z': math.pi * 5 / 4,
            },
        }

        self_pos = P(self.pos.x, H - self.pos.y)

        gk_pos = P(gk.pos.x, H - gk.pos.y)

        possible_shots = []

        for k, v in angles[self.team_dir].items():
            line = [  # Equation of line as A*x +B*y + C = 0
                math.sin(v),  # x coeff
                -math.cos(v),  # y coeff
                self_pos.y * math.cos(v) - self_pos.x * math.sin(v),  # constant
            ]
            intersection_pt = -(line[2] + line[0] * goal_x) / line[1]
            if GOAL_POS[0] * H < intersection_pt < GOAL_POS[1] * H:
                possible_shots.append((-self.dist_to_line(line, gk_pos), k))

        if possible_shots:
            shot = sorted(possible_shots)[0][1]
        else:
            shot = 'NOTHING'
        return shot

    def gk_move(self, goal_x, ball):
        """
        How the AI goalkeeper moves

        Attributes:
            goal_x (int): the x-coordinate of the enemy's
            ball (Ball): The football object

        Returns an ACT

        **Working**:

        - Moves towards the ball (tracks the y coordinate)
        - Does not go outside the goals boundary
        """

        if ball.pos.dist(P(goal_x, H // 2)) < (AI_SHOOT_RADIUS + (AI_SHOOT_RADIUS * (self.st[1] / 100))):
            # Goal keeper does not go into the goal himself
            if abs(self.pos.x - goal_x) > BALL_RADIUS + MAX_PLAYER_RADIUS:
                if GOAL_POS[0] * H < self.pos.y < GOAL_POS[1] * H:
                    if ball.vel.x == 0 or ball.pos.dist(P(goal_x, H / 2)) < (AI_SHOOT_RADIUS * (self.st[1] / 100)) / 3:
                        ball_intercept = ball.pos.y
                    else:
                        if ball.vel.x > 0 :
                            ball_intercept = ball.pos.y + ((goal_x - ball.pos.x)/2) * (ball.vel.y / ball.vel.x)
                        else:
                            ball_intercept = ball.pos.y + ((goal_x - ball.pos.x)/2) * (ball.vel.y / ball.vel.x)
                    if ball_intercept - self.pos.y >= 0:
                        return 'MOVE_D'
                    else:
                        return 'MOVE_U'
                else:
                    return 'FORM'  # IMM_PASS
        else:
            return 'FORM'

    def gk_pass(self, team, enemy_players, goal_x):
        """
        How the AI goalkeeper passes

        Attributes:
            enemy_players (list): A list of the positions (coordinates) of the enemy players
            goal_x (int): The x-coordinate of the team's goal post

        Returns an ACT

        **Working**:

        - Pass such that enemy players in AI_SHOOT_RADIUS do not get the ball
        """

        if self.catch_delay > 0:
            self.catch_delay -= 2

            return 'GK_catch'

        angles = {
            'L': {  # For team 1
                'SHOOT_E': math.pi / 4,
                'SHOOT_D': 0,
                'SHOOT_C': -math.pi / 4,
            },
            'R': {  # For team 2
                'SHOOT_Q': -math.pi * 5 / 4,
                'SHOOT_A': math.pi,
                'SHOOT_Z': math.pi * 3 / 4,
            },
        }

        self_pos = P(self.pos.x, H - self.pos.y)
        near_enemy_players = [player for player in enemy_players if player.pos.dist(
            P(goal_x, H // 2)) <= (AI_SHOOT_RADIUS * (self.st[1] / 100))]
        near_enemy_pos = [P(player.pos.x, H - player.pos.y)
                          for player in near_enemy_players]

        possible_passes = []
        for k, v in angles[self.team_dir].items():
            possible_passes.append(k)
            # line = [  # Equation of line as A*x +B*y + C = 0
            #     math.sin(v),  # x coeff
            #     -math.cos(v),  # y coeff
            #     self_pos.y * math.cos(v) - self_pos.x * math.sin(v),  # constant
            # ]
            #
            # if near_enemy_pos:
            #     dist = math.inf
            #     dir = 'NOTHING'
            #     dist = min([self.dist_to_line(line, pos)
            #                 for pos in near_enemy_pos])
            #     possible_passes.append((-dist, k))
            # else:
            #     near_our_players = team
            #     near_our_pos = [P(player.pos.x, H - player.pos.y)
            #                     for player in near_our_players]
            #     dist = min([self.dist_to_line(line, pos)
            #                 for pos in near_our_pos])
            #     possible_passes.append((dist, k))
        if possible_passes:

            # print(sorted(possible_passes)[0][1])
            # shot = sorted(possible_passes)[0][1]
            # print(random.sample(possible_passes,k=1)[0])
            shot = random.sample(possible_passes,k=1)[0]
        else:
            shot = 'NOTHING'

        return shot

    def check_upside(self, enemy_team, dir):
        for enemy_player in enemy_team:
            if enemy_player.position == "DEF":
                if dir == 'L':
                    if self.pos.x >= enemy_player.pos.x:
                        return True
                elif dir == 'R':
                    if self.pos.x <= enemy_player.pos.x:
                        return True
        return False

    def update(self, action, players):
        if self.action_delay == 0:

            if action in ['MOVE_U', 'MOVE_D', "MOVE_L", "MOVE_R"]:
                if action == "MOVE_L":
                    if self.walk_dir == 'R':
                        self.walk_dir = 'L'

                elif action == "MOVE_R":
                    if self.walk_dir == 'L':
                        self.walk_dir = 'R'
                gk = 0.7
                if self.id != 0:
                    gk = 1
                self.pos += P(int((MAX_PLAYER_SPEED / 2) + ((MAX_PLAYER_SPEED / 2) * (self.st[0] / 100)))*gk,
                              int((MAX_PLAYER_SPEED / 2) + ((MAX_PLAYER_SPEED / 2) * (self.st[0] / 100)))*gk) * P(ACT[action])
                self.pos = P(min(max(MAX_PLAYER_RADIUS, self.pos.x), W - MAX_PLAYER_RADIUS),
                             min(max(MAX_PLAYER_RADIUS, self.pos.y), H - MAX_PLAYER_RADIUS))

    def move(self, stats_prev, state, reward):
        if state:
            if self.team_id == state['team1']['id']:  # Set correct teams based on team id
                self_team = state['team1']
                other_team = state['team2']
            else:
                self_team = state['team2']
                other_team = state['team1']

            if self.id == 0:  # Special for the goal-keeper
                ai_gk_pass = self.gk_pass(self_team['players'],
                                          other_team['players'], self_team['goal_x'])
                ai_gk_move = self.gk_move(self_team['goal_x'], state['ball'])
                # GK has the ball
                if state['ball'].ball_stats['player'] == self.id:
                    state['ball'].ball_stats['catch'] = True
                    if ai_gk_pass != 'NOTHING':
                        return ai_gk_pass
                    else:
                        return ai_gk_move
                else:
                    state['ball'].ball_stats['catch'] = False
                    return ai_gk_move

            # Selected player has the ball
            if state['ball'].ball_stats['player'] == self.id:
                ai_shoot = self.ai_shoot(
                    other_team['players'][0], other_team['goal_x'])
                ai_pass = self.ai_pass(
                    self_team['players'], other_team['players'])
                # If shot is possible, take it
                if self.pos.dist(P(other_team['goal_x'], H // 2)) <= (
                        AI_SHOOT_RADIUS + (AI_SHOOT_RADIUS/2 +(AI_SHOOT_RADIUS/2 *(self.st[1] / 100)))) and ai_shoot != 'NOTHING':

                    return ai_shoot
                # Else, pass if possible (passes towards the enemy goal are prioritized)
                elif ai_pass != 'NOTHING' and random.random() >= AI_PASS_PROB:
                    return ai_pass
                else:
                    # Move towards the goal
                    return self.ai_move_with_ball(other_team['players'], other_team['goal_x'])

            else:  # Move towards the ball if posssbile, otherwise return to formation
                move = self.ai_move_without_ball(state['ball'])
                if move != 'NOTHING' or move != "FORM":
                    return move
                else:
                    is_upside = self.check_upside(other_team['players'], other_team['dir'])
                    if is_upside:
                        return f"MOVE_{self_team.dir}"
                    else:
                        return 'FORM'  # Special action, not defined in ACT
        else:
            return 'NOTHING'  # Otherwise do nothing
