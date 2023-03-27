import asyncio
import os

from discord.ext import commands
from dotenv import load_dotenv
from command_func import *
from steam_market import SteamMarket
from buff_market import BuffMarket
from client import Client


def run_discord_bot():
    load_dotenv()
    token = os.getenv('TOKEN')
    aliases = load_aliases()

    client = Client()
    steam_market = SteamMarket(client.steam_client)
    buff_market = BuffMarket(client.steam_client)

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='-', intents=intents)

    @bot.event
    async def on_ready():
        print("1")
        await steam_market.login()
        await asyncio.sleep(5)
        print("2")
        await buff_market.login()
        print("-"*30)
        print(f"Logged in as {bot.user}\n")

    # Steam commands
    @bot.command()
    async def gets(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_steam_query(query, aliases)
        data = await steam_market.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_response_text(data)
        embed, image = create_results_embed(data, ctx.invoked_with)

        await ctx.send(f'{response}', embed=embed, file=image)

    @gets.error
    async def gets_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"`Missing argument:\n\"{ctx.message.content}\" command requires to pass query as an argument`")
        print(error)

    @bot.command()
    async def get(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_steam_query(query, aliases)
        data = await steam_market.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_response_embeds(data)
        for embeds_list in response:
            await ctx.send(embeds=embeds_list)

        embed, image = create_results_embed(data, ctx.invoked_with)
        await ctx.send(embed=embed, file=image)

    @get.error
    async def get_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"`Missing argument:\n\"{ctx.message.content}\" command requires to pass query as an argument`")
        print(error)

    # Buff commands
    @bot.command()
    async def buffs(ctx, *, query):
        await ctx.typing()

        search, page_size, sort_by = prepare_buff_query(query, aliases)
        data = await buff_market.get_items(search, page_size=page_size, sort_by=sort_by)

        response = create_response_text(data)
        embed, image = create_results_embed(data, ctx.invoked_with)

        await ctx.send(f'{response}', embed=embed, file=image)

    @bot.command()
    async def buff(ctx, *, query):
        await ctx.typing()

        search, page_size, sort_by = prepare_buff_query(query, aliases)
        data = await buff_market.get_items(search, page_size=page_size, sort_by=sort_by)

        response = create_response_embeds(data)
        for embeds_list in response:
            await ctx.send(embeds=embeds_list)

        embed, image = create_results_embed(data, ctx.invoked_with)
        await ctx.send(embed=embed, file=image)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.typing()
            await ctx.send(f"`Invalid Command:\n \"{ctx.message.content}\" command is not found`")
        print(error)

    bot.run(token)


if __name__ == "__main__":
    print("Running version 2.0.1")
    run_discord_bot()
