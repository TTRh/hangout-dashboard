import json
import csv
from math import log
from collections import namedtuple, OrderedDict
from jinja2 import Environment, FileSystemLoader

# function helpers

def tojson(obj):
    return json.dumps(obj)

def smoothlognorm(n,nmax):
    return log(1+n)/log(nmax)

def dow(n):
    return dict(zip(xrange(0,7),['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']))[n]

# writers

class HangoutStatisticHtmlWriter:

    _template_dir = "template"

    def __init__(self,statistics,user_info_file=None):
        self.statistics = statistics
        self._load_user_info(user_info_file)
        self.env = Environment(loader=FileSystemLoader(self._template_dir))
        self.env.filters['tojson'] = tojson
        self.env.filters['smoothlognorm'] = smoothlognorm
        self.env.filters['dow'] = dow

    def _load_user_info(self,path_file):
        if path_file is not None:
            with open(path_file) as json_file:
                self.users = json.load(json_file)
        else:
            self.users = None

    def _views(self,name):
        return name + ".jinja.html"

    def _get_metrics(self,uid,p):
        result = p.statistics()
        result["aliases"] = [ (alias,self.users[sender]["name"]) for alias,sender in self.statistics.global_metrics.metrics("g_alias")[uid] ]
        result["bestlinks"] = self.statistics.global_metrics.metrics("g_best_links")[uid]
        result["rankings"] = self.statistics.score_metrics.metrics("ranks")[uid]
        result["max_user_dns"] = self.statistics.score_metrics.metrics("max_user_dns")
        result["userinfo"] = self.users[uid]
        return result

    def _write_user(self,output_dir):
        self.template = self.env.get_template(self._views("user/main"))
        for uid,p in self.statistics.participants_metrics.iteritems():
            with open(output_dir + "/" + uid + ".html",'wb') as outfile:
                outfile.write(self.template.render(metrics=self._get_metrics(uid,p)).encode('utf8'))

    def _write_overview(self,output_dir):
        self.template = self.env.get_template(self._views("overview/main"))
        with open(output_dir + "/index.html",'wb') as outfile:
            outfile.write(self.template.render(users=self.users).encode('utf8'))

    def write(self,output_dir):
        self._write_user(output_dir)
        self._write_overview(output_dir)

class HangoutStatisticJsonWriter:

    def __init__(self,statistics):
        self.statistics = statistics

    def write(self,filename):
        with open(filename,'wb') as outfile:
            result = map(lambda x:x[1].metrics,self.statistics.iter_participant_statistics())
            json.dump(result,outfile,indent=4)


class HangoutCsvWriter:

    def __init__(self,hangout):
        self.hangout = hangout

    def write(self,filename):
        with open(filename,'wb') as csv_data:
            writer = csv.writer(csv_data,delimiter=';',quoting=csv.QUOTE_NONNUMERIC)
            for c in self.hangout.iter_conversation():
                for e in c.get_sorted_events():
                    row = []
                    # conversation id
                    row.append(c.uid)
                    # participant
                    name = "UNKWOWN"
                    p = c.get_participant(e.sender)
                    name = p.name if p != None else name
                    row.append(unicode(name).encode('utf8'))
                    # timestamp
                    row.append(long(e.timestamp)/10**6)
                    # text
                    text = ' '.join(e.iter_text())
                    row.append(unicode(text).encode('utf8'))
                    # number words
                    row.append(len(text.split()))
                    writer.writerow(row)
