import os
import requests
import json
from pprint import pprint as pp

class Facebook:
    def __init__(self) -> None:
        self.ACCESS_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')


    def send_message(self, message, recipient_id):
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",

            params={"access_token": self.ACCESS_TOKEN},

            headers={"Content-Type": "application/json"},

            data=json.dumps({
            "recipient": {"id": recipient_id},
            "message": {"text": message}
        }))

        return r.json()

    def profile(self, psid):
        
        # psid = "5073425082670155"

        params = {
            "fields": "first_name,last_name,profile_pic",
            "access_token": self.ACCESS_TOKEN
        }
        r = requests.get(f"https://graph.facebook.com/{psid}", params=params)

        return r.json()
        # {
        # 'first_name': 'Mundia',
        # 'id': '5073425082670155',
        # 'last_name': 'Mwala',
        # 'profile_pic': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?psid=5073425082670155&width=1024&ext=1644412180&hash=AeTIsMlUAGiCvosj5Bk'
        # }
