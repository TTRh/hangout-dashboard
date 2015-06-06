#####################
# standard import
#####################

import nltk
nltk.data.path.append('/home/pierre/app/nltk_data')
import itertools
import re
from datetime import date,timedelta
from collections import *
import json

from hangout import *

#####################
# helper
#####################

RE_URL = re.compile(r'https?://[^ ]*')
RE_SITE = re.compile(r'https?://([^/ ]*)/?')
RE_WORDS = re.compile(r'\w+')
STOP = set(nltk.corpus.stopwords.words("french"))

def extract_site(url):
    site = RE_SITE.search(url)
    if site is None:
        return None
    reverse_site = site.group(1).split('.')[::-1]
    result, ok = "", False
    for p in reverse_site:
        if len(p) <= 4 and ok:
            break
        if len(p) >= 5:
             ok = True
        result = p + '.' + result
    return result[:-1]

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

def median_low(lst):
    n = len(lst)
    if n == 0:
        return None
    elif n % 2 == 0:
        return lst[n/2-1]
    else:
        return lst[n/2]

def strtime2seconds(strtime):
    return int(strtime[:2])*3600 + int(strtime[2:5])*60 + int(strtime[-2:])

def iter_months(ym1,ym2):
    y1,m1 = int(ym1[:-2]),int(ym1[-2:])
    y2,m2 = int(ym2[:-2]),int(ym2[-2:])
    if ym1 > ym2:
        raise StopIteration
    else:
        for y in xrange(y1,y2+1):
            for m in xrange(1 if y != y1 else m1, 13 if y != y2 else m2+1):
                yield str(y*100 + m)

def iter_days(d1,d2,step=1):
    start,end = datetime.strptime(d1,'%Y%m%d'),datetime.strptime(d2,'%Y%m%d')
    delta = timedelta(days=step)
    while start<=end:
        yield start.strftime("%Y%m%d")
        start += delta

def iter_minutes(hm1,hm2,step=1):
    h1,m1 = int(hm1[:-2]),int(hm1[-2:])
    h2,m2 = int(hm2[:-2]),int(hm2[-2:])
    if hm1 > hm2:
        raise StopIteration
    else:
        for h in xrange(h1,h2+1):
            for m in xrange(0 if h != h1 else m1, 60 if h != h2 else m2+1,step):
                stime = str(h*100+m)
                yield '0'*(4-len(stime)) + stime

#####################
# statistic engine
#####################

class HangoutStatistic:

    def __init__(self,hangout,conversation_ids):
        self.hangout = hangout
        self.conversation_ids = conversation_ids
        # statistics structures
        self.user_statistics_accumulator = {}
        self.user_statistics = {}
        self.global_statistics_accumulator = {}
        self.global_statistics = {}

    def init_user_statistics(self,user_id):
        # init accumulators
        acc = {
            "event_per_Ym" : Counter(),
            "event_per_Ymd" : Counter(),
            "event_per_YmdH" : Counter(),
            "event_per_YmdHMS" : Counter(),
            "event_per_HM" : Counter(),
            "HMS_per_Ymd" : defaultdict(list),
            "links_per_site" : Counter(),
            "words" : Counter(),
            "words_per_event" : []
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
            "longest_event", # longuest event text posted
            "avg_words_event", # avg number of words by event
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
        acc = self.user_statistics_accumulator[user_id]
        stats = self.user_statistics[user_id]
        gacc = self.global_statistics_accumulator
        gstats = self.global_statistics
        all_Ym = iter_months(gstats["min_Ym"],gstats["max_Ym"])
        all_Ymd = iter_days(gstats["min_Ymd"],gstats["max_Ymd"])
        all_HM = iter_minutes('0000','2359',10)
        # TODO : deal spy users
        if len(acc["event_per_YmdHMS"]) == 0:
            return
        # update statistics
        stats["sum_events"] = sum(acc["event_per_YmdHMS"].itervalues())
        stats["sum_links"] = sum(acc["links_per_site"].itervalues())
        stats["sum_words"] = sum(acc["words"].itervalues())
        stats["sum_uniq_words"] = len(acc["words"])
        first_name = stats["name"].split(' ')[0].lower()
        stats["sum_reference"] = gacc["words"][first_name] if first_name in gacc["words"] else 0
        stats["main_words"] = acc["words"].most_common(20)
        stats["main_site"] = acc["links_per_site"].most_common(10)
        stats["aliases"] = None
        stats["quotes"] = None
        stats["longest_word"] = reduce(lambda x,y:x if len(x) > len(y) else y,acc["words"].iterkeys())
        stats["longest_event"] = None
        stats["avg_words_event"] = median_low(sorted(acc["words_per_event"]))
        stats["sparkline_sum_events_vs_month"] = [ acc["event_per_Ym"][str(k)] for k in all_Ym ]
        stats["avg_day_events"] = mean(acc["event_per_Ymd"].values())
        stats["avg_day_links"] = None
        stats["sum_days_with_event"] = len(acc["event_per_Ymd"])
        stats["max_day_events"] = max(acc["event_per_Ymd"].itervalues())
        stats["sparkline_sum_events_vs_day"] = [ acc["event_per_Ymd"][k] for k in all_Ymd ]
        stats["max_hour_events"] = max(acc["event_per_YmdH"].itervalues())
        stats["sparkline_avg_events_vs_time"] = [ acc["event_per_HM"][k] for k in all_HM ]
        stats["max_time_event"] = max(reduce(lambda x,y:x+y,acc["HMS_per_Ymd"].itervalues()))
        stats["min_time_event"] = min(reduce(lambda x,y:x+y,acc["HMS_per_Ymd"].itervalues()))
        stats["avg_max_time_event"] = median_low(sorted([max(l) for l in acc["HMS_per_Ymd"].itervalues()]))
        stats["avg_min_time_event"] = median_low(sorted([min(l) for l in acc["HMS_per_Ymd"].itervalues()]))

    def init_global_statistics(self):
        # init accumulators
        acc = {
            "event_per_Ym" : Counter(),
            "event_per_Ymd" : Counter(),
            "words" : Counter()
        }
        self.global_statistics_accumulator = acc
        # init statistics
        stats = [
            "max_Ym",
            "min_Ym",
            "max_Ymd",
            "min_Ymd",
            "sum_events"
        ]
        self.global_statistics = dict.fromkeys(stats)

    def update_global_statistics(self):
        acc = self.global_statistics_accumulator
        stats = self.global_statistics
        stats["max_Ym"] = max(acc["event_per_Ym"].iterkeys())
        stats["min_Ym"] = min(acc["event_per_Ym"].iterkeys())
        stats["max_Ymd"] = max(acc["event_per_Ymd"].iterkeys())
        stats["min_Ymd"] = min(acc["event_per_Ymd"].iterkeys())
        stats["sum_events"] = sum(acc["event_per_Ym"].itervalues())

    def init(self):
        self.init_global_statistics()
        for c_id in self.conversation_ids:
            c = self.hangout.get_conversation(c_id)
            for p in c.iter_participant():
                if p in self.user_statistics:
                    continue
                self.init_user_statistics(p.get_id())
                self.user_statistics[p.get_id()]["name"] = p.get_name()

    def optimize(self):
        for c_id in self.conversation_ids:
            c = self.hangout.get_conversation(c_id)
            for e in c.iter_event():
                # TODO : deal unknow users
                if e.get_sender() not in self.user_statistics_accumulator:
                    continue
                # local variable helper
                text = e.get_text()
                dt = e.get_datetime()
                dt_Ym = dt[:6]
                dt_Ymd = dt[:8]
                dt_YmdH = dt[:-4]
                dt_HMS = dt[-6:]
                dt_HM = dt[-6:-3] + '0' # by 10 minutes step
                # update global accumulators
                gacc = self.global_statistics_accumulator
                gacc["event_per_Ym"][dt_Ym] += 1
                gacc["event_per_Ymd"][dt_Ymd] += 1
                # update user accumulators
                # events counter
                uacc = self.user_statistics_accumulator[e.get_sender()]
                uacc["event_per_Ym"][dt_Ym] += 1
                uacc["event_per_Ymd"][dt_Ymd] += 1
                uacc["event_per_YmdH"][dt_YmdH] += 1
                uacc["event_per_HM"][dt_HM] += 1
                uacc["HMS_per_Ymd"][dt_Ymd].append(dt_HMS)
                uacc["event_per_YmdHMS"][dt] += 1
                # text accumulators
                nwords = 0
                for w in RE_WORDS.findall(RE_URL.sub('',text).lower()):
                    nwords += 1
                    if len(w) > 3 and w not in STOP:
                        uacc["words"][w] += 1
                        gacc["words"][w] += 1
                uacc["words_per_event"].append(nwords)
                for url in RE_URL.findall(text):
                    site = extract_site(url)
                    if site is not None:
                        uacc["links_per_site"][site] += 1

    def update(self):
        self.update_global_statistics()
        for u in self.user_statistics.iterkeys():
            self.update_user_statistics(u)

    def run(self):
        self.init()
        self.optimize()
        self.update()
        print json.dumps(self.user_statistics["100004041546029582490"])
        print json.dumps(self.user_statistics["111122836618407997682"])


class HangoutStatisticWriter:

    def __init__(self,hangoutstatistic,filename):
        self.hangoutstatistic = hangoutstatistic
        self.filename = filename

    def write(self):
        with open(self.filename,'wb') as outfile:
            result = map(None,self.hangoutstatistic.user_statistics.itervalues())
            json.dump(result,outfile,indent=4)


if __name__ == '__main__':

    print map(None,iter_months("201501","201504"))
    print map(None,iter_months("201501","201604"))
    print map(None,iter_months("201501","201502"))
    print map(None,iter_months("201701","201502"))

    print map(None,iter_days('20150201','20150220'))

    print map(None,iter_minutes('1010','1100'))
    print map(None,iter_minutes('0000','2359',10))


    print extract_site("http://www.dailymail.co.uk")
    print extract_site("http://www.gfycat.com")
    print extract_site("http://lh3.googleusercontent.com")
    print extract_site("http://motherboard.vice.com")
    print extract_site("http://i.giflike.com")
