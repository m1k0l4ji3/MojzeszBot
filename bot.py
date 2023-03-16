import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from steam_func import MyClient


def prepare_query(message_query):
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
    return query, count, sort_column, sort_directory


def create_gets_response(data):
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


def create_embed(data):
    return discord.Embed(title=f"Results for: \"{data['query']}\"", url=data['query_url'])


def create_get_embeds(data):
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


def run_discord_bot():
    load_dotenv()
    token = os.getenv('TOKEN')

    steam_user = MyClient()
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='-', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}\n")

    @bot.command()
    async def gets(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_query(query)
        data = steam_user.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_gets_response(data)
        embed = create_embed(data)

        await ctx.send(f'{response}', embed=embed)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.typing()
            await ctx.send(f"`Invalid Command:\n \"{ctx.message.content}\" command is not found`")
        print(error)

    @bot.command()
    async def get(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_query(query)
        data = steam_user.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_get_embeds(data)
        for embeds_list in response:
            await ctx.send(embeds=embeds_list)

        embed = create_embed(data)
        await ctx.send(embed=embed)

    @get.error
    @gets.error
    async def get_gets_errors(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"`Missing argument111:\n\"{ctx.message.content}\" command requires to pass query as an argument`")
        print(error)

    bot.run(token)
