#####################
# standard import
#####################

import nltk
nltk.data.path.append('/home/pierre/app/nltk_data')
import itertools
import re
from datetime import datetime,date,timedelta
from collections import *
import json

#####################
# helpers
#####################

RE_URL = re.compile(r'https?://[^ ]*')
RE_SITE = re.compile(r'https?://([^/ ]*)/?')
RE_WORDS = re.compile(r'\w+')
RE_HASHTAG = re.compile(r'#\w+')
STOP = set(nltk.corpus.stopwords.words("french"))

def extract_site(url):
    # extract full domain name
    dn = RE_SITE.search(url)
    if dn is None:
        return None
    reverse_dn = dn.group(1).split('.')[::-1]
    result, ok = "", False
    # append from end to begin each sub domain name if current db < 4 characters and we don't add already 5 characters sub dn
    for p in reverse_dn:
        if len(p) <= 4 and ok:
            break
        if len(p) >= 5:
             ok = True
        result = p + '.' + result
    return result[:-1]

# TODO: delete that
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

# TODO: delete that
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

# TODO: detete that
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
# statistic objects
#####################

class ParticipantSatistic:

    _metrics = [
        "name", # username - initialization
        # global
        "sum_reference", # total number of user reference - global words counter
        "aliases", # list of alias - apply alias parser on global events
        "quotes", # list of quote - apply quote parser on global events
        # incremental
        "sum_events", # total number of events - incremental
        "sum_links", # total numbers of links - incremental
        "sum_words", # total number of words - incremental
        # text
        "sum_uniq_words", # total number of unique words (vocabulary) - set words
        "main_words", # main words - words counter
        "main_site", # main site redirection - incremental site parser and site counter
        "hashtags", # main hashtag - incremental hashtag parser and hashtag counter
        "longest_word", # longuest words posted - incremental / set words
        "longest_event", # longuest event text posted - incremental / list events
        "avg_words_event", # avg number of words by event - list nb words/event
        # events counter
        "sparkline_sum_events_vs_month", # sum of event per month - event counter per Ym
        "avg_day_events", # avg number of event by day - event counter per Ymd
        "avg_day_links", # avg number of links by day - links counter per Ymd
        "sum_days_with_event", # total days with at least one event - set on Ymd event
        "max_day_events", # max event in one day - event counter per Ymd
        "sparkline_sum_events_vs_day", # number of event per day - event counter per Ymd
        "max_hour_events", # max number of events posted in one hour - event counter per YmdH
        "sparkline_avg_events_vs_time", # sum number of event per time in a day - event counter per YmdHM
        "max_time_event", # max time event - incremental / default dict listed HMS per Ymd
        "min_time_event", # min time event - incremental / default dict listed HMS per Ymd
        "avg_max_time_event",  # median low time of last daily event - default dict listed HMS per Ymd
        "avg_min_time_event", # median low time of first daily event - default dict listed HMS per Ymd
    ]

    def __init__(self,participant):
        self.participant = participant
        self.statistic = dict.fromkeys(self._metrics)
        # init some metrics
        self.statistic["name"] = participant.name
        self.statistic["quotes"] = []
        self.statistic["aliases"] = []
        self.statistic["sum_reference"] = 0
        # init accumulators
        self.acc_event_per_ym = Counter()
        self.acc_event_per_ymd = Counter()
        self.acc_event_per_ymdh = Counter()
        self.acc_event_per_hm = Counter()
        self.acc_hms_per_ymd = defaultdict(set)
        self.acc_dns = Counter()
        self.acc_hashtags = Counter()
        self.acc_words = Counter()
        self.acc_words_per_event = []
        # compile specific regex
        name = self.participant.name.split(' ')
        self.re_reference = re.compile(name[0],re.IGNORECASE)
        if len(name) == 2:
            self.re_alias = re.compile(r'' + name[0] + '.*\w+.*' + name[1],re.IGNORECASE)
        else:
            self.re_alias = re.compile(r'' + name[0] + '\w+',re.IGNORECASE)

    def _update_simple_statistics(self,e):
        dt = e.get_datetime()
        ym = dt[:6]
        ymd = dt[:8]
        ymdh = dt[:-4]
        hms = dt[-6:]
        hm = dt[-6:-3] + '0' # by 10 minutes step
        self.acc_event_per_ym[ym] += 1
        self.acc_event_per_ymd[ymd] += 1
        self.acc_event_per_ymdh[ymdh] += 1
        self.acc_event_per_hm[hm] += 1
        self.acc_hms_per_ymd[ymd].add(hms)

    def _update_text_statistics(self,e):
        content = e.get_text()
        text = RE_URL.sub('',content)
        # extract words
        words = RE_WORDS.findall(text.lower())
        if len(words) > 0:
            self.acc_words_per_event.append(len(words))
        for w in words:
            if len(w) > 3 and w not in STOP:
                self.acc_words[w] += 1
        # extract url
        for url in RE_URL.findall(content):
            site = extract_site(url)
            if site is not None:
                self.acc_dns[site] += 1
        # extract hashtag
        for hashtag in RE_HASHTAG.findall(content):
            self.acc_hashtags[hashtag] += 1

    def _update_general_statistics(self,e):
        s = self.statistic
        content = e.get_text()
        # update aliases
        alias = self.re_alias.search(content)
        if alias is not None:
            s["aliases"].append((alias.group(0),e.sender))
        # update reference
        reference = self.re_reference.search(content)
        if reference is not None:
            s["sum_reference"] += 1

    def update(self,event):
        self._update_general_statistics(event)
        if event.sender == self.participant.uid:
            self._update_simple_statistics(event)
            self._update_text_statistics(event)

    def _finalize_simple_statistics(self):
        s = self.statistic
        s["sum_events"] = sum(self.acc_event_per_ym.itervalues())
        s["sum_links"] = sum(self.acc_dns.itervalues())
        s["sum_words"] = sum(self.acc_words.itervalues())
        s["sum_uniq_words"] = len(self.acc_words)
        s["main_words"] = self.acc_words.most_common(20)
        s["main_site"] = self.acc_dns.most_common(10)
        s["hashtags"] = self.acc_hashtags.most_common(50)
        s["longest_word"] = reduce(lambda x,y:x if len(x) > len(y) else y,self.acc_words.iterkeys())
        s["longest_event"] = None
        s["avg_words_event"] = mean(self.acc_words_per_event)
        s["avg_day_events"] = mean(self.acc_event_per_ymd.itervalues())
        s["avg_day_links"] = None
        s["sum_days_with_event"] = len(self.acc_event_per_ymd)
        s["max_day_events"] = max(self.acc_event_per_ymd.itervalues())
        s["max_hour_events"] = max(self.acc_event_per_ymdh.itervalues())
        s["sparkline_avg_events_vs_time"] = [ self.acc_event_per_hm[k] for k in iter_minutes('0000','2359',10) ]
        s["max_time_event"] = max(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))
        s["min_time_event"] = min(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))
        s["avg_max_time_event"] = median_low(sorted([max(l) for l in self.acc_hms_per_ymd.itervalues()]))
        s["avg_min_time_event"] = median_low(sorted([min(l) for l in self.acc_hms_per_ymd.itervalues()]))

    def _finalize_general_statistics(self,g):
        s = self.statistic
        gs = g.statistic
        # update sparkline with global scale
        s["sparkline_sum_events_vs_month"] = [ self.acc_event_per_ym[str(k)] for k in iter_months(gs["min_ym"],gs["max_ym"]) ]
        s["sparkline_sum_events_vs_day"] = [ self.acc_event_per_ymd[k] for k in iter_days(gs["min_ymd"],gs["max_ymd"]) ]
        # transform participant reference uid to full name
        s["aliases"] = [ (alias,gs["participants"][p_id]) for alias,p_id in s["aliases"] ]

    def finalize(self,generalstatistic):
        # TODO : deal with "spy" users
        if len(self.acc_event_per_ym) == 0:
            return
        self._finalize_simple_statistics()
        self._finalize_general_statistics(generalstatistic)


class GeneralStatistic:

    _metrics = [
        "max_ym",
        "min_ym",
        "max_ymd",
        "min_ymd",
        "sum_events",
        "participants"
    ]

    def __init__(self):
        self.statistic = dict.fromkeys(self._metrics)
        self.statistic["participants"] = {}
        self.acc_event_per_ym = Counter()
        self.acc_event_per_ymd = Counter()

    def add_participant(self,p):
        self.statistic["participants"][p.uid] = p.name

    def update(self,event):
        dt = event.get_datetime()
        ym = dt[:6]
        ymd = dt[:8]
        self.acc_event_per_ym[ym] += 1
        self.acc_event_per_ymd[ymd] += 1

    def finalize(self):
        s = self.statistic
        s["max_ym"] = max(self.acc_event_per_ym.iterkeys())
        s["min_ym"] = min(self.acc_event_per_ym.iterkeys())
        s["max_ymd"] = max(self.acc_event_per_ymd.iterkeys())
        s["min_ymd"] = min(self.acc_event_per_ymd.iterkeys())
        s["sum_events"] = sum(self.acc_event_per_ym.itervalues())


class HangoutStatisticManager:

    def __init__(self,hangout):
        self.hangout = hangout
        self.conversation_ids = []
        self.general = None
        self.participants = {}

    def _init_statistics_metrics(self):
        self.general = GeneralStatistic()
        for uid in self.conversation_ids:
            c = self.hangout.get_conversation(uid)
            for p in c.iter_participant():
                self.general.add_participant(p)
                if p.uid not in self.participants:
                    self.participants[p.uid] = ParticipantSatistic(p)

    def _scan_hangout(self):
        for uid in self.conversation_ids:
            c = self.hangout.get_conversation(uid)
            for e in c.iter_event():
                # TODO : deal unknow users
                if e.sender not in self.participants:
                    continue
                self.general.update(e)
                for ps in self.participants.itervalues():
                    ps.update(e)

    def _finalize(self):
        self.general.finalize()
        for ps in self.participants.itervalues():
            ps.finalize(self.general)

    def run(self):
        self._init_statistics_metrics()
        self._scan_hangout()
        self._finalize()
        print json.dumps(self.participants["100004041546029582490"].statistic)
        print json.dumps(self.participants["111122836618407997682"].statistic)

    def iter_participant(self):
        for p in self.participants.itervalues():
            yield p.statistic


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
