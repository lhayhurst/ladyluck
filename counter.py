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

        self.red_hits_added = 0
        self.red_crits_added = 0
        self.green_evades_added = 0
        self.total_reds_added = 0
        self.total_greens_added = 0

        if recursive_counter:
            self.reroll_counter  = Counter()
            self.convert_counter = Counter()


    def count_reroll(self, roll):
        self.reroll_counter.count(roll)
        return self

    def count_convert(self, roll):
        self.convert_counter.count(roll)

    def count(self, dice ):
        if dice.is_attack() and dice.was_rolled():
            self.total_reds += 1
            if dice.is_hit():
                self.red_hits += 1
            elif dice.is_crit():
                self.red_crits += 1
            elif dice.is_focus():
                self.red_eyes += 1
            elif dice.is_blank():
                self.red_blanks += 1
        elif dice.is_defense() and dice.was_rolled():
            self.total_greens += 1
            if dice.is_evade():
                self.green_evades += 1
            elif dice.is_focus():
                self.green_eyes += 1
            elif dice.is_blank():
                self.green_blanks += 1
        elif dice.is_attack() and dice.was_added():
            self.total_reds_added +=1
            if dice.is_hit():
                self.red_hits_added +=1
            elif dice.is_crit():
                self.red_crits_added +=1
        elif dice.is_defense() and dice.was_added():
            self.total_greens_added +=1
            if dice.is_evade():
                self.green_evades_added +=1
        return self

    NUM_REDS_HITS    = 3.0 / 8.0
    NUM_RED_CRITS    = 1.0 / 8.0
    NUM_RED_EYES     = 2.0 / 8.0
    NUM_RED_BLANKS   = 2.0 / 8.0

    NUM_GREEN_EYES   = 2.0 / 8.0
    NUM_GREEN_EVADES = 3.0 / 8.0
    NUM_GREEN_BLANKS = 3.0 / 8.0

    def total_reds_after_rerolls(self):
        return self.total_reds + self.reroll_counter.total_reds

    def total_greens_after_rerolls(self):
        return self.total_greens + self.reroll_counter.total_greens


    def total_red_hits_after_rerolls(self):
        return self.red_hits + self.reroll_counter.red_hits

    def total_red_crits_after_rerolls(self):
        return self.red_crits + self.reroll_counter.red_crits

    def total_red_crits_after_converts(self):
        return self.total_red_crits_after_rerolls() + self.convert_counter.red_crits

    def total_red_hits_after_converts(self):
        return self.total_red_hits_after_rerolls() + self.convert_counter.red_hits

    def total_green_evades_after_converts(self):
        return self.total_green_evades_after_rerolls() + self.convert_counter.green_evades


    def total_red_focuses_after_rerolls(self):
        return self.red_eyes + self.reroll_counter.red_eyes

    def total_red_focuses_after_converts(self):
        #this one is interesting, as the total number of focuses could go down due to the converts
        return self.total_red_focuses_after_rerolls() - self.convert_counter.red_hits - self.convert_counter.red_crits

    def total_green_evades_after_rerolls(self):
        return self.green_evades + self.reroll_counter.green_evades

    def total_green_focuses_after_converts(self):
        #same logic as above
        return self.total_green_focuses_after_rerolls() - self.convert_counter.green_evades

    def total_red_blanks_after_rerolls(self):
        return self.red_blanks + self.reroll_counter.red_blanks

    def total_green_blanks_after_rerolls(self):
        return self.green_blanks + self.reroll_counter.green_blanks


    def total_red_blanks_after_converts(self):
        return self.total_red_blanks_after_rerolls() + self.convert_counter.red_blanks

    def total_green_blanks_after_converts(self):
        return self.total_green_blanks_after_rerolls() + self.convert_counter.green_blanks

    def total_green_focuses_after_rerolls(self):
        return self.green_eyes + self.reroll_counter.green_eyes

    def expected_red_hits(self):
        t = self.total_reds
        return t * Counter.NUM_REDS_HITS

    def expected_hits_after_rerolls(self):
        t1 = self.total_reds
        t2 = self.reroll_counter.total_reds
        t3 = t1 + t2
        return t3 * Counter.NUM_REDS_HITS

    def expected_green_evades_after_rerolls(self):
        t1 = self.total_greens
        t2 = self.reroll_counter.total_greens
        t3 = t1 + t2
        return t3 * Counter.NUM_GREEN_EVADES


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

    def expected_green_focuses_after_rerolls(self):
        t1 = self.total_greens
        t2 = self.reroll_counter.total_greens
        t3 = t1 + t2
        return t3 * Counter.NUM_GREEN_EYES

    def expected_red_blanks(self):
        t = self.total_reds
        return t * Counter.NUM_RED_BLANKS

    def expected_blanks_after_rerolls(self):
        t1 = self.total_reds
        t2 = self.reroll_counter.total_reds
        t3 = t1 + t2
        return t3 * Counter.NUM_RED_BLANKS

    def expected_green_blanks_after_rerolls(self):
        t1 = self.total_greens
        t2 = self.reroll_counter.total_greens
        t3 = t1 + t2
        return t3 * Counter.NUM_GREEN_BLANKS

    def expected_red_eyes(self):
        t = self.total_reds
        return t * Counter.NUM_RED_EYES

    def expected_green_evades(self):
        t = self.total_greens
        return t * Counter.NUM_GREEN_EVADES

    def expected_green_blanks(self):
        t = self.total_greens
        return t * Counter.NUM_GREEN_BLANKS

    def expected_green_eyes(self ):
        t = self.total_greens
        return t * Counter.NUM_GREEN_EYES