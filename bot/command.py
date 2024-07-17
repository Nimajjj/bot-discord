import discord

from typing import Callable, List


class Command:
    def __init__(self, name: str, description: str, callback: Callable, options: List[discord.Option] = None):
        self.name = name
        self.description = description
        self.callback = callback
        self.options = options or []