# local package

from helper import *
import metrics

class ParticipantMetrics(MetricsItem):

    def __init__(self,participant):
        self.participant = participant

        # Here is all participants statistics
        self._statistics = {
            # global
            "sum_reference" : Calculus(lambda g_acc_words,name:g_acc_words[name.split(' ')[0].lower()]), # total number of user reference - global words counter
            "quotes": None, # list of quote - apply quote parser on global events
            # incremental
            "sum_events" : Calculus(lambda x:x+1, 0), # total number of events - incremental
            "perc_events" : Calculus(lambda sum_events,g_sum_events:1.0*sum_events/g_sum_events), # % of events over total events
            "sum_url": Calculus(lambda x,urls:x+len(urls),0), # total numbers of links - incremental
            "sum_words": Calculus(lambda x,words:x+len(words),0), # total number of words - incremental
            # text
            "sum_characters": Calculus(lambda x,content:x+len(content),0), # total number of characters - incremental
            "avg_characters_event": None, # avg number of characters by events
            "sum_uniq_words": Calculus(lambda acc_words:len(acc_words)), # total number of unique words (vocabulary) - set words
            "main_words": Calculus(lambda acc_words:acc_words.most_common(20)), # main words - words counter
            "favorite_words": Calculus(metrics.update_favorite_words), # favorite/specifc words - tfidf score
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
            "max_time_event": Calculus(lambda acc_hms_per_ymd:max(reduce(lambda x,y:x|y,acc_hms_per_ymd.itervalues()))), # max time event - incremental / default dict listed HMS per Ymd
            "min_time_event": Calculus(lambda acc_hms_per_ymd:min(reduce(lambda x,y:x|y,acc_hms_per_ymd.itervalues()))), # min time event - incremental / default dict listed HMS per Ymd
            "avg_max_time_event": Calculus(lambda acc_hms_per_ymd:median_low(sorted((max(l) for l in acc_hms_per_ymd.itervalues())))) ,  # median low time of last daily event - default dict listed HMS per Ymd
            "avg_min_time_event": Calculus(lambda acc_hms_per_ymd:median_low(sorted((min(l) for l in acc_hms_per_ymd.itervalues())))) , # median low time of first daily event - default dict listed HMS per Ymd
        }

        self._accumulators = {
            "acc_event_per_ym" : Calculus(lambda x,ym: x.update([ym]),Counter()),
            "acc_event_per_ymd" : Calculus(lambda x,ymd: x.update([ymd]),Counter()),
            "acc_event_per_ymdh" : Calculus(lambda x,ymdh: x.update([ymdh]),Counter()),
            "acc_event_per_hm" : Calculus(lambda x,hm: x.update([hm]),Counter()),
            "acc_hms_per_ymd" : Calculus(lambda x,ymd,hms: x[ymd].add(hms),defaultdict(set)),
            "acc_dns" : Calculus(lambda x,urls: x.update(ifilter(None,(extract_site(url) for url in urls))),Counter()),
            "acc_hashtags" : Calculus(lambda x,text: x.update(RE_HASHTAG.findall(text)),Counter()),
            "acc_words" : Calculus(lambda x,words: x.update(iter_words(words)),Counter()),
            "acc_words_per_event" : Calculus(lambda x,words:x.append(len(words)) if len(words) > 0 else None,[])
        }

        self._metrics = {}
        self._metrics.update(self._statistics)
        self._metrics.update(self._accumulators)

    def statistics(self):
        return { key:self.metrics(key) for key in self._statistics.iterkeys() }

class GlobalMetrics(MetricsItem):

    def __init__(self):

        self.re_participant_aliases = {}

        # Here is all global metrics computed
        self._metrics = {
            "max_ym" : Calculus(lambda g_acc_ym:max(g_acc_ym)),
            "min_ym" : Calculus(lambda g_acc_ym:min(g_acc_ym)),
            "max_ymd" : Calculus(lambda g_acc_ymd:max(g_acc_ymd)),
            "min_ymd" : Calculus(lambda g_acc_ymd:min(g_acc_ymd)),
            "g_alias" : Calculus(metrics.update_alias,defaultdict(set),re_aliases = self.re_participant_aliases),
            "g_sum_events" : Calculus(lambda x:x+1,0),
            "g_corpus" : Calculus(lambda x,sender,words: x[sender].update(iter_words(words)),defaultdict(set)),
            "g_best_links" : Calculus(metrics.update_best_links,defaultdict(set),pending_link = None),
            "g_acc_ym" : Calculus(lambda x,ym: x.add(ym),set()),
            "g_acc_ymd" : Calculus(lambda x,ymd: x.add(ymd),set()),
            "g_acc_words" : Calculus(lambda x,words: x.update(iter_words(words)),Counter())
        }

    def add_participant(self,p):
        self._add_participant_alias_re(p)

    def _add_participant_alias_re(self,p):
        name = p.name.split(' ')
        # alias regex
        alias_pattern = name[0] + '\w+'
        if len(name) >= 2:
            alias_pattern += '|' + name[0] + '.*\w+.*' + name[-1]
        self.re_participant_aliases[p.uid] = re.compile(alias_pattern,re.UNICODE|re.IGNORECASE)

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
            "ranks" : Calculus(metrics.update_ranked,None,ranked_metrics=self._ranked_metrics),
            "max_user_dns" : Calculus(lambda participants: max(max_counter_value(p.metrics("acc_dns")) if len(p.metrics("acc_dns")) > 0 else 0 for p in participants.itervalues()))
        }


class HangoutStatisticEngine:

    def __init__(self,hangout):
        self.hangout = hangout
        self.conversations = []
        # init metrics
        self.participants_metrics = {}
        self.global_metrics = GlobalMetrics()
        self.score_metrics = ScoreMetrics()

    def _init_metrics_items(self):
        for c in self.conversations:
            for p in self.hangout.get_conversation(c).iter_participant():
                self.global_metrics.add_participant(p)
                if p.uid not in self.participants_metrics:
                    self.participants_metrics[p.uid] = ParticipantMetrics(p)

    def run(self):
        # init metrics
        self._init_metrics_items()
        # collect part
        for c in self.conversations:
            for e in self.hangout.get_conversation(c).iter_events():
                # TODO : deal unknow users
                if e.sender not in self.participants_metrics:
                    continue
                self._collect_metrics(e)
        # update part
        self._remove_inactive_users()
        self._update_metrics()
        print self.participants_metrics["100004041546029582490"].statistics()
        print self.global_metrics.metrics("g_alias")
        print self.global_metrics.metrics("g_best_links")

    def _collect_metrics(self,event):
        p = self.participants_metrics[event.sender]
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
            "words" : RE_WORDS.findall(text.lower()),
            "urls" : RE_URL.findall(content)
        }
        # update global incremental statistics
        for key,calculus in self.global_metrics.iter_incremental_metrics():
            calculus.update(**values)
        # update users incremental statistics
        for key,calculus in p.iter_incremental_metrics():
            calculus.update(**values)

    def _remove_inactive_users(self):
      self.participants_metrics = { uid:p for uid,p in self.participants_metrics.iteritems() if p.metrics("sum_events") > 0 }

    def _update_metrics(self):
        values = self.global_metrics.metrics()
        # update global final metrics
        for key,calculus in self.global_metrics.iter_final_metrics():
            calculus.update(**values)
        values.update(self.global_metrics.metrics())
        # update participant final metrics
        for p in self.participants_metrics.itervalues():
            values["name"] = p.participant.name
            values.update(p.metrics())
            for key,calculus in p.iter_final_metrics():
                calculus.update(**values)
        # update score metrics
        values = { "participants" : self.participants_metrics }
        for key,calculus in self.score_metrics.iter_final_metrics():
            calculus.update(**values)
