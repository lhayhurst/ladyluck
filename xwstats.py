from __future__ import print_function
import argparse
import re
from matplotlib.patches import Rectangle
from parser import LogFileParser




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Analyze vassal txt logs')
    parser.add_argument('--input_file', action="store", metavar="PATH TO FILE",
        help="Input file.  Defaults to log.txt.")

    args = parser.parse_args()

    parser = LogFileParser( args.input_file )
    parser.run_finite_state_machine()

    dice_roll_sets = parser.get_roll_sets()

    create_luck_stat_graphs(dice_roll_sets)
    print_summary_stats( dice_roll_sets )











