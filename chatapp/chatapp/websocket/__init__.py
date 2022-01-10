from tornado.websocket import WebSocketHandler
from tornado.websocket import WebSocketClosedError
from pprint import pprint as pp
from uuid import uuid4
import json
# from collections import OrderedDict
# import collections
from dataclasses import dataclass
import traceback
import logging
from chatapp.channels.whatsapp import WhatsApp
from chatapp.channels.facebook import Facebook

logger = logging.getLogger(__name__)

CHAT_CHANNEL_WEB = 'WEB'
CHAT_CHANNEL_WHATSAPP = 'WHATSAPP'
CHAT_CHANNEL_FB = 'FB'


class HashableDict(dict):
    """Class to create hashable dictionary objects to be used with set
    """

    def __key(self):
        return tuple((k,self[k]) for k in sorted(self))
    def __hash__(self):
            return hash(self.__key())
    def __eq__(self, other):
        return self.__key() == other.__key()

class WebSocket(WebSocketHandler):
    """WebSocket class    
    """

    # Dummy storage. TODO: use redis
    clients = set()
    agents = set()

    def check_origin(self, origin):
        return True

    def open(self):
        """Handle opening websockets
        
        """
        try:
            token = self.get_query_argument("token", default=None)

            self.id = uuid4().hex

            self.is_agent = False
            self.chat_channel = CHAT_CHANNEL_WEB
    
            if token:
                self.is_agent = True
                self.agents.add(self)
            else:
                self.clients.add(self)

                try:
                    # send and set client uuid after openning connections
                    self.write_message(
                        json.dumps({
                            'type':'SET_UID',
                            'uid': self.id,
                            'username': getattr(self, 'username', 'Anonymous')
                        })
                    )
                    # request for client name
                    self.write_message(
                        json.dumps({
                            'type':'MSG',
                            'message': "Hello there! What's your name?",
                            'next_action': 'SET_NAME'
                        })
                    )
                except WebSocketClosedError as e:
                    # remove closed sockets from client set
                    self.clients.remove(self)

            # Get connected client list
            clients_data = [{
                'username' : getattr(client, 'username', 'Anonymous') ,
                'client_id' : client.id ,
                'channel': client.chat_channel,
                } for client in self.clients ]
            
            # agents_copy = self.agents.copy()# fix - Error: RuntimeError: Set changed size during iteration
            agents_copy = self.agents

            # send connected client list to agents
            for agent in agents_copy:
                try:
                    agent.write_message(json.dumps({
                        'agent_id': self.id,
                        'clients': clients_data
                    }))
                except WebSocketClosedError as e:
                    # remove closed sockets from agent set
                    # logger.error(traceback.format_exc())
                    self.agents.remove(agent)

        except WebSocketClosedError as e:
            logger.error(traceback.format_exc())
        except Exception as e:
            logger.error(traceback.format_exc())

    
    def on_message(self, message):
        """Process incoming messages
        
        This function has three action types
        1. MSG - This contains messages meant to be transafered between an Agent and Client
        2. ACTIVE - This allows the Agent to engage a different Client 
        3. SET_NAME - This allows Client's to set they names
        """
        try:
            data = json.loads(message)
            type = data.get('type') # message action type
            rid = data.get('to') # recipient id or whatsapp number
            message = data.get('message', '').strip() # message text

            logger.info('DATA: {data}')

            logger.info(f'To Recipient: {rid}')
            logger.info(f'From User: {self.id}')

            # Handle action 'MSG'
            if type == 'MSG':
                clients = [*self.clients, *self.agents]
                for client in clients:

                    # Send Client message to all Agents
                    if not rid and client.is_agent and (self != client):
                        if client.chat_channel ==  CHAT_CHANNEL_WEB:
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
                            if client.chat_channel ==  CHAT_CHANNEL_WEB:
                                client.write_message(
                                    json.dumps({
                                        'type': type,
                                        'message': message,
                                        'sender': self.id,
                                        'is_agent': self.is_agent,
                                    }
                                ))

                            if client.chat_channel ==  CHAT_CHANNEL_WHATSAPP:
                                    wa = WhatsApp()

                                    wa.send(
                                        message,
                                        phone=rid
                                    )

                            if client.chat_channel ==  CHAT_CHANNEL_FB:
                                fb = Facebook()

                                res = fb.send_message(
                                    message,
                                    recipient_id=rid
                                )

                                logger.info(res)

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
                    'client_id': client.id,
                    'channel': client.chat_channel,
                } for client in self.clients ]
                
                for agent in self.agents:

                    agent.write_message(json.dumps({
                        'agent_id': self.id,
                        'clients': client_ids,
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
            logger.error(traceback.print_exc())

    def on_close(self):
        """Handle closing sockets
        
        """
        logger.info(f"closing socket: {self.id}")
        try:

            self.clients.remove(self)

            client_ids = [{
                'username': getattr(client, 'username', 'Anonymous'),
                'client_id': client.id,
                'channel': client.chat_channel,
            } for client in self.clients ]
            
            for agent in self.agents:

                agent.write_message(json.dumps({
                    'agent_id': self.id,
                    'clients': client_ids
                }))

        except Exception as e:
            logger.error(traceback.print_exc())

    @classmethod
    def write_to_clients(cls, message):
        for client in cls.clients:
            if client.chat_channel ==  CHAT_CHANNEL_WEB:
                client.write_message(json.dumps({
                    "msg": message
                }))

    @classmethod
    def write_to_agents(cls, message, sender=None, channel=CHAT_CHANNEL_WHATSAPP):
        """Send message from non web Clients(e.g from whatsapp) to Agents
        
        """
        if sender:
            client_data = HashableDict()
            client_data.id = sender
            client_data.username = sender
            client_data.chat_channel = channel
            
            try:
                clients = [{
                    'username': getattr(client, 'username', 'Anonymous'),
                    'id': client.id,
                    'client_id': client.id,
                    'channel': getattr(client, 'channel', 'WEB'),
                } for client in cls.clients ]

                if not any([ c.get('id', None)  ==  sender for c in clients]):

                    if channel == CHAT_CHANNEL_FB:
                        fb = Facebook()
                        fb_profile = fb.profile(
                            sender
                        )
                        logger.info(fb_profile)
                        first_name = fb_profile.get('first_name')
                        last_name =  fb_profile.get('last_name')
                        client_data.username = f'{first_name} {last_name} (FB)'

                    cls.clients.add(client_data)

                    clients.append({
                        'username': getattr(client_data, 'username', 'Anonymous'),
                        'client_id': client_data.id,
                        'channel': getattr(client_data, 'channel', 'WEB'),
                    } )
                    
                    for agent in cls.agents:

                        try:
                            agent.write_message(json.dumps({
                                'agent_id': agent.id,
                                'clients': clients,
                                "message": message,
                                "type": "ACTIVE_CHAT",
                                "channel": channel,
                                'username': getattr(client_data, 'username', 'Anonymous'),
                                'client_id': client_data.id,
                            }))
                        except WebSocketClosedError as e:
                            cls.agents.remove(agent)
            except Exception as e:
                logger.error(traceback.print_exc())


            for agent in cls.agents:
                agent.write_message(json.dumps({
                    "message": message,
                    "type": "MSG",
                    "cbannel": channel
                }))