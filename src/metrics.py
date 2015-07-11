def update_alias(self,event,content,re_alias):
    alias = re_alias.search(content)
    if alias:
        self.append((alias.group(0),event.sender))

def compute_sparkline_sum_events_vs_month(acc_event_per_ym,min_ym,max_ym):
    return [(k,acc_event_per_ym[str(k)]) for k in iter_months(min_ym,max_ym)]

def update_best_links(self,sender,text,urls,pending_link):
    if RE_LAUGH.search(text) and pending_link:
        # add link to user's best link list
        self[pending_link[0]].add(pending_link[1])
    # update pending link with last link in event
    if len(urls) > 0:
        # pending_link = [ user, url, remaining active time ]
        pending_link = [sender,urls[-1],4]
    # update persistance of pending url
    if pending_link:
        if pending_link[2] > 0:
            pending_link[2] -= 1
        # flush pending url
        else:
            pending_link = None


def update_ranked_metrics(participants,ranked_metrics):
    result = { uid : {} for uid in participants.iterkeys() }
    for k,order in ranked_metrics.iteritems():
        rank = OrderedDict(sorted(( (uid,p.metrics[k]) for uid,p in participants.iteritems() ),key=lambda t:t[1],reverse=order))
        for r,uid in enumerate(rank):
            result[uid][k] = r
    return result
