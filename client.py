import os

from dotenv import load_dotenv
import json

from pysteamauth.auth import Steam


class Client:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('STEAM_USERNAME')
        self.password = os.getenv('STEAM_PASSWORD')
        self.secret = json.loads(os.getenv('STEAM_SECRET'))
        self.steam_client = Steam(login=self.username, password=self.password, shared_secret=self.secret['shared_secret'])

    async def status(self):
        print(id(self.steam_client))
        try:
            print(f"Is Steam client logged in: {await self.steam_client.is_authorized()}")
        except TypeError as e:
            print(e)
