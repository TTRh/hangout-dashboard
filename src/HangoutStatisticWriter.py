#####################
# standard import
#####################
import json
from jinja2 import Environment, FileSystemLoader

#####################
# writers
#####################
class HangoutStatisticHtmlWriter:

    def __init__(self,hg_stats,template_file):
        self.hg_stats = hg_stats
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template_file = template_file

    def write(self):
        self.template = self.env.get_template(self.template_file)
        print self.template.render(foo="Hello World !")

class HangoutStatisticJsonWriter:

    def __init__(self,hg_stats,filename):
        self.hg_stats = hg_stats
        self.filename = filename

    def write(self):
        with open(self.filename,'wb') as outfile:
            result = map(None,self.hg_stats.user_statistics.itervalues())
            json.dump(result,outfile,indent=4)

if __name__ == '__main__':

    test = HangoutStatisticHtmlWriter(None,"test.html")
    test.write()
