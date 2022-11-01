class Stats(object):
    """
    Keep track of game statistics
    """

    def __init__(self, team1, team2):
        """
        Initializes the possession, pass accuracy and shot accuracy
        """
        self.team1 = team1
        self.team2 = team2

        self.pos = {team1.id: 0, team2.id: 0}
        self.goals = {team1.id: 0, team2.id: 0}
        self.shot_count = {team1.id:0, team2.id:0}
        self.tackle_acc = {
            team1.id: {
                'succ': 0,
                'fail': 0
            },
            team2.id: {
                'succ': 0,
                'fail': 0
            },
        }
        self.pass_acc = {
            team1.id: {
                'succ': 0,
                'fail': 0
            },
            team2.id: {
                'succ': 0,
                'fail': 0
            },
        }
        self.shot_acc = {
            team1.id: {
                'succ': 0,
                'fail': 0
            },
            team2.id: {
                'succ': 0,
                'fail': 0
            },
        }

    def get_goal(self):
        return self.goals[self.team1.id], self.goals[self.team2.id]

    def get_possession(self):
        """
        Return a tuple containing the current possesion (between 0 and 1) for each team
        It is rounded to 2 decimal places and their sum is guaranteed to be 1
        """
        if self.pos[self.team1.id] + self.pos[self.team2.id] == 0:
            team1_pos = 0.5
        else:
            team1_pos = round(self.pos[self.team1.id] / (self.pos[self.team1.id] + self.pos[self.team2.id]), 2)
        return team1_pos, 1 - team1_pos

    def get_pass_acc(self):
        """
        Return a tuple containing the current pass accuracy (between 0 and 1) for each team
        It is rounded to 2 decimal places
        """
        if self.pass_acc[self.team1.id]['succ'] + self.pass_acc[self.team1.id]['fail'] == 0:
            team1_pass = 0
        else:
            team1_pass = round(self.pass_acc[self.team1.id]['succ'] / (
                        self.pass_acc[self.team1.id]['succ'] + self.pass_acc[self.team1.id]['fail']), 2)

        if self.pass_acc[self.team2.id]['succ'] + self.pass_acc[self.team2.id]['fail'] == 0:
            team2_pass = 0
        else:
            team2_pass = round(self.pass_acc[self.team2.id]['succ'] / (
                        self.pass_acc[self.team2.id]['succ'] + self.pass_acc[self.team2.id]['fail']), 2)

        return team1_pass, team2_pass

    def get_shot_shout(self):
        self.shot_count[self.team1.id] = self.goals[self.team1.id] + self.shot_acc[self.team1.id]['fail']
        self.shot_count[self.team2.id] = self.goals[self.team2.id] + self.shot_acc[self.team2.id]['fail']

        return self.shot_count[self.team1.id], self.shot_count[self.team2.id]

    def get_shot_acc(self):
        """
        Return a tuple containing the current shot accuracy (between 0 and 1) for each team
        It is rounded to 2 decimal places
        """
        self.shot_acc[self.team1.id]['succ'] = self.goals[self.team1.id]
        self.shot_acc[self.team2.id]['succ'] = self.goals[self.team2.id]
        self.shot_count[self.team1.id] = self.goals[self.team1.id] + self.shot_acc[self.team1.id]['fail']
        self.shot_count[self.team2.id] = self.goals[self.team2.id] + self.shot_acc[self.team2.id]['fail']
        if self.shot_acc[self.team1.id]['succ'] + self.shot_acc[self.team1.id]['fail'] == 0:
            team1_shot = 0
        else:
            team1_shot = round(self.shot_acc[self.team1.id]['succ'] / (
                        self.shot_acc[self.team1.id]['succ'] + self.shot_acc[self.team1.id]['fail']), 2)

        if self.shot_acc[self.team2.id]['succ'] + self.shot_acc[self.team2.id]['fail'] == 0:
            team2_shot = 0
        else:
            team2_shot = round(self.shot_acc[self.team2.id]['succ'] / (
                        self.shot_acc[self.team2.id]['succ'] + self.shot_acc[self.team2.id]['fail']), 2)

        return team1_shot, team2_shot

    def get_tackle_acc(self):
        """
        Return a tuple containing the current shot accuracy (between 0 and 1) for each team
        It is rounded to 2 decimal places
        """
        if self.tackle_acc[self.team1.id]['succ'] + self.tackle_acc[self.team1.id]['fail'] == 0:
            team1_tackle = 0
        else:
            team1_tackle = round(self.tackle_acc[self.team1.id]['succ'] / (
                        self.tackle_acc[self.team1.id]['succ'] + self.tackle_acc[self.team1.id]['fail']), 2)

        if self.tackle_acc[self.team2.id]['succ'] + self.tackle_acc[self.team2.id]['fail'] == 0:
            team2_tackle = 0
        else:
            team2_tackle = round(self.tackle_acc[self.team2.id]['succ'] / (
                        self.tackle_acc[self.team2.id]['succ'] + self.tackle_acc[self.team2.id]['fail']), 2)

        return team1_tackle, team2_tackle
