from tornado.websocket import WebSocketHandler
from tornado.websocket import WebSocketClosedError
from pprint import pprint as pp
from uuid import uuid4
import json


class WebSocket(WebSocketHandler):

    clients = set()
    agents = set()

    def check_origin(self, origin):
        return True

    def open(self):
        try:
            token = self.get_query_argument("token", default=None)

            self.id = uuid4().hex

            self.is_agent = False
    
            if token:
                self.is_agent = True
                self.agents.add(self)
            else:
                self.clients.add(self)

                try:
                    self.write_message(
                        json.dumps({
                            'type':'SET_UID',
                            'uid': self.id,
                            'username': getattr(self, 'username', 'Anonymous')
                        })
                    )
                    self.write_message(
                        json.dumps({
                            'type':'MSG',
                            'message': "Hello there! What's your name?",
                            'next_action': 'SET_NAME'
                        })
                    )
                except WebSocketClosedError as e:
                    self.clients.remove(self)

            client_data = [{
                'username' : getattr(client, 'username', 'Anonymous') ,
                'client_id' : client.id ,
                } for client in self.clients ]
            
            for agent in self.agents:
                try:
                    agent.write_message(json.dumps({
                        'agent_id': self.id,
                        'clients': client_data
                    }))
                except WebSocketClosedError as e:
                    self.agents.remove(agent)

        except WebSocketClosedError as e:
            print('WebSocketClosedError')
            print(str(e))
        except Exception as e:
            print(str(e))

    
    def on_message(self, message):

        try:
            data = json.loads(message)
            pp(data)
            type = data.get('type')
            rid = data.get('to')
            message = data.get('message', '').strip()

            print(f'To Recipient: {rid}')
            print(f'From User: {self.id}')

            if type == 'MSG':
                clients = [*self.clients, *self.agents]
                for client in clients:
                    if not rid and client.is_agent and (self != client):
                        client.write_message(
                                json.dumps({
                                    'type': type,
                                    'message': message,
                                    'sender': self.id,
                                    'is_agent': self.is_agent,
                                }
                            ))
                    else:
                        if rid == client.id:
                            client.write_message(
                                json.dumps({
                                    'type': type,
                                    'message': message,
                                    'sender': self.id,
                                    'is_agent': self.is_agent,
                                }
                            ))

            if type == 'ACTIVE_CHAT':
                client_id = data.get('client_id')
                for client in self.clients:
                    if client.id == client_id:
                        self.write_message(
                            json.dumps({
                                'username': getattr(client, 'username', 'Anonymous'),
                                'client_id': client.id,
                                'type': type
                            })
                        )

            if type == 'SET_NAME':
                self.username = message
                client_ids = [{
                    'username': getattr(client, 'username', 'Anonymous'),
                    'client_id': client.id
                } for client in self.clients ]
                
                for agent in self.agents:

                    agent.write_message(json.dumps({
                        'agent_id': self.id,
                        'clients': client_ids
                    }))
                
                username = self.username if self.username != 'Anonymous' else 'there'
                self.write_message(
                        json.dumps({
                            'type': 'MSG',
                            'message': f'Hello {username}! One of our agent will chat with you shortly.',
                            'sender': self.id,
                            'is_agent': self.is_agent,
                        }
                    ))

        except Exception as e:
            print(str(e))

    def on_close(self):
        print("Socket closed.")
        try:

            self.clients.remove(self)

            client_ids = [{
                'username': client.username,
                'client_id': client.id
            } for client in self.clients ]
            
            for agent in self.agents:

                agent.write_message(json.dumps({
                    'agent_id': self.id,
                    'clients': client_ids
                }))

        except Exception as e:
            pass

    @classmethod
    def write_to_clients(cls, msg):
        for client in cls.clients:
            client.write_message(json.dumps({
                "msg": msg
            }))