import nltk
import re
from datetime import datetime,date,timedelta

# global variable helper

nltk.data.path.append('/home/pierre/app/nltk_data')
STOP = set(nltk.corpus.stopwords.words("french"))

# regex helpers

RE_URL = re.compile(r'https?://[^ ]*')
RE_SITE = re.compile(r'https?://([^/ ]*)/?')
RE_WORDS = re.compile(r'\w+',re.UNICODE)
RE_HASHTAG = re.compile(r'#\w+')
RE_LAUGH = re.compile(r'g.nial|ahah|haha|mdr|excellent|lol|.norme|xD|:D|\^\^',re.IGNORECASE)
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
    if not dn:
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
