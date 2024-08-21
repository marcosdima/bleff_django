# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.urls import reverse

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
        elif event_type == 'chosen_word':
            self.handle_chosen_word()
        elif event_type == 'start_game':
            self.handle_start_game()
        elif event_type == 'guesses_ready':
            self.handle_guesses_ready()


    def handle_player_join(self, data):
        player_username = data['player_username']

        async_to_sync(self.channel_layer.group_send)(
            self.game_name, 
            {
                "type": "player_join",
                'player_username': player_username
            }
        )


    def handle_chosen_word(self):
        async_to_sync(self.channel_layer.group_send)(
            self.game_name, 
            {
                "type": "chosen_word",
            }
        )


    def handle_start_game(self):
        async_to_sync(self.channel_layer.group_send)(
            self.game_name, 
            {
                "type": "start_game",
            }
        )


    def handle_guesses_ready(self):
        async_to_sync(self.channel_layer.group_send)(
            self.game_name, 
            {
                "type": "guesses_ready",
            }
        )


    def start_game(self, event):
        game_id = int(self.game_id)
        self.send(text_data=json.dumps({"start_game": True, "url": reverse('game:hand', args=(game_id,))}))


    def player_join(self, event):
        player_username = event['player_username']

        self.send(text_data=json.dumps({"player_username": player_username}))


    def chosen_word(self, event):
        self.send(text_data=json.dumps({"chosen_word": True}))


    def new_guess(self, event):
        new_guess = event['new_guess']
        self.send(text_data=json.dumps({"new_guess": new_guess}))


    def new_vote(self, event):
            new_vote = event['new_vote']
            self.send(text_data=json.dumps({"new_vote": new_vote}))


    def guesses_ready(self, event):
        self.send(text_data=json.dumps({"guesses_ready": True}))


    def hand_finished(self, event):
        self.send(text_data=json.dumps({"hand_finished": True}))
