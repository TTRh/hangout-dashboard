import json
from hangout import *


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
