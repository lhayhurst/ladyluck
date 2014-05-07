from persistence import DiceType

__author__ = 'lhayhurst'


class Score:

    HIT_WEIGHT         = 1
    CRIT_WEIGHT        = 1.25
    RED_FOCUS_WEIGHT   = 0.5
    RED_BLANK_WEIGHT   = 0
    EVADE_WEIGHT       = 1
    GREEN_FOCUS_WEIGHT = 0.75
    GREEN_BLANK_WEIGHT = 0

    def __init__(self):
        self.red_luck   = []
        self.green_luck = []

    def get_last_red_luck(self):
        if len(self.red_luck) > 0:
            return self.red_luck[-1]
        else:
            return None

    def get_last_green_luck(self):
        if len(self.green_luck) > 0:
            return self.green_luck[-1]
        else:
            return None


    def eval(self, dice_type, counter):
        if dice_type == DiceType.RED:
            return self.eval_red(counter)
        elif dice_type == DiceType.GREEN:
            return self.eval_green(counter)

    def eval_red(self, counter):

        exp_hits         = counter.expected_red_hits()
        hit_dev          = counter.red_hits - exp_hits
        weighted_hit_dev = hit_dev * Score.HIT_WEIGHT

        exp_crits         = counter.expected_red_crits()
        crit_dev          = counter.red_crits - exp_crits
        weighted_crit_dev = crit_dev * Score.CRIT_WEIGHT

        exp_focus          = counter.expected_red_eyes()
        focus_dev          = counter.red_eyes - exp_focus
        weighted_focus_dev = focus_dev * Score.RED_FOCUS_WEIGHT

        exp_blank          = counter.expected_red_blanks()
        blank_dev          = counter.red_blanks - exp_blank
        weighted_blank_dev = blank_dev * Score.RED_BLANK_WEIGHT

        luck = weighted_hit_dev + weighted_crit_dev + weighted_focus_dev + weighted_blank_dev

        self.red_luck.append(luck)

        return luck

    def eval_green(self, counter):
        exp_evades         = counter.expected_green_evades()
        evade_dev          = counter.green_evades - exp_evades
        weighted_evade_dev = evade_dev * Score.EVADE_WEIGHT

        exp_focus          = counter.expected_green_eyes()
        focus_dev          = counter.green_eyes - exp_focus
        weighted_focus_dev = focus_dev * Score.GREEN_FOCUS_WEIGHT

        exp_blank          = counter.expected_green_blanks()
        blank_dev          = counter.green_blanks - exp_blank
        weighted_blank_dev = blank_dev * Score.GREEN_BLANK_WEIGHT

        luck = weighted_evade_dev + weighted_focus_dev + weighted_blank_dev

        self.green_luck.append(luck)

        return luck