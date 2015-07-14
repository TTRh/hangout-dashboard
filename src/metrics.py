from math import log

from helper import *

class PendingLink:

    def __init__(self):
        self.user = None
        self.url = None
        self.duration = None

    def update(self,user,url,duration):
        self.user = user
        self.url = url
        self.duration = duration

    def flush(self):
        self.user = None
        self.url = None
        self.duration = None

def create_alias_re(name):
    fullname = name.split(' ')
    # simple alias by first name call
    alias_pattern = fullname[0] + '\w+'
    # alias with first and last name
    if len(fullname) > 1:
        alias_pattern += '|' + fullname[0] + '.*\w+.*' + fullname[-1]
        composite_name = fullname[-1].split('-')
        # alias for composite last name
        if len(composite_name) > 1:
            alias_pattern += '|' + fullname[0] + '.*\w+.*' + composite_name[0]
            alias_pattern += '|' + fullname[0] + '.*\w+.*' + composite_name[-1]
    return re.compile(alias_pattern,re.UNICODE|re.IGNORECASE)


def update_alias(this,sender,content,re_aliases):
    for uid,regex in re_aliases.iteritems():
        alias = regex.search(content)
        if alias:
            this[uid].add((alias.group(0),sender))

def update_best_links(this,sender,text,urls,pending_link):
    if RE_LAUGH.search(text) and pending_link.duration:
        # add link to user's best link list
        this[pending_link.user].add(pending_link.url)
    # update pending link with last link in event
    if len(urls) > 0:
        pending_link.update(sender,urls[-1],4)
    # update persistance of pending url
    if pending_link:
        if pending_link.duration:
            pending_link.duration -= 1
        else:
            pending_link.flush()

def update_ranked(participants,ranked_metrics):
    result = { uid : {} for uid in participants.iterkeys() }
    for k,order in ranked_metrics.iteritems():
        rank = OrderedDict(sorted(( (uid,p.metrics(k)) for uid,p in participants.iteritems() ),key=lambda t:t[1],reverse=order))
        for r,uid in enumerate(rank):
            result[uid][k] = r
    return result

def update_favorite_words(acc_words,g_corpus):
    total_users = len(g_corpus)
    total_user_words = len(acc_words)
    max_ftd = 1.0*max_counter_value(acc_words)/total_user_words
    ftd = lambda n: 0.5 + (0.5*n/total_user_words)/max_ftd
    idf = lambda w: log(1.0*total_users/reduce(lambda x,y: x + (1 if w in y else 0),g_corpus.itervalues(),0))
    tfidf = OrderedDict(sorted(((w,ftd(n)*idf(w)) for w,n in acc_words.iteritems()), key=lambda x:x[1], reverse=True))
    return tfidf.items()[:30]
