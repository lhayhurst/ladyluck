from collections import OrderedDict
import unittest

from scipy.stats import binom

from persistence import DiceType


HIT_NO_FOCUS = 4.0/8.0   #three hits, one crit
CRIT_NO_FOCUS = 1.0/8.0 #1 crit
MISS = 4.0/8.0  #2 blanks, 2 focuses
HIT_FOCUS    = 6.0/8.0  #three hits, one crit, two focuses
HIT_FOCUS_REROLL = 15.0/16.0 #the bestest!
EVADE_NO_FOCUS = 3.0/8.0  #three evades
MISS_NO_FOCUS  = 4.0/8.0 #two eyes, two blanks
EVADE_FOCUS  = 5.0/8.0   #three evades, two eyes

def get_hit_prob( focus, target_lock ):
    if focus and target_lock:
        return HIT_FOCUS_REROLL
    if focus:
        return HIT_FOCUS
    return HIT_NO_FOCUS

def get_evade_prob( focus ):
    if focus:
        return EVADE_FOCUS
    return EVADE_NO_FOCUS

class XWingDiceProbabilityMassFunction:

    def __init__ (self, dice_type, num_dice, use_focus=False, use_target_lock=False):
        self.num_dice = num_dice
        self.results = [ x for x in range(num_dice+1)]
        self.probability_of_success = 0
        if dice_type == DiceType.RED:
            self.probability_of_success = get_hit_prob(use_focus, use_target_lock)
        else:
            self.probability_of_success = get_evade_prob(use_focus)

        self.pmf = binom.pmf( self.results, num_dice, self.probability_of_success)



class MergedProbabilityMassFunction:
       #get the probability mass function results.
        #these are just an array of probabilities for each dice result.
        #for example, given 6 red dice, the probably of getting 0, 1, 2, ...6 hits, without a focus, is:
        #[0.0156, 0.093, 0.2343, 0.3125, 0.234, 0.093, 0.0156]

    def __init__(self, red_pmf, green_pmf):
        self.red_pmf = red_pmf
        self.green_pmf = green_pmf

        self.merged = OrderedDict()
        i = 0
        j = 0
        while i <= red_pmf.num_dice:
            while j <= green_pmf.num_dice:
                num_hits = 0
                if i > j:
                    num_hits = i - j
                phit = red_pmf.pmf[i] * green_pmf.pmf[j]
                if not self.merged.has_key( num_hits ):
                    self.merged[ num_hits ] = phit
                else:
                    self.merged[ num_hits ] = self.merged[num_hits] + phit
                j = j + 1
            i = i + 1
            j = 0

        self.weighted_avg = 0
        for hit in self.merged.keys():
            self.weighted_avg += hit * self.merged[hit]

class TestProbs(unittest.TestCase):
    #@unittest.skip("skipping")
    def test_probs(self):

        #see http://blog.mcbryan.co.uk/2013/02/the-binomial-distribution-python-and.html
        #for an explanation of the python/scipy stuff

        #see http://boardgamegeek.com/thread/915146/math-wing-hit-probabilities/page/2
        #for an explanation of the Big Idea, and the values used for the asserts below
        #thanks to VorpalSword for taking the time to write it up

        hit_results = XWingDiceProbabilityMassFunction(DiceType.RED, 2, use_focus=True, use_target_lock=True)
        evade_results = XWingDiceProbabilityMassFunction(DiceType.GREEN, 2, use_focus=True)
        merged_results = MergedProbabilityMassFunction(hit_results, evade_results)

        self.assertEqual( .25, hit_results.pmf[0])
        self.assertEqual( .5, hit_results.pmf[1])
        self.assertEqual( .25, hit_results.pmf[2])

        self.assertEqual( .390625, evade_results.pmf[0])
        self.assertEqual( .46875, evade_results.pmf[1])
        self.assertEqual( .140625, evade_results.pmf[2])

        self.assertEqual( .58984375, merged_results.merged[0])
        self.assertEqual( .3125, merged_results.merged[1])
        self.assertEqual( .09765625, merged_results.merged[2])

        #and finally the average
        self.assertEqual( .5078125, merged_results.weighted_avg)



if __name__ == "__main__":
    unittest.main()