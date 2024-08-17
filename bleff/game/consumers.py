# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_name = f'game_{self.game_id}'

        async_to_sync(self.channel_layer.group_add)(
            self.game_name, self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.game_name, self.channel_name
        )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json['event_type']

        if event_type == 'player_join':
            self.handle_player_join(text_data_json)


    def handle_player_join(self, data):
        player_username = data['player_username']

        async_to_sync(self.channel_layer.group_send)(
            self.game_name, 
            {
                "type": "player_join",
                'player_username': player_username
            }
        )


    def player_join(self, event):
        player_username = event['player_username']

        self.send(text_data=json.dumps({"player_username": player_username}))