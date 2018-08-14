import json

import requests


class Telegrammer:
    def __init__(self, token, chat_id, heartbeat_id):
        self.message_url = "https://api.telegram.org/bot{}/".format(token)
        self.chat = chat_id
        self.heartbeat = heartbeat_id

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self):
        url = self.message_url + "getUpdates"
        js = self.get_json_from_url(url)
        return js

    def get_last_chat_id_and_text(self, updates):
        text = updates["result"][-1]["message"]["text"]
        chat_id = updates["result"][-1]["message"]["chat"]["id"]
        return (text, chat_id)

    def send_message(self, text, chat_id, parse_mode=None):
        url = self.message_url + \
            "sendMessage?text={}&chat_id={}".format(text, chat_id)
        if parse_mode:
            url += f'&parse_mode={parse_mode}'
        response = self.get_url(url)

    def send_text(self, body, formatted=False):
        if formatted:
            self.send_message(body, self.chat, parse_mode='markdown')
        else:
            self.send_message(body, self.chat)
        print(body)

    def send_heartbeat(self, body):
        self.send_message(body, self.heartbeat)

    def send_image(self, photo):
        # myfile = {"file": ("photo", photo)}
        data = {'chat_id': self.chat}
        files = {'photo': photo}
        response = requests.post(url=self.message_url + 'sendPhoto', data=data, files=files)