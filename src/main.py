#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from hangout import *
from parser import *
from writer import *
from statistics import *

def main(argv):

    # 0 - declare parser
    parser = argparse.ArgumentParser(description="Commandline python script to read and transform Google Hangout json files.")
    parser.add_argument('jsonfile',type=str,help="path to Hangouts.json")
    args = parser.parse_args()

    # 1 - create hangout object
    hg = Hangout()

    # 2 - read fill and describe
    hr = HangoutReader(args.jsonfile,hg)
    hr.read()
    hg.describe()

    # 3 - compute statistics
    hs = HangoutStatisticEngine(hg)
    hs.conversations = ["UgybBVlmYKlQ5IF4Ccl4AaABAQ"]
    hs.run()

    # 4 - dump statistics
    # hsw = HangoutStatisticJsonWriter(hs)
    # hsw.write('HangoutsStatistic.json')

    # 5 - dump dashboard
    hsd = HangoutStatisticHtmlWriter(hs,"../data/user.json")
    hsd.write('../web')

if __name__ == '__main__':
    main(sys.argv)
