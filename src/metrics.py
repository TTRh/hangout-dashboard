def update_alias(x,event,content,re_alias):
    alias = re_alias.search(content)
    if alias:
        x.append((alias.group(0),event.sender))

def update_words(x,words):
    for w in words:
        if len(w) > 3 and w not in STOP:
            self.acc_words[w] += 1
