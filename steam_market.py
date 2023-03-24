import json
from urllib.parse import quote


class SteamMarket:
    def __init__(self, client):
        self.steam_client = client

    async def get_items(self, query, start=0, count=10, sort_col='', sort_dir='', app_id=730):

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

        response = await self.steam_client.request("https://steamcommunity.com/market/search/render", params=params)
        print(type(response))  # TODO: DELETE THIS LATER
        data = json.loads(response)

        query_url = f"https://steamcommunity.com/market/search?appid={app_id}&q={quote(query)}#p1_{sort_col}_{sort_dir}"
        result = {
            "success": data['success'],
            "start": data['start'],
            "pagesize": data['pagesize'],
            "total_count": data['total_count'],
            "query": query,
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
