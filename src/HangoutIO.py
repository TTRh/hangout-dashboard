#####################
# standard import
#####################

import json
import csv

from HangoutBO import *

#####################
# function helper
#####################

def try2get(atr,obj):
    try:
        result = obj[atr]
    except KeyError:
        result = None
    return result

#####################
# object helper
#####################

class HangoutReader:

    def __init__(self,jsonfile,hangout):
        self.jsonfile = jsonfile
        self.hangout = hangout

    def read(self):
        with open(self.jsonfile,'rb') as json_data:
            data = json.load(json_data)
            for conversation in data['conversation_state']:
                self.extract_conversation_data(conversation)

    def extract_conversation_data(self,conversation):
        # create new conversation
        c = Conversation()
        # set general param
        c.set_id(conversation['conversation_id']['id'])
        # set conversation participant
        for item in conversation['conversation_state']['conversation']['participant_data']:
            p = Participant()
            p.set_name(try2get('fallback_name',item))
            p.set_id(item['id']['gaia_id'])
            c.add_participant(p)
        # set conversation event
        for item in conversation['conversation_state']['event']:
            e = Event()
            e.set_id(item['event_id'])
            e.set_sender(item['sender_id']['gaia_id'])
            e.set_timestamp(item['timestamp'])
            # set text
            try:
                for content in item['chat_message']['message_content']['segment']:
                    e.add_text(content['text'])
            except KeyError:
                pass
            # get image
            try:
                for content in item['chat_message']['message_content']['attachment']:
                    e.add_text(content['embed_item']['embeds.PlusPhoto.plus_photo']['url'])
            except KeyError:
                pass
            c.add_event(e)
        # finally add conversation to context
        self.hangout.add_conversation(c)


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
                    row.append(c.get_id())
                    # participant
                    name = "UNKWOWN"
                    p = c.get_participant(e.get_sender())
                    name = p.get_name() if p != None else name
                    row.append(unicode(name).encode('utf8'))
                    # timestamp
                    row.append(long(e.get_timestamp())/10**6)
                    # text
                    text = ' '.join(e.iter_text())
                    row.append(unicode(text).encode('utf8'))
                    # number words
                    row.append(len(text.split()))
                    writer.writerow(row)
