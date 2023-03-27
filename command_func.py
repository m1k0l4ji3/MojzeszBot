import discord
import json


def prepare_steam_query(message_query, aliases):
    parameters = message_query.split("/")
    parameters_lower = [param.lower() for param in parameters]
    sort_column = sort_directory = query = ""
    count = 10

    for param in parameters_lower:
        if param in ("name", "price", "quantity"):
            sort_column = param
        elif param in ("asc", "desc"):
            sort_directory = param
        elif param.isdecimal():
            count = int(param)
            if count > 20:
                count = 20
        elif param != "":
            query = param.strip()
            if query in aliases:
                query = aliases[query]
    return query, count, sort_column, sort_directory


def prepare_buff_query(message_query, aliases):
    parameters = message_query.split("/")
    parameters_lower = [param.lower() for param in parameters]
    sort_by = search = ""
    page_size = 10
    for param in parameters_lower:
        if param in ("price", "quantity, name"):
            pass
        if param in ("asc", "desc"):
            sort_by = f"price.{param}"
        elif param.isdecimal():
            page_size = int(param)
            if page_size > 20:
                page_size = 20
        elif param != "":
            search = param.strip()
            if search in aliases:
                search = aliases[search]
    return search, page_size, sort_by


def create_response_text(data):
    if data['results']:
        lengths = [(len(item['hash_name']), len(item['sell_price_text'])) for item in data['results']]
        max_name_length = max(lengths, key=lambda elem: elem[0])[0]
        max_price_length = max(lengths, key=lambda elem: elem[1])[1]

        response = f"```"
        for item in data['results']:
            response += f"{item['hash_name'].ljust(max_name_length + 1)}{item['sell_price_text'].ljust(max_price_length)} | {item['sell_listings']}\n"
        response += "```"
        return response
    else:
        return "`There were no items matching your search. Try again with different keywords.`"


def create_results_embed(data, cmd_name):
    if cmd_name in ("buff", "buffs"):
        image = "buff_icon.png"
    else:
        image = "steam_icon.png"
    file = discord.File(f"./images/{image}", filename=image)

    embed = discord.Embed(title=f"Results for: \"{data['query']}\"", url=data['query_url'])
    embed.set_thumbnail(url=f"attachment://{image}")
    return embed, file


def create_response_embeds(data):
    if data['results']:
        embeds_lists = []
        embeds_list = []
        for item in data['results']:
            if len(embeds_list) == 10:
                embeds_lists.append(embeds_list)
                embeds_list = []
            embed = discord.Embed(title=item['hash_name'],
                                  url=item['item_url'],
                                  color=0x644A3B)
            embed.set_thumbnail(url=item['icon_url'])
            embed.add_field(name=f"{item['sell_price_text']}\t{item['sell_listings']}", value="")

            embeds_list.append(embed)
        embeds_lists.append(embeds_list)
        return embeds_lists
    else:
        return [[discord.Embed(title="There were no items matching your search. Try again with different keywords.",
                               color=0x644A3B)]]


def load_aliases():
    with open("aliases.json", "r") as f:
        return json.load(f)
