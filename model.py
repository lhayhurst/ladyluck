class DiceRoll:
    def __init__(self, result, num, player ):
        self.player = player
        self.values = []
        self.num = num
        self.values.append( result )

    HIT = "Hit"
    CRIT = "Crit"
    BLANK = "Blank"
    FOCUS = "Focus"
    EVADE = "Evade"

    def value_is(self, value):
        return self.values[-1] == value

    def is_crit(self):
        return self.value_is(DiceRoll.CRIT)

    def is_hit(self):
        return self.value_is(DiceRoll.HIT)

    def is_evade(self):
        return self.value_is(DiceRoll.EVADE)

    def add_value(self, value):
        self.values.append(value)

    def get_result(self):
        return self.values[-1]

    def was_modified(self):
        return len(self.values) > 1

    def started_out_as(self):
        return self.values[0]


class AttackSet:
    def __init__(self, attacking_player, defending_player ):
        self.attack_rolls  = []
        self.defense_rolls = []
        self.attacking_player = attacking_player
        self.defending_player = defending_player

    def num_uncancelled_hits(self):
        count = 0
        for roll in self.attack_rolls:
            if roll.is_hit() or roll.is_crit():
                count = count + 1
        for roll in self.defense_rolls:
            if roll.is_evade():
                count = count - 1
        if count < 0:
            count = 0
        return count

    def add_attack_roll(self, roll):
        if self.attacking_player == None:
            self.attacking_player = roll.player
        self.attack_rolls.append( roll )

    def add_defense_roll(self, roll):
        if self.defending_player == None:
            self.defending_player = roll.player
        self.defense_rolls.append(roll)

    def get_rolls(self):
        return self.rolls

    def add_attack_reroll(self, dice_num, dice_value ):
        roll = self.attack_rolls[ int(dice_num) - 1 ]
        roll.add_value( dice_value )

    def add_defense_reroll(self, dice_num, dice_value ):
        roll = self.defense_rolls[ int(dice_num) - 1 ]
        roll.add_value( dice_value )

    def was_likely_an_asteroid_roll(self):
        return len(self.attack_rolls) == 1 and len( self.defense_rolls ) == 0