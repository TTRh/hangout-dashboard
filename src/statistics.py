#####################
# standard import
#####################

import nltk
import itertools
import re
from datetime import timedelta
from collections import *
import json

from hangout import *

#####################
# helper
#####################

RE_URL = re.compile(r'http://[^ ]*')

def init_counter(counter,keyfunc=lambda k:k,valfunc=lambda x,y:x+y,default_type=None):
    result = None
    # init counter
    if default_type is None:
        result = Counter()
    else:
        result = defaultdict(default_type)
    # fill counter
    for k,v in counter.iteritems():
        val = valfunc(result[keyfunc(k)],v)
        if val is not None:
            result[keyfunc(k)] = val
    return result

def mean(iterable):
    n,total = 0,0
    for v in iterable:
        n+=1
        total += v
    if n == 0:
        return None
    else:
        return float(total)/n

def median(lst):
    n = len(lst)
    if n == 0:
        return None
    elif n % 2 == 0:
        return float(lst[n/2-1] + lst[n/2])/2
    else:
        return lst[n/2]

def strtime2seconds(strtime):
    return int(strtime[:2])*3600 + int(strtime[2:5])*60 + int(strtime[-2:])

#####################
# statistic engine
#####################

class HangoutStatistic:

    def __init__(self,hangout,conversation_id):
        # input param
        self.hangout = hangout
        self.conversation = hangout.get_conversation(conversation_id)
        # private variables
        self.user_statistics_accumulator = {}
        self.user_statistics = {}
        self.global_statistics = {}

    def init_user_statistics(self,user_id):
        # init accumulators
        acc = {
            "event_per_Ym" : Counter(),
            "event_per_Ymd" : Counter(),
            "event_per_YmdH" : Counter(),
            "event_per_YmdHM" : Counter(),
            "event_per_YmdHMS" : Counter(),
            "HMS_per_Ymd" : defaultdict(list)
        }
        self.user_statistics_accumulator[user_id] = acc
        # init statistics
        stats = [
            "name", # username
            "sum_events", # total number of events
            "sum_links", # total numbers of links
            "sum_words", # total number of words
            "sum_uniq_words", # total number of unique words (vocabulary)
            "sum_reference", # total number of user reference
            # text analysis
            "main_words", # main words
            "main_site", # main site redirection
            "aliases", # list of alias
            "quotes", # list of quote
            "longest_word", # longuest words posted
            "longest_post", # longuest message text posted
            # Ym vs events
            "sparkline_sum_events_vs_month", # number of event per month
            # Ymd vs events
            "avg_day_events", # avg number of event by day
            "avg_day_links", # avg number of links by day
            "sum_days_with_event", # total days with at least one event
            "max_day_events", # max event in one day
            "sparkline_sum_events_vs_day", # number of event per day
            # YmdH vs events
            "max_hour_events", # max frequency event posted in one hour
            # YmdHM vs events
            "sparkline_avg_events_vs_time", # avg number of event per time in a day
            # Ymd vs HMS
            "max_time_event", 
            "min_time_event", 
            "avg_max_time_event", 
            "avg_min_time_event", 
        ]
        self.user_statistics[user_id] = dict.fromkeys(stats)

    def update_user_statistics(self,user_id):
        # init local variable
        acc = self.user_statistics_accumulator[user_id]
        stats = self.user_statistics[user_id]
        all_HM = map(lambda x:(3-len(x))*'0' + x,[ str(i*10 + j) for i in xrange(0,24) for j in xrange(0,6) ])
        # TODO : deal spy users
        if len(acc["event_per_YmdHMS"]) == 0:
            return
        # update statistics
        stats["sum_events"] = sum(acc["event_per_YmdHMS"].itervalues())
        stats["sum_links"] = None
        stats["sum_words"] = None
        stats["sum_uniq_words"] = None
        stats["sum_reference"] = None
        stats["main_words"] = None
        stats["main_site"] = None
        stats["aliases"] = None
        stats["quotes"] = None
        stats["longest_word"] = None
        stats["longest_post"] = None
        stats["sparkline_sum_events_vs_month"] = None # [ acc["event_per_Ym"][k] for k in all_Ym ]
        stats["avg_day_events"] = mean(acc["event_per_Ymd"].values())
        stats["avg_day_links"] = None
        stats["sum_days_with_event"] = len(acc["event_per_Ymd"])
        stats["max_day_events"] = max(acc["event_per_Ymd"].itervalues())
        stats["sparkline_sum_events_vs_day"] = None # [ acc["event_per_Ymd"][k] for k in all_Ymd ]
        stats["max_hour_events"] = max(acc["event_per_YmdH"].itervalues())
        acc_event_per_HM = init_counter(acc["event_per_YmdHM"],lambda k:k[-3:],lambda x,y:x.append(y),list)
        stats["sparkline_avg_events_vs_time"] = [ (k,sum(acc_event_per_HM[k])) if len(acc_event_per_HM[k]) > 0 else (k, 0) for k in all_HM ]
        stats["max_time_event"] = max(reduce(lambda x,y:x+y,acc["HMS_per_Ymd"].itervalues()))
        stats["min_time_event"] = min(reduce(lambda x,y:x+y,acc["HMS_per_Ymd"].itervalues()))
        stats["avg_max_time_event"] = str(timedelta(seconds = median(map(strtime2seconds,[max(l) for l in acc["HMS_per_Ymd"].itervalues()]))))
        stats["avg_min_time_event"] = str(timedelta(seconds = median(map(strtime2seconds,[min(l) for l in acc["HMS_per_Ymd"].itervalues()]))))

    def init_global_statistics(self):
        stats = [
            "max_YM",
            "min_YM",
            "sum_events"
        ]
        self.global_statistics = dict.fromkeys(stats)

    def init(self):
        # init global statistics
        self.init_global_statistics()
        # init users statistics
        for p in self.conversation.iter_participant():
            self.init_user_statistics(p.get_id())
            self.user_statistics[p.get_id()]["name"] = p.get_name()

    def optimize(self):
        for e in self.conversation.iter_event():
            # TODO : deal unknow users
            if e.get_sender() not in self.user_statistics_accumulator:
                continue
            # local variable helper
            acc = self.user_statistics_accumulator[e.get_sender()]
            text = e.get_text()
            dt = e.get_datetime()
            dt_Ym = dt[:6]
            dt_Ymd = dt[:8]
            dt_YmdH = dt[:-4]
            dt_YmdHM = dt[:-3]
            dt_HMS = dt[-6:]
            # update accumulators
            acc["event_per_Ym"][dt_Ym] += 1
            acc["event_per_Ymd"][dt_Ymd] += 1
            acc["event_per_YmdH"][dt_YmdH] += 1
            acc["event_per_YmdHM"][dt_YmdHM] += 1
            acc["HMS_per_Ymd"][dt_Ymd].append(dt_HMS)
            acc["event_per_YmdHMS"][dt] += 1

    def update(self):
        for u in self.user_statistics.iterkeys():
            self.update_user_statistics(u)

    def run(self):
        self.init()
        self.optimize()
        self.update()
        print json.dumps(self.user_statistics["100004041546029582490"])
