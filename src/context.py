#####################
# standard import
#####################

import sys
import os
import json
import argparse
import csv
from datetime import datetime

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

class Event:

    def __init__(self):
        self.id = None
        self.sender = None
        self.timestamp = None
        self.text = []

    def set_id(self,id):
        self.id = id

    def set_timestamp(self,timestamp):
        self.timestamp = timestamp

    def set_sender(self,sender):
        self.sender = sender

    def add_text(self,text):
        self.text.append(text)

    def get_id(self):
        return self.id

    def get_sender(self):
        return self.sender

    def get_timestamp(self):
        return self.timestamp

    def get_datetime(self):
        return datetime.fromtimestamp(long(self.timestamp)/10**6).strftime('%Y%m%d%H%M%S')

    def iter_text(self):
        return iter(self.text)

    def get_text(self):
        return ' '.join(self.iter_text())


class Participant:

    def __init__(self):
        self.name = None
        self.id = None

    def set_name(self,name):
        self.name = name

    def set_id(self,id):
        self.id = id

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class Conversation:

    def __init__(self):
        self.id = None
        self.participants = {}
        self.events = []

    def set_id(self,id):
        self.id = id

    def add_participant(self,participant):
        self.participants[participant.get_id()] = participant

    def add_event(self,event):
        self.events.append(event)

    def get_id(self):
        return self.id

    def get_participant(self,id):
        if id in self.participants:
            return self.participants[id]
        else:
            None

    def iter_participant(self):
        return self.participants.itervalues()

    def iter_event(self):
        return iter(self.events)

    def get_sorted_events(self):
        return sorted(self.events,key=lambda item: item.get_timestamp())


class Hangout:

    def __init__(self):
        self.conversations = {}

    def add_conversation(self,conversation):
        self.conversations[conversation.id] = conversation

    def get_conversation(self,conversation_id):
        return self.conversations[conversation_id]

    def iter_conversation(self):
        return self.conversations.itervalues()

    def describe(self):
        print "nb conversation : %d" % len(self.conversations)
        for c_id,c in self.conversations.iteritems():
            c_nb = len(c.participants)
            e_nb = len(c.events)
            print "conversation id %s. %d events, %d participants :" % (c_id,e_nb,c_nb)
            for p in c.iter_participant():
                    print "\t %s %s" % (p.get_id(), p.get_name())


class HangoutStatistic:

    def __init__(self,hangout):
        self.hangout = hangout
        self.user_statistics = {}

    def init_user(self,user_id):
        stats = {}
        # global counter
        stats["total_event"] = 0 # total number of events
        stats["avg_daily_event"] = 0 # avg daily number of events
        stats["total_links"] = 0 # total numbers of links
        stats["avg_daily_links"] = 0 # avg daily numbers of links
        stats["total_words"] = 0 # total number of words
        stats["total_vocabulary"] = 0 # total number of unique words
        stats["total_reference"] = 0 # total number of self reference
        # trends
        stats["main_words"] = {} # main words
        stats["main_site"] = [] # main site redirection
        stats["event_monthly_sparkline"] = {} # number of event per month
        stats["event_daily_sparkline"] = {} # number of event per day
        stats["avg_event_daily_sparkline"] = {} # avg number of event per minute in a day
        # specific
        stats["aliases"] = [] # list of alias
        stats["quotes"] = [] # list of quote
        # records
        stats["longest_word"] = "" # longuest words posted
        stats["longest_post"] = "" # longuest message text posted
        stats["max_frequency_day"] = 0 # max frequency event in one day
        stats["max_frequency_hour"] = 0 # max frequency event posted in one hour
        stats["max_event_hour"] = None
        stats["min_event_hour"] = None
        # initialization
        self.user_statistics[user_id] = stats

    def optimize(self,conversation_id):
        c = self.hangout.get_conversation(conversation_id)
        for p in c.iter_participant():
            self.init_user(p.id)
        for e in c.iter_event():
            stats = self.user_statistics[e.get_sender()]
            stats["total_event"] += 1


class HangoutWriter:

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
