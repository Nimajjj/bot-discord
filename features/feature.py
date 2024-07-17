import discord 

from bot.command import Command
from bot.client import Client


class Feature:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.client.register_feature(self)


    def setup(self) -> None:
        pass


    async def on_message(self, message: discord.Message) -> None:
        pass