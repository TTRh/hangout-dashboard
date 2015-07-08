# standard package

import itertools
from collections import *
from math import log
import json

# local package

from helper import *

# statistics objects

class ParticipantSatistic:

    # here is all metrics computed
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
        "favorite_words", # favorite/specifc words - tfidf score
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
        self._init_metrics()
        self._init_accumulators()
        self._init_user_regex()

    def collect_metrics(self,event):
        self._collect_global_metrics(event)
        if event.sender == self.participant.uid:
            self._collect_simple_metrics(event)
            self._collect_text_metrics(event)

    def compute_metrics(self,globalmetrics):
        # TODO : deal with "spy" users
        if len(self.acc_event_per_ym) == 0:
            return
        self._compute_simple_metrics()
        self._compute_global_metrics(globalmetrics)

    def _init_metrics(self):
        self.metrics = dict.fromkeys(self._metrics)
        s = self.metrics
        s["uid"] = self.participant.uid
        s["name"] = self.participant.name
        s["quotes"] = []
        s["aliases"] = []
        s["sum_characters"] = 0
        s["sum_laughs"] = 0
        s["sum_coffee"] = 0
        s["sum_chouquette"] = 0

    def _init_accumulators(self):
        self.acc_event_per_ym = Counter()
        self.acc_event_per_ymd = Counter()
        self.acc_event_per_ymdh = Counter()
        self.acc_event_per_hm = Counter()
        self.acc_hms_per_ymd = defaultdict(set)
        self.acc_dns = Counter()
        self.acc_hashtags = Counter()
        self.acc_words = Counter()
        self.acc_words_per_event = []

    def _init_user_regex(self):
        name = self.participant.name.split(' ')
        # alias regex
        alias_pattern = name[0] + '\w+'
        if len(name) >= 2:
            alias_pattern += '|' + name[0] + '.*\w+.*' + name[-1]
        self.re_alias = re.compile(alias_pattern,re.IGNORECASE)

    def _collect_simple_metrics(self,e):
        dt = e.get_datetime()
        self.acc_event_per_ym[get_ym(dt)] += 1
        self.acc_event_per_ymd[get_ymd(dt)] += 1
        self.acc_event_per_ymdh[get_ymdh(dt)] += 1
        self.acc_event_per_hm[get_hm(dt)] += 1
        self.acc_hms_per_ymd[get_ymd(dt)].add(get_hms(dt))

    def _collect_text_metrics(self,e):
        content = e.get_text()
        text = RE_URL.sub('',content)
        s = self.metrics
        # number of characters
        s["sum_characters"] += len(content)
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
            if site:
                self.acc_dns[site] += 1
        # extract hashtag
        for hashtag in RE_HASHTAG.findall(text):
            self.acc_hashtags[hashtag] += 1
        # count specific flag
        s["sum_laughs"] += len(RE_LAUGH.findall(text))
        s["sum_coffee"] += len(RE_COFFEE.findall(text))
        s["sum_chouquette"] += len(RE_CHOUQUETTE.findall(text))

    def _collect_global_metrics(self,e):
        s = self.metrics
        content = e.get_text()
        # collect aliases
        alias = self.re_alias.search(content)
        if alias:
            s["aliases"].append((alias.group(0),e.sender))

    def _compute_simple_metrics(self):
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
        s["max_day_events"] = self.acc_event_per_ymd.most_common(1)[0][1]
        s["max_hour_events"] = self.acc_event_per_ymdh.most_common(1)[0][1]
        s["sparkline_sum_events_vs_time"] = [ (k,self.acc_event_per_hm[k]) for k in iter_minutes('0000','2359',10) ]
        s["max_time_event"] = max(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))
        s["min_time_event"] = min(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))
        s["avg_max_time_event"] = median_low(sorted((max(l) for l in self.acc_hms_per_ymd.itervalues())))
        s["avg_min_time_event"] = median_low(sorted((min(l) for l in self.acc_hms_per_ymd.itervalues())))

    def _compute_global_metrics(self,g):
        s = self.metrics
        gm = g.metrics
        # collect global indicators
        s["perc_events"] = 1.0*s["sum_events"]/gm["sum_events"]
        # update reference
        s["sum_reference"] = g.acc_words[self.participant.name.split(' ')[0].lower()]
        # update sparkline with global scale
        s["sparkline_sum_events_vs_month"] = [ (k,self.acc_event_per_ym[str(k)]) for k in iter_months(gm["min_ym"],gm["max_ym"]) ]
        s["sparkline_sum_events_vs_day"] = [ (k,self.acc_event_per_ymd[k]) for k in iter_days(gm["min_ymd"],gm["max_ymd"]) ]
        # transform participant reference uid to full name
        s["aliases"] = [ (alias,gm["participants"][p_id]) for alias,p_id in s["aliases"] ]
        # tfidf computation
        self._compute_favorite_words_metrics(g)

    def _compute_favorite_words_metrics(self,g):
        total_users = len(g.acc_corpus)
        total_user_words = len(self.acc_words)
        max_ftd = 1.0*self.acc_words.most_common(1)[0][1]/total_user_words
        ftd = lambda n: 0.5 + (0.5*n/total_user_words)/max_ftd
        idf = lambda w: log(1.0*total_users/reduce(lambda x,y: x + (1 if w in y else 0),g.acc_corpus.itervalues(),0))
        tfidf = OrderedDict(sorted(((w,ftd(n)*idf(w)) for w,n in self.acc_words.iteritems()), key=lambda x:x[1], reverse=True))
        self.metrics["favorite_words"] = tfidf.items()[:30]


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

    # here is all ranked metrics computed
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
        self._init_metrics()
        self._init_accumulators()
        self.rankings = {}
        self.pending_link = None

    def add_participant(self,p):
        self.metrics["participants"][p.uid] = p.name
        self.rankings[p.uid] = dict.fromkeys(self._ranked_metrics.keys())

    def collect_metrics(self,event):
        self._collect_simple_metrics(event)
        self._collect_text_metrics(event)

    def compute_metrics(self):
        s = self.metrics
        s["max_ym"] = max(self.acc_event_per_ym.iterkeys())
        s["min_ym"] = min(self.acc_event_per_ym.iterkeys())
        s["max_ymd"] = max(self.acc_event_per_ymd.iterkeys())
        s["min_ymd"] = min(self.acc_event_per_ymd.iterkeys())
        s["sum_events"] = sum(self.acc_event_per_ym.itervalues())
        s["main_words"] = self.acc_words.most_common(20)

    def compute_ranks(self,participants):
        for k,order in self._ranked_metrics.iteritems():
            rank = OrderedDict(sorted(( (uid,p.metrics[k]) for uid,p in participants.iteritems() ),key=lambda t:t[1],reverse=order))
            for r,uid in enumerate(rank):
                self.rankings[uid][k] = r

    def _init_metrics(self):
        self.metrics = dict.fromkeys(self._metrics)
        self.metrics["participants"] = {}

    def _init_accumulators(self):
        self.acc_event_per_ym = Counter()
        self.acc_event_per_ymd = Counter()
        self.acc_words = Counter()
        self.acc_best_links = defaultdict(set)
        self.acc_corpus = defaultdict(set)

    def _collect_text_metrics(self,event):
        content = event.get_text()
        text = RE_URL.sub('',content)
        # update words counter
        for w in iter_words(text):
            self.acc_words[w] += 1
            self.acc_corpus[event.sender].add(w)
        # udpate best link accumulator :
        # check if someone laugh and there is a pending recent link
        if RE_LAUGH.search(text) and self.pending_link:
            # add link to user's best link list
            self.acc_best_links[self.pending_link[0]].add(self.pending_link[1])
        # update pending link with last link in event
        urls = RE_URL.findall(content)
        if len(urls) > 0:
            # pending_link = [ user, url, remaining active time ]
            self.pending_link = [event.sender,urls[-1],4]
        # update persistance of pending url
        if self.pending_link:
            if self.pending_link[2] > 0:
                self.pending_link[2] -= 1
            # flush pending url
            else:
                self.pending_link = None

    def _collect_simple_metrics(self,event):
        dt = event.get_datetime()
        self.acc_event_per_ym[get_ym(dt)] += 1
        self.acc_event_per_ymd[get_ymd(dt)] += 1


class HangoutStatisticManager:

    def __init__(self,hangout):
        self.hangout = hangout
        self.conversation_ids = []
        self.globalstatistics = None
        self.participants = {}

    def run(self):
        self._init_statistics_item()
        self._update_metrics()
        self._update_rankings()
        print json.dumps(self.participants["100004041546029582490"].metrics)
        print json.dumps(self.globalstatistics.rankings["118243095948748495574"])

    def iter_participant(self):
        return self.participants.iteritems()

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
                self.globalstatistics.collect_metrics(e)
                for ps in self.participants.itervalues():
                    ps.collect_metrics(e)

    def _compute_metrics(self):
        # compute final metrics
        self.globalstatistics.compute_metrics()
        for ps in self.participants.itervalues():
            ps.compute_metrics(self.globalstatistics)
        # remove inactive users
        self.participants = { uid:p for uid,p in self.participants.iteritems() if p.metrics["sum_events"] > 0  }

    def _update_metrics(self):
        self._collect_metrics()
        self._compute_metrics()

    def _update_rankings(self):
        self.globalstatistics.compute_ranks(self.participants)
