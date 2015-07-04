import nltk
nltk.data.path.append('/home/pierre/app/nltk_data')
import itertools
import re
from datetime import datetime,date,timedelta
from collections import *
import json

# global variable helper

STOP = set(nltk.corpus.stopwords.words("french"))

# regex helpers

RE_URL = re.compile(r'https?://[^ ]*')
RE_SITE = re.compile(r'https?://([^/ ]*)/?')
RE_WORDS = re.compile(r'\w+')
RE_HASHTAG = re.compile(r'#\w+')
RE_LAUGH = re.compile(r'ahah|haha|mdr|excellent|lol|.norme|xD|:D|\^\^',re.IGNORECASE)
RE_COFFEE = re.compile(r'caf.+',re.IGNORECASE)
RE_CHOUQUETTE = re.compile(r'chouquette',re.IGNORECASE)

# lambda helpers

get_ym = lambda dt: dt[:6]
get_ymd = lambda dt: dt[:8]
get_ymdh = lambda dt: dt[:-4]
get_hms = lambda dt: dt[-6:]
get_hm = lambda dt: dt[-6:-3] + '0' # by 10 minutes step

# function helpers

def pretty_time(stime):
    return stime[:2] + ":" + stime[2:4]

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

def mean(iterable):
    n,total = 0,0
    for v in iterable:
        n+=1
        total += v
    if n == 0:
        return None
    else:
        return float(total)/n

def median_low(lst):
    n = len(lst)
    if n == 0:
        return None
    elif n % 2 == 0:
        return lst[n/2-1]
    else:
        return lst[n/2]

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

def iter_words(text):
    tokens = RE_WORDS.findall(text.lower())
    for w in tokens:
        if len(w) > 3 and w not in STOP:
            yield w

# statistics objects

class ParticipantSatistic:

    _metrics = [
        "uid", # user id - initialization
        "name", # username - initialization
        # global
        "sum_reference", # total number of user reference - global words counter
        "aliases", # list of alias - apply alias parser on global events
        "quotes", # list of quote - apply quote parser on global events
        # incremental
        "sum_events", # total number of events - incremental
        "perc_events" # percentage of events over total events
        "sum_url", # total numbers of links - incremental
        "sum_words", # total number of words - incremental
        # text
        "sum_characters", # total number of characters - incremental
        "avg_characters_event", # avg number of characters by events
        "sum_uniq_words", # total number of unique words (vocabulary) - set words
        "main_words", # main words - words counter
        "main_site", # main site redirection - incremental site parser and site counter
        "hashtags", # main hashtag - incremental hashtag parser and hashtag counter
        "sum_hashtags", # main hashtag - incremental hashtag parser and hashtag counter
        "longest_words", # longuest words posted - incremental / set words
        "longest_event", # longuest event text posted - incremental / list events
        "avg_words_event", # avg number of words by event - list nb words/event
        "sum_laughs", # total number of laughs
        "sum_coffee", # total number of coffee call
        "sum_chouquette", # total number of chouquette call
        # events counter
        "sparkline_sum_events_vs_month", # sum of event per month - event counter per Ym
        "avg_day_events", # avg number of event by day - event counter per Ymd
        "avg_day_links", # avg number of links by day - links counter per Ymd
        "sum_days_with_event", # total days with at least one event - set on Ymd event
        "max_day_events", # max event in one day - event counter per Ymd
        "sparkline_sum_events_vs_day", # number of event per day - event counter per Ymd
        "max_hour_events", # max number of events posted in one hour - event counter per YmdH
        "sparkline_sum_events_vs_time", # sum number of event per time in a day - event counter per YmdHM
        "max_time_event", # max time event - incremental / default dict listed HMS per Ymd
        "min_time_event", # min time event - incremental / default dict listed HMS per Ymd
        "avg_max_time_event",  # median low time of last daily event - default dict listed HMS per Ymd
        "avg_min_time_event", # median low time of first daily event - default dict listed HMS per Ymd
    ]

    def __init__(self,participant):
        self.participant = participant
        s = dict.fromkeys(self._metrics)
        # set user info
        s["uid"] = participant.uid
        s["name"] = participant.name
        # init some metrics
        s["quotes"] = []
        s["aliases"] = []
        s["sum_reference"] = 0
        s["sum_characters"] = 0
        s["sum_laughs"] = 0
        s["sum_coffee"] = 0
        s["sum_chouquette"] = 0
        self.metrics = s
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
        # compile username dependent regex
        name = self.participant.name.split(' ')
        self.re_reference = re.compile(name[0],re.IGNORECASE)
        if len(name) == 2:
            self.re_alias = re.compile(r'' + name[0] + '.*\w+.*' + name[1],re.IGNORECASE)
        else:
            self.re_alias = re.compile(r'' + name[0] + '\w+',re.IGNORECASE)

    def _update_simple_metrics(self,e):
        dt = e.get_datetime()
        self.acc_event_per_ym[get_ym(dt)] += 1
        self.acc_event_per_ymd[get_ymd(dt)] += 1
        self.acc_event_per_ymdh[get_ymdh(dt)] += 1
        self.acc_event_per_hm[get_hm(dt)] += 1
        self.acc_hms_per_ymd[get_ymd(dt)].add(get_hms(dt))

    def _update_text_metrics(self,e):
        content = e.get_text()
        text = RE_URL.sub('',content)
        s = self.metrics
        # number of characters
        s["sum_characters"] += len(content)
        # extract words
        # TODO: use iter words function
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
        for hashtag in RE_HASHTAG.findall(text):
            self.acc_hashtags[hashtag] += 1
        # count specific flag
        s["sum_laughs"] += len(RE_LAUGH.findall(text))
        s["sum_coffee"] += len(RE_COFFEE.findall(text))
        s["sum_chouquette"] += len(RE_CHOUQUETTE.findall(text))

    def _update_global_metrics(self,e):
        s = self.metrics
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
        self._update_global_metrics(event)
        if event.sender == self.participant.uid:
            self._update_simple_metrics(event)
            self._update_text_metrics(event)

    def _finalize_simple_metrics(self):
        s = self.metrics
        s["sum_events"] = sum(self.acc_event_per_ym.itervalues())
        s["sum_url"] = sum(self.acc_dns.itervalues())
        s["avg_characters_event"] = 1.0*s["sum_characters"]/s["sum_events"]
        s["sum_words"] = sum(self.acc_words.itervalues())
        s["sum_words"] = sum(self.acc_words.itervalues())
        s["sum_uniq_words"] = len(self.acc_words)
        s["main_words"] = self.acc_words.most_common(20)
        s["main_site"] = self.acc_dns.most_common(10)
        s["sum_hashtags"] = len(self.acc_hashtags)
        s["hashtags"] = self.acc_hashtags.most_common(50)
        s["longest_words"] = sorted(self.acc_words.iterkeys(),key=lambda x:len(x),reverse=True)[:10]
        s["longest_event"] = None
        s["avg_words_event"] = mean(self.acc_words_per_event)
        s["avg_day_events"] = mean(self.acc_event_per_ymd.itervalues())
        s["avg_day_links"] = None
        s["sum_days_with_event"] = len(self.acc_event_per_ymd)
        s["max_day_events"] = max(self.acc_event_per_ymd.itervalues())
        s["max_hour_events"] = max(self.acc_event_per_ymdh.itervalues())
        s["sparkline_sum_events_vs_time"] = [ (k,self.acc_event_per_hm[k]) for k in iter_minutes('0000','2359',10) ]
        s["max_time_event"] = max(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))
        s["min_time_event"] = min(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))
        s["avg_max_time_event"] = median_low(sorted([max(l) for l in self.acc_hms_per_ymd.itervalues()]))
        s["avg_min_time_event"] = median_low(sorted([min(l) for l in self.acc_hms_per_ymd.itervalues()]))

    def _finalize_global_metrics(self,g):
        s = self.metrics
        gs = g.metrics
        # update global indicators
        s["perc_events"] = 1.0*s["sum_events"]/gs["sum_events"]
        # update sparkline with global scale
        s["sparkline_sum_events_vs_month"] = [ (k,self.acc_event_per_ym[str(k)]) for k in iter_months(gs["min_ym"],gs["max_ym"]) ]
        s["sparkline_sum_events_vs_day"] = [ (k,self.acc_event_per_ymd[k]) for k in iter_days(gs["min_ymd"],gs["max_ymd"]) ]
        # transform participant reference uid to full name
        s["aliases"] = [ (alias,gs["participants"][p_id]) for alias,p_id in s["aliases"] ]

    def finalize(self,globalmetrics):
        # TODO : deal with "spy" users
        if len(self.acc_event_per_ym) == 0:
            return
        self._finalize_simple_metrics()
        self._finalize_global_metrics(globalmetrics)


class GlobalStatistic:

    _metrics = [
        "max_ym",
        "min_ym",
        "max_ymd",
        "min_ymd",
        "sum_events",
        "participants",
        "main_words"
    ]

    _ranked_metrics = {
        "sum_reference": True,
        "sum_events": True,
        "sum_url": True,
        "sum_words": True,
        "sum_uniq_words": True,
        "sum_characters": True,
        "sum_hashtags" : True,
        "sum_laughs": True,
        "sum_coffee": True,
        "sum_chouquette": True,
        "avg_max_time_event": True,
        "avg_min_time_event": False
    }

    def __init__(self):
        self.metrics = dict.fromkeys(self._metrics)
        self.rankings = {}
        self.metrics["participants"] = {}
        self.acc_event_per_ym = Counter()
        self.acc_event_per_ymd = Counter()
        self.acc_words = Counter()

    def add_participant(self,p):
        self.metrics["participants"][p.uid] = p.name
        self.rankings[p.uid] = dict.fromkeys(self._ranked_metrics.keys())

    def update(self,event):
        dt = event.get_datetime()
        self.acc_event_per_ym[get_ym(dt)] += 1
        self.acc_event_per_ymd[get_ymd(dt)] += 1
        # text metrics
        content = event.get_text()
        text = RE_URL.sub('',content)
        for w in iter_words(text):
            self.acc_words[w] += 1

    def finalize(self):
        s = self.metrics
        s["max_ym"] = max(self.acc_event_per_ym.iterkeys())
        s["min_ym"] = min(self.acc_event_per_ym.iterkeys())
        s["max_ymd"] = max(self.acc_event_per_ymd.iterkeys())
        s["min_ymd"] = min(self.acc_event_per_ymd.iterkeys())
        s["sum_events"] = sum(self.acc_event_per_ym.itervalues())
        s["main_words"] = self.acc_words.most_common(20)

    def compute_ranks(self,participants):
        for k,order in self._ranked_metrics.iteritems():
            d = { uid:p.metrics[k] for uid,p in participants.iteritems()}
            rank = OrderedDict(sorted(d.iteritems(),key=lambda t:t[1],reverse=order))
            for uid,p in participants.iteritems():
                self.rankings[uid][k] = rank.keys().index(uid)

class HangoutStatisticManager:

    def __init__(self,hangout):
        self.hangout = hangout
        self.conversation_ids = []
        self.globalstatistics = None
        self.participants = {}

    def _init_statistics_item(self):
        self.globalstatistics = GlobalStatistic()
        for uid in self.conversation_ids:
            c = self.hangout.get_conversation(uid)
            for p in c.iter_participant():
                self.globalstatistics.add_participant(p)
                if p.uid not in self.participants:
                    self.participants[p.uid] = ParticipantSatistic(p)

    def _collect_metrics(self):
        for uid in self.conversation_ids:
            c = self.hangout.get_conversation(uid)
            for e in c.iter_event():
                # TODO : deal unknow users
                if e.sender not in self.participants:
                    continue
                # update accumulators
                self.globalstatistics.update(e)
                for ps in self.participants.itervalues():
                    ps.update(e)

    def _finalize_metrics(self):
        # compute final metrics
        self.globalstatistics.finalize()
        for ps in self.participants.itervalues():
            ps.finalize(self.globalstatistics)
        # remove inactive users
        self.participants = { uid:p for uid,p in self.participants.iteritems() if p.metrics["sum_events"] > 0  }

    def _compute_metrics(self):
        self._collect_metrics()
        self._finalize_metrics()

    def _compute_rankings(self):
        self.globalstatistics.compute_ranks(self.participants)

    def iter_participant(self):
        return self.participants.iteritems()

    def run(self):
        self._init_statistics_item()
        self._compute_metrics()
        self._compute_rankings()
        print json.dumps(self.participants["100004041546029582490"].metrics)
        print json.dumps(self.globalstatistics.rankings["118243095948748495574"])
        # print json.dumps(self.participants["111122836618407997682"].metrics)
