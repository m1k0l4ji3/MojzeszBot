import json
from urllib.parse import quote
from bufflogin import Buff


class BuffMarket:
    def __init__(self, client):
        self.steam_client = client
        self.buff_client = Buff(self.steam_client)

    async def login(self):
        if await self.buff_client.is_authorized():
            return
        try:
            await self.buff_client.login_to_buff()
            print("[Buff163] Login succeed")
        except Exception as e:
            print(e)

    async def get_items(self, search, page=1, page_size='10', sort_by="", game='csgo'):
        while not await self.buff_client.is_authorized():
            await self.login()

        params = {
            "search": search,
            "page": page,
            "game": game,
            "page_size": page_size,
            "use_suggestion": 0
        }
        if sort_by != "":
            params['sort_by'] = sort_by

        response = await self.buff_client.request("https://buff.163.com/api/market/goods", params=params)
        data = json.loads(response)

        query_url = f"https://buff.163.com/market/{game}#tab=selling&page_num={page}&search={quote(search)}"
        result = {
            "success": data['code'] == "OK",
            "start": data['data']['page_num'],
            "pagesize": data['data']['page_size'],
            "total_count": data['data']['total_count'],
            "query": search,
            "query_url": query_url,
            "results": []
        }

        for item in data['data']['items']:
            result['results'].append({
                "hash_name": item['market_hash_name'],
                "item_url": f"https://buff.163.com/goods/{item['id']}",
                "sell_listings": f"{item['sell_num']:,}".replace(',', ' '),
                "sell_price_text": f"¥ {item['sell_min_price']}",
                "icon_url": item['goods_info']['original_icon_url']
            })
        return result
