# local package

from helper import *
import metrics

class ParticipantMetrics(MetricsItem):

    def __init__(self,participant):
        self.participant = p

        # Here is all participant metrics computed
        self._metrics = {
            "uid": None, # user id - initialization
            "name": None, # username - initialization
            # global
            "sum_reference" : Calculus(lambda g_acc_words,name:g_acc_words[name.split(' ')[0].lower()]), # total number of user reference - global words counter
            # TODO
            "aliases": None, # list of alias - apply alias parser on global events
            "quotes": None, # list of quote - apply quote parser on global events
            # incremental
            "sum_events" : Calculus(lambda x:x+1, 0), # total number of events - incremental
            "perc_events" : Calculus(lambda sum_events,g_sum_events:1.0*sum_events/g_sum_events), # % of events over total events
            "sum_url": Calculus(lambda x,urls:x+len(urls),0), # total numbers of links - incremental
            "sum_words": Calculus(lambda words:len(words)), # total number of words - incremental
            # text
            "sum_characters": Calculus(lambda x,content:x+len(content),0), # total number of characters - incremental
            "avg_characters_event": None, # avg number of characters by events
            "sum_uniq_words": Calculus(lambda acc_words:len(acc_words)), # total number of unique words (vocabulary) - set words
            "main_words": Calculus(lambda acc_words:acc_words.most_common(20)), # main words - words counter
            "favorite_words": None, # favorite/specifc words - tfidf score
            "main_site": Calculus(lambda acc_dns:acc_dns.most_common(10)), # main site redirection - incremental site parser and site counter
            "hashtags": Calculus(lambda acc_hashtags:acc_hashtags.most_common(50)), # main hashtag - incremental hashtag parser and hashtag counter
            "sum_hashtags": Calculus(lambda acc_hashtags:len(acc_hashtags)), # hashtag - sum
            "longest_words": Calculus(lambda acc_words:sorted(acc_words.iterkeys(),key=lambda x:len(x),reverse=True)[:10]), # longuest words posted - incremental / set words
            "longest_event": None, # longuest event text posted - incremental / list events
            "avg_words_event": Calculus(lambda acc_words_per_event:mean(acc_words_per_event)), # avg number of words by event - list nb words/event
            "sum_laughs": Calculus(lambda x,text:x+len(RE_LAUGH.findall(text)),0), # total number of laughs
            "sum_coffee": Calculus(lambda x,text:x+len(RE_COFFEE.findall(text)),0), # total number of coffee call
            "sum_chouquette": Calculus(lambda x,text:x+len(RE_CHOUQUETTE.findall(text)),0), # total number of chouquette call
            # events counter
            "sparkline_sum_events_vs_month": Calculus(lambda acc_event_per_ym,min_ym,max_ym:[(k,acc_event_per_ym[str(k)]) for k in iter_months(min_ym,max_ym)]), # sum of event per month - event counter per Ym
            "avg_day_events": Calculus(lambda acc_event_per_ymd:mean(acc_event_per_ymd.itervalues())), # avg number of event by day - event counter per Ymd
            "avg_day_links": None, # avg number of links by day - links counter per Ymd
            "sum_days_with_event": Calculus(lambda acc_event_per_ymd:len(acc_event_per_ymd)), # total days with at least one event - set on Ymd event
            "max_day_events": Calculus(lambda acc_event_per_ymd:max_counter_value(acc_event_per_ymd)), # max event in one day - event counter per Ymd
            "sparkline_sum_events_vs_day": Calculus(lambda acc_event_per_ymd,min_ymd,max_ymd:[(k,acc_event_per_ymd[k]) for k in iter_days(min_ymd,max_ymd)]), # number of event per day - event counter per Ymd
            "max_hour_events": Calculus(lambda acc_event_per_ymdh:max_counter_value(acc_event_per_ymdh)), # max number of events posted in one hour - event counter per YmdH
            "sparkline_sum_events_vs_time": Calculus(lambda acc_event_per_hm:[(k,acc_event_per_hm[k]) for k in iter_minutes('0000','2359',10)]), # sum number of event per time in a day - event counter per YmdHM
            "max_time_event": Calculus(lambda acc_hms_per_ymd:max(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))), # max time event - incremental / default dict listed HMS per Ymd
            "min_time_event": Calculus(lambda acc_hms_per_ymd:min(reduce(lambda x,y:x|y,self.acc_hms_per_ymd.itervalues()))), # min time event - incremental / default dict listed HMS per Ymd
            "avg_max_time_event": Calculus(lambda acc_hms_per_ymd:median_low(sorted((max(l) for l in acc_hms_per_ymd.itervalues())))) ,  # median low time of last daily event - default dict listed HMS per Ymd
            "avg_min_time_event": Calculus(lambda acc_hms_per_ymd:median_low(sorted((min(l) for l in acc_hms_per_ymd.itervalues())))) , # median low time of first daily event - default dict listed HMS per Ymd
            # accumulators
            "acc_event_per_ym" : Calculus(lambda x,ym: x.update([ym]),Counter()),
            "acc_event_per_ymd" : Calculus(lambda x,ymd: x.update([ymd]),Counter()),
            "acc_event_per_ymdh" : Calculus(lambda x,ymdh: x.update([ymdh]),Counter()),
            "acc_event_per_hm" : Calculus(lambda x,hm: x.update([hm]),Counter()),
            "acc_hms_per_ymd" : Calculus(lambda x,ymd,hms: x[ymd].add(hms),defaultdict(set)),
            "acc_dns" : Calculus(lambda x,urls: x.update(ifilter(None,extract_site(url) for url in urls)),Counter()),
            "acc_hashtags" : Calculus(lambda x,text: x.update(RE_HASHTAG.findall(text)),Counter()),
            "acc_words" : Calculus(lambda x,words: x.update(iter_words(words)),Counter()),
            "acc_words_per_event" : Calculus(lambda x,words:x.append(len(words)) if len(words) > 0 else None,[])
        }


class GlobalMetrics(MetricsItem):

    def __init__(self):

        # Here is all global metrics computed
        self._metrics = {
            # statistics
            "max_ym" : Calculus(lambda g_acc_ym:max(g_acc_ym)),
            "min_ym" : Calculus(lambda g_acc_ym:min(g_acc_ym)),
            "max_ymd" : Calculus(lambda g_acc_ymd:max(g_acc_ymd)),
            "min_ymd" : Calculus(lambda g_acc_ymd:min(g_acc_ymd)),
            "g_sum_events" : Calculus(lambda x:x+1,0),
            "g_corpus" : Calculus(lambda x,sender,words: x[sender].add(w),defaultdict(set)),
            "g_best_links" : Calculus(metrics.update_best_links,defaultdict(set),pending_link = None),
            # accumulators
            "g_acc_ym" : Calculus(lambda x,ym: x.add(ym),set()),
            "g_acc_ymd" : Calculus(lambda x,ymd: x.add(ymd),set()),
            "g_acc_words" : Calculus(lambda x,words: x.update(iter_words(words)),Counter())
        }


class ScoreMetrics(MetricsItem):

    def __init__(self):
        self._ranked_metrics = {
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

        # Here is all ranked metrics computed
        self._metrics = {
            "rank" : Calculus(update_ranked_metrics,None,ranked_metrics=self._ranked_metrics)
        }


class StatisticEngine:

    def __init__(self):
        self.participants_metrics = {}
        self.global_metrics = GlobalMetrics()
        self.score_metrics = ScoreMetrics()

    def run(self):
        # collect part
        for e in self._iter_events():
            self._collect_metrics()
        # update part
        self._update_metrics()

    def _collect_metrics(self,event):
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
        # update global incremental statistics
        for key in self.global_metrics.iter_incremental_metrics():
            self.global_metrics.update_metrics[key](values)
        # update users incremental statistics
        for key in p.iter_incremental_metrics():
            p.update_metrics(key,**values)

    def _update_metrics(self):
        # update global final metrics
        for key in self.global_metrics.iter_final_metrics():
            self.global_metrics.update_metrics(key,**values)
        # update participant final metrics
        for p in self.participants.itervalues():
            # extract all possible values
            values = {}
            values.update(p.metrics())
            for key in p.iter_final_metrics():
                p.update_metrics(key,**values)

    def _iter_events(self):
        for c in self.conversations:
            for e in self.hangout.get_conversation(c).iter_event():
                # TODO : deal unknow users
                if e.sender not in self.participants:
                    continue
                yield e
