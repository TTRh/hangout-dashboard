#####################
# standard import
#####################
import json
import csv
from jinja2 import Environment, FileSystemLoader

#####################
# writers
#####################

class HangoutStatisticHtmlWriter:

    def __init__(self,statistics,template_file):
        self.statistics = statistics
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template_file = template_file

    def write(self):
        self.template = self.env.get_template(self.template_file)
        print self.template.render(foo="Hello World !")


class HangoutStatisticJsonWriter:

    def __init__(self,statistics,filename):
        self.statistics = statistics
        self.filename = filename

    def write(self):
        with open(self.filename,'wb') as outfile:
            result = map(None,self.statistics.iter_participant())
            json.dump(result,outfile,indent=4)


class HangoutCsvWriter:

    def __init__(self,hangout,filename):
        self.hangout = hangout
        self.filename = filename

    def write(self):
        with open(self.filename,'wb') as csv_data:
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
