import os
from typing import List
from datetime import timedelta

import pandas as pd
import discord

from .config import Config
from .command import Command


CHANNEL_ID = 1252164978539106374
TIME_GAME_MINUTES: int = 30
DISCUSSIONS_PATH: str = "data/discussions"


class Client:
    def __init__(self, config: Config):
        self.config = config
        self.commands: List[Command] = []
        self.bot = discord.Bot(intents=discord.Intents.all())
        self.features: list = []


    def run(self) -> None:
        self._setup_client()
        self.bot.run(self.config.load_token())


    def register_command(self, command: Command) -> None:
        self.commands.append(command)


    def register_feature(self, ft) -> None:
        self.features.append(ft)
    

    def get_channel(self, id: int = 0) -> discord.channel:
        channel_id: int = id if id else CHANNEL_ID
        channel: discord.channel = self.bot.get_channel(channel_id)
        assert channel, f"[ERROR] Channel with ID {channel_id} not found."
        return channel
    

    def _setup_client(self) -> None:
        @self.bot.event
        async def on_ready():
            print(f"[ INFO] {self.bot.user} is ready and online!")

        @self.bot.event
        async def on_message(message: discord.Message):
            # return if message is from bot
            if message.author == self.bot.user:
                return
            
            # call on_Message method of all features
            for ft in self.features:
                await ft.on_message(message=message)    
    
        # create all commands
        for command in self.commands:
            print(f"[ INFO] Registering slash command `/{command.name}`")
            self.bot.slash_command(
                name=command.name,
                description=command.description,
                options=command.options
            )(command.callback)
        
    
    def group_messages_into_discussions(self, messages: list) -> list:
        discussions: list = []
        current_discussion: list = []

        for __, (timestamp, author, message) in enumerate(messages):
            if not current_discussion:
                current_discussion.append((timestamp, author, message))
            else:
                last_message_time = current_discussion[-1][0]
                if (timestamp - last_message_time) <= timedelta(minutes=TIME_GAME_MINUTES):
                    current_discussion.append((timestamp, author, message))
                else:
                    discussions.append(current_discussion)
                    current_discussion = [(timestamp, author, message)]

        if current_discussion:
            discussions.append(current_discussion)

        return discussions
    

    def store_discussions(self, discussions: list) -> None:
        if not os.path.exists(DISCUSSIONS_PATH):
            os.makedirs(DISCUSSIONS_PATH)

        for i, messages in enumerate(discussions):
            df = pd.DataFrame(messages, columns=['Timestamp', 'Author', 'Message'])
            df.to_csv(f'{DISCUSSIONS_PATH}/discussion_{i}.csv', index=False)
    