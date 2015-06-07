#####################
# standard import
#####################
from jinja2 import Environment, FileSystemLoader

class HangoutStatisticHtmlWriter:

    def __init__(self,hangoutstatistic,template_file):
        self.hangoutstatistic = hangoutstatistic
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template_file = template_file

    def write(self):
        self.template = self.env.get_template(self.template_file)
        print self.template.render(foo="Hello World !")

if __name__ == '__main__':

    test = HangoutStatisticHtmlWriter(None,"test.html")
    test.write()
