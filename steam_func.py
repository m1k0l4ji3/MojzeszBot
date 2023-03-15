import json

from requests import get
from steam.guard import SteamAuthenticator
from urllib.parse import quote


def get_items(query, start=0, count=10, sort_col='', sort_dir='', app_id=730, login_secure=''):
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
    headers = {
        "Cookie": f'steamLoginSecure={login_secure}'
    }

    response = get("https://steamcommunity.com/market/search/render", params=params, headers=headers)
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


def get_cookie(user, username, password, secret):
    sa = SteamAuthenticator(secret) if secret else None
    twofactor_code = sa.get_code() if sa is not None else ""

    print(f"Is already logged on: {user.logged_on}")
    if not user.logged_on:
        print(f"Login attempt for {username}")
        try:
            user.cli_login(password=password, twofactor_code=twofactor_code)
        except TypeError:
            print("Can't login now, try later...")
        print(f"Successfully logged in as: {username}\n")

    cookies = user.session.cookies
    login_secure = cookies.get_dict()['steamLoginSecure']

    return login_secure
