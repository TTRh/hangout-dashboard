import json
import csv
from collections import namedtuple, OrderedDict
from jinja2 import Environment, FileSystemLoader

# function helpers

def tojson(obj):
  return json.dumps(obj)

# writers

class HangoutStatisticHtmlWriter:

    _template_dir = "template"

    def __init__(self,statistics,user_info_file=None):
        self.statistics = statistics
        self._load_user_info(user_info_file)
        self.env = Environment(loader=FileSystemLoader(self._template_dir))
        self.env.filters['tojson'] = tojson

    def _load_user_info(self,path_file):
        if path_file is not None:
            with open(path_file) as json_file:
                self.users = json.load(json_file)
        else:
            self.users = None

    def _views(self,name):
        return name + ".jinja.html"

    def _write_user(self,output_dir):
        self.template = self.env.get_template(self._views("user/main"))
        for uid,user in self.statistics.iter_participant():
            global_metrics = {
                "rankings" : self.statistics.globalstatistics.rankings[uid],
                "bestlinks": self.statistics.globalstatistics.acc_best_links[uid],
                "userinfo": self.users[uid]
            }
            with open(output_dir + "/" + uid + ".html",'wb') as outfile:
                outfile.write(self.template.render(umetrics=user.metrics,gmetrics=global_metrics).encode('utf8'))

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
            result = map(lambda x:x[1].metrics,self.statistics.iter_participant())
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

if __name__ == '__main__':

    env = Environment(loader=FileSystemLoader("template"))
    template = env.get_template("test.html")
    print template.render(foo="Arnaud Canu")
