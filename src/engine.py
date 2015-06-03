#####################
# standard import
#####################

import nltk
import itertools
import re
from datetime import timedelta
from collections import *

from context import *

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

#####################
# statistic engine
#####################

class HangoutStatistic:

    def __init__(self,hangout,conversation_id):
        self.hangout = hangout
        self.conversation = hangout.get_conversation(conversation_id)
        self.user_statistics_accumulator = {}
        self.user_statistics = {}

    def init_user_statistics(self,user_id):
        sa = {}
        s = {}
        # structures
        sa["events_vs_datetime"] = Counter()
        # general info
        s["name"] = self.conversation.get_participant(user_id).get_name()
        # global counters
        s["sum_events"] = None # total number of events
        s["sum_links"] = None # total numbers of links
        s["sum_words"] = None # total number of words
        s["sum_uniq_words"] = None # total number of unique words (vocabulary)
        s["sum_reference"] = None # total number of user reference
        # text analysis
        s["main_words"] = None # main words
        s["main_site"] = None # main site redirection
        s["aliases"] = None # list of alias
        s["quotes"] = None # list of quote
        s["longest_word"] = None # longuest words posted
        s["longest_post"] = None # longuest message text posted
        # Ym vs events
        s["sparkline_sum_events_vs_month"] = None # number of event per month
        # Ymd vs events
        s["avg_day_events"] = None # avg number of event by day
        s["avg_day_links"] = None # avg number of links by day
        s["sum_days_with_event"] = None # total days with at least one event
        s["max_day_events"] = None # max event in one day
        s["sparkline_sum_events_vs_day"] = None # number of event per day
        # YmdH vs events
        s["max_hour_events"] = None # max frequency event posted in one hour
        # YmdHM vs events
        s["sparkline_avg_events_vs_time"] = None # avg number of event per time in a day
        # HMS vs events
        s["max_time_event"] = None 
        s["min_time_event"] = None 
        # Ymd vs HMS
        s["avg_max_time_event"] = None 
        s["avg_min_time_event"] = None 
        # initialization
        self.user_statistics[user_id] = s
        self.user_statistics_accumulator[user_id] = sa

    def update_user_statistics(self,user_id):
        sa = self.user_statistics_accumulator[user_id]
        s = self.user_statistics[user_id]
        # structure
        c_datetime = sa["events_vs_datetime"]
        if len(c_datetime) == 0:
            return
        # global counters
        s["sum_events"] = sum(c_datetime.itervalues())
        # Ym vs events
        c_datetime_Ym = init_counter(c_datetime,lambda k:k[:6])
        # s["sparkline_sum_events_vs_month"] = [ c_datetime_Ym[k] for k in all_months ]
        # Ymd vs events
        c_datetime_Ymd = init_counter(c_datetime,lambda k:k[:8])
        s["avg_day_events"] = sum(c_datetime_Ymd.itervalues())/len(c_datetime_Ymd)
        s["sum_days_with_event"] = len(c_datetime_Ymd)
        s["max_day_events"] = max(c_datetime_Ymd.itervalues())
        # s["sparkline_sum_events_vs_day"] = [ c_datetime_Ymd[k] for k in all_days ]
        # YmdH vs events
        c_datetime_YmdH = init_counter(c_datetime,lambda k:k[:-4])
        s["max_hour_events"] = max(c_datetime_YmdH.itervalues())
        # YmdHM vs events
        c_datetime_YmdHM = init_counter(c_datetime,lambda k:k[:-2])
        c_datetime_HM = init_counter(c_datetime_YmdHM,lambda k:k[-4:],lambda x,y:x.append(y),list)
        # s["sparkline_avg_events_vs_time"] = [ sum(c_datetime_HM[k])/len(c_datetime_HM[k]) if len(c_datetime_HM[k])>0 else 0 for k in all_times ]
        # HMS vs events
        c_datetime_HMS = init_counter(c_datetime,lambda k:k[-6:])
        s["max_time_event"] = max(c_datetime_HMS.iterkeys())
        s["min_time_event"] = min(c_datetime_HMS.iterkeys())
        # Ymd vs HMS
        c_datetime_Ymd_vs_HMS = defaultdict(list)
        for k in c_datetime.iterkeys():
            c_datetime_Ymd_vs_HMS[k[:8]].append(k[:-8])
        max_HMS = map(lambda x:max(x),c_datetime_Ymd_vs_HMS.itervalues())
        max_HMS = map(lambda x:int(x[:2])*3600+int(x[3:5])*60+int(x[:-2]),max_HMS)
        max_S = sum(max_HMS)/len(max_HMS)
        s["avg_max_time_event"] = str(timedelta(seconds=max_S))

        min_HMS = map(lambda x:min(x),c_datetime_Ymd_vs_HMS.itervalues())
        min_HMS = map(lambda x:int(x[:2])*3600+int(x[3:5])*60+int(x[:-2]),min_HMS)
        min_S = sum(min_HMS)/len(min_HMS)
        s["avg_min_time_event"] = str(timedelta(seconds=max_S))

    def init(self):
        # init users statistics
        for p in self.conversation.iter_participant():
            self.init_user_statistics(p.get_id())

    def optimize(self):
        for e in self.conversation.iter_event():
            # deal unknow users
            if e.get_sender() not in self.user_statistics_accumulator:
                continue
            # get user stats object
            sa = self.user_statistics_accumulator[e.get_sender()]
            # local variable helper
            datetime = e.get_datetime()
            text = e.get_text()
            # fill structures
            sa["events_vs_datetime"][datetime] += 1
            # compute stats
            # s["total_links"] += len(RE_URL.findall(text))

    def update(self):
        for u in self.user_statistics.iterkeys():
            self.update_user_statistics(u)

    def run(self):
        self.init()
        self.optimize()
        self.update()
        print self.user_statistics["100004041546029582490"]

if __name__ == '__main__':

    test = Counter()
    test["201504"] += 1
    test["201404"] += 1
    test["201405"] += 1

    print "test:"
    print test

    print "identity:"
    test1 = init_counter(test)
    print test1

    print "year:"
    test2 = init_counter(test,lambda k:k[:4])
    print test2

    print "avg month:"
    test3 = init_counter(test,lambda k:k[-2:],lambda x,y:x.append(y),list)
    print test3
