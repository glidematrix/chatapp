import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class WhatsApp:

    def __init__(self) -> None:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.client = Client(account_sid, auth_token)

    def send(self, message: str, phone: str) -> None:
        message = self.client.messages.create(
                                    from_='whatsapp:+14155238886',
                                    body=message,
                                    to=phone
                                )

        print(message.sid)




