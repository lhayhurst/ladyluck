__author__ = 'lhayhurst'


COUNTER = "counter"


class Counter:
    def __init__(self, recursive_counter=False):

        self.total_reds   = 0
        self.total_greens = 0

        self.red_hits     = 0
        self.red_blanks   = 0
        self.red_eyes     = 0
        self.red_crits    = 0

        self.green_evades = 0
        self.green_blanks = 0
        self.green_eyes   = 0

        if recursive_counter:
            self.reroll_counter  = Counter()
            self.convert_counter = Counter()


    def count_reroll(self, roll):
        self.reroll_counter.count(roll)
        return self

    def count_convert(self, roll):
        self.convert_counter.count(roll)

    def count(self, roll ):
        if roll.is_attack():
            self.total_reds += 1
            if roll.is_hit():
                self.red_hits += 1
            elif roll.is_crit():
                self.red_crits += 1
            elif roll.is_focus():
                self.red_eyes += 1
            elif roll.is_blank():
                self.red_blanks += 1
        elif roll.is_defense():
            self.total_greens += 1
            if roll.is_evade():
                self.green_evades += 1
            elif roll.is_focus():
                self.green_eyes += 1
            elif roll.is_blank():
                self.green_blanks += 1
        return self

    NUM_REDS_HITS  = 3.0 / 8.0
    NUM_RED_CRITS  = 1.0 / 8.0
    NUM_RED_EYES   = 2.0 / 8.0
    NUM_RED_BLANKS = 2.0 / 8.0

    def total_reds_after_rerolls(self):
        return self.total_reds + self.reroll_counter.total_reds

    def total_red_hits_after_rerolls(self):
        return self.red_hits + self.reroll_counter.red_hits

    def total_red_crits_after_rerolls(self):
        return self.red_crits + self.reroll_counter.red_crits

    def total_red_crits_after_converts(self):
        return self.total_red_crits_after_rerolls() + self.convert_counter.red_crits

    def total_red_hits_after_converts(self):
        return self.total_red_hits_after_rerolls() + self.convert_counter.red_hits

    def total_red_focuses_after_rerolls(self):
        return self.red_eyes + self.reroll_counter.red_eyes

    def total_red_focuses_after_converts(self):
        #this one is interesting, as the total number of focuses could go down due to the converts
        return self.total_red_focuses_after_rerolls() - self.convert_counter.red_hits - self.convert_counter.red_crits

    def expected_red_hits(self):
        t = self.total_reds
        return t * Counter.NUM_REDS_HITS

    def expected_hits_after_rerolls(self):
        t1 = self.total_reds
        t2 = self.reroll_counter.total_reds
        t3 = t1 + t2
        return t3 * Counter.NUM_REDS_HITS

    def expected_red_crits(self ):
        t = self.total_reds
        return t *  Counter.NUM_RED_CRITS

    def expected_crits_after_rerolls(self):
        t1 = self.total_reds
        t2 = self.reroll_counter.total_reds
        t3 = t1 + t2
        return t3 * Counter.NUM_RED_CRITS

    def expected_focuses_after_rerolls(self):
        t1 = self.total_reds
        t2 = self.reroll_counter.total_reds
        t3 = t1 + t2
        return t3 * Counter.NUM_RED_EYES

    def expected_red_blanks(self):
        t = self.total_reds
        return t * Counter.NUM_RED_BLANKS

    def expected_red_eyes(self):
        t = self.total_reds
        return t * Counter.NUM_RED_EYES

    def expected_green_evades(self):
        t = self.total_greens
        return t * (3.0 / 8.0)

    def expected_green_blanks(self):
        t = self.total_greens
        return t * (3.0 / 8.0)

    def expected_green_eyes(self ):
        t = self.total_greens
        return t * (2.0 / 8.0)