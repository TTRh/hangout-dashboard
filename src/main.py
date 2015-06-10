#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from hangout import *
from parser import *
from writer import *
from statistics import *

def main(argv):
    # declare parser
    parser = argparse.ArgumentParser(description="Commandline python script to read and transform Google Hangout json files.")
    parser.add_argument('jsonfile',type=str,help="path to Hangouts.json")
    args = parser.parse_args()

    # declare object
    hg = Hangout()
    hr = HangoutReader(args.jsonfile,hg)
    hw = HangoutCsvWriter(hg,'Hangouts.csv')

    # read and describe
    hr.read()
    hg.describe()
    # hw.write()

    # compute stats
    hs = HangoutStatisticManager(hg)
    hs.conversation_ids = ["UgybBVlmYKlQ5IF4Ccl4AaABAQ"]
    hs.run()

    # dump stats
    hsw = HangoutStatisticJsonWriter(hs,'HangoutsStatistic.json')
    hsw.write()

if __name__ == '__main__':
    main(sys.argv)
