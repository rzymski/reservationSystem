# from channels.generic.websocket import WebsocketConsumer
# import json
# from time import sleep
#
# class WSConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#
#         count = 0
#         for i in range(100):
#             if count < 10:
#                 count += 1
#             else:
#                 count = 1
#             self.send(json.dumps({'message': count}))
#             sleep(1)
#     def disconnect(self, code):
#         pass
#
#
# from icecream import ic
#
#
# class ReceiveNotification(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#         ic("Notification")
#
#     def receive(self, text_data=None, bytes_data=None):
#         ic("RECEIVE =", text_data)
#         count = int(text_data)
#         count += 1
#         self.send(text_data=json.dumps({'count': count}))
#
#     def disconnect(self, close_code):
#         ic("DISCONNECT")

# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from icecream import ic


class TestConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'testConsumer'
        self.room_group_name = 'testConsumerGroup'
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.room_group_name)
        self.accept()
        self.send(text_data=json.dumps({'count': 10}))
        ic("Notification")

    def receive(self, text_data=None, bytes_data=None):
        ic("Dostal", text_data)

    def disconnect(self, close_code):
        pass

