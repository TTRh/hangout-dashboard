import json
import csv
from collections import namedtuple, OrderedDict
from jinja2 import Environment, FileSystemLoader


class HangoutStatisticHtmlWriter:

    _template_dir = "template"
    _summary = OrderedDict([
        ("sum_events" , "total number of events"),
        ("avg_day_events" , "avg number of event per day"),
        ("max_day_events" , "max event in one day"),
        ("sum_url", "total number of urls"),
        ("sum_words" , "total number of words"),
        ("sum_uniq_words" , "total unique words"),
        ("avg_min_time_event" , "avg first time event"),
        ("avg_max_time_event" , "avg last time event"),
        ("sum_reference" , "total number of name referenced")
    ])
    _descriptor = namedtuple('descriptor','summary')

    def __init__(self,statistics):
        self.statistics = statistics
        self.env = Environment(loader=FileSystemLoader(self._template_dir))

    def _views(self,name):
        return name + ".jinja.html"

    def _write_user(self,output_dir):
        descriptor = self._descriptor(self._summary)
        self.template = self.env.get_template(self._views("user/main"))
        # for user in self.statistics.iter_participant():
        user = self.statistics.participants["100004041546029582490"].statistic
        with open(output_dir + "/" + user["uid"] + ".html",'wb') as outfile:
            outfile.write(self.template.render(user=user,descriptor=descriptor))

    def _write_overview(self,output_dir):
        self.template = self.env.get_template(self._views("overview/main"))
        with open(output_dir + "/index.html",'wb') as outfile:
            outfile.write(self.template.render(overview=None))

    def write(self,output_dir):
        self._write_user(output_dir)
        # self._write_overview(output_dir)


class HangoutStatisticJsonWriter:

    def __init__(self,statistics):
        self.statistics = statistics

    def write(self,filename):
        with open(filename,'wb') as outfile:
            result = map(None,self.statistics.iter_participant())
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
