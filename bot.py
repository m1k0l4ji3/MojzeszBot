import os

from discord.ext import commands
from dotenv import load_dotenv
from command_func import *
from steam_market import SteamMarket


def run_discord_bot():
    load_dotenv()
    token = os.getenv('TOKEN')
    aliases = load_aliases()

    steam_client = SteamMarket()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='-', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}\n")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.typing()
            await ctx.send(f"`Invalid Command:\n \"{ctx.message.content}\" command is not found`")
        print(error)

    # Steam commands
    @bot.command()
    async def gets(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_steam_query(query, aliases)
        data = steam_client.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_gets_response(data)
        embed = create_embed(data)

        await ctx.send(f'{response}', embed=embed)

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
        data = steam_client.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_get_embeds(data)
        for embeds_list in response:
            await ctx.send(embeds=embeds_list)

        embed = create_embed(data)
        await ctx.send(embed=embed)

    @get.error
    async def get_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"`Missing argument:\n\"{ctx.message.content}\" command requires to pass query as an argument`")
        print(error)

    bot.run(token)


if __name__ == "__main__":
    print("Running version 1.3.0")
    run_discord_bot()
