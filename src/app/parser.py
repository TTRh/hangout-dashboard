import json
from hangout import *


class HangoutReader:

    def __init__(self,jsonfile,hangout,user_info_file=None):
        self.jsonfile = jsonfile
        self.hangout = hangout
        self.users = {}
        if user_info_file:
            with open(user_info_file) as json_file:
                self.users = json.load(json_file)

    def read(self):
        with open(self.jsonfile,'rb') as json_data:
            data = json.load(json_data)
            for conversation in data['conversation_state']:
                self._extract_conversation_data(conversation)
        self._consolidate_participant()

    def _extract_conversation_data(self,conversation):
        c = Conversation(conversation['conversation_id']['id'])
        # set conversation participant
        for item in conversation['conversation_state']['conversation']['participant_data']:
            p = Participant(item['id']['gaia_id'])
            try:
                p.name = item['fallback_name']
            except KeyError:
                pass
            c.add_participant(p)
        # set conversation event
        for item in conversation['conversation_state']['event']:
            e = Event(item['event_id'])
            e.sender = item['sender_id']['gaia_id']
            # consolidation : add unknow user to participant list
            if e.sender not in c.participants:
                p = Participant(e.sender)
                c.add_participant(p)
            e.timestamp = item['timestamp']
            # get text
            try:
                for content in item['chat_message']['message_content']['segment']:
                    e.add_text(content['text'])
            except KeyError:
                pass
            # get images
            try:
                for content in item['chat_message']['message_content']['attachment']:
                    e.add_text(content['embed_item']['embeds.PlusPhoto.plus_photo']['url'])
            except KeyError:
                pass
            c.add_event(e)
        # finally add conversation to context
        self.hangout.add_conversation(c)

    def _consolidate_participant(self):
        for c in self.hangout.iter_conversation():
            for p in c.iter_participant():
                if p.uid in self.users:
                    p.name = self.users[p.uid]["name"]
