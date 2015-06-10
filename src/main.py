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
    hs = HangoutStatisticManager(hg)
    hs.conversation_ids = ["UgybBVlmYKlQ5IF4Ccl4AaABAQ"]
    hs.run()

    # 4 - dump statistics
    hsw = HangoutStatisticJsonWriter(hs,'HangoutsStatistic.json')
    hsw.write()

if __name__ == '__main__':
    main(sys.argv)
