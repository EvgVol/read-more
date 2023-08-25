import json

from datetime import datetime
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        # принять соединение
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        now = datetime.now()
        time_stamp = now.strftime("%H:%M")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # отправить сообщение в WebSocket
        self.send(text_data=json.dumps({'message': message,
                                        'time_stamp': time_stamp,}))
