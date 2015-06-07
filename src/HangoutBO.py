#####################
# standard import
#####################

from datetime import datetime

#####################
# hangout objects
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

