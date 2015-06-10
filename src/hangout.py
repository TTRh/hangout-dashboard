from datetime import datetime


class Participant:

    def __init__(self,uid):
        self.uid = uid
        self.name = None


class Event:

    def __init__(self,uid):
        self.uid = uid
        self.sender = None
        self.timestamp = None
        self.text = []

    def add_text(self,text):
        self.text.append(text)

    def get_datetime(self):
        return datetime.fromtimestamp(long(self.timestamp)/10**6).strftime('%Y%m%d%H%M%S')

    def iter_text(self):
        return iter(self.text)

    def get_text(self):
        return ' '.join(self.iter_text())


class Conversation:

    def __init__(self,uid):
        self.uid = uid
        self.participants = {}
        self.events = []

    def add_participant(self,participant):
        self.participants[participant.uid] = participant

    def add_event(self,event):
        self.events.append(event)

    def get_participant(self,uid):
        if uid in self.participants:
            return self.participants[uid]
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
        self.conversations[conversation.uid] = conversation

    def get_conversation(self,uid):
        return self.conversations[uid]

    def iter_conversation(self):
        return self.conversations.itervalues()

    def describe(self):
        print "nb conversation : %d" % len(self.conversations)
        for c in self.conversations.itervalues():
            print "conversation id %s. %d events, %d participants :" % (c.uid,len(c.events),len(c.participants))
            for p in c.iter_participant():
                    print "\t %s %s" % (p.uid, p.name)
