#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard import
import sys
import argparse
# local import
from app.hangout import *
from app.parser import *
from app.writer import *
from app.statistics import *

def main(argv):

    # 0 - declare parser
    parser = argparse.ArgumentParser(description="command line python script to read and transform Google Hangout json files.")
    parser.add_argument('jsonfile',type=str,help="path to Hangouts.json")
    # get arguments from command line
    args = parser.parse_args()

    # 1 - create an hangout object
    hg = Hangout()

    # 2 - read hangout file, fill and describe
    hr = HangoutReader(args.jsonfile,hg,"data/user.json")
    hr.read()
    hg.describe()

    # 3 - compute statistics
    hs = HangoutStatisticEngine(hg)
    hs.conversations = ["UgybBVlmYKlQ5IF4Ccl4AaABAQ","Ugw3YvIwot8EY4-YOPR4AaABAQ"]
    hs.run()

    # 4 - dump statistics
    # hsw = HangoutStatisticJsonWriter(hs)
    # hsw.write('HangoutsStatistic.json')

    # 5 - dump hangout dashboard
    hsd = HangoutStatisticHtmlWriter(hs,"data/user.json")
    hsd.write('web')

if __name__ == '__main__':
    main(sys.argv)
