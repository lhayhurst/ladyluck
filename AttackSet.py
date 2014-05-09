from counter import Counter, COUNTER
from score import Score

__author__ = 'lhayhurst'

END = "end"
SCORE = "score"
INITIAL = "initial"


class AttackSet:
    def __init__(self, attack_set, throw):
        self.attacking_throw = throw
        self.number = attack_set
        self.records = []
        self.attacking_player = None
        self.defending_player = None

    def add_defending_throw(self, throw):
        self.defending_throw = throw
        self.defending_player = throw.player

    def get_record_for_dice_num(self, dice_num):
        for rec in self.records:
            if rec.dice_num == dice_num:
                return rec
        return None


    def total_attack_end_luck(self):
        return self.total_by_luck_attr("attack_end_luck")

    def total_defense_end_luck(self):
        return self.total_by_luck_attr("defense_end_luck")

    def total_by_luck_attr(self, attr):
        score = None
        for rec in self.records:
            if hasattr( rec, attr) and getattr(rec, attr) is not None:
                if score is None:
                    score = getattr(rec, attr)
                else:
                    score = getattr(rec, attr)
        return score

    def get_hits(self):
        ret = []
        for rec in self.records:
            if rec.was_hit():
                ret.append(rec)
        return ret

    def get_crits(self):
        ret = []
        for rec in self.records:
            if rec.was_crit():
                ret.append(rec)
        return ret

    def get_evades(self):
        ret = []
        for rec in self.records:
            if rec.was_evade():
                ret.append(rec)
        return ret

    def num_net_hits(self):
        return self.net_hits

    def num_net_crits(self):
        return self.net_crits

    def hits_comma_crits_string(self):

        nnh = self.num_net_hits()
        nnc = self.net_crits
        if nnh == 0 and nnc == 0:
            return ""
        if nnh >0 and nnc == 0:
            return str(nnh) + "h"
        if nnh == 0 and nnc > 0:
            return str(nnc) + "c"
        return str(nnh) +"h, " + str(nnc) + "c"

    def net_results(self):
        #first extract all the hits

        hits = self.get_hits()
        self.net_hits = len(hits)
        #then crits
        crits = self.get_crits()
        self.net_crits = len(crits)

        if len(hits) == 0 and len(crits) == 0:
            return

        evades = self.get_evades()
        num_evades = len(evades)

        #first cancel the hits
        for hit in hits:
            if num_evades > 0:
                num_evades = num_evades - 1
                hit.cancel()
                self.net_hits = self.net_hits - 1
            elif num_evades == 0:
                break

        #now try to cancel the crits
        for crit in crits:
            if num_evades > 0:
                num_evades = num_evades - 1
                crit.cancel()
                self.net_crits = self.net_crits - 1

            elif num_evades == 0:
                break


    def score(self, tape_stats):

        self.end_counter               = Counter(True)
        self.end_score                 = Score()


        for rec in self.records:

            initial_attack_score   = tape_stats[rec.attacking_player.name][INITIAL][SCORE]
            initial_attack_counter = tape_stats[rec.attacking_player.name][INITIAL][COUNTER]

            initial_defend_score   = None
            initial_defend_counter = None
            if rec.defending_player is not None:
                initial_defend_score = tape_stats[rec.defending_player.name][INITIAL][SCORE]
                initial_defend_counter = tape_stats[rec.defending_player.name][INITIAL][COUNTER]

            if rec.attack_roll is not None:
                initial_attack_score.eval(
                    rec.attack_roll.dice_type,
                    initial_attack_counter.count( rec.attack_roll )
                )

            if rec.defense_roll is not None:
                if rec.defending_player is not None:
                    initial_defend_score.eval(
                        rec.defense_roll.dice_type,
                        initial_defend_counter.count( rec.defense_roll )
                    )

            if rec.attack_reroll is not None:
                initial_attack_counter.count_reroll( rec.attack_reroll )

            if rec.defense_reroll is not None:
                initial_defend_counter.count_reroll( rec.defense_reroll )

            if rec.attack_convert is not None:
                initial_attack_counter.count_convert( rec.attack_convert )

            if rec.defense_convert is not None:
                initial_defend_counter.count_convert( rec.defense_convert )

            if rec.attack_end is not None:
                luck = self.end_score.eval( rec.attack_end.dice_type, self.end_counter.count(rec.attack_end))
                rec.attack_end_luck = luck

                end_attack_score       = tape_stats[rec.attacking_player.name][END][SCORE]
                end_attack_counter     = tape_stats[rec.attacking_player.name][END][COUNTER]
                end_attack_score.eval( rec.attack_end.dice_type, end_attack_counter.count( rec.attack_end ))


            if rec.defense_end is not None:
                luck = self.end_score.eval( rec.defense_end.dice_type, self.end_counter.count(rec.defense_end))
                rec.defense_end_luck = luck
                if rec.defending_player is not None:
                    end_defense_score   = tape_stats[rec.defending_player.name][END][SCORE]
                    end_defense_counter = tape_stats[rec.defending_player.name][END][COUNTER]
                    end_defense_score.eval( rec.defense_end.dice_type,end_defense_counter.count( rec.defense_end ) )
