import json
import os

from requests import get
from steam.guard import SteamAuthenticator
from urllib.parse import quote
import steam.webauth as wa
from dotenv import load_dotenv


class MyClient:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('STEAM_USERNAME')
        self.password = os.getenv('STEAM_PASSWORD')
        self.secret = json.loads(os.getenv('STEAM_SECRET'))
        self.steam_user = wa.WebAuth(self.username)
        self.cookie = self.get_cookie()

    def get_items(self, query, start=0, count=10, sort_col='', sort_dir='', app_id=730):

        while not self.steam_user.logged_on:
            self.get_cookie()

        params = {
            "query": query,
            "start": start,
            "count": count,
            "search_descriptions": 0,
            "sort_column": sort_col,
            "sort_dir": sort_dir,
            "appid": app_id,
            "norender": 1
        }

        response = get("https://steamcommunity.com/market/search/render", params=params, cookies=self.cookie)
        data = json.loads(response.text)

        query_url = f"https://steamcommunity.com/market/search?appid={app_id}&q={quote(data['searchdata']['query'])}"
        result = {
            "success": data['success'],
            "start": data['start'],
            "pagesize": data['pagesize'],
            "total_count": data['total_count'],
            "query": data['searchdata']['query'],
            "query_url": query_url,
            "results": []
        }

        for item in data['results']:
            result['results'].append({
                "hash_name": item['hash_name'],
                "item_url": f"https://steamcommunity.com/market/listings/{app_id}/{quote(item['hash_name'])}",
                "sell_listings": f"{item['sell_listings']:,}".replace(',', ' '),
                "sell_price_text": item['sell_price_text'],
                "icon_url": f"https://steamcommunity-a.akamaihd.net/economy/image/{item['asset_description']['icon_url']}"
            })
        return result

    def get_cookie(self):
        sa = SteamAuthenticator(self.secret)
        twofactor_code = sa.get_code()

        print(f"Is steam user [{self.username}] already logged on: {self.steam_user.logged_on}")
        if not self.steam_user.logged_on:
            print(f"Login attempt for {self.username}")
            try:
                self.steam_user.cli_login(password=self.password, twofactor_code=twofactor_code)
                print(f"Successfully logged in as: {self.username}\n")
            except TypeError:
                print("Can't login now, try later...")

        return self.steam_user.session.cookies

siema =MyClient()

print(siema.get_items("antwerp capsule"))