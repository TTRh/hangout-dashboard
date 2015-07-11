# standard package

import inspect
import itertools
from collections import *
from math import log
import json

# local package

from helper import *
import metrics

# statistics objects

class MetricsReducer:

    def __init__(self,func_reducer = lambda x:x+1,initializer=None):
        self.func_reducer = func_reducer
        self.result = initializer
        self.args = inspect.getargspec(self.func_reducer).args[1:]

    def update(self, **kwargs):
        args = { k:kwargs[k] for k in self.args }
        result = self.func_reducer(self.result, **args)
        if result:
            self.result = result

class ParticipantSatistic:

    # here is all metrics computed
    _metrics = {
        "uid": None, # user id - initialization
        "name": None, # username - initialization
        # global
        "sum_reference" : None, # total number of user reference - global words counter
        # TODO: do not use this function on user scope, use global scope
        "aliases": CollectorReducer(metrics.udpate_alias,[]), # list of alias - apply alias parser on global events
        "quotes": None, # list of quote - apply quote parser on global events
        # incremental
        "sum_events" : CollectorReducer(None, 0), # total number of events - incremental
        "perc_events" # percentage of events over total events
        "sum_url": None, # total numbers of links - incremental
        "sum_words": None, # total number of words - incremental
        # text
        "sum_characters": CollectorReducer(lambda x,content:x+len(content),0), # total number of characters - incremental
        "avg_characters_event": None, # avg number of characters by events
        "sum_uniq_words": None, # total number of unique words (vocabulary) - set words
        "main_words": None, # main words - words counter
        "favorite_words": None, # favorite/specifc words - tfidf score
        "main_site": None, # main site redirection - incremental site parser and site counter
        "hashtags": None, # main hashtag - incremental hashtag parser and hashtag counter
        "sum_hashtags": None, # main hashtag - incremental hashtag parser and hashtag counter
        "longest_words": None, # longuest words posted - incremental / set words
        "longest_event": None, # longuest event text posted - incremental / list events
        "avg_words_event": None, # avg number of words by event - list nb words/event
        "sum_laughs": CollectorReducer(lambda x,text:x+len(RE_LAUGH.findall(text)),0), # total number of laughs
        "sum_coffee": CollectorReducer(lambda x,text:x+len(RE_COFFEE.findall(text)),0), # total number of coffee call
        "sum_chouquette": CollectorReducer(lambda x,text:x+len(RE_CHOUQUETTE.findall(text)),0), # total number of chouquette call
        # events counter
        "sparkline_sum_events_vs_month": None, # sum of event per month - event counter per Ym
        "avg_day_events": None, # avg number of event by day - event counter per Ymd
        "avg_day_links": None, # avg number of links by day - links counter per Ymd
        "sum_days_with_event": None, # total days with at least one event - set on Ymd event
        "max_day_events": None, # max event in one day - event counter per Ymd
        "sparkline_sum_events_vs_day": None, # number of event per day - event counter per Ymd
        "max_hour_events": None, # max number of events posted in one hour - event counter per YmdH
        "sparkline_sum_events_vs_time": None, # sum number of event per time in a day - event counter per YmdHM
        "max_time_event": None, # max time event - incremental / default dict listed HMS per Ymd
        "min_time_event": None, # min time event - incremental / default dict listed HMS per Ymd
        "avg_max_time_event": None,  # median low time of last daily event - default dict listed HMS per Ymd
        "avg_min_time_event": None, # median low time of first daily event - default dict listed HMS per Ymd
    }

    _accumulators = {
        "event_per_ym" : CollectorReducer(lambda x,ym: x.update([ym]),Counter()),
        "event_per_ymd" : CollectorReducer(lambda x,ymd: x.update([ymd]),Counter()),
        "event_per_ymdh" : CollectorReducer(lambda x,ymdh: x.update([ymdh]),Counter()),
        "event_per_hm" : CollectorReducer(lambda x,hm: x.update([hm]),Counter()),
        "hms_per_ymd" : CollectorReducer(lambda x,ymd,hms: x[ymd].add(hms),defaultdict(set)),
        "dns" : CollectorReducer(None,Counter()),
        "hashtags" : CollectorReducer(None,Counter()),
        "words" : CollectorReducer(None,Counter()),
        "words_per_event" : CollectorReducer(lambda x,words:x.append(len(words)) if len(words) > 0 else None,[])
    }

    def __init__(self,p):
        self.participant = p
        self.metrics = dict.fromkeys(self._metrics)

    def update_simple_metrics(self,metrics,**kwargs):
        self.metrics[metrics] = self._metrics[metrics].udpate(**kwargs)  


class StatisticEngine:

    def __init__(self):
        self.participants = {}

    def collect(event):
        p = self.participants[event.sender]
        dt = event.get_datetime()
        content = event.get_text()
        text = RE_URL.sub('',event.get_text())
        # extract all possible common values
        values = {
            "event" : event,
            "sender" : event.sender,
            "datetime" : dt,
            "ym" : get_ym(dt),
            "ymd" : get_ymd(dt),
            "ymdh" : get_ymdh(dt),
            "hm" : get_hm(dt),
            "hms" : get_hms(dt),
            "content" : content,
            "text" : text,
            "words" : RE_WORDS.findall(text.lower())
        }
        # update users simple metrics
        for key,reducer in p._metrics.iteritems():
          if reducer:
              p.metrics[key] = reducer.update(**values)
        # update users simple collectors
        for key,accumulator in p._accumulators.iteritems():
            if accumulator:
                p.accumulators[key](values)

