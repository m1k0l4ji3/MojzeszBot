import discord
import json


def prepare_steam_query(message_query: str, aliases: dict):
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
            query = ""
            for word in param.split():
                if word in aliases:
                    word = aliases[word]
                query += word + " "

    return query[:-1], count, sort_column, sort_directory


def prepare_buff_query(message_query: str, aliases: dict):
    parameters = message_query.split("/")
    parameters_lower = [param.lower() for param in parameters]
    sort_by = search = ""
    page_size = 10

    for param in parameters_lower:
        if param in ("price", "quantity, name"):
            pass
        elif param in ("asc", "desc"):
            sort_by = f"price.{param}"
        elif param.isdecimal():
            page_size = int(param)
            if page_size > 20:
                page_size = 20
        elif param != "":
            for word in param.split():
                if word in aliases:
                    word = aliases[word]
                search += word + " "

    return search[:-1], page_size, sort_by


def prepare_chart_query(message_query: str):
    aliases = {"w": "week", "m": "month", "y": "year", "a": "all"}
    chart_types = []
    parameters = message_query.split("/")
    name = parameters.pop(0)

    if len(parameters) == 0:
        chart_types.append("month")

    parameters_lower = [param.lower() for param in parameters]

    for param in parameters_lower:
        if param in ("week", "month", "year", "all"):
            chart_types.append(param)
        elif param in ("w", "m", "y", "a"):
            chart_types.append(aliases[param])

    return name, chart_types


def create_response_text(data: dict):
    if data['results']:
        lengths = [(len(item['hash_name']), len(item['sell_price_text'])) for item in data['results']]
        max_name_length = max(lengths, key=lambda elem: elem[0])[0]
        max_price_length = max(lengths, key=lambda elem: elem[1])[1]

        response = f"```"
        for item in data['results']:
            response += f"{item['hash_name'].ljust(max_name_length + 1)}" \
                        f"{item['sell_price_text'].ljust(max_price_length)} | {item['sell_listings']}\n"
        response += "```"
        return response
    else:
        return "`There were no items matching your search. Try again with different keywords.`"


def create_results_embed(data: dict, image: str):
    file = discord.File(f"./images/{image}", filename=image)

    embed = discord.Embed(title=f"Results for: \"{data['query']}\"", url=data['query_url'], color=0x644A3B)
    embed.set_thumbnail(url=f"attachment://{image}")
    return embed, file


def create_response_embeds(data: dict):
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
