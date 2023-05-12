import asyncio
import os

from discord.ext import commands
from dotenv import load_dotenv

from buff_market import BuffMarket
from command_func import *
from help_command import CustomHelpCommand
from steam_market import SteamMarket
from chart_creator import ChartCreator


def run_discord_bot():
    load_dotenv()
    token = os.getenv('TOKEN')
    aliases_dict = load_aliases()

    steam_market = SteamMarket()
    buff_market = BuffMarket(steam_market.steam_client)
    creator = ChartCreator()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='-', intents=intents, help_command=CustomHelpCommand())

    @bot.event
    async def on_ready():
        print("Steam login attempt:")
        await steam_market.login()
        await asyncio.sleep(5)

        print("Buff163 login attempt:")
        await buff_market.login()
        print("-" * 30)
        print(f"Logged in as {bot.user}\n")

    # Steam commands
    @bot.command()
    async def gets(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_steam_query(query, aliases_dict)
        data = await steam_market.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_response_text(data)
        embed, image = create_results_embed(data, ctx.invoked_with)

        await ctx.send(f'{response}', embed=embed, file=image)

    @bot.command()
    async def get(ctx, *, query):
        await ctx.typing()

        query, count, sort_col, sort_dir = prepare_steam_query(query, aliases_dict)
        data = await steam_market.get_items(query, count=count, sort_col=sort_col, sort_dir=sort_dir)

        response = create_response_embeds(data)
        for embeds_list in response:
            await ctx.send(embeds=embeds_list)

        embed, image = create_results_embed(data, ctx.invoked_with)
        await ctx.send(embed=embed, file=image)

    @bot.command()
    async def chart(ctx, *, query):
        await ctx.typing()

        name, chart_types = prepare_chart_query(query)
        creator.get_charts(name, chart_types)
        for chart_type in chart_types:
            file = discord.File(f"./images/{chart_type}.png", filename=f"{chart_type}.png")
            await ctx.send(file=file)

    # Buff commands
    @bot.command()
    async def buffs(ctx, *, query):
        await ctx.typing()

        search, page_size, sort_by = prepare_buff_query(query, aliases_dict)
        data = await buff_market.get_items(search, page_size=page_size, sort_by=sort_by)

        response = create_response_text(data)
        embed, image = create_results_embed(data, ctx.invoked_with)

        await ctx.send(f'{response}', embed=embed, file=image)

    @bot.command()
    async def buff(ctx, *, query):
        await ctx.typing()

        search, page_size, sort_by = prepare_buff_query(query, aliases_dict)
        data = await buff_market.get_items(search, page_size=page_size, sort_by=sort_by)

        response = create_response_embeds(data)
        for embeds_list in response:
            await ctx.send(embeds=embeds_list)

        embed, image = create_results_embed(data, ctx.invoked_with)
        await ctx.send(embed=embed, file=image)

    # general commands
    @bot.command()
    async def aliases(ctx):
        await ctx.typing()
        embed = discord.Embed(title="Aliases", color=0x644A3B)
        for alias in aliases_dict:
            embed.add_field(name="", value=f"`{alias}` - {aliases_dict[alias]}")
        await ctx.send(embed=embed)

    @bot.event
    async def on_command_error(ctx, error):
        await ctx.typing()
        command = ctx.invoked_with
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(embed=discord.Embed(title="Invalid Command:",
                                               description=f"`{command}` command is not found.\n\nUse `help` to list all available commands.",
                                               color=0xdb0f27))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(title="Missing Argument:",
                                               description=f"`{command}` command requires to pass an argument.\n\nUse `help [command]` to to get more details about the command.",
                                               color=0xdb0f27))
        else:
            print(error)
            await ctx.send(embed=discord.Embed(title="Unexpected error:",
                                               description=f"`{command}` command caused unidentified error.\n\nTry again later.",
                                               color=0xdb0f27))

    bot.run(token)


if __name__ == "__main__":
    print("Running version 2.4.0")
    run_discord_bot()
