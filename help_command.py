import json

import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.command_info = get_command_info()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help",
                              description="Type `-help [command]` for more info on a command.\n\nAvailable commands:",
                              color=0x644A3B)
        for command in self.command_info:
            arguments_short = self.command_info[command]['arguments_short']

            embed.add_field(name="", value=f"\t`-{command} {arguments_short}`", inline=False)
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        title = command.name
        description = self.command_info[command.name]['description']
        arguments_desc = self.command_info[command.name]['arguments_desc']
        example = self.command_info[command.name]['example']

        embed = discord.Embed(title=title,
                              description=description,
                              color=0x644A3B)
        embed.add_field(name="Arguments:", value=arguments_desc)
        if example:
            embed.add_field(name="Example:", value=example)
        await self.get_destination().send(embed=embed)


def get_command_info():
    with open("commands.json", "r") as f:
        return json.load(f)
